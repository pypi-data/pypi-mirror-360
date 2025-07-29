use libc::c_int;
use log::{debug, error, info};
use mio::{Events, Interest, Poll, Token};
use pyo3::{PyObject, Python};
use signal_hook::consts::signal::SIGINT;
use signal_hook::iterator::Signals;
use std::collections::HashMap;
use std::io;
use std::time::Duration;

use crate::globals::ServerOptions;
use crate::request::WSGIRequest;
use crate::transport::{would_block, HTTP11Connection, Listener, Listening, Read, Result};
use crate::workerpool::WorkerPool;
use crate::workers::non_blocking_worker;

pub const SERVER: Token = Token(0);
const READBUFSIZE: usize = 16384;
const POLL_TIMEOUT: u64 = 100;

fn next(current: &mut Token) -> Token {
    let next = current.0;
    current.0 += 1;
    Token(next)
}

pub struct Server<L: Listener> {
    poll: Poll,
    events: Events,
    listener: L,
    workers: WorkerPool<L::Connected>,
    connections: HashMap<Token, HTTP11Connection<L::Connected>>,
    reusable: HashMap<Token, HTTP11Connection<L::Connected>>,
    requests: HashMap<Token, WSGIRequest>,
    current_token: Token,
    server_options: ServerOptions,
}

impl<L: 'static + Listener + Listening + Send> Server<L> {
    pub fn new(
        application: PyObject,
        listener: L,
        server_options: ServerOptions,
        py: Python,
    ) -> io::Result<Server<L>> {
        let worker_fn = non_blocking_worker::<L, L::Connected>;
        let workers = WorkerPool::new(&server_options, application, worker_fn, py);
        let mut listener = listener;
        let poll = Poll::new()?;
        poll.registry()
            .register(&mut listener, SERVER, Interest::READABLE)?;

        Ok(Server {
            poll,
            events: Events::with_capacity(1024),
            listener,
            workers,
            connections: HashMap::new(),
            reusable: HashMap::new(),
            requests: HashMap::new(),
            current_token: Token(SERVER.0 + 1),
            server_options,
        })
    }

    /// Returns a new WSGIRequest if reading is successful.
    fn handle_read_event(
        &self,
        connection: &mut impl Read,
        request: Option<WSGIRequest>,
    ) -> io::Result<WSGIRequest> {
        let mut connection_closed = false;
        let mut req = match request {
            Some(request) => request,
            None => {
                debug!("creating new WSGI request");
                WSGIRequest::new(
                    self.server_options.max_number_headers,
                    connection.peer_addr(),
                )
            }
        };
        // We can (maybe) read from the connection.
        loop {
            let mut buf = [0; READBUFSIZE];
            match connection.read(&mut buf) {
                Ok(0) => {
                    // Reading 0 bytes means the other side has closed the
                    // connection or is done writing, then so are we.
                    debug!("Reading 0 bytes, consider reading done");
                    connection_closed = true;
                    if req.stage.not_parsed() {
                        return Err(io::Error::other("Incomplete request"));
                    }
                    break;
                }
                Ok(n) => {
                    debug!("appending {n} bytes to buffer");
                    req.append(&buf[..n])
                }
                // Would block "errors" are the OS's way of saying that the
                // connection is not actually ready to perform this I/O operation.
                Err(ref err) if would_block(err) => {
                    debug!("handle_read_event would block");
                    break;
                }
                // Other errors we'll consider fatal.
                Err(err) => return Err(err),
            }
        }

        if connection_closed & !req.stage.complete() & !req.data.is_empty() {
            debug!("Connection closed");
            Err(io::Error::other("Incomplete request"))
        } else {
            Ok(req)
        }
    }

    pub fn poll_once(&mut self) -> Result<()> {
        match self
            .poll
            .poll(&mut self.events, Some(Duration::from_millis(POLL_TIMEOUT)))
        {
            Ok(_) => {
                for (token, conn) in self.workers.reusable_connections.try_iter() {
                    self.reusable.insert(token, conn);
                }
                for event in self.events.iter() {
                    match event.token() {
                        SERVER => {
                            while let Ok(mut connection) = self
                                .listener
                                .accept(self.server_options.connection_options.clone())
                            {
                                let token = next(&mut self.current_token);
                                debug!("current token: {token:?}");

                                self.poll.registry().register(
                                    &mut connection,
                                    token,
                                    Interest::READABLE,
                                )?;
                                self.connections.insert(token, connection);
                            }
                        }
                        token if event.is_readable() => {
                            // (maybe) received an event for a connection.
                            if let Some(mut connection) = if self.reusable.contains_key(&token) {
                                self.reusable.remove(&token)
                            } else {
                                self.connections.remove(&token)
                            } {
                                let req = self.requests.remove(&token);
                                match self.handle_read_event(&mut connection, req) {
                                    Ok(mut req) => {
                                        if req.parse_data() {
                                            debug!("Request complete, relaying to worker pool");
                                            self.poll.registry().deregister(&mut connection)?;
                                            self.workers.execute(token, req, Some(connection))?;
                                        } else {
                                            if req.stage.expect_100_continue() {
                                                if let Err(e) = connection.write_100_continue() {
                                                    error!("Error sending 100 Continue: {e:?}");
                                                }
                                            }
                                            self.requests.insert(token, req);
                                            self.connections.insert(token, connection);
                                        }
                                    }
                                    Err(e) => {
                                        error!("Could not handle read event: {e:?}");
                                    }
                                }
                            }
                        }
                        _ => (),
                    }
                }
                // reinsert reusable connection for which there were no events, but increase the
                // reuse count
                for (token, conn) in self.reusable.drain() {
                    debug!("Reusing connection {conn:?} for token {token:?}");
                    self.connections.insert(token, conn);
                }
            }
            Err(e) => return Err(Box::new(e)),
        }
        Ok(())
    }

    pub fn serve(&mut self, py: Python) -> Result<()> {
        info!(
            "pyruvate listening on {}",
            self.listener.local_addr_string()
        );
        let mut signals = Signals::new([SIGINT])?; // Ctrl + C
        py.allow_threads(|| {
            'outer: loop {
                #[allow(clippy::never_loop)]
                for signal in signals.pending() {
                    match signal as c_int {
                        SIGINT => break 'outer,
                        _ => unreachable!(),
                    }
                }
                if let Err(e) = self.poll_once() {
                    error!("Error processing poll events: {e:?}");
                }
            }
            self.workers.join()?;
            Ok(())
        })
    }
}

#[cfg(test)]
mod tests {

    use mio::net::TcpListener;
    use mio::Token;
    use pyo3::types::{PyDict, PyDictMethods};
    use pyo3::Python;
    use std::ffi::CString;
    use std::io::{self, Read as IORead, Write};
    use std::net::{SocketAddr, TcpStream};
    use std::ops::Range;
    use std::sync::mpsc::channel;
    use std::thread;
    use std::time::Duration;

    use crate::globals::{shared_wsgi_options, SharedWSGIOptions};
    use crate::server::{next, Server, ServerOptions};
    use crate::transport::{shared_connection_options, Read};

    struct StreamMock {
        pub data: Vec<u8>,
        block_pos: usize,
        raise: bool,
        pos: usize,
        error: Option<io::ErrorKind>,
    }

    impl StreamMock {
        pub fn new(data: Vec<u8>, block_before_complete: bool, raise: bool) -> StreamMock {
            let block_pos = if block_before_complete {
                10
            } else {
                data.len()
            };
            StreamMock {
                data,
                block_pos,
                raise,
                pos: 0,
                error: None,
            }
        }

        pub fn read_slice(&mut self, range: Range<usize>, buf: &mut [u8]) -> usize {
            self.pos = range.start;
            let start = range.start;
            let num_bytes = range.end - self.pos;
            for idx in range {
                let offset = idx - start;
                match self.data.get(idx) {
                    Some(d) => {
                        buf[offset] = *d;
                        self.pos = self.pos + 1;
                    }
                    None => return offset,
                }
            }
            num_bytes
        }
    }

    impl io::Read for StreamMock {
        fn read(&mut self, buf: &mut [u8]) -> io::Result<usize> {
            match self.error {
                None => {
                    let num_bytes = self.read_slice(0..self.block_pos, buf);
                    self.error = Some(io::ErrorKind::WouldBlock);
                    Ok(num_bytes)
                }
                Some(errkind) if errkind == io::ErrorKind::WouldBlock => {
                    self.error = Some(io::ErrorKind::Other);
                    Err(io::Error::new(
                        io::ErrorKind::WouldBlock,
                        "StreamMock blocking",
                    ))
                }
                Some(errkind) if errkind == io::ErrorKind::Other => {
                    self.error = Some(io::ErrorKind::WriteZero);
                    Ok(self.read_slice(self.block_pos..buf.len(), buf))
                }
                Some(_) => {
                    if self.raise {
                        Err(io::Error::new(
                            io::ErrorKind::BrokenPipe,
                            "StreamMock raising",
                        ))
                    } else {
                        Ok(0)
                    }
                }
            }
        }
    }

    impl Read for StreamMock {
        fn peer_addr(&self) -> String {
            String::from("foo42")
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

    fn server_options(globals: SharedWSGIOptions) -> ServerOptions {
        ServerOptions {
            num_workers: 2,
            max_number_headers: 16,
            connection_options: shared_connection_options(10, Duration::from_secs(60)),
            wsgi_options: globals,
        }
    }

    #[test]
    fn test_next() {
        let mut start = Token(0);
        for idx in 0..6 {
            let got = next(&mut start);
            assert_eq!(Token(idx), got);
            assert_eq!(start.0, idx + 1);
        }
    }

    #[test]
    fn test_handle_read_event() {
        Python::with_gil(|py| {
            let (g, si) = make_globals(py);
            let listener = TcpListener::bind(si).unwrap();
            let server = Server::new(py.None(), listener, server_options(g), py).unwrap();
            let expected = b"GET /foo42?bar=baz HTTP/1.1\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\n\r\n";
            let mut s = StreamMock::new(expected.to_vec(), true, false);
            // read interrupted by WouldBlock, block will occur
            // before complete parsing of request is possible
            match server.handle_read_event(&mut s, None) {
                Ok(mut req) => {
                    assert!(req.data.len() == 10);
                    assert!(expected.iter().zip(req.data.iter()).all(|(p, q)| p == q));
                    let res = req.parse_data();
                    assert!(req.data.len() == 10);
                    assert!(!res);
                }
                Err(_) => {
                    assert!(false);
                }
            }
            let mut s = StreamMock::new(expected.to_vec(), false, false);
            // read interrupted by WouldBlock, block will occur
            // when complete parsing of request is possible
            match server.handle_read_event(&mut s, None) {
                Ok(mut req) => {
                    assert!(req.data.iter().zip(expected.iter()).all(|(p, q)| p == q));
                    assert!(req.parse_data());
                }
                Err(_) => {
                    assert!(false);
                }
            }
            let mut s = StreamMock::new(expected.to_vec(), true, true);
            // read until WouldBlock, block will occur
            // before complete parsing of request is possible
            // and then raise BrokenPipe
            match server.handle_read_event(&mut s, None) {
                Ok(req) => match server.handle_read_event(&mut s, Some(req)) {
                    Ok(_) => assert!(false),
                    Err(e) => {
                        assert!(e.kind() == io::ErrorKind::BrokenPipe);
                    }
                },
                Err(_) => assert!(false),
            }
        });
    }

    #[test]
    fn test_handle_read_event_too_many_headers() {
        Python::with_gil(|py| {
            let (g, si) = make_globals(py);
            let listener = TcpListener::bind(si).unwrap();
            let server = Server::new(py.None(), listener, server_options(g), py).unwrap();
            let expected = b"GET /foo42?bar=baz HTTP/1.1\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\nH1: 1\r\nH2: 2\r\nH3: 3\r\nH4: 4\r\nH5: 5\r\nH6: 6\r\nH7: 7\r\nH8: 8\r\nH9: 9\r\nH10: 10\r\nH11: 11\r\nH12: 12\r\n\r\n";
            let mut s = StreamMock::new(expected.to_vec(), true, false);
            // read interrupted by WouldBlock, block will occur
            // before complete parsing of request is possible
            match server.handle_read_event(&mut s, None) {
                Ok(req) => match server.handle_read_event(&mut s, Some(req)) {
                    Ok(_) => assert!(false),
                    Err(e) => {
                        assert!(e.kind() == io::ErrorKind::Other);
                    }
                },
                Err(_) => assert!(false),
            }
        });
    }

    #[test]
    fn test_create_blocking_server() {
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
                    let (g, si) = make_globals(py);
                    let listener = TcpListener::bind(si).unwrap();
                    let app = locals
                        .get_item("app")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    match Server::new(app, listener, server_options(g), py) {
                        Ok(got) => {
                            assert!(got.current_token == Token(1));
                        }
                        Err(_) => {
                            assert!(false);
                        }
                    }
                }
                _ => assert!(false),
            }
        });
    }

    #[test]
    fn test_create_server() {
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
                    let (g, si) = make_globals(py);
                    let listener = TcpListener::bind(si).unwrap();
                    let app = locals
                        .get_item("app")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    match Server::new(app, listener, server_options(g), py) {
                        Ok(got) => {
                            assert!(got.current_token == Token(1));
                        }
                        Err(_) => {
                            assert!(false);
                        }
                    }
                }
                _ => assert!(false),
            }
        });
    }

    #[test]
    fn test_create_server_socket_activation() {
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
                    let (g, si) = make_globals(py);
                    let listener = TcpListener::bind(si).unwrap();
                    let app = locals
                        .get_item("app")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    match Server::new(app, listener, server_options(g), py) {
                        Ok(got) => {
                            assert!(got.current_token == Token(1));
                        }
                        Err(_) => {
                            assert!(false);
                        }
                    }
                }
                _ => assert!(false),
            }
        });
    }

    #[test]
    fn test_server_poll_once() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            let app = py.run(
                CString::new(
                    r#"
def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain'), ]
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
                    let app = locals
                        .get_item("app")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let si: SocketAddr = "127.0.0.1:0".parse().unwrap();
                    let listener = TcpListener::bind(si).unwrap();
                    let addr = listener.local_addr().unwrap();
                    match Server::new(app, listener, server_options(g), py) {
                        Ok(mut got) => {
                            // accept
                            got.poll_once().unwrap();
                            // create request in separate thread
                            let t = thread::spawn(move || {
                                let mut connection =
                                    TcpStream::connect_timeout(&addr, Duration::from_millis(1000))
                                        .expect("Failed to connect to server");
                                let req = b"GET /foo42?bar=baz HTTP/1.1\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\n\r\n";
                                match connection.write(req) {
                                    Ok(num_bytes) => assert_eq!(num_bytes, req.len()),
                                    Err(_) => assert!(false),
                                };
                            });
                            // read + propagate HTTPrequest
                            if let Err(_) = got.poll_once() {
                                // accept connection
                                assert!(false);
                            }
                            if let Err(_) = got.poll_once() {
                                // handle request in worker
                                assert!(false);
                            }
                            t.join().expect("Could not join thread");
                        }
                        Err(_) => {
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
    fn test_server_poll_once_expect_continue() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            let app = py.run(
                CString::new(
                    r#"
def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain'), ]
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
                    let app = locals
                        .get_item("app")
                        .unwrap()
                        .unwrap()
                        .unbind()
                        .clone_ref(py);
                    let si: SocketAddr = "127.0.0.1:0".parse().unwrap();
                    let listener = TcpListener::bind(si).unwrap();
                    let addr = listener.local_addr().unwrap();
                    match Server::new(app, listener, server_options(g), py) {
                        Ok(mut got) => {
                            let (tx, rx) = channel();
                            let (snd, rcv) = channel();
                            // create request in separate thread
                            let t = thread::spawn(move || {
                                let mut connection =
                                    TcpStream::connect_timeout(&addr, Duration::from_millis(1000))
                                        .expect("Failed to connect to server");
                                let headers = b"POST /test HTTP/1.1\r\nHost: foo.example\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 27\r\nExpect: 100-continue\r\n\r\n";
                                let body = b"field1=value1&field2=value2";
                                match connection.write(headers) {
                                    Ok(num_bytes) => assert_eq!(num_bytes, headers.len()),
                                    Err(_) => assert!(false),
                                };
                                let mut buf = [0; 25];
                                // Attempting to read 100 Continue
                                connection.read(&mut buf).unwrap();
                                snd.clone().send(buf).unwrap();
                                match connection.write(body) {
                                    Ok(num_bytes) => assert_eq!(num_bytes, body.len()),
                                    Err(_) => assert!(false),
                                };
                                rx.recv().unwrap();
                            });
                            // Listener accept
                            // retry if the server is not immediately available
                            for _ in 0..2 {
                                match got.poll_once() {
                                    Ok(_) => break,
                                    Err(_) => (),
                                }
                                assert!(false);
                            }
                            // Expect -> continue
                            if let Err(_) = got.poll_once() {
                                assert!(false);
                            }
                            // Read 100 continue from channel
                            let b = rcv.recv().unwrap();
                            assert_eq!(&b[..], b"HTTP/1.1 100 Continue\r\n\r\n");
                            // read + propagate HTTPrequest
                            if let Err(_) = got.poll_once() {
                                assert!(false);
                            }
                            if let Err(_) = got.poll_once() {
                                // handle request in worker
                                assert!(false);
                            }
                            tx.send(()).unwrap();
                            t.join().unwrap();
                        }
                        Err(_) => {
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
}
