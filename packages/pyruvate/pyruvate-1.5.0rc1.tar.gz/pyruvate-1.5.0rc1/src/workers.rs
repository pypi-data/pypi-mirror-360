use crossbeam_channel::{Receiver, Sender, TryRecvError};
use log::{debug, error, warn};
use mio::{Events, Interest, Poll, Token};
use pyo3::{PyObject, Python};
use std::collections::HashMap;
use std::time::{Duration, SystemTime};

use crate::globals::SharedWSGIOptions;
use crate::pyutils::init_python_threadinfo;
use crate::response::{handle_request, WSGIResponse};
use crate::transport::{Connection, HTTP11Connection, Listener, NonBlockingWrite};
use crate::workerpool::{WorkerPayload, MARKER};

pub fn reuse_connection<T: Connection>(
    mut conn: HTTP11Connection<T>,
    token: Token,
    snd: &Sender<(Token, HTTP11Connection<T>)>,
) {
    if conn.reuse() {
        debug!("Sending back connection {conn:?} for reuse.");
        if let Err(e) = snd.send((token, conn)) {
            error!("Could not send back connection for reuse, error: {e:?}");
        }
    }
}

struct WorkerState<T: Connection> {
    // Helper struct used to keep track
    // of requests handled by this worker
    idx: usize,
    send_timeout: Duration,
    poll: Poll,
    events: Events,
    responses: HashMap<Token, (WSGIResponse<T>, SystemTime)>,
}

impl<T: Connection> WorkerState<T> {
    const MAX_EVENTS: usize = 1024;

    fn new(idx: usize, send_timeout: Duration) -> Self {
        Self {
            idx,
            send_timeout,
            poll: match Poll::new() {
                Ok(poll) => poll,
                Err(e) => panic!("Could not create poll instance: {e:?}"),
            },
            // Create storage for events.
            events: Events::with_capacity(WorkerState::<T>::MAX_EVENTS),
            // Responses
            responses: HashMap::new(),
        }
    }

    // Returns true if the connection is done.
    fn handle_write_event(response: &mut WSGIResponse<T>) -> bool {
        // We can (maybe) write to the connection.
        Python::with_gil(|py| {
            response.write_loop(py);
        });
        response.complete()
    }

    fn recv_or_try_recv<R>(&self, rcv: &Receiver<R>) -> Result<R, TryRecvError> {
        if self.responses.is_empty() {
            match rcv.recv() {
                Ok(t) => Ok(t),
                Err(e) => Err(TryRecvError::from(e)),
            }
        } else {
            rcv.try_recv()
        }
    }

    fn handle_events(&mut self) {
        for event in self.events.iter() {
            debug!("Processing event: {event:?}");
            match event.token() {
                token if event.is_writable() => {
                    // (maybe) received an event for a TCP connection.
                    if let Some(mut resp) = self.responses.remove(&token) {
                        debug!("Received writable event: {event:?}");
                        if Self::handle_write_event(&mut resp.0) {
                            // s. https://docs.rs/mio/0.7.11/mio/event/trait.Source.html#dropping-eventsources
                            if let Err(e) = self.poll.registry().deregister(&mut resp.0.connection)
                            {
                                error!("Could not deregister connection: {e:?}");
                            }
                        } else {
                            self.responses.insert(token, resp);
                        }
                    }
                }
                _ => {
                    error!(
                        "Received unexpected event {:?} in worker {}",
                        event, self.idx
                    );
                }
            }
        }
    }

    fn stash_response(&mut self, token: Token, mut response: WSGIResponse<T>) {
        debug!("registering response for later write: {token:?}");
        if let Err(e) =
            self.poll
                .registry()
                .register(&mut response.connection, token, Interest::WRITABLE)
        {
            error!(
                "Could not register connection for writable events in worker {}, error: {:?}",
                self.idx, e
            );
        }
        self.responses.insert(token, (response, SystemTime::now()));
    }

    fn timeout_responses(&mut self) {
        let thresh = SystemTime::now() - self.send_timeout;
        let mut timed_out: HashMap<Token, (WSGIResponse<T>, SystemTime)> =
            self.responses.extract_if(|_k, v| v.1 < thresh).collect();
        let removed = timed_out.len();
        if removed > 0 {
            for (_token, resp) in timed_out.iter_mut() {
                if let Err(e) = self.poll.registry().deregister(&mut resp.0.connection) {
                    warn!("Could not deregister connection: {e:?}");
                }
            }
            warn!("Write timeout - removed {removed} response(s)");
        }
    }

    fn handle_stashed_responses(&mut self) {
        if !self.responses.is_empty() {
            self.poll();
            self.handle_events();
            self.timeout_responses();
        }
    }

    fn poll(&mut self) {
        if let Err(e) = self
            .poll
            .poll(&mut self.events, Some(Duration::from_millis(1)))
        {
            error!("Could not poll in worker {}, error: {:?}", self.idx, e);
        }
    }
}

pub fn non_blocking_worker<L: Listener, T: Connection + NonBlockingWrite>(
    idx: usize,
    thread_globals: SharedWSGIOptions,
    threadapp: PyObject,
    rcv: Receiver<(Token, WorkerPayload<T>)>,
    snd: Sender<(Token, HTTP11Connection<T>)>,
) {
    let mut worker_state = WorkerState::new(idx, thread_globals.send_timeout);

    Python::with_gil(|py| {
        init_python_threadinfo(py, format!("pyruvate-{idx}"));
        py.allow_threads(|| {
            loop {
                // if we do not need to process stashed responses,
                // we can block and use less CPU.
                match worker_state.recv_or_try_recv(&rcv) {
                    Ok((token, (mut req, out))) => {
                        if token == MARKER {
                            break;
                        }
                        debug!("Handling request in worker {idx}");
                        match out {
                            Some(connection) => {
                                debug!(
                                    "worker {idx} creating response for token: {token:?}, using connection {connection:?}"
                                );
                                let mut response =
                                    WSGIResponse::new(connection, thread_globals.chunked_transfer);
                                Python::with_gil( |py| {
                                    handle_request(
                                        &threadapp,
                                        thread_globals.clone(),
                                        &mut req,
                                        &mut response,
                                        py,
                                    );
                                    response.write_loop(py);
                                });
                                if !response.complete() {
                                    worker_state.stash_response(token, response);
                                } else {
                                    reuse_connection(response.connection, token, &snd);
                                }
                            }
                            None => {
                                error!("No connection to write to");
                            }
                        }
                    }
                    Err(e) => {
                        if e.is_disconnected() {
                            error!("Couldn't receive from queue: {e:?} (sender has hung up)");
                            break;
                        }
                    }
                }
                worker_state.handle_stashed_responses()
            }
        });
    });
}

#[cfg(test)]
mod tests {
    use crossbeam_channel::unbounded;
    use env_logger;
    use mio::event::Source;
    use mio::net::{TcpListener as MioTcpListener, TcpStream};
    use mio::{Interest, Registry, Token};
    use pyo3::types::{PyDict, PyDictMethods};
    use pyo3::{Py, Python};
    use std::ffi::CString;
    use std::io::{self, Read, Seek, Write};
    use std::os::unix::io::{AsRawFd, RawFd};
    use std::sync::mpsc::channel;
    use std::thread;
    use std::time::{Duration, SystemTime};
    use tempfile::NamedTempFile;

    use crate::globals::shared_wsgi_options;
    use crate::request::WSGIRequest;
    use crate::response::WSGIResponse;
    use crate::startresponse::{StartResponse, WriteResponse};
    use crate::transport::{self, shared_connection_options, Connection, HTTP11Connection};
    use crate::workerpool::MARKER;
    use crate::workers::{non_blocking_worker, reuse_connection, WorkerState};

    #[derive(Debug)]
    struct WriteMock {
        block_pos: usize,
        raise: bool,
        pub error: Option<io::ErrorKind>,
        pub file: NamedTempFile,
        registered: bool,
        deregistered: bool,
    }

    impl WriteMock {
        fn new(block_pos: usize, raise: bool) -> Self {
            WriteMock {
                block_pos,
                raise,
                error: None,
                file: NamedTempFile::new().unwrap(),
                registered: false,
                deregistered: false,
            }
        }
    }

    impl Write for WriteMock {
        fn write(&mut self, buf: &[u8]) -> io::Result<usize> {
            match self.error {
                None => {
                    let num_bytes = self.file.write(&buf[0..self.block_pos]).unwrap();
                    self.error = Some(io::ErrorKind::WouldBlock);
                    Ok(num_bytes)
                }
                Some(errkind) if errkind == io::ErrorKind::WouldBlock => {
                    self.error = Some(io::ErrorKind::Other);
                    Err(io::Error::new(
                        io::ErrorKind::WouldBlock,
                        "WriteMock blocking",
                    ))
                }
                Some(errkind) if errkind == io::ErrorKind::Other => {
                    self.error = Some(io::ErrorKind::BrokenPipe);
                    self.file.write(buf)
                }
                Some(errkind) if errkind == io::ErrorKind::BrokenPipe => {
                    self.error = Some(io::ErrorKind::WriteZero);
                    if self.raise {
                        Err(io::Error::new(
                            io::ErrorKind::BrokenPipe,
                            "WriteMock raising",
                        ))
                    } else {
                        Ok(0)
                    }
                }
                Some(_) => Err(io::Error::new(io::ErrorKind::WriteZero, "Other error")),
            }
        }

        fn flush(&mut self) -> io::Result<()> {
            self.file.flush()
        }
    }

    impl Read for WriteMock {
        fn read(&mut self, buf: &mut [u8]) -> io::Result<usize> {
            self.file.flush().unwrap();
            let mut f = self.file.reopen().unwrap();
            f.seek(std::io::SeekFrom::Start(0)).unwrap();
            f.read(buf)
        }
    }

    impl transport::Read for WriteMock {
        fn peer_addr(&self) -> String {
            format!("WriteMock on {:?}", self.file)
        }
    }

    impl AsRawFd for WriteMock {
        fn as_raw_fd(&self) -> RawFd {
            self.file.as_raw_fd()
        }
    }

    impl Source for WriteMock {
        fn register(
            &mut self,
            _registry: &Registry,
            _token: Token,
            _interests: Interest,
        ) -> io::Result<()> {
            self.registered = true;
            Ok(())
        }
        fn reregister(
            &mut self,
            _registry: &Registry,
            _token: Token,
            _interests: Interest,
        ) -> io::Result<()> {
            Ok(())
        }
        fn deregister(&mut self, _registry: &Registry) -> io::Result<()> {
            self.deregistered = true;
            Ok(())
        }
    }

    fn dummy_persistent_connection<C: Connection>(connection: C) -> HTTP11Connection<C> {
        HTTP11Connection::from_connection(
            connection,
            shared_connection_options(10, Duration::from_secs(60)),
        )
    }

    fn init() {
        let _ = env_logger::builder().is_test(true).try_init();
    }

    #[test]
    fn test_non_blocking_worker() {
        init();
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
                    let app = locals
                        .get_item("app")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let server_name = String::from("127.0.0.1");
                    let port = String::from("0");
                    let sn = "/foo";
                    let raw = b"GET /foo42?bar=baz HTTP/1.1\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\n\r\n";
                    let mut req = WSGIRequest::new(16, String::new());
                    req.append(raw);
                    req.parse_data();
                    let token = Token(42);
                    let expected = b"HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nExpires: Sat, 1 Jan 2000 00:00:00 GMT\r\nVia: pyruvate\r\nConnection: keep-alive\r\n\r\nHello world!\n";
                    let (input, rcv) =
                        unbounded::<(Token, (WSGIRequest, Option<HTTP11Connection<WriteMock>>))>();
                    let (snd, _) = unbounded::<(Token, HTTP11Connection<WriteMock>)>();
                    let connection = WriteMock::new(20, false);
                    let mut f = connection.file.reopen().unwrap();
                    input
                        .send((token, (req, Some(dummy_persistent_connection(connection)))))
                        .unwrap();
                    input
                        .send((MARKER, (WSGIRequest::new(16, String::new()), None)))
                        .unwrap();
                    non_blocking_worker::<MioTcpListener, WriteMock>(
                        23,
                        shared_wsgi_options(
                            server_name.clone(),
                            port.clone(),
                            sn.to_string(),
                            false,
                            Some(10),
                            Duration::from_secs(60),
                            py,
                        ),
                        app.clone_ref(py),
                        rcv.clone(),
                        snd.clone(),
                    );
                    let mut buf: [u8; 20] = [0; 20];
                    let b = f.read(&mut buf).unwrap();
                    assert!(b == 20);
                    assert!(buf == expected[..20]);
                    let mut req = WSGIRequest::new(16, String::new());
                    req.append(raw);
                    req.parse_data();
                    let token = Token(42);
                    let mut connection = WriteMock::new(raw.len(), false);
                    let mut f = connection.file.reopen().unwrap();
                    f.seek(std::io::SeekFrom::Start(0)).unwrap();
                    connection.error = Some(io::ErrorKind::Other);
                    input
                        .send((token, (req, Some(dummy_persistent_connection(connection)))))
                        .unwrap();
                    input
                        .send((MARKER, (WSGIRequest::new(16, String::new()), None)))
                        .unwrap();
                    non_blocking_worker::<MioTcpListener, WriteMock>(
                        23,
                        shared_wsgi_options(
                            server_name,
                            port,
                            sn.to_string(),
                            false,
                            Some(10),
                            Duration::from_secs(60),
                            py,
                        ),
                        app,
                        rcv.clone(),
                        snd.clone(),
                    );
                    let mut buf: [u8; 200] = [0; 200];
                    let b = f.read(&mut buf).unwrap();
                    assert!(b == expected.len());
                    assert!(buf.iter().zip(expected.iter()).all(|(p, q)| p == q));
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_handle_write_event() {
        // function under test needs GIL
        Python::with_gil(|py| {
            let connection = WriteMock::new(4, true);
            let mut r = WSGIResponse::new(dummy_persistent_connection(connection), false);
            r.current_chunk = b"Foo 42".to_vec();
            r.last_chunk_or_file_sent = true;
            py.allow_threads(|| {
                if !WorkerState::<_>::handle_write_event(&mut r) {
                    let mut expected: [u8; 10] = [0; 10];
                    let b = r.connection.read(&mut expected).unwrap();
                    assert!(b == 4);
                    assert!(&expected[..4] == b"Foo ");
                    assert!(!r.complete());
                } else {
                    assert!(false);
                }
                if WorkerState::<_>::handle_write_event(&mut r) {
                    let mut expected: [u8; 10] = [0; 10];
                    let b = r.connection.read(&mut expected).unwrap();
                    assert!(b == 6);
                    assert!(&expected[..6] == b"Foo 42");
                } else {
                    assert!(false);
                }
                if !WorkerState::<_>::handle_write_event(&mut r) {
                    assert!(false);
                }
                if !WorkerState::<_>::handle_write_event(&mut r) {
                    assert!(false);
                }
            });
        });
    }

    #[test]
    fn test_reuse_connection() {
        let (send, recv) = unbounded::<(Token, HTTP11Connection<WriteMock>)>();
        let token = Token(42);
        let connection = HTTP11Connection::from_connection(
            WriteMock::new(20, false),
            shared_connection_options(2, Duration::from_secs(60)),
        );
        reuse_connection(connection, token, &send);
        let mut got = recv.recv().unwrap();
        assert!(!got.1.reuse());
    }

    #[test]
    fn test_handle_events() {
        let mut wstate = WorkerState::<TcpStream>::new(0, Duration::from_secs(60));
        let token = Token(42);
        // create connection to write to
        let si = "127.0.0.1:0".parse().unwrap();
        let server = MioTcpListener::bind(si).expect("Failed to bind address");
        let addr = server.local_addr().unwrap();
        let mut connection = TcpStream::connect(addr).expect("Failed to connect");
        let (snd, rcv) = channel();
        let t = thread::spawn(move || {
            let (mut conn, _addr) = server.accept().unwrap();
            // register connection with WorkerState.poll
            match wstate
                .poll
                .registry()
                .register(&mut conn, token, Interest::WRITABLE)
            {
                Ok(_) => {
                    Python::with_gil(|py| {
                        // create response
                        let environ = PyDict::new(py);
                        let headers = vec![(
                            "200 OK".to_string(),
                            vec![("Content-type".to_string(), "text/plain".to_string())],
                        )];
                        let sr = StartResponse::new(environ.clone().unbind(), headers);
                        let mut r = WSGIResponse::new(dummy_persistent_connection(conn), false);
                        r.start_response = Some(
                            Py::new(py, sr)
                                .expect("Could not wrap StartResponse.")
                                .into_any(),
                        );
                        r.current_chunk = b"Foo 42".to_vec();
                        // prevent an endless loop in handle_write_event
                        r.last_chunk_or_file_sent = true;
                        // add response to WorkerState
                        wstate.responses.insert(token, (r, SystemTime::now()));
                        // trigger EAGAIN on connection by repeatedly writing to connection
                        let mut buf = [42; 65535];
                        loop {
                            let mut r = wstate.responses.remove(&token).unwrap();
                            match r.0.connection.write(&mut buf) {
                                Ok(_) => {
                                    wstate.responses.insert(token, r);
                                }
                                Err(e) => {
                                    assert!(e.kind() == io::ErrorKind::WouldBlock);
                                    // pass control to the main thread
                                    snd.send(()).unwrap();
                                    wstate.responses.insert(token, r);
                                    loop {
                                        wstate
                                            .poll
                                            .poll(
                                                &mut wstate.events,
                                                Some(Duration::from_millis(200)),
                                            )
                                            .unwrap();
                                        if !wstate.events.is_empty() {
                                            break;
                                        }
                                    }
                                    break;
                                }
                            }
                        }
                        py.allow_threads(|| {
                            // call handle_events
                            wstate.handle_events();
                        });
                        // successfully handling events will drop the
                        // response and the connection with it.
                        // This will close the connection,
                        // attempting to read from it will result
                        // in a connection refused error.
                        // Therefore we only test whether the
                        // response has been removed from the list.
                        assert!(wstate.responses.is_empty());
                    });
                }
                Err(_) => assert!(false),
            }
        });
        // accept
        connection.write(b"x").unwrap();
        rcv.recv().unwrap();
        // Empty socket buffer, thereby
        // triggering a writeable event on the connection
        let mut buf = [0; 65535];
        loop {
            if connection.read(&mut buf).is_err() {
                break;
            }
        }
        t.join().unwrap();
    }

    #[test]
    fn test_handle_stashed_responses_timeout() {
        let mut wstate = WorkerState::<WriteMock>::new(0, Duration::from_secs(60));
        let token = Token(42);
        Python::with_gil(|py| {
            let connection = WriteMock::new(0, false);
            let r = WSGIResponse::new(dummy_persistent_connection(connection), false);
            wstate
                .responses
                .insert(token, (r, SystemTime::now() - Duration::from_secs(60)));
            py.allow_threads(|| {
                Python::with_gil(|_py| wstate.handle_stashed_responses());
            });
            assert!(wstate.responses.is_empty());
        });
    }
}
