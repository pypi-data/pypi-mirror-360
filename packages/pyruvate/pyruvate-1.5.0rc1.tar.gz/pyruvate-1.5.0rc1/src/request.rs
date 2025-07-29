use encoding::all::ISO_8859_1;
use encoding::{DecoderTrap, Encoding};
use log::{debug, error};
use pyo3::types::{PyBytes, PyDict, PyDictMethods, PyTuple};
use pyo3::{IntoPyObject, Py, PyResult, Python};
use std::string::String;
use urlencoding::decode_binary;

use crate::globals::SharedWSGIOptions;

// https://tools.ietf.org/html/rfc7230#section-3.2
// Each header field consists of a case-insensitive field name ...
pub const CONTENT_LENGTH_HEADER: &str = "CONTENT-LENGTH";
const CONTENT_TYPE_HEADER: &str = "CONTENT-TYPE";
const EXPECT_HEADER: &str = "EXPECT";
const CONTINUE_EXPECTATION: &str = "100-CONTINUE";
const CONTENT_TYPE: &str = "CONTENT_TYPE";
const TRANSFER_ENCODING_HEADER: &str = "TRANSFER-ENCODING";
pub const REQUEST_METHOD: &str = "REQUEST_METHOD";
const PATH_INFO: &str = "PATH_INFO";
const QUERY_STRING: &str = "QUERY_STRING";
const SERVER_PROTOCOL: &str = "SERVER_PROTOCOL";

macro_rules! latin1_decode {
    ($val: expr) => {
        ISO_8859_1.decode($val, DecoderTrap::Strict)
    };
}

#[derive(PartialEq, Eq, Debug)]
pub enum ParsingStage {
    NotParsed,
    HeadersSuccess,
    HeadersError, // parsing headers returned an error, covering the too many headers case
    Expect100Continue, // the client expects a 100 Continue response before sending the complete request
    ContentPartial,
    ContentComplete,
}

impl ParsingStage {
    pub fn not_parsed(&self) -> bool {
        self == &ParsingStage::NotParsed
    }

    pub fn headers_complete(&self) -> bool {
        (self != &ParsingStage::NotParsed)
            && (self != &ParsingStage::HeadersError)
            && (self != &ParsingStage::Expect100Continue)
    }

    pub fn complete(&self) -> bool {
        (self == &ParsingStage::ContentComplete) | (self == &ParsingStage::HeadersError)
    }

    pub fn expect_100_continue(&self) -> bool {
        self == &ParsingStage::Expect100Continue
    }
}

pub struct WSGIRequest {
    pub data: Vec<u8>,
    pub stage: ParsingStage,
    pub content_length: usize,
    pub content_start: usize,
    pub http_headers: Vec<(String, String)>,
    pub peer_addr: String,
    num_headers: usize,
}

impl WSGIRequest {
    pub fn new(num_headers: usize, peer_addr: String) -> WSGIRequest {
        WSGIRequest {
            data: Vec::new(),
            stage: ParsingStage::NotParsed,
            content_length: 0,
            content_start: 0,
            http_headers: Vec::new(),
            peer_addr,
            num_headers,
        }
    }

    #[inline]
    pub fn append(&mut self, data: &[u8]) {
        self.data.extend_from_slice(data);
    }

    fn parse_content_length(&self, header_value: &[u8]) -> Result<usize, ParsingStage> {
        let mut cl = 0;
        for bt in header_value {
            if (*bt < 48_u8) || (*bt > 57_u8) {
                return Err(ParsingStage::HeadersError);
            } else {
                cl = cl * 10 + (*bt - 48) as usize;
            }
        }
        Ok(cl)
    }

    fn parse_headers(&mut self) -> ParsingStage {
        let mut headers = vec![httparse::EMPTY_HEADER; self.num_headers];
        let mut req = httparse::Request::new(&mut headers);
        let length = self.data.len();
        debug!("parse_headers: data length {length}");
        let mut expect_100_continue = false;
        match req.parse(&self.data) {
            Ok(res) => {
                if let httparse::Status::Complete(size) = res {
                    self.content_start = size;
                    let (mut content_length_seen, mut transfer_encoding_seen) = (false, false);
                    for header in req.headers.iter() {
                        let uname = header.name.to_ascii_uppercase();
                        match uname.as_str() {
                            CONTENT_LENGTH_HEADER => {
                                if content_length_seen {
                                    return ParsingStage::HeadersError;
                                }
                                content_length_seen = true;
                                if let Ok(val) = latin1_decode!(header.value) {
                                    if let Ok(parsedval) = val.parse() {
                                        self.content_length = parsedval;
                                    }
                                }
                                match self.parse_content_length(header.value) {
                                    Ok(cl) => self.content_length = cl,
                                    Err(stage) => return stage,
                                }
                            }
                            EXPECT_HEADER => match latin1_decode!(header.value) {
                                Ok(val) if val.to_ascii_uppercase() == CONTINUE_EXPECTATION => {
                                    expect_100_continue = true
                                }
                                _ => {
                                    error!(
                                        "Could not parse Expect header, error value: {:?}",
                                        header.value
                                    );
                                    return ParsingStage::HeadersError;
                                }
                            },
                            &_ => {
                                let key = if uname.as_str() == CONTENT_TYPE_HEADER {
                                    CONTENT_TYPE.to_string()
                                } else {
                                    if uname.as_str() == TRANSFER_ENCODING_HEADER {
                                        transfer_encoding_seen = true;
                                    }
                                    let mut key = "HTTP_".to_string();
                                    key.push_str(&uname.replace('-', "_"));
                                    key
                                };
                                match latin1_decode!(header.value) {
                                    Ok(val) => self.http_headers.push((key, val.to_string())),
                                    Err(e) => {
                                        error!("{:?} encountered for value: {:?}", e, header.value);
                                        return ParsingStage::HeadersError;
                                    }
                                }
                            }
                        }
                    }
                    if transfer_encoding_seen || !content_length_seen {
                        self.content_length = length - self.content_start;
                    }
                    if let Some(method) = req.method {
                        self.http_headers
                            .push((REQUEST_METHOD.to_string(), method.to_string()));
                    }
                    if let Some(path) = req.path {
                        let parts: Vec<&str> = path.splitn(2, '?').collect();
                        let path_info = decode_binary(parts[0].as_bytes());
                        match latin1_decode!(&path_info) {
                            Ok(latin1_path_info) => self
                                .http_headers
                                .push((PATH_INFO.to_string(), latin1_path_info)),
                            Err(e) => {
                                error!("Could not urldecode path info: {e:?}");
                                return ParsingStage::HeadersError;
                            }
                        }
                        if parts.len() > 1 {
                            self.http_headers
                                .push((QUERY_STRING.to_string(), parts[1].to_string()));
                        } else {
                            self.http_headers
                                .push((QUERY_STRING.to_string(), "".to_string()));
                        }
                    }
                    if let Some(version) = req.version {
                        // httparse ensures version is either 1.0 or 1.1,
                        // no need to check
                        let protocol = format!("HTTP/1.{version}");
                        self.http_headers
                            .push((SERVER_PROTOCOL.to_string(), protocol));
                    }
                    if !self.stage.expect_100_continue() && expect_100_continue {
                        ParsingStage::Expect100Continue
                    } else {
                        ParsingStage::HeadersSuccess
                    }
                } else {
                    ParsingStage::NotParsed
                }
            }
            Err(e) => {
                error!("Could not parse request: {e:?}");
                ParsingStage::HeadersError
            }
        }
    }

    pub fn parse_data(&mut self) -> bool {
        if !self.stage.headers_complete() {
            debug!("Parsing request headers: {:?}", self.stage);
            self.stage = self.parse_headers();
        }
        if self.stage.headers_complete() && !self.stage.expect_100_continue() {
            let length = self.data.len();
            self.stage = if self.content_length > length - self.content_start {
                // expecting more data, maybe from the next read
                debug!(
                    "Expecting more data; content_length: {}, length: {}, content_start: {}",
                    self.content_length, length, self.content_start
                );
                ParsingStage::ContentPartial
            } else {
                ParsingStage::ContentComplete
            }
        }
        self.stage.complete()
    }

    pub fn wsgi_environ(&self, globals: SharedWSGIOptions, py: Python) -> PyResult<Py<PyDict>> {
        let io = &globals.io_module;
        let environ = globals.wsgi_environ.bind(py).copy()?;
        for (k, v) in self.http_headers.iter() {
            environ.set_item(k, v)?;
        }
        environ.set_item(globals.peer_addr_key.clone_ref(py), &self.peer_addr)?;
        let input = io.call_method0(py, "BytesIO")?;
        if self.content_length > 0 {
            environ.set_item(
                globals.content_length_key.clone_ref(py),
                self.content_length,
            )?;
            input.call_method(
                py,
                "write",
                PyTuple::new(
                    py,
                    &[PyBytes::new(
                        py,
                        &self.data[self.content_start..self.content_start + self.content_length],
                    )],
                )?,
                None,
            )?;
            input.call_method(
                py,
                "seek",
                PyTuple::new(py, &[(0_i32).into_pyobject(py)?])?,
                None,
            )?;
        }
        environ.set_item(globals.wsgi_input_key.clone_ref(py), input)?;
        Ok(environ.unbind())
    }

    pub fn is_bad_request(&self) -> bool {
        self.stage == ParsingStage::HeadersError
    }
}

#[cfg(test)]
mod tests {
    use log::debug;
    use pyo3::types::{PyAnyMethods, PyBytes, PyBytesMethods, PyDictMethods, PyString};
    use pyo3::{Bound, Python};
    use std::net::SocketAddr;
    use std::time::Duration;

    use crate::globals::{shared_wsgi_options, SharedWSGIOptions};
    use crate::request::{ParsingStage, WSGIRequest};

    macro_rules! assert_header {
        ($got:ident, $py:ident, $key:literal, $value:expr) => {
            assert!(
                $got.bind($py)
                    .get_item($key)
                    .unwrap()
                    .unwrap()
                    .extract::<Bound<PyString>>()
                    .unwrap()
                    .to_string()
                    == $value
            );
        };
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

    #[test]
    fn test_get() {
        let raw = b"GET /foo42?bar=baz HTTP/1.1\r\nAuthorization: Basic YWRtaW46YWRtaW4=\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\n\r\n";
        let mut got = WSGIRequest::new(16, String::new());
        got.append(raw);
        got.parse_data();
        assert!(got.http_headers.len() == 13);
        for (name, value) in got.http_headers.iter() {
            match name.as_str() {
                "HTTP_COOKIE" => assert!(&value[..] == "foo_language=en;"),
                "PATH_INFO" => assert!(&value[..] == "/foo42"),
                "QUERY_STRING" => assert!(&value[..] == "bar=baz"),
                "HTTP_ACCEPT" => assert!(&value[..] == "image/webp,*/*"),
                "HTTP_ACCEPT_LANGUAGE" => assert!(&value[..] == "de-DE,en-US;q=0.7,en;q=0.3"),
                "HTTP_ACCEPT_ENCODING" => assert!(&value[..] == "gzip, deflate"),
                "HTTP_AUTHORIZATION" => assert!(&value[..] == "Basic YWRtaW46YWRtaW4="),
                "HTTP_CONNECTION" => assert!(&value[..] == "keep-alive"),
                "REQUEST_METHOD" => assert!(&value[..] == "GET"),
                "HTTP_HOST" => assert!(&value[..] == "localhost:7878"),
                "HTTP_USER_AGENT" => {
                    let expected = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0";
                    assert_eq!(value, expected);
                }
                "HTTP_DNT" => assert_eq!(&value[..], "1"),
                "SERVER_PROTOCOL" => assert_eq!(&value[..], "HTTP/1.1"),
                &_ => {}
            }
        }
    }

    #[test]
    fn test_url_decode() {
        let raw = b"GET /foo%2042?bar=baz%20foo&next=newsletter%3D%252F434%252F%252F2021-03-05%26rw%3Dtrue HTTP/1.1\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\n\r\n";
        let mut got = WSGIRequest::new(16, String::new());
        got.append(raw);
        got.parse_data();
        assert!(got.http_headers.len() == 12);
        for (name, value) in got.http_headers.iter() {
            match name.as_str() {
                "HTTP_COOKIE" => assert!(&value[..] == "foo_language=en;"),
                "PATH_INFO" => assert!(&value[..] == "/foo 42"),
                "QUERY_STRING" => assert!(&value[..] == "bar=baz%20foo&next=newsletter%3D%252F434%252F%252F2021-03-05%26rw%3Dtrue"),
                "HTTP_ACCEPT" => assert!(&value[..] == "image/webp,*/*"),
                "HTTP_ACCEPT_LANGUAGE" => assert!(&value[..] == "de-DE,en-US;q=0.7,en;q=0.3"),
                "HTTP_ACCEPT_ENCODING" => assert!(&value[..] == "gzip, deflate"),
                "HTTP_CONNECTION" => assert!(&value[..] == "keep-alive"),
                "REQUEST_METHOD" => assert!(&value[..] == "GET"),
                "HTTP_HOST" => assert!(&value[..] == "localhost:7878"),
                "HTTP_USER_AGENT" => {
                    let expected = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0";
                    assert_eq!(value, expected);
                }
                "HTTP_DNT" => assert_eq!(&value[..], "1"),
                "SERVER_PROTOCOL" => assert_eq!(&value[..], "HTTP/1.1"),
                &_ => {}
            }
        }
    }

    #[test]
    fn test_latin1_url() {
        let raw = b"GET /f%C3%A4%C3%A4%2042?bar=baz%20foo&next=newsletter%3D%252F434%252F%252F2021-03-05%26rw%3Dtrue HTTP/1.1\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\n\r\n";
        let mut got = WSGIRequest::new(16, String::new());
        got.append(raw);
        got.parse_data();
        assert!(got.http_headers.len() == 12);
        for (name, value) in got.http_headers.iter() {
            match name.as_str() {
                "HTTP_COOKIE" => assert!(&value[..] == "foo_language=en;"),
                // PATH_INFO contains latin-1 escape characters.
                // The expected result should be the same as
                // if we would be using the following Python expression:
                //
                // urlib.parse.unquote('/f%C3%A4%C3%A4%2042', encoding='latin-1')
                //
                // i.e. the following UTF-8 encoded byte sequence
                // b'/f\xc3\x83\xc2\xa4\xc3\x83\xc2\xa4 42'
                "PATH_INFO" => assert!(value.as_bytes() == b"/f\xc3\x83\xc2\xa4\xc3\x83\xc2\xa4 42"),
                "QUERY_STRING" => assert!(&value[..] == "bar=baz%20foo&next=newsletter%3D%252F434%252F%252F2021-03-05%26rw%3Dtrue"),
                "HTTP_ACCEPT" => assert!(&value[..] == "image/webp,*/*"),
                "HTTP_ACCEPT_LANGUAGE" => assert!(&value[..] == "de-DE,en-US;q=0.7,en;q=0.3"),
                "HTTP_ACCEPT_ENCODING" => assert!(&value[..] == "gzip, deflate"),
                "HTTP_CONNECTION" => assert!(&value[..] == "keep-alive"),
                "REQUEST_METHOD" => assert!(&value[..] == "GET"),
                "HTTP_HOST" => assert!(&value[..] == "localhost:7878"),
                "HTTP_USER_AGENT" => {
                    let expected = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0";
                    assert_eq!(value, expected);
                }
                "HTTP_DNT" => assert_eq!(&value[..], "1"),
                "SERVER_PROTOCOL" => assert_eq!(&value[..], "HTTP/1.1"),
                &_ => {}
            }
        }
    }

    #[test]
    fn test_latin1_path_info() {
        // seen in production logs
        let raw = b"GET /%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/etc/passwd HTTP/1.1\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\n\r\n";
        let mut got = WSGIRequest::new(16, String::new());
        got.append(raw);
        if got.parse_data() {
            assert!(got.stage == ParsingStage::ContentComplete);
        } else {
            assert!(false);
        }
    }

    #[test]
    fn test_error_url() {
        let raw = b"GET /foo 42?bar=baz foo HTTP/1.1\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\n\r\n";
        let mut got = WSGIRequest::new(16, String::new());
        got.append(raw);
        match got.parse_data() {
            true => {
                assert!(got.stage == ParsingStage::HeadersError);
            }
            false => assert!(false),
        }
    }

    #[test]
    fn test_parse_body_once() {
        let raw = b"POST /test HTTP/1.1\r\nHost: foo.example\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 27\r\n\r\nfield1=value1&field2=value2";
        let mut got = WSGIRequest::new(16, String::new());
        got.append(raw);
        got.parse_data();
        assert!(got.stage.complete());
        for (name, value) in got.http_headers.iter() {
            match name.as_str() {
                "CONTENT_TYPE" => {
                    let expected = "application/x-www-form-urlencoded";
                    assert_eq!(value, expected);
                }
                &_ => {}
            }
        }
        let body = &got.data[got.content_start..got.content_start + got.content_length];
        assert_eq!(body, b"field1=value1&field2=value2");
    }

    #[test]
    fn test_parse_multiple() {
        let raw1 = b"POST /test HTTP/1.1\r\nHost: foo.example\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 41\r\n\r\nfield1=value1&field2=value2";
        let raw2 = b"&field3=value3";
        let mut got = WSGIRequest::new(16, String::new());
        got.append(raw1);
        got.parse_data();
        assert!(!got.stage.complete());
        assert!(got.content_length == 41);
        got.append(raw2);
        got.parse_data();
        assert!(got.stage.complete());
        assert!(got.content_length == 41);
        for (name, value) in got.http_headers.iter() {
            match name.as_str() {
                "CONTENT_TYPE" => {
                    let expected = "application/x-www-form-urlencoded";
                    assert_eq!(expected, value);
                }
                &_ => {}
            }
        }
        let expected = b"field1=value1&field2=value2&field3=value3";
        let body = &got.data[got.content_start..got.content_start + got.content_length];
        debug!("{:?}", body);
        assert!(body.iter().zip(expected.iter()).all(|(p, q)| p == q));
    }

    #[test]
    fn test_parse_expect_continue() {
        let raw = b"POST /test HTTP/1.1\r\nHost: foo.example\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 27\r\nExpect: 100-continue\r\n\r\n";
        let body = b"field1=value1&field2=value2";
        let mut got = WSGIRequest::new(16, String::new());
        got.append(raw);
        got.parse_data();
        assert!(!got.stage.headers_complete());
        assert!(!got.stage.complete());
        assert!(got.stage.expect_100_continue());
        got.append(body);
        got.parse_data();
        assert!(got.stage.headers_complete());
        assert!(got.stage.complete());
        assert!(!got.stage.expect_100_continue());
        let body = &got.data[got.content_start..got.content_start + got.content_length];
        assert_eq!(body, b"field1=value1&field2=value2");
        let raw = b"POST /test HTTP/1.1\r\nHost: foo.example\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 27\r\nExpect: 101-whatever\r\n\r\n";
        let mut got = WSGIRequest::new(16, String::new());
        got.append(raw);
        got.parse_data();
        assert!(!got.stage.headers_complete());
        assert!(got.stage.complete());
        assert!(!got.stage.expect_100_continue());
        assert_eq!(got.stage, ParsingStage::HeadersError);
        got.append(body);
        got.parse_data();
        assert!(!got.stage.headers_complete());
        assert!(got.stage.complete());
        assert!(!got.stage.expect_100_continue());
        assert_eq!(got.stage, ParsingStage::HeadersError);
    }

    #[test]
    fn test_environ_dict() {
        Python::with_gil(|py| {
            let (g, _) = make_globals(py);
            let raw = b"GET /foo42?bar=baz HTTP/1.1\r\nAuthorization: Basic YWRtaW46YWRtaW4=\r\nHost: localhost:7878\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0\r\nAccept: image/webp,*/*\r\nAccept-Language: de-DE,en-US;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nCookie: foo_language=en;\r\nDNT: 1\r\n\r\n";
            let mut req = WSGIRequest::new(16, String::from("192.168.1.23"));
            req.append(raw);
            req.parse_data();
            let got = req.wsgi_environ(g, py).unwrap();
            assert_header!(got, py, "SERVER_NAME", "127.0.0.1");
            assert_header!(got, py, "SERVER_PORT", "0");
            assert_header!(got, py, "SCRIPT_NAME", "/foo");
            assert_header!(got, py, "REMOTE_ADDR", "192.168.1.23");
            assert_header!(got, py, "HTTP_COOKIE", "foo_language=en;");
            assert_header!(got, py, "PATH_INFO", "/foo42");
            assert_header!(got, py, "QUERY_STRING", "bar=baz");
            assert_header!(got, py, "HTTP_ACCEPT", "image/webp,*/*");
            assert_header!(
                got,
                py,
                "HTTP_ACCEPT_LANGUAGE",
                "de-DE,en-US;q=0.7,en;q=0.3"
            );
            assert_header!(got, py, "HTTP_ACCEPT_ENCODING", "gzip, deflate");
            assert_header!(got, py, "HTTP_AUTHORIZATION", "Basic YWRtaW46YWRtaW4=");
            assert_header!(got, py, "HTTP_CONNECTION", "keep-alive");
            assert_header!(got, py, "REQUEST_METHOD", "GET");
            assert_header!(got, py, "HTTP_HOST", "localhost:7878");
            assert_header!(
                got,
                py,
                "HTTP_USER_AGENT",
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0"
            );
            assert_header!(got, py, "HTTP_DNT", "1");
            assert_header!(got, py, "SERVER_PROTOCOL", "HTTP/1.1");
        });
    }

    #[test]
    fn test_post_simple_form() {
        Python::with_gil(|py| {
            let (g, _) = make_globals(py);
            let raw = b"POST /test HTTP/1.1\r\nHost: foo.example\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 27\r\n\r\nfield1=value1&field2=value2";
            let mut req = WSGIRequest::new(16, String::new());
            req.append(raw);
            req.parse_data();
            let got = req.wsgi_environ(g, py).unwrap();
            assert_header!(got, py, "CONTENT_TYPE", "application/x-www-form-urlencoded");
            let input = got
                .bind(py)
                .get_item("wsgi.input")
                .unwrap()
                .unwrap()
                .unbind()
                .clone_ref(py);
            debug!("{:?}", input);
            let input = input.call_method0(py, "read").unwrap();
            debug!("{:?}", input);
            assert!(
                input.extract::<Bound<PyBytes>>(py).unwrap().as_bytes()
                    == b"field1=value1&field2=value2"
            );
        });
    }

    #[test]
    fn test_post_multipart_formdata() {
        Python::with_gil(|py| {
            let (g, _) = make_globals(py);
            let raw = b"POST /test HTTP/1.1\r\nHost: foo.example\r\nConnection: close\r\nContent-Length: 346\r\nContent-Type: multipart/form-data; boundary=---------------------------2534525279945612714245917864\r\nDNT: 1\r\n\r\n-----------------------------2534525279945612714245917864\r\nContent-Disposition: form-data; name=\"file\"; filename=\"dummy.text\"\r\nContent-Type: text/plain\r\n\r\ndummy\r\n\r\n-----------------------------2534525279945612714245917864\r\nContent-Disposition: form-data; name=\"upload\"\r\n\r\nUpload File\r\n-----------------------------2534525279945612714245917864--\r\n";
            let mut req = WSGIRequest::new(16, String::new());
            req.append(raw);
            req.parse_data();
            let got = req.wsgi_environ(g, py).unwrap();
            assert_header!(
                got,
                py,
                "CONTENT_TYPE",
                "multipart/form-data; boundary=---------------------------2534525279945612714245917864"
            );
            let input = got
                .bind(py)
                .get_item("wsgi.input")
                .unwrap()
                .unwrap()
                .unbind()
                .clone_ref(py);
            let input = input.call_method0(py, "read").unwrap();
            let expected = b"-----------------------------2534525279945612714245917864\r\nContent-Disposition: form-data; name=\"file\"; filename=\"dummy.text\"\r\nContent-Type: text/plain\r\n\r\ndummy\r\n\r\n-----------------------------2534525279945612714245917864\r\nContent-Disposition: form-data; name=\"upload\"\r\n\r\nUpload File\r\n-----------------------------2534525279945612714245917864--\r\n";
            let got = input.extract::<Bound<PyBytes>>(py).unwrap();
            let got = got.as_bytes();
            debug!("got: {}, expected: {}", got.len(), expected.len());
            assert!(got.len() == expected.len());
            assert!(got.iter().zip(expected.iter()).all(|(p, q)| p == q));
        });
    }

    #[test]
    fn test_parsing_stages() {
        assert!(ParsingStage::HeadersSuccess.headers_complete());
        assert!(!ParsingStage::HeadersError.headers_complete());
        assert!(!ParsingStage::Expect100Continue.headers_complete());
        assert!(!ParsingStage::HeadersSuccess.complete());
        assert!(ParsingStage::ContentComplete.complete());
        assert!(!ParsingStage::Expect100Continue.complete());
    }

    #[test]
    fn test_content_length_only_digits() {
        // https://www.rfc-editor.org/rfc/rfc7230#section-3.3.2
        // a Content-Length header field can provide the anticipated size, as a
        // decimal number of octets, for a potential payload body.
        // ...
        // Content-Length = 1*DIGIT
        let raw = b"POST /test HTTP/1.1\r\nHost: foo.example\r\nConnection: close\r\nContent-Length: 0x8bca\r\nContent-Type: multipart/form-data; boundary=---------------------------2534525279945612714245917864\r\nDNT: 1\r\n\r\n-----------------------------2534525279945612714245917864\r\nContent-Disposition: form-data; name=\"file\"; filename=\"dummy.text\"\r\nContent-Type: text/plain\r\n\r\ndummy\r\n\r\n-----------------------------2534525279945612714245917864\r\nContent-Disposition: form-data; name=\"upload\"\r\n\r\nUpload File\r\n-----------------------------2534525279945612714245917864--\r\n";
        let mut req = WSGIRequest::new(16, String::new());
        req.append(raw);
        req.parse_data();
        assert!(req.stage == ParsingStage::HeadersError);
        let raw = b"POST /test HTTP/1.1\r\nHost: foo.example\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: +27\r\n\r\nfield1=value1&field2=value2";
        let mut req = WSGIRequest::new(16, String::new());
        req.append(raw);
        req.parse_data();
        assert!(req.stage == ParsingStage::HeadersError);
        let raw = b"POST /test HTTP/1.1\r\nHost: foo.example\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 27\r\n\r\nfield1=value1&field2=value2";
        let mut req = WSGIRequest::new(16, String::new());
        req.append(raw);
        req.parse_data();
        assert!(req.stage == ParsingStage::ContentComplete);
        let raw = b"POST /test HTTP/1.1\r\nHost: foo.example\r\nConnection: close\r\nContent-Length: -20\r\nContent-Type: multipart/form-data; boundary=---------------------------2534525279945612714245917864\r\nDNT: 1\r\n\r\n-----------------------------2534525279945612714245917864\r\nContent-Disposition: form-data; name=\"file\"; filename=\"dummy.text\"\r\nContent-Type: text/plain\r\n\r\ndummy\r\n\r\n-----------------------------2534525279945612714245917864\r\nContent-Disposition: form-data; name=\"upload\"\r\n\r\nUpload File\r\n-----------------------------2534525279945612714245917864--\r\n";
        let mut req = WSGIRequest::new(16, String::new());
        req.append(raw);
        req.parse_data();
        assert!(req.stage == ParsingStage::HeadersError);
    }

    #[test]
    fn test_content_length_twice() {
        // example from https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn
        let raw = b"POST / HTTP/1.1\r\nHost: example.com\r\nContent-Length: 6\r\nContent-Length: 5\r\n\r\n12345GPOST / HTTP/1.1\r\nHost: example.com";
        let mut req = WSGIRequest::new(16, String::new());
        req.append(raw);
        req.parse_data();
        assert!(req.stage == ParsingStage::HeadersError);
    }

    #[test]
    fn test_parse_content_length_transfer_encoding_present() {
        // https://www.rfc-editor.org/rfc/rfc7230#section-3.3.2
        // A sender MUST NOT send a Content-Length header field in any message
        // that contains a Transfer-Encoding header field.
        // https://www.rfc-editor.org/rfc/rfc2616#section-4.4
        // If a message is received with both a
        // Transfer-Encoding header field and a Content-Length header field,
        // the latter MUST be ignored.
        //
        // --> use calculated content length and ignore content-length header if transfer-encoding is present
        //
        // example from https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn
        let raw = b"POST / HTTP/1.1\r\nHost: example.com\r\nContent-Length: 6\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\nGPOST / HTTP/1.1\r\nHost: example.com";
        let mut req = WSGIRequest::new(16, String::new());
        req.append(raw);
        req.parse_data();
        assert!(req.stage == ParsingStage::ContentComplete);
        assert!(req.content_length == 40);
        let raw = b"POST / HTTP/1.1\r\nHost: example.com\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\nGPOST / HTTP/1.1\r\nHost: example.com";
        let mut req = WSGIRequest::new(16, String::new());
        req.append(raw);
        req.parse_data();
        assert!(req.content_length == 40);
        assert!(req.stage == ParsingStage::ContentComplete);
    }
}
