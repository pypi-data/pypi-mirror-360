use log::{debug, error};
use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::types::{
    PyAny, PyAnyMethods, PyBytes, PyBytesMethods, PyDictMethods, PyIterator, PyString,
    PyStringMethods, PyTuple,
};
use pyo3::{Bound, Py, PyErr, PyObject, PyResult, Python};
use pyo3_ffi as ffi;
use std::io::{self, Write};

use crate::filewrapper::{FileWrapper, SendFile};
use crate::globals::SharedWSGIOptions;
use crate::request::{WSGIRequest, REQUEST_METHOD};
use crate::startresponse::{StartResponse, WriteResponse};
use crate::transport::{broken_pipe, would_block, Connection, HTTP11Connection};

pub const HTTP500: &[u8] = b"HTTP/1.1 500 Internal Server Error\r\n\r\n";
pub const HTTP400: &[u8] = b"HTTP/1.1 400 Bad Request\r\n\r\n";

fn wsgi_iterable(obj: PyObject, py: Python) -> PyResult<PyObject> {
    unsafe {
        let ptr = ffi::PyObject_GetIter(obj.as_ptr());
        // Returns NULL if an object cannot be iterated.
        if ptr.is_null() {
            Err(PyErr::fetch(py))
        } else {
            Ok(PyObject::from_owned_ptr(py, ptr))
        }
    }
}

pub struct WSGIResponse<C: Connection> {
    pub pyobject: Option<Py<PyAny>>,
    pub iterable: Option<Py<PyAny>>,
    pub start_response: Option<Py<PyAny>>,
    // flag indicating whether either this is the last chunk of the wsgi iterable or
    // we are using a file wrapper + sendfile and the file has been sent completely
    // (assuming no iterable in the file wrapper case)
    pub last_chunk_or_file_sent: bool,
    pub sendfileinfo: bool,
    pub chunked_transfer: bool,
    pub current_chunk: Vec<u8>,
    pub content_length: Option<usize>,
    pub written: usize, // current chunk
    pub connection: HTTP11Connection<C>,
}

impl<C: Connection> WSGIResponse<C> {
    pub fn new(connection: HTTP11Connection<C>, chunked_transfer: bool) -> WSGIResponse<C> {
        debug!("Creating WSGIResponse using connection {connection:?}");
        WSGIResponse {
            pyobject: None,
            iterable: None,
            start_response: None,
            last_chunk_or_file_sent: false,
            sendfileinfo: false,
            chunked_transfer,
            current_chunk: Vec::new(),
            content_length: None,
            written: 0,
            connection,
        }
    }

    pub fn set_pyobject(&mut self, pyobject: Py<PyAny>, py: Python) {
        self.iterable = match wsgi_iterable(pyobject.clone_ref(py), py) {
            Ok(pyiter) => Some(pyiter),
            Err(e) => {
                debug!("Could not create iterator: {e:?}");
                None
            }
        };
        if let Ok(fw) = pyobject.extract::<Bound<'_, FileWrapper>>(py) {
            if fw.borrow().sendfileinfo.fd != -1 {
                self.sendfileinfo = true;
            }
        }
        self.pyobject = Some(pyobject);
    }

    fn set_error_500(&mut self) {
        self.current_chunk = HTTP500.to_vec();
        self.last_chunk_or_file_sent = true;
        self.connection.expire();
    }

    fn set_bad_request_400(&mut self) {
        self.current_chunk = HTTP400.to_vec();
        self.last_chunk_or_file_sent = true;
        self.connection.expire();
    }

    fn check_content_length_exceeds_data(
        &mut self,
        start_response: &mut StartResponse,
        py: Python,
    ) {
        if let Some(cl) = start_response.content_length {
            if start_response.content_bytes_written < cl {
                // check for HEAD request
                if let Some(method) = start_response
                    .environ(py)
                    .bind(py)
                    .get_item(REQUEST_METHOD)
                    .unwrap_or(None)
                {
                    match method.extract::<Bound<PyString>>() {
                        // HTTP method names are always upper case, see
                        // https://datatracker.ietf.org/doc/html/rfc7231#section-4.1
                        Ok(methodstr) if methodstr.to_string_lossy() == "HEAD" => return,
                        Err(e) => error!("Could not extract PyString: {e}"),
                        _ => (),
                    }
                }
                // From the PEP:
                // if the application does not provide enough data to meet its
                // stated Content-Length, the server should close the connection and log
                // or otherwise report the error.
                self.connection.expire();
                // The headers have already been sent,
                // so rendering a 500 error is impossible.
                // But we log the error.
                error!("Expected content length: {cl}");
            }
        }
    }

    pub fn render_next_chunk(&mut self, py: Python) -> PyResult<()> {
        match self.start_response.as_mut() {
            Some(pyob) => {
                let close_conn = self.connection.expired();
                match self.iterable.as_mut() {
                    None => {
                        // No iterator, no FileWrapper, there's nothing we can do
                        debug!("Could not extract Iterator or FileWrapper");
                        self.last_chunk_or_file_sent = true;
                        return Ok(());
                    }
                    Some(obj) => match PyIterator::from_object(obj.clone_ref(py).bind(py)) {
                        Ok(mut iter) => match iter.next() {
                            None => {
                                let mut start_response = pyob
                                    .clone_ref(py)
                                    .extract::<Bound<StartResponse>>(py)?
                                    .try_borrow_mut()?;
                                if start_response.headers_not_sent() {
                                    start_response.write(
                                        b"",
                                        &mut self.current_chunk,
                                        close_conn,
                                        self.chunked_transfer,
                                    );
                                }
                                self.last_chunk_or_file_sent = true;
                                self.check_content_length_exceeds_data(&mut start_response, py);
                                return Ok(());
                            }
                            Some(Err(e)) => return Err(e),
                            Some(Ok(any)) => match any.extract::<Bound<PyBytes>>() {
                                Ok(cont) => {
                                    let mut start_response = pyob
                                        .clone_ref(py)
                                        .extract::<Bound<StartResponse>>(py)?
                                        .try_borrow_mut()?;
                                    start_response.write(
                                        cont.as_bytes(),
                                        &mut self.current_chunk,
                                        close_conn,
                                        self.chunked_transfer,
                                    );
                                    if self.sendfileinfo & self.content_length.is_none() {
                                        self.content_length = start_response.content_length;
                                    }
                                    if start_response.content_complete() {
                                        debug!("start_response content complete");
                                        self.last_chunk_or_file_sent = true;
                                    }
                                }
                                Err(_) => {
                                    return Err(PyTypeError::new_err(format!(
                                        "Expected bytestring, got {any:?}"
                                    )));
                                }
                            },
                        },
                        Err(_) => {
                            return Err(PyTypeError::new_err(format!(
                                "Could not create iterator from {obj:?}"
                            )))
                        }
                    },
                }
                Ok(())
            }
            None => Err(PyValueError::new_err("StartResponse not set")),
        }
    }

    // true: chunk written completely, false: there's more
    fn write_chunk(&mut self, py: Python) -> io::Result<bool> {
        let mut chunk_complete = false;
        if !self.last_chunk_or_file_sent & (self.written == 0) {
            debug!("Attempt to render next chunk");
            if let Err(e) = self.render_next_chunk(py) {
                error!("Could not render WSGI chunk: {e:?}");
                PyErr::fetch(py);
                self.set_error_500();
            }
        }
        if self.last_chunk_or_file_sent && self.content_length.is_none() {
            // final chunk and no content length header
            self.connection.expire();
            if self.chunked_transfer {
                // chunked transfer encoding requested
                debug!("writing final chunk: last_chunk_or_file_sent");
                self.current_chunk.extend(b"0\r\n\r\n");
            }
        }
        match self.connection.write(&self.current_chunk[self.written..]) {
            Ok(n) => {
                self.written += n;
                debug!(
                    "{} bytes written to connection {:?}",
                    self.written, self.connection
                );
                if self.written == self.current_chunk.len() {
                    chunk_complete = true;
                    self.written = 0;
                    debug!("done writing");
                    if !self.last_chunk_or_file_sent {
                        self.current_chunk.clear();
                    }
                }
            }
            Err(err) => return Err(err),
        }
        if self.sendfileinfo {
            if let Some(ob) = self.pyobject.as_mut() {
                self.last_chunk_or_file_sent =
                    match ob.clone_ref(py).extract::<Bound<FileWrapper>>(py) {
                        Ok(fw) => {
                            debug!("self.content_length: {:?}", self.content_length);
                            let mut c_l = 0;
                            let mut fw = fw.borrow_mut();
                            if let Some(cl) = self.content_length {
                                c_l = cl;
                                fw.update_content_length(cl, py);
                            }
                            let (done, offset) = fw.send_file(&mut self.connection, py);
                            if done && (offset < c_l) {
                                self.connection.expire();
                                // The headers have already been sent,
                                // so rendering a 500 error is impossible.
                                // But we log the error.
                                error!("Sendfile: expected content length: {c_l}");
                            }
                            done
                        }
                        Err(_) => {
                            // No iterator, no FileWrapper, there's nothing we can do here
                            debug!("Could not extract FileWrapper");
                            true
                        }
                    }
            }
        }
        self.connection.flush()?;
        debug!(
            "write_chunk last_chunk: {} chunk_complete: {}",
            self.last_chunk_or_file_sent, chunk_complete
        );
        Ok(chunk_complete && self.last_chunk_or_file_sent)
    }

    pub fn write_loop(&mut self, py: Python) {
        loop {
            match self.write_chunk(py) {
                Ok(done) => {
                    if done {
                        debug!("wrote response immediately");
                        break;
                    }
                }
                Err(ref err) if would_block(err) => {
                    break;
                }
                Err(ref err) if broken_pipe(err) => {
                    debug!("Broken pipe");
                    self.last_chunk_or_file_sent = true;
                    break;
                }
                Err(e) => {
                    error!("Write error: {e:?}");
                    self.last_chunk_or_file_sent = true;
                    break;
                }
            }
        }
    }

    pub fn complete(&self) -> bool {
        // needed in case of EAGAIN error
        self.last_chunk_or_file_sent && (self.written == 0)
    }
}

pub fn handle_request<C: Connection>(
    application: &PyObject,
    globals: SharedWSGIOptions,
    req: &mut WSGIRequest,
    resp: &mut WSGIResponse<C>,
    py: Python,
) {
    // no need to proceed if we have a bad request
    if req.is_bad_request() {
        resp.set_bad_request_400();
    } else {
        match req.wsgi_environ(globals, py) {
            Ok(env) => {
                // allocate the Python object on the heap
                let sr = StartResponse::new(env, Vec::new());
                let envarg = sr.environ(py);
                let pysr = Py::new(py, sr).expect("Could not allocate StartResponse.");
                let args = PyTuple::new(py, &[envarg.into_any(), pysr.as_any().clone_ref(py)])
                    .expect("Could not create argument tuple");
                debug!(
                    "Refcounts application: {:?} start_response: {:?}",
                    application.get_refcnt(py),
                    pysr.get_refcnt(py),
                );
                resp.start_response = Some(pysr.into_any());
                let result = application.call(py, args, None); // call the object
                match result {
                    Ok(o) => {
                        debug!("Refcount result: {:?}", o.get_refcnt(py));
                        resp.set_pyobject(o, py);
                    }
                    Err(e) => {
                        e.print_and_set_sys_last_vars(py);
                        resp.set_error_500();
                    }
                }
            }
            Err(e) => {
                error!("Error handling request: {e:?}");
                e.print_and_set_sys_last_vars(py);
                resp.set_error_500();
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use log::{debug, error};
    use mio::net::TcpStream;
    use nix::fcntl::{fcntl, FcntlArg, OFlag};
    use pyo3::types::{PyAnyMethods, PyDict, PyDictMethods, PyTuple, PyTypeMethods};
    use pyo3::{Bound, Py, PyObject, Python};
    use std::ffi::CString;
    use std::io::{Read, Seek, Write};
    use std::net::{SocketAddr, TcpListener};
    use std::os::fd::AsFd;
    use std::os::unix::io::AsRawFd;
    use std::sync::mpsc::channel;
    use std::thread;
    use std::time::Duration;
    use tempfile::NamedTempFile;
    use test_log::test;

    use crate::filewrapper::{FileWrapper, SendFile};
    use crate::globals::{shared_wsgi_options, SharedWSGIOptions};
    use crate::request::{ParsingStage, WSGIRequest};
    use crate::response::{handle_request, WSGIResponse, HTTP400, HTTP500};
    use crate::startresponse::{StartResponse, WriteResponse};
    use crate::transport::{self, shared_connection_options, Connection, HTTP11Connection};

    /// set a file descriptor into blocking mode
    trait SetBlocking: AsFd {
        fn set_blocking(&mut self) -> transport::Result<()>;
    }

    impl<T: AsFd> SetBlocking for T {
        fn set_blocking(&mut self) -> transport::Result<()> {
            let flags = fcntl(&self, FcntlArg::F_GETFL)?;
            let mut new_flags = OFlag::from_bits(flags).expect("Could not create flags from bits");
            new_flags.remove(OFlag::O_NONBLOCK);
            fcntl(&self, FcntlArg::F_SETFL(new_flags))?;
            Ok(())
        }
    }

    fn make_globals(py: Python) -> (SharedWSGIOptions, SocketAddr) {
        let server_name = "127.0.0.1";
        let port = "0";
        let sn = String::from("/foo");
        (
            shared_wsgi_options(
                String::from(server_name),
                String::from(port),
                sn,
                false,
                None,
                Duration::from_secs(60),
                py,
            ),
            (server_name.to_string() + ":" + port).parse().unwrap(),
        )
    }

    fn dummy_persistent_connection<C: Connection>(connection: C) -> HTTP11Connection<C> {
        HTTP11Connection::from_connection(
            connection,
            shared_connection_options(10, Duration::from_secs(60)),
        )
    }

    fn dummy_connection() -> HTTP11Connection<TcpStream> {
        let addr: SocketAddr = "127.0.0.1:0".parse().expect("Failed to parse address");
        let server = TcpListener::bind(addr).expect("Failed to bind address");
        let addr = server.local_addr().unwrap();
        let connection = TcpStream::connect(addr).expect("Failed to connect");
        dummy_persistent_connection(connection)
    }

    fn handle_test_request(
        app: &PyObject,
        g: SharedWSGIOptions,
        mut req: &mut WSGIRequest,
        py: Python,
    ) -> WSGIResponse<TcpStream> {
        let mut resp = WSGIResponse::new(dummy_connection(), false);
        handle_request(&app, g, &mut req, &mut resp, py);
        resp
    }

    #[test]
    fn test_create() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            match py.run(
                CString::new(r#"li = iter([b"Hello", b"world", b"!"])"#)
                    .unwrap()
                    .as_c_str(),
                None,
                Some(&locals),
            ) {
                Ok(_) => {
                    let pylist = locals
                        .get_item("li")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let environ = PyDict::new(py);
                    let headers = vec![(
                        "200 OK".to_string(),
                        vec![("Content-type".to_string(), "text/plain".to_string())],
                    )];
                    let sr = StartResponse::new(environ.unbind(), headers);
                    let mut resp = WSGIResponse::new(dummy_connection(), false);
                    resp.set_pyobject(pylist, py);
                    assert!(resp.iterable.is_some());
                    resp.start_response = Some(Py::new(py, sr).unwrap().into_any().clone_ref(py));
                    let mut expectedv: Vec<&[u8]> = Vec::new();
                    expectedv.push(
                    b"HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nVia: pyruvate\r\nConnection: keep-alive\r\n\r\nHello",
                );
                    expectedv.push(b"world");
                    expectedv.push(b"!");
                    for expected in expectedv {
                        match resp.render_next_chunk(py) {
                            Err(e) => {
                                debug!("Error encountered: {:?}", e);
                                assert!(false);
                            }
                            Ok(()) => {
                                assert!(!resp.last_chunk_or_file_sent);
                                debug!("current chunk: {:?}", resp.current_chunk);
                                assert!(resp
                                    .current_chunk
                                    .iter()
                                    .zip(expected.iter())
                                    .all(|(p, q)| p == q));
                                resp.current_chunk.clear();
                            }
                        }
                    }
                    match resp.render_next_chunk(py) {
                        Ok(()) => {
                            assert!(resp.last_chunk_or_file_sent);
                        }
                        Err(_) => assert!(false),
                    }
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_iterator() {
        // From the PEP:
        // When called by the server, the application object must return an iterable yielding zero or more bytestrings.
        // This can be accomplished in a variety of ways, such as by returning a list of bytestrings,
        // or by the application being a generator function that yields bytestrings,
        // or by the application being a class whose instances are iterable.
        // Regardless of how it is accomplished,
        // the application object must always return an iterable yielding zero or more bytestrings.
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            match py.run(
                CString::new(r#"it = iter([b'Hello', b' world', b'!'])"#)
                    .unwrap()
                    .as_c_str(),
                None,
                Some(&locals),
            ) {
                Ok(_) => {
                    let pyit = locals
                        .get_item("it")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let environ = PyDict::new(py);
                    let headers = vec![(
                        "200 OK".to_string(),
                        vec![("Content-type".to_string(), "text/plain".to_string())],
                    )];
                    let sr = StartResponse::new(environ.unbind(), headers);
                    let mut resp = WSGIResponse::new(dummy_connection(), false);
                    resp.set_pyobject(pyit, py);
                    resp.start_response = Some(Py::new(py, sr).unwrap().into_any().clone_ref(py));
                    let mut expected: Vec<&[u8]> = Vec::new();
                    expected.push(b"HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nVia: pyruvate\r\nConnection: keep-alive\r\n\r\nHello");
                    expected.push(b" world");
                    expected.push(b"!");
                    for word in expected {
                        match resp.render_next_chunk(py) {
                            Err(e) => {
                                debug!("Error encountered: {:?}", e);
                                assert!(false);
                            }
                            Ok(()) => {
                                assert!(!resp.last_chunk_or_file_sent);
                                debug!("Bytes: {:?}", &resp.current_chunk);
                                assert!(resp.current_chunk == word);
                                resp.current_chunk.clear();
                            }
                        }
                    }
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            };
            // 'iterable' is a list of bytestrings:
            match py.run(
                CString::new(r#"it = [b'Hello', b'world', b'!']"#)
                    .unwrap()
                    .as_c_str(),
                None,
                Some(&locals),
            ) {
                Ok(_) => {
                    let pyit = locals
                        .get_item("it")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let environ = PyDict::new(py);
                    let headers = vec![(
                        "200 OK".to_string(),
                        vec![("Content-type".to_string(), "text/plain".to_string())],
                    )];
                    let sr = StartResponse::new(environ.unbind(), headers);
                    let mut resp = WSGIResponse::new(dummy_connection(), false);
                    resp.set_pyobject(pyit, py);
                    resp.start_response = Some(Py::new(py, sr).unwrap().into_any().clone_ref(py));
                    let mut expected: Vec<&[u8]> = Vec::new();
                    expected.push(
                    b"HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nVia: pyruvate\r\nConnection: keep-alive\r\n\r\nHello",
                );
                    expected.push(b"world");
                    expected.push(b"!");
                    for word in expected {
                        match resp.render_next_chunk(py) {
                            Ok(()) => {
                                debug!("{:?}", &resp.current_chunk[..]);
                                assert!(resp.current_chunk == word);
                                resp.current_chunk.clear();
                            }
                            Err(_) => assert!(false),
                        }
                    }
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_set_pyobject() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            match py.run(
                CString::new(r#"li = [b"Hello", b"world", b"!"]"#)
                    .unwrap()
                    .as_c_str(),
                None,
                Some(&locals),
            ) {
                Ok(_) => {
                    let pylist = locals
                        .get_item("li")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let mut resp = WSGIResponse::new(dummy_connection(), false);
                    let refcnt = pylist.get_refcnt(py);
                    resp.set_pyobject(pylist, py);
                    match &resp.pyobject {
                        Some(po) => assert!(po.get_refcnt(py) == refcnt + 1),
                        None => assert!(false),
                    }
                }
                _ => assert!(false),
            }
        });
    }

    #[test]
    fn test_set_error() {
        let mut resp = WSGIResponse::new(dummy_connection(), false);
        resp.set_error_500();
        assert_eq!(&resp.current_chunk[..], HTTP500);
        assert!(resp.last_chunk_or_file_sent);
    }

    #[test]
    fn test_set_bad_request() {
        let mut resp = WSGIResponse::new(dummy_connection(), false);
        resp.set_bad_request_400();
        assert_eq!(&resp.current_chunk[..], HTTP400);
        assert!(resp.last_chunk_or_file_sent);
    }

    #[test]
    fn test_write_chunk() {
        let addr: SocketAddr = "127.0.0.1:0".parse().expect("Failed to parse address");
        let server = TcpListener::bind(addr).expect("Failed to bind address");
        let addr = server.local_addr().expect("Could not get local_addr");
        let mut connection = TcpStream::connect(addr).expect("Failed to connect");
        connection.set_blocking().expect("Could not set_blocking");
        let mut r = WSGIResponse::new(dummy_persistent_connection(connection), false);
        r.current_chunk = b"Foo 42".to_vec();
        r.last_chunk_or_file_sent = true;
        let (tx, rx) = channel();
        let (snd, got) = channel();
        let t = thread::spawn(move || {
            let (mut conn, _addr) = server.accept().expect("Could not accept()");
            conn.set_read_timeout(Some(Duration::from_secs(1)))
                .expect("Failed to set read timeout");
            let mut buf = [0; 6];
            conn.read(&mut buf).unwrap();
            snd.clone().send(buf).unwrap();
            rx.recv().unwrap();
            drop(conn);
        });
        debug!("Response SendFileInfo: {:?}", r.sendfileinfo);
        Python::with_gil(|py| match r.write_chunk(py) {
            Err(_) => {
                assert!(false);
            }
            Ok(true) => {
                let b = got.recv().expect("Could not recv()");
                assert!(&b[..] == b"Foo 42");
            }
            _ => assert!(false),
        });
        tx.send(()).unwrap();
        t.join().unwrap();
    }

    #[test]
    fn test_write_chunk_sendfile() {
        Python::with_gil(|py| {
            let addr: SocketAddr = "127.0.0.1:0".parse().expect("Failed to parse address");
            let server = TcpListener::bind(addr).expect("Failed to bind address");
            let addr = server.local_addr().unwrap();
            let mut tmp = NamedTempFile::new().unwrap();
            let mut f = tmp.reopen().unwrap();
            f.seek(std::io::SeekFrom::Start(0)).unwrap();
            let fw = FileWrapper::new(py, f.as_raw_fd(), 42).unwrap();
            let connection = TcpStream::connect(addr).expect("Failed to connect");
            let mut r = WSGIResponse::new(dummy_persistent_connection(connection), false);
            r.set_pyobject(Py::new(py, fw).unwrap().into_any().clone_ref(py), py);
            r.current_chunk = b"Foo 42".to_vec();
            r.last_chunk_or_file_sent = true;
            r.sendfileinfo = true;
            tmp.write_all(b"Hello World!\n").unwrap();
            let (tx, rx) = channel();
            let (snd, got) = channel();
            let t = thread::spawn(move || {
                let (mut conn, _addr) = server.accept().unwrap();
                conn.set_read_timeout(Some(Duration::from_secs(1)))
                    .expect("Failed to set read timeout");
                let mut buf = [0; 19];
                match conn.read(&mut buf) {
                    Ok(len) => {
                        if len < 19 {
                            conn.read(&mut buf[len..]).unwrap();
                        }
                        snd.clone().send(buf).unwrap();
                        rx.recv().unwrap();
                    }
                    Err(e) => error!("Could not read: {e}"),
                }
            });
            match r.write_chunk(py) {
                Err(_) => {
                    assert!(false);
                }
                Ok(_) => {
                    let b = got.recv().unwrap();
                    assert_eq!(&b[..], b"Foo 42Hello World!\n");
                }
            }
            tx.send(()).unwrap();
            t.join().unwrap();
        });
    }

    #[test]
    fn test_write_chunk_sendfile_no_filewrapper() {
        Python::with_gil(|py| {
            let addr: SocketAddr = "127.0.0.1:0".parse().expect("Failed to parse address");
            let server = TcpListener::bind(addr).expect("Failed to bind address");
            let addr = server.local_addr().unwrap();
            let fw = py.None();
            let connection = TcpStream::connect(addr).expect("Failed to connect");
            let mut r = WSGIResponse::new(dummy_persistent_connection(connection), false);
            r.set_pyobject(fw, py);
            r.current_chunk = b"Foo 42".to_vec();
            r.last_chunk_or_file_sent = true;
            r.sendfileinfo = true;
            let (tx, rx) = channel();
            let (snd, got) = channel();
            let t = thread::spawn(move || {
                let (mut conn, _addr) = server.accept().unwrap();
                conn.set_read_timeout(Some(Duration::from_secs(1)))
                    .expect("Failed to set read timeout");
                let mut buf = [0; 10];
                conn.read(&mut buf).unwrap();
                snd.clone().send(buf).unwrap();
                rx.recv().unwrap();
            });
            match r.write_chunk(py) {
                Err(_) => {
                    assert!(false);
                }
                Ok(true) => {
                    let b = got.recv().unwrap();
                    assert_eq!(&b[..], b"Foo 42\0\0\0\0");
                }
                _ => assert!(false),
            }
            tx.send(()).unwrap();
            t.join().unwrap();
        });
    }

    #[test]
    fn test_handle_request() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            let app = py.run(
                CString::new(
                    r#"
def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain'), ("Expires", "Sat, 1 Jan 2000 00:00:00 GMT")]
    start_response(status, response_headers)
    return [b"Hello world!\n"]

app = simple_app"#,
                )
                .unwrap()
                .as_c_str(),
                None,
                Some(&locals),
            );
            match app {
                Ok(_) => {
                    let (g, _) = make_globals(py);
                    let app = locals.get_item("app").unwrap().unwrap().unbind();
                    let raw = b"GET /foo42?bar=baz HTTP/1.1\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\n\r\n";
                    let mut req = WSGIRequest::new(16, String::new());
                    req.append(raw);
                    req.parse_data();
                    let mut resp = handle_test_request(&app, g, &mut req, py);
                    resp.render_next_chunk(py).unwrap();
                    let expected = b"HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nExpires: Sat, 1 Jan 2000 00:00:00 GMT\r\nVia: pyruvate\r\nConnection: keep-alive\r\n\r\nHello world!\n";
                    assert!(expected.len() == resp.current_chunk.len());
                    assert!(resp
                        .current_chunk
                        .iter()
                        .zip(expected.iter())
                        .all(|(p, q)| p == q));
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_handle_request_generator() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            let app = py.run(
                CString::new(
                    r#"
def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    yield b"Hello world!\n"

app = simple_app"#,
                )
                .unwrap()
                .as_c_str(),
                None,
                Some(&locals),
            );
            match app {
                Ok(_) => {
                    let (g, _) = make_globals(py);
                    let app = locals.get_item("app").unwrap().unwrap().unbind();
                    let raw = b"GET /foo HTTP/1.1\r\n\r\n";
                    let mut req = WSGIRequest::new(16, String::new());
                    req.append(raw);
                    req.parse_data();
                    let mut resp = handle_test_request(&app, g, &mut req, py);
                    match resp.render_next_chunk(py) {
                        Ok(_) => (),
                        Err(e) => {
                            error!("Could not render_next_chunk: {e}");
                            assert!(false);
                        }
                    }
                    let expected =
                    b"HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nVia: pyruvate\r\nConnection: keep-alive\r\n\r\nHello world!\n";
                    debug!("got: {:?}", resp.current_chunk);
                    assert!(expected.len() == resp.current_chunk.len());
                    assert!(resp
                        .current_chunk
                        .iter()
                        .zip(expected.iter())
                        .all(|(p, q)| p == q));
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_handle_request_multi_chunk_content_length() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            let app = py.run(CString::new(r#"
def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain'), ("Expires", "Sat, 1 Jan 2000 00:00:00 GMT"), ('Content-Length', 13)]
    start_response(status, response_headers)
    return [b"Hello ", b"world!\n"]

app = simple_app"#).unwrap().as_c_str(), None, Some(&locals));
            match app {
                Ok(_) => {
                    let app = locals
                        .get_item("app")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let (g, _) = make_globals(py);
                    let raw = b"GET /foo42?bar=baz HTTP/1.1\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\n\r\n";
                    let mut req = WSGIRequest::new(16, String::new());
                    req.append(raw);
                    req.parse_data();
                    let mut resp = handle_test_request(&app, g, &mut req, py);
                    resp.chunked_transfer = true;
                    resp.render_next_chunk(py).unwrap();
                    let mut expected: Vec<&[u8]> = Vec::new();
                    expected.push(b"HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nExpires: Sat, 1 Jan 2000 00:00:00 GMT\r\nContent-Length: 13\r\nVia: pyruvate\r\nConnection: keep-alive\r\n\r\nHello ");
                    expected.push(b"world!\n");
                    for word in expected {
                        debug!("{:?}", &resp.current_chunk[..]);
                        assert_eq!(resp.current_chunk, word);
                        resp.current_chunk.clear();
                        match resp.render_next_chunk(py) {
                            Ok(_) => {}
                            _ => assert!(false),
                        }
                    }
                    assert!(resp.last_chunk_or_file_sent);
                    assert!(resp
                        .start_response
                        .as_mut()
                        .unwrap()
                        .extract::<Bound<StartResponse>>(py)
                        .unwrap()
                        .borrow()
                        .content_complete());
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_handle_request_multi_chunk_chunked_transfer() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            let app = py.run(
                CString::new(
                    r#"
def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain'), ("Expires", "Sat, 1 Jan 2000 00:00:00 GMT")]
    start_response(status, response_headers)
    return [b"Hello ", b"world!\n"]

app = simple_app"#,
                )
                .unwrap()
                .as_c_str(),
                None,
                Some(&locals),
            );
            match app {
                Ok(_) => {
                    let app = locals
                        .get_item("app")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let (g, _) = make_globals(py);
                    let raw = b"GET /foo42?bar=baz HTTP/1.1\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\n\r\n";
                    let mut req = WSGIRequest::new(16, String::new());
                    req.append(raw);
                    req.parse_data();
                    let mut resp = handle_test_request(&app, g, &mut req, py);
                    resp.chunked_transfer = true;
                    resp.render_next_chunk(py).unwrap();
                    let mut expected: Vec<&[u8]> = Vec::new();
                    expected.push(b"HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nExpires: Sat, 1 Jan 2000 00:00:00 GMT\r\nVia: pyruvate\r\nConnection: keep-alive\r\nTransfer-Encoding: chunked\r\n\r\n6\r\nHello \r\n");
                    // final chunk will be missing, it's written by WSGIResponse::write_chunk method
                    expected.push(b"7\r\nworld!\n\r\n");
                    for word in expected {
                        debug!("{:?}", &resp.current_chunk);
                        assert_eq!(resp.current_chunk, word);
                        resp.current_chunk.clear();
                        match resp.render_next_chunk(py) {
                            Ok(_) => {}
                            _ => assert!(false),
                        }
                    }
                    assert!(resp.last_chunk_or_file_sent);
                    assert!(!resp
                        .start_response
                        .as_mut()
                        .unwrap()
                        .extract::<Bound<StartResponse>>(py)
                        .unwrap()
                        .borrow()
                        .content_complete());
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_handle_request_application_error() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            let app = py.run(
                CString::new(
                    r#"
def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain'), ("Expires", "Sat, 1 Jan 2000 00:00:00 GMT")]
    start_response(status, response_headers)
    raise Exception("Baz")

app = simple_app"#,
                )
                .unwrap()
                .as_c_str(),
                None,
                Some(&locals),
            );
            match app {
                Ok(_) => {
                    let app = locals
                        .get_item("app")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let (g, _) = make_globals(py);
                    let raw = b"GET /foo42?bar=baz HTTP/1.1\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\n\r\n";
                    let mut req = WSGIRequest::new(16, String::new());
                    req.append(raw);
                    req.parse_data();
                    let mut resp = handle_test_request(&app, g, &mut req, py);
                    if let Err(e) = resp.render_next_chunk(py) {
                        e.print_and_set_sys_last_vars(py);
                        assert!(false);
                    }
                    let expected = b"HTTP/1.1 500 Internal Server Error\r\n\r\n";
                    debug!("{:?}", &resp.current_chunk[..]);
                    assert!(resp
                        .current_chunk
                        .iter()
                        .zip(expected.iter())
                        .all(|(p, q)| p == q));
                    assert!(resp.last_chunk_or_file_sent);
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_handle_request_result_not_iterable() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            let app = py.run(
                CString::new(
                    r#"
def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain'), ("Expires", "Sat, 1 Jan 2000 00:00:00 GMT")]
    start_response(status, response_headers)
    return None

app = simple_app"#,
                )
                .unwrap()
                .as_c_str(),
                None,
                Some(&locals),
            );
            match app {
                Ok(_) => {
                    let app = locals
                        .get_item("app")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let (g, _) = make_globals(py);
                    let raw = b"GET /foo42?bar=baz HTTP/1.1\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\n\r\n";
                    let mut req = WSGIRequest::new(16, String::new());
                    req.append(raw);
                    req.parse_data();
                    let mut resp = handle_test_request(&app, g, &mut req, py);
                    resp.render_next_chunk(py).unwrap();
                    let expected = b"HTTP/1.1 500 Internal Server Error\r\n\r\n";
                    debug!("{:?}", &resp.current_chunk[..]);
                    assert!(resp
                        .current_chunk
                        .iter()
                        .zip(expected.iter())
                        .all(|(p, q)| p == q));
                    assert!(resp.last_chunk_or_file_sent);
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_handle_request_result_is_empty_list() {
        // PEP-3333 allows for using an empty list
        // for the response body - we still need
        // to send the headers.
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            let app = py.run(
                CString::new(
                    r#"
def simple_app(environ, start_response):
    status = '302'
    response_headers = [('Location', '/foo'), ]
    start_response(status, response_headers)
    return []

app = simple_app"#,
                )
                .unwrap()
                .as_c_str(),
                None,
                Some(&locals),
            );
            match app {
                Ok(_) => {
                    let app = locals
                        .get_item("app")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let (g, _) = make_globals(py);
                    let raw = b"GET /foo42?bar=baz HTTP/1.1\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\n\r\n";
                    let mut req = WSGIRequest::new(16, String::new());
                    req.append(raw);
                    req.parse_data();
                    let mut resp = handle_test_request(&app, g, &mut req, py);
                    resp.render_next_chunk(py).unwrap();
                    let expected = b"HTTP/1.1 302\r\nLocation: /foo\r\nVia: pyruvate\r\nConnection: keep-alive\r\n\r\n";
                    assert!(expected.len() == resp.current_chunk.len());
                    assert!(expected
                        .iter()
                        .zip(resp.current_chunk.iter())
                        .all(|(p, q)| p == q));
                    assert!(resp.last_chunk_or_file_sent);
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_handle_request_bad_request() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            let app = py.run(
                CString::new(
                    r#"
def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain'), ("Expires", "Sat, 1 Jan 2000 00:00:00 GMT")]
    start_response(status, response_headers)
    return None

app = simple_app"#,
                )
                .unwrap()
                .as_c_str(),
                None,
                Some(&locals),
            );
            match app {
                Ok(_) => {
                    let app = locals
                        .get_item("app")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let (g, _) = make_globals(py);
                    let raw = b"GET /foo42?bar=baz HTTP/1.1\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\n\r\n";
                    let mut req = WSGIRequest::new(16, String::new());
                    req.append(raw);
                    req.parse_data();
                    let mut req = WSGIRequest::new(16, String::new());
                    req.stage = ParsingStage::HeadersError;
                    assert!(req.is_bad_request());
                    let resp = handle_test_request(&app, g, &mut req, py);
                    let expected = b"HTTP/1.1 400 Bad Request\r\n\r\n";
                    debug!("{:?}", &resp.current_chunk[..]);
                    assert!(expected
                        .iter()
                        .zip(resp.current_chunk.iter())
                        .all(|(p, q)| p == q));
                    assert!(resp.last_chunk_or_file_sent);
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_render_next_chunk_no_iterator() {
        Python::with_gil(|py| {
            let environ = PyDict::new(py);
            let headers = vec![(
                "200 OK".to_string(),
                vec![("Content-type".to_string(), "text/plain".to_string())],
            )];
            let sr = StartResponse::new(environ.unbind(), headers);
            let mut resp = WSGIResponse::new(dummy_connection(), false);
            resp.start_response = Some(Py::new(py, sr).unwrap().into_any().clone_ref(py));
            resp.iterable = Some(py.None());
            match resp.render_next_chunk(py) {
                Err(e) => {
                    assert!(e.get_type(py).name().unwrap() == "TypeError");
                }
                _ => assert!(false),
            }
        });
    }

    #[test]
    fn test_render_next_chunk_no_bytes_in_iterator() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            match py.run(
                CString::new(r#"li = ["Hello", 42, None]"#)
                    .unwrap()
                    .as_c_str(),
                None,
                Some(&locals),
            ) {
                Ok(_) => {
                    let pylist = locals
                        .get_item("li")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let environ = PyDict::new(py);
                    let headers = vec![(
                        "200 OK".to_string(),
                        vec![("Content-type".to_string(), "text/plain".to_string())],
                    )];
                    let sr = StartResponse::new(environ.unbind(), headers);
                    let mut resp = WSGIResponse::new(dummy_connection(), false);
                    resp.start_response = Some(Py::new(py, sr).unwrap().into_any().clone_ref(py));
                    resp.set_pyobject(pylist, py);
                    match resp.render_next_chunk(py) {
                        Ok(()) => {
                            assert!(false);
                        }
                        Err(e) => assert!(e.get_type(py).name().unwrap() == "TypeError"),
                    }
                }
                _ => assert!(false),
            }
        });
    }

    #[test]
    fn test_render_next_chunk_filewrapper() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            match py.run(
                CString::new(
                    r#"
class FL(object):

    def read(self, blocksize):
        return b'Hello world!\n'

    def fileno(self):
        return -1

f = FL()"#,
                )
                .unwrap()
                .as_c_str(),
                None,
                Some(&locals),
            ) {
                Ok(_) => {
                    let filelike = locals
                        .get_item("f")
                        .expect("Could not get file object")
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let fwtype = py.get_type::<FileWrapper>();
                    let fwany = fwtype
                        .call(PyTuple::new(py, &[filelike]).unwrap(), None)
                        .unwrap();
                    let environ = PyDict::new(py);
                    let headers = vec![(
                        "200 OK".to_string(),
                        vec![("Content-type".to_string(), "text/plain".to_string())],
                    )];
                    let sr = StartResponse::new(environ.unbind(), headers);
                    let mut resp = WSGIResponse::new(dummy_connection(), false);
                    resp.start_response = Some(Py::new(py, sr).unwrap().into_any().clone_ref(py));
                    resp.set_pyobject(fwany.unbind().clone_ref(py), py);
                    match resp.render_next_chunk(py) {
                        Ok(_) => {
                            let expected = b"HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nVia: pyruvate\r\nConnection: keep-alive\r\n\r\nHello world!\n";
                            assert!(resp.current_chunk == expected);
                        }
                        Err(e) => {
                            e.print_and_set_sys_last_vars(py);
                            assert!(false);
                        }
                    }
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_content_length_gt_data_len() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            match py.run(
                CString::new(r#"li = [b"Hello world!\n"]"#)
                    .unwrap()
                    .as_c_str(),
                None,
                Some(&locals),
            ) {
                Ok(_) => {
                    let pylist = locals
                        .get_item("li")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let environ = PyDict::new(py);
                    environ.set_item("REQUEST_METHOD", "GET").unwrap();
                    let headers = vec![(
                        "200 OK".to_string(),
                        vec![
                            ("Content-type".to_string(), "text/plain".to_string()),
                            ("Content-Length".to_string(), "15".to_string()),
                        ],
                    )];
                    let sr = StartResponse::new(environ.unbind(), headers);
                    let mut resp = WSGIResponse::new(dummy_connection(), false);
                    assert!(!resp.connection.expired());
                    resp.start_response = Some(Py::new(py, sr).unwrap().into_any().clone_ref(py));
                    resp.set_pyobject(pylist, py);
                    match resp.render_next_chunk(py) {
                        Ok(()) => {
                            assert!(!resp.connection.expired());
                            match resp.render_next_chunk(py) {
                                Ok(()) => assert!(resp.connection.expired()),
                                Err(_) => assert!(false),
                            }
                        }
                        Err(e) => {
                            e.print_and_set_sys_last_vars(py);
                            assert!(false);
                        }
                    }
                }
                _ => assert!(false),
            }
        });
    }

    #[test]
    fn test_content_length_gt_data_len_filewrapper() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            match py.run(
                CString::new(
                    r#"
class FL(object):

    def __init__(self):
        self.sent = False 

    def read(self, blocksize):
        if not self.sent:
            self.sent = True
            return b'Hello world!\n'
        return b''

    def fileno(self):
        return -1

f = FL()"#,
                )
                .unwrap()
                .as_c_str(),
                None,
                Some(&locals),
            ) {
                Ok(_) => {
                    let filelike = locals
                        .get_item("f")
                        .expect("Could not get file object")
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let fwtype = py.get_type::<FileWrapper>();
                    let fwany = fwtype
                        .call(PyTuple::new(py, &[filelike]).unwrap(), None)
                        .unwrap();
                    let environ = PyDict::new(py);
                    let headers = vec![(
                        "200 OK".to_string(),
                        vec![
                            ("Content-type".to_string(), "text/plain".to_string()),
                            ("Content-Length".to_string(), "42".to_string()),
                        ],
                    )];
                    let sr = StartResponse::new(environ.unbind(), headers);
                    let mut resp = WSGIResponse::new(dummy_connection(), false);
                    resp.start_response = Some(Py::new(py, sr).unwrap().into_any().clone_ref(py));
                    resp.set_pyobject(fwany.unbind().clone_ref(py), py);
                    match resp.render_next_chunk(py) {
                        Ok(_) => {
                            assert!(!resp.connection.expired());
                            match resp.render_next_chunk(py) {
                                Ok(()) => assert!(resp.connection.expired()),
                                Err(_) => assert!(false),
                            }
                        }
                        Err(e) => {
                            e.print_and_set_sys_last_vars(py);
                            assert!(false);
                        }
                    }
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_content_length_gt_data_len_sendfile() {
        Python::with_gil(|py| {
            let addr: SocketAddr = "127.0.0.1:0".parse().expect("Failed to parse address");
            let server = TcpListener::bind(addr).expect("Failed to bind address");
            let addr = server.local_addr().unwrap();
            let mut tmp = NamedTempFile::new().unwrap();
            let mut f = tmp.reopen().unwrap();
            f.seek(std::io::SeekFrom::Start(0)).unwrap();
            let fw = FileWrapper::new(py, f.as_raw_fd(), 100).unwrap();
            tmp.write_all(b"Hello World!\n").unwrap();
            let mut connection = TcpStream::connect(addr).expect("Failed to connect");
            connection.set_blocking().unwrap();
            let environ = PyDict::new(py);
            let headers = vec![(
                "200 OK".to_string(),
                vec![
                    ("Content-type".to_string(), "text/plain".to_string()),
                    ("Content-Length".to_string(), "42".to_string()),
                ],
            )];
            let sr = StartResponse::new(environ.unbind(), headers);
            let mut r = WSGIResponse::new(dummy_persistent_connection(connection), false);
            r.start_response = Some(Py::new(py, sr).unwrap().into_any().clone_ref(py));
            r.set_pyobject(Py::new(py, fw).unwrap().into_any().clone_ref(py), py);
            // r.current_chunk = b"".to_vec();
            // r.last_chunk_or_file_sent = true;
            r.sendfileinfo = true;
            let (tx, rx) = channel();
            let (snd, got) = channel();
            let t = thread::spawn(move || {
                let (mut conn, _addr) = server.accept().unwrap();
                conn.set_read_timeout(Some(Duration::from_secs(1)))
                    .expect("Failed to set read timeout");
                let mut buf = [0; 150];
                match conn.read(&mut buf) {
                    Ok(len) => {
                        if len < 117 {
                            conn.read(&mut buf[len..]).unwrap();
                        }
                        snd.send(buf).unwrap();
                        rx.recv().unwrap();
                    }
                    Err(e) => error!("Could not read: {e}"),
                }
            });
            match r.write_chunk(py) {
                Err(_) => {
                    assert!(false);
                }
                Ok(false) => {
                    let b = got.recv().unwrap();
                    let expected = b"HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nContent-Length: 42\r\nVia: pyruvate\r\nConnection: keep-alive\r\n\r\nHello World!\n";
                    assert!(expected.iter().zip(b.iter()).all(|(p, q)| p == q));
                    assert!(!r.connection.expired());
                    match r.write_chunk(py) {
                        Ok(true) => {
                            assert!(r.connection.expired())
                        }
                        Err(_) => assert!(false),
                        _ => assert!(false),
                    }
                }
                _ => assert!(false),
            }
            tx.send(()).unwrap();
            t.join().unwrap();
        });
    }

    #[test]
    fn test_content_length_gt_data_len_head() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            match py.run(
                CString::new(r#"li = [b"Hello world!\n"]"#)
                    .unwrap()
                    .as_c_str(),
                None,
                Some(&locals),
            ) {
                Ok(_) => {
                    let pylist = locals
                        .get_item("li")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let environ = PyDict::new(py);
                    environ.set_item("REQUEST_METHOD", "HEAD").unwrap();
                    let headers = vec![(
                        "200 OK".to_string(),
                        vec![
                            ("Content-type".to_string(), "text/plain".to_string()),
                            ("Content-Length".to_string(), "15".to_string()),
                        ],
                    )];
                    let sr = StartResponse::new(environ.unbind(), headers);
                    let mut resp = WSGIResponse::new(dummy_connection(), false);
                    assert!(!resp.connection.expired());
                    resp.start_response = Some(Py::new(py, sr).unwrap().into_any().clone_ref(py));
                    resp.set_pyobject(pylist, py);
                    match resp.render_next_chunk(py) {
                        Ok(()) => {
                            assert!(!resp.connection.expired());
                            match resp.render_next_chunk(py) {
                                Ok(()) => assert!(!resp.connection.expired()),
                                Err(_) => assert!(false),
                            }
                        }
                        Err(e) => {
                            e.print_and_set_sys_last_vars(py);
                            assert!(false);
                        }
                    }
                }
                _ => assert!(false),
            }
        });
    }

    #[test]
    fn test_content_length_gt_data_len_method_error() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            match py.run(
                CString::new(r#"li = [b"Hello world!\n"]"#)
                    .unwrap()
                    .as_c_str(),
                None,
                Some(&locals),
            ) {
                Ok(_) => {
                    let pylist = locals
                        .get_item("li")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    // request method is not a string
                    let environ = PyDict::new(py);
                    environ.set_item("REQUEST_METHOD", py.None()).unwrap();
                    let headers = vec![(
                        "200 OK".to_string(),
                        vec![
                            ("Content-type".to_string(), "text/plain".to_string()),
                            ("Content-Length".to_string(), "15".to_string()),
                        ],
                    )];
                    let sr = StartResponse::new(environ.unbind(), headers);
                    let mut resp = WSGIResponse::new(dummy_connection(), false);
                    assert!(!resp.connection.expired());
                    resp.start_response = Some(
                        Py::new(py, sr)
                            .expect("Could not wrap StartResponse.")
                            .into_any(),
                    );
                    resp.set_pyobject(pylist, py);
                    match resp.render_next_chunk(py) {
                        Ok(()) => {
                            assert!(!resp.connection.expired());
                            match resp.render_next_chunk(py) {
                                Ok(()) => assert!(resp.connection.expired()),
                                Err(_) => assert!(false),
                            }
                        }
                        Err(e) => {
                            e.print_and_set_sys_last_vars(py);
                            assert!(false);
                        }
                    }
                    // XXX request method is not valid utf-8
                }
                _ => assert!(false),
            }
        });
    }
}
