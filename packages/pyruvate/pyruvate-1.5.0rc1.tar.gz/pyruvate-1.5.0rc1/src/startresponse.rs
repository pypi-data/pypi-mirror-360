#![allow(clippy::transmute_ptr_to_ptr, clippy::zero_ptr)]
// suppress warnings in py_class invocation
use log::error;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyListMethods};
use pyo3::{PyObject, PyResult, Python};
use std::cmp;

use crate::request::CONTENT_LENGTH_HEADER;

type WSGIHeaders = Vec<(String, Vec<(String, String)>)>;

#[pyclass]
pub struct StartResponse {
    pub environ: Py<PyDict>,
    headers_set: WSGIHeaders,
    headers_sent: WSGIHeaders,
    pub content_length: Option<usize>,
    pub content_bytes_written: usize,
}

#[pymethods]
impl StartResponse {
    #[pyo3(signature = (status, headers, exc_info=None))]
    fn __call__(
        &mut self,
        py: Python,
        status: PyObject,
        headers: PyObject,
        exc_info: Option<PyObject>,
    ) -> PyResult<PyObject> {
        let response_headers: Bound<PyList> = headers.extract(py)?;
        if exc_info.is_some() {
            error!("exc_info from application: {exc_info:?}");
        }
        let mut rh = Vec::<(String, String)>::new();
        for ob in response_headers.iter() {
            rh.push((ob.get_item(0)?.to_string(), ob.get_item(1)?.to_string()));
        }
        self.headers_set = vec![(status.to_string(), rh)];
        Ok(py.None())
    }
}

///
/// The only StartResponse member we need to be able to
/// access from Python is __call__(). This is the only reason
/// why we need to wrap StartResponse in [pyclass].
/// Since we can assume Python will never access any other StartResponse
/// attributes, we can avoid Send + Sync precautions that
/// come with [py_class] by putting everything else in a Rust trait.
///
pub trait WriteResponse {
    #[allow(clippy::new_ret_no_self)]
    fn new(environ: Py<PyDict>, headers_set: WSGIHeaders) -> StartResponse;
    fn content_complete(&self) -> bool;
    fn write(
        &mut self,
        data: &[u8],
        output: &mut Vec<u8>,
        close_connection: bool,
        chunked_tranfer: bool,
    );
    fn environ(&self, py: Python) -> Py<PyDict>;
    fn headers_not_sent(&self) -> bool;
}

impl WriteResponse for StartResponse {
    fn new(environ: Py<PyDict>, headers_set: WSGIHeaders) -> StartResponse {
        StartResponse {
            environ,
            headers_set,
            headers_sent: Vec::new(),
            content_length: None,
            content_bytes_written: 0,
        }
    }

    fn content_complete(&self) -> bool {
        if let Some(length) = self.content_length {
            self.content_bytes_written >= length
        } else {
            false
        }
    }

    fn write(
        &mut self,
        data: &[u8],
        output: &mut Vec<u8>,
        close_connection: bool,
        chunked_transfer: bool,
    ) {
        if self.headers_not_sent() {
            if self.headers_set.is_empty() {
                error!("write() before start_response()")
            }
            // Before the first output, send the stored headers
            self.headers_sent = self.headers_set.clone();
            let respinfo = self.headers_set.pop(); // headers_sent|set should have only one element
            match respinfo {
                Some(respinfo) => {
                    let response_headers: Vec<(String, String)> = respinfo.1;
                    let status: String = respinfo.0;
                    output.extend(b"HTTP/1.1 ");
                    output.extend(status.as_bytes());
                    output.extend(b"\r\n");
                    let mut maybe_chunked = true;
                    for header in response_headers.iter() {
                        let headername = &header.0;
                        output.extend(headername.as_bytes());
                        output.extend(b": ");
                        output.extend(header.1.as_bytes());
                        output.extend(b"\r\n");
                        if headername.to_ascii_uppercase() == CONTENT_LENGTH_HEADER {
                            match header.1.parse::<usize>() {
                                Ok(length) => {
                                    self.content_length = Some(length);
                                    // no need to use chunked transfer encoding if we have a valid content length header,
                                    // see e.g. https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding#Chunked_encoding
                                    maybe_chunked = false;
                                }
                                Err(e) => error!("Could not parse Content-Length header: {e:?}"),
                            }
                        }
                    }
                    output.extend(b"Via: pyruvate\r\n");
                    if close_connection {
                        output.extend(b"Connection: close\r\n");
                    } else {
                        output.extend(b"Connection: keep-alive\r\n");
                    }
                    if maybe_chunked && chunked_transfer {
                        output.extend(b"Transfer-Encoding: chunked\r\n");
                    }
                }
                None => {
                    error!("write(): No respinfo!");
                }
            }
            output.extend(b"\r\n");
        }
        match self.content_length {
            Some(length) => {
                let cbw = self.content_bytes_written;
                if length > cbw {
                    let num = cmp::min(length - cbw, data.len());
                    if num > 0 {
                        output.extend(&data[..num]);
                        self.content_bytes_written = cbw + num;
                    }
                }
            }
            None => {
                // no content length header, use
                // chunked transfer encoding if specified
                let cbw = self.content_bytes_written;
                let length = data.len();
                if length > 0 {
                    if chunked_transfer {
                        output.extend(format!("{length:X}").as_bytes());
                        output.extend(b"\r\n");
                        output.extend(data);
                        output.extend(b"\r\n");
                    } else {
                        output.extend(data);
                    }
                    self.content_bytes_written = cbw + length;
                }
            }
        }
    }

    fn environ(&self, py: Python) -> Py<PyDict> {
        self.environ.clone_ref(py)
    }

    fn headers_not_sent(&self) -> bool {
        self.headers_sent.is_empty()
    }
}

#[cfg(test)]
mod tests {
    use log::LevelFilter;
    use pyo3::types::{PyDict, PyDictMethods};
    use pyo3::Python;
    use simplelog::{Config, WriteLogger};
    use std::env::temp_dir;
    use std::ffi::CString;
    use std::fs::File;
    use std::io::Read;

    use crate::startresponse::{StartResponse, WriteResponse};

    #[test]
    fn test_write() {
        Python::with_gil(|py| {
            let environ = PyDict::new(py);
            let headers = vec![(
                "200 OK".to_string(),
                vec![("Content-type".to_string(), "text/plain".to_string())],
            )];
            let data = b"Hello world!\n";
            let mut sr = StartResponse::new(environ.into(), headers);
            assert_eq!(sr.content_length, None);
            assert!(!sr.content_complete());
            let mut output: Vec<u8> = Vec::new();
            sr.write(data, &mut output, true, false);
            let expected =
                b"HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nVia: pyruvate\r\nConnection: close\r\n\r\nHello world!\n";
            assert!(output.iter().zip(expected.iter()).all(|(p, q)| p == q));
            assert!(!sr.content_complete());
            // chunked transfer requested and no content length header
            // The final chunk will be missing; it's written in WSGIResponse::write_chunk
            let expected =
                b"HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nVia: pyruvate\r\nConnection: close\r\nTransfer-Encoding: chunked\r\n\r\nD\r\nHello world!\n";
            let environ = PyDict::new(py);
            let headers = vec![(
                "200 OK".to_string(),
                vec![("Content-type".to_string(), "text/plain".to_string())],
            )];
            let mut sr = StartResponse::new(environ.into(), headers);
            let mut output: Vec<u8> = Vec::new();
            assert!(!sr.content_complete());
            sr.write(data, &mut output, true, true);
            assert!(output.iter().zip(expected.iter()).all(|(p, q)| p == q));
            assert!(!sr.content_complete());
        });
    }

    #[test]
    fn test_honour_content_length_header() {
        Python::with_gil(|py| {
            let environ = PyDict::new(py);
            let headers = vec![(
                "200 OK".to_string(),
                vec![
                    ("Content-type".to_string(), "text/plain".to_string()),
                    ("Content-length".to_string(), "5".to_string()),
                ],
            )];
            let mut sr = StartResponse::new(environ.into(), headers);
            let mut output: Vec<u8> = Vec::new();
            let data = b"Hello world!\n";
            assert!(!sr.content_complete());
            sr.write(data, &mut output, true, false);
            let expected =
                b"HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nContent-length: 5\r\nVia: pyruvate\r\nConnection: close\r\n\r\nHello";
            assert_eq!(sr.content_length, Some(5));
            assert_eq!(sr.content_bytes_written, 5);
            assert!(sr.content_complete());
            assert!(expected.iter().zip(output.iter()).all(|(p, q)| p == q));
            // chunked transfer set - ignored if content length header available
            let environ = PyDict::new(py);
            let headers = vec![(
                "200 OK".to_string(),
                vec![
                    ("Content-type".to_string(), "text/plain".to_string()),
                    ("Content-length".to_string(), "5".to_string()),
                ],
            )];
            let mut sr = StartResponse::new(environ.into(), headers);
            let mut output: Vec<u8> = Vec::new();
            assert!(!sr.content_complete());
            sr.write(data, &mut output, true, true);
            let expected =
                b"HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nContent-length: 5\r\nVia: pyruvate\r\nConnection: close\r\n\r\nHello";
            assert_eq!(sr.content_length, Some(5));
            assert_eq!(sr.content_bytes_written, 5);
            assert!(sr.content_complete());
            assert!(expected.iter().zip(output.iter()).all(|(p, q)| p == q));
        });
    }

    #[ignore]
    #[test]
    fn test_exc_info_is_none() {
        // do not display an error message when exc_info passed
        // by application is None
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            let pycode = py.run(
                CString::new(
                    r#"
status = '200 OK'
response_headers = [('Content-type', 'text/plain'), ("Expires", "Sat, 1 Jan 2000 00:00:00 GMT")]
exc_info = 'Foo'
"#,
                )
                .unwrap()
                .as_c_str(),
                None,
                Some(&locals),
            );
            match pycode {
                Ok(_) => {
                    let status = locals.get_item("status").unwrap().unwrap();
                    let headers = locals.get_item("response_headers").unwrap().unwrap();
                    let exc_info = locals.get_item("exc_info").unwrap().unwrap();
                    let environ = PyDict::new(py);
                    // create logger
                    let mut path = temp_dir();
                    path.push("foo42.log");
                    let path = path.into_os_string();
                    WriteLogger::init(
                        LevelFilter::Info,
                        Config::default(),
                        File::create(&path).unwrap(),
                    )
                    .unwrap();

                    let mut sr = StartResponse::new(environ.into(), Vec::new());
                    match sr.__call__(py, status.clone().into(), headers.clone().into(), None) {
                        Ok(pynone) if pynone.is_none(py) => {
                            let mut errs = File::open(&path).unwrap();
                            let mut got = String::new();
                            errs.read_to_string(&mut got).unwrap();
                            assert!(!got.contains("exc_info"));
                            assert!(!got.contains("Foo"));
                        }
                        _ => assert!(false),
                    }
                    match sr.__call__(py, status.into(), headers.into(), Some(exc_info.into())) {
                        Ok(pynone) if pynone.is_none(py) => {
                            let mut errs = File::open(&path).unwrap();
                            let mut got = String::new();
                            errs.read_to_string(&mut got).unwrap();
                            assert!(got.len() > 0);
                            assert!(got.contains("exc_info"));
                            assert!(got.contains("Foo"));
                        }
                        _ => assert!(false),
                    }
                }
                _ => assert!(false),
            }
        });
    }
}
