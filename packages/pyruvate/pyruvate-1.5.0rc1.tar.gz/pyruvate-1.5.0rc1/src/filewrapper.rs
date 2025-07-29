#![allow(
    clippy::transmute_ptr_to_ptr,
    clippy::zero_ptr,
    clippy::manual_strip,
    unused_variables
)] // suppress warnings in py_class invocation
use errno::errno;
use log::{debug, error};
use pyo3::prelude::*;
use pyo3::type_object::PyTypeInfo;
use pyo3::types::{PyAnyMethods, PyBytes, PyTuple};
use pyo3::{PyResult, Python};
use std::cmp;
use std::io::Error;
use std::os::unix::io::{AsRawFd, RawFd};

use crate::pyutils::close_pyobject;
use crate::transport::would_block;

// This is the maximum the Linux kernel will write in a single sendfile call.
#[cfg(target_os = "linux")]
const SENDFILE_MAXSIZE: isize = 0x7fff_f000;

pub struct SendFileInfo {
    pub content_length: isize,
    pub blocksize: isize,
    pub offset: libc::off_t,
    pub fd: RawFd,
    pub done: bool,
}

impl SendFileInfo {
    pub fn new(fd: RawFd, blocksize: isize) -> Self {
        Self {
            content_length: -1,
            blocksize,
            offset: 0,
            fd,
            done: false,
        }
    }

    // true: chunk written completely, false: there's more
    #[cfg(target_os = "linux")]
    pub fn send_file(&mut self, out: &dyn AsRawFd) -> (bool, usize) {
        debug!("Sending file");
        let mut count = if self.blocksize < 0 {
            SENDFILE_MAXSIZE
        } else {
            self.blocksize
        };
        if self.content_length >= 0 {
            count = cmp::min(self.content_length - self.offset as isize, count);
            debug!(
                "content_length: {}, offset: {}, count: {}",
                self.content_length, self.offset, count
            );
        }
        self.done = (count == 0) || {
            match unsafe {
                libc::sendfile(out.as_raw_fd(), self.fd, &mut self.offset, count as usize)
            } {
                -1 => {
                    // will cover the case where count is too large as EOVERFLOW
                    // s. sendfile(2)
                    let err = Error::from(errno());
                    if !would_block(&err) {
                        error!("Could not sendfile(): {err:?}");
                        true
                    } else {
                        false
                    }
                }
                // 0 bytes written, assuming we're done
                0 => true,
                _ if (self.content_length > 0) => self.content_length == self.offset as isize,
                // If no content length is given, num_written might be less than count.
                // However the subsequent call will write 0 bytes -> done.
                _ => false,
            }
        };
        (self.done, self.offset as usize)
    }

    #[cfg(target_os = "macos")]
    pub fn send_file(&mut self, out: &mut dyn AsRawFd) -> (bool, usize) {
        debug!("Sending file");
        let mut count: i64 = cmp::max(0, self.blocksize as i64);
        if (self.content_length > 0) && (count > 0) {
            count = cmp::min(self.content_length as i64 - self.offset, count);
        }
        self.done = {
            let res = unsafe {
                libc::sendfile(
                    self.fd,
                    out.as_raw_fd(),
                    self.offset,
                    &mut count,
                    std::ptr::null_mut(),
                    0,
                )
            };
            if count == 0 {
                true
            } else {
                self.offset += count;
                if res == -1 {
                    let err = Error::from(errno());
                    if !would_block(&err) {
                        error!("Could not sendfile(): {:?}", err);
                        true
                    } else {
                        false
                    }
                } else {
                    if self.content_length > 0 {
                        self.content_length <= self.offset as isize
                    } else {
                        false
                    }
                }
            }
        };
        (self.done, self.offset as usize)
    }

    fn update_content_length(&mut self, content_length: isize) {
        self.content_length = content_length;
        if self.blocksize > content_length {
            self.blocksize = content_length;
        }
    }
}

#[pyclass]
pub struct FileWrapper {
    filelike: PyObject,
    pub sendfileinfo: SendFileInfo,
}

#[pymethods]
impl FileWrapper {
    #[new]
    #[pyo3(signature = (filelike, blocksize=None))]
    fn __new__(filelike: PyObject, blocksize: Option<isize>) -> Self {
        let blocksize = blocksize.unwrap_or(-1);
        let mut fd: RawFd = -1;
        Python::with_gil(|py| {
            if let Ok(fdpyob) = filelike.call_method(py, "fileno", (), None) {
                if let Ok(pyfd) = fdpyob.extract(py) {
                    fd = pyfd;
                }
            }
        });
        let sendfileinfo = SendFileInfo::new(fd, blocksize);
        FileWrapper {
            filelike,
            sendfileinfo,
        }
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(slf: PyRefMut<'_, Self>) -> Option<PyObject> {
        let py = unsafe { Python::assume_gil_acquired() };
        let sfi = &slf.sendfileinfo;
        if sfi.fd != -1 {
            return if sfi.done {
                None
            } else {
                Some(PyBytes::new(py, b"").unbind().into_any())
            };
        }
        let args = PyTuple::new(py, [slf.sendfileinfo.blocksize])
            .expect("Could not create arguments tuple.");
        if let Ok(bytes) = slf.filelike.call_method(py, "read", args, None) {
            let bytes = bytes.bind(py);
            if PyBytes::is_type_of(bytes) {
                // the following test must avoid memory allocation
                // else iteration will be slow
                match bytes.extract::<Bound<'_, PyBytes>>() {
                    Ok(pybytes) => {
                        if pybytes.is_empty().unwrap_or(true) {
                            None
                        } else {
                            Some(pybytes.unbind().into_any())
                        }
                    }
                    Err(e) => {
                        error!("Error trying to downcast: {e}");
                        None
                    }
                }
            } else {
                match slf.close(py) {
                    Err(e) => e.print_and_set_sys_last_vars(py),
                    Ok(_) => {
                        debug!("WSGIResponse dropped successfully")
                    }
                }
                None
            }
        } else {
            None
        }
    }

    fn close(&self, py: Python) -> PyResult<PyObject> {
        match close_pyobject(&self.filelike, py) {
            Ok(_) => Ok(py.None()),
            Err(e) => Err(e),
        }
    }

    pub fn has_file(&self) -> bool {
        self.sendfileinfo.fd != -1
    }
}

pub trait SendFile {
    // Put this in a trait for more flexibility.
    fn send_file(&mut self, out: &mut (dyn AsRawFd + Send + Sync), py: Python) -> (bool, usize);
    fn update_content_length(&mut self, content_length: usize, py: Python);
    // XXX used only for testing
    #[allow(dead_code, clippy::new_ret_no_self)]
    fn new(py: Python, fd: RawFd, bs: isize) -> PyResult<FileWrapper>;
}

impl SendFile for FileWrapper {
    // public getter
    fn send_file(&mut self, out: &mut (dyn AsRawFd + Send + Sync), py: Python) -> (bool, usize) {
        py.allow_threads(|| self.sendfileinfo.send_file(out))
    }

    fn update_content_length(&mut self, content_length: usize, py: Python) {
        self.sendfileinfo
            .update_content_length(content_length as isize);
    }

    fn new(py: Python, fd: RawFd, bs: isize) -> PyResult<FileWrapper> {
        Ok(FileWrapper {
            filelike: py.None(),
            sendfileinfo: SendFileInfo::new(fd, bs),
        })
    }
}

#[cfg(test)]
mod tests {
    use log::debug;
    use pyo3::types::{
        PyAnyMethods, PyBytes, PyBytesMethods, PyDict, PyDictMethods, PyInt, PyIterator, PyTuple,
        PyTypeMethods,
    };
    use pyo3::{Bound, PyRefMut, Python};
    use std::ffi::CString;
    use std::io::{Read, Seek, Write};
    use std::net::{SocketAddr, TcpListener, TcpStream};
    use std::os::unix::io::{AsRawFd, RawFd};
    use std::sync::mpsc::channel;
    use std::thread;
    use tempfile::NamedTempFile;
    use test_log::test;

    use crate::filewrapper::{FileWrapper, SendFile};

    #[test]
    fn test_no_fileno() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            match py.run(
                CString::new(
                    r#"
class FL(object):

    def __init__(self):
        self.offset = 0

    def fileno(self):
        return -1

    def read(self, blocksize):
        result = b'Foo 42'[self.offset:self.offset+blocksize]
        self.offset += blocksize
        return result

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
                        .unwrap();
                    let fd: RawFd = filelike
                        .call_method("fileno", (), None)
                        .expect("Could not call fileno method")
                        .extract()
                        .expect("Could not extract RawFd");
                    let fwtype = py.get_type::<FileWrapper>();
                    let bs: i32 = 2;
                    let fwany = fwtype
                        .call(
                            PyTuple::new(py, &[filelike, PyInt::new(py, bs).into_any()]).unwrap(),
                            None,
                        )
                        .unwrap();
                    match fwany.extract::<PyRefMut<'_, FileWrapper>>() {
                        Ok(fw) => {
                            assert_eq!(fw.sendfileinfo.fd, fd);
                        }
                        Err(e) => {
                            assert!(false);
                        }
                    }
                    match PyIterator::from_object(&fwany) {
                        Ok(mut fwiter) => {
                            for chunk in vec![b"Fo", b"o ", b"42"] {
                                match fwiter.next() {
                                    Some(got) => {
                                        assert_eq!(
                                            chunk,
                                            got.unwrap()
                                                .extract::<Bound<PyBytes>>()
                                                .unwrap()
                                                .as_bytes()
                                        );
                                    }
                                    None => {
                                        assert!(false);
                                    }
                                }
                            }
                        }
                        Err(e) => {
                            assert!(false)
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
    fn test_no_read_method() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            match py.run(
                CString::new(
                    r#"
class FL(object):

    def __init__(self):
        self.offset = 0

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
                    let bs: i32 = 2;
                    let fwany = fwtype
                        .call(
                            PyTuple::new(py, &[filelike, PyInt::new(py, bs).into_any().unbind()])
                                .unwrap(),
                            None,
                        )
                        .unwrap();
                    match PyIterator::from_object(&fwany) {
                        Ok(mut fw) => match fw.next() {
                            Some(pyresult) => match pyresult {
                                Ok(_) => assert!(false),
                                Err(_) => assert!(true),
                            },
                            None => {
                                assert!(true);
                            }
                        },
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
    fn test_bytes_not_convertible() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            match py.run(
                CString::new(
                    r#"
class FL(object):

    def __init__(self):
        self.offset = 0

    def read(self, blocksize):
        result = 'öäü'
        self.offset += blocksize
        return result

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
                    let filelike = locals.get_item("f").expect("Could not get file object");
                    let fwtype = py.get_type::<FileWrapper>();
                    let bs: i32 = 2;
                    let fwany = fwtype
                        .call(
                            PyTuple::new(py, &[filelike, Some(PyInt::new(py, bs).into_any())])
                                .unwrap(),
                            None,
                        )
                        .unwrap();
                    match PyIterator::from_object(&fwany) {
                        Ok(mut fw) => match fw.next() {
                            None => {
                                assert!(true);
                            }
                            Some(_) => {
                                assert!(false);
                            }
                        },
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
    fn test_send_file_default_params() {
        Python::with_gil(|py| {
            let addr: SocketAddr = "127.0.0.1:0".parse().expect("Failed to parse address");
            let server = TcpListener::bind(addr).expect("Failed to bind address");
            let addr = server.local_addr().unwrap();
            let mut tmp = NamedTempFile::new().unwrap();
            let mut f = tmp.reopen().unwrap();
            f.seek(std::io::SeekFrom::Start(0)).unwrap();
            let locals = PyDict::new(py);
            locals.set_item("fd", f.as_raw_fd()).unwrap();
            match py.run(
                CString::new(
                    r#"
f = open(fd)"#,
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
                        .unwrap();
                    let fw = FileWrapper::__new__(filelike.unbind(), Some(4));
                    tmp.write_all(b"Hello World!\n").unwrap();
                    let (tx, rx) = channel();
                    let (snd, got) = channel();
                    let t = thread::spawn(move || {
                        let (mut conn, _addr) = server.accept().unwrap();
                        let mut buf = [0; 13];
                        let snd = snd.clone();
                        conn.read(&mut buf).unwrap();
                        snd.send(buf).unwrap();
                        buf = [0; 13];
                        conn.read(&mut buf).unwrap();
                        snd.send(buf).unwrap();
                        buf = [0; 13];
                        conn.read(&mut buf).unwrap();
                        snd.send(buf).unwrap();
                        buf = [0; 13];
                        conn.read(&mut buf).unwrap();
                        snd.send(buf).unwrap();
                        rx.recv().unwrap();
                    });
                    let mut connection = TcpStream::connect(addr).expect("Failed to connect");
                    let mut sfi = fw.sendfileinfo;
                    sfi.send_file(&mut connection);
                    let mut b = got.recv().unwrap();
                    assert_eq!(&b[..], b"Hell\0\0\0\0\0\0\0\0\0");
                    assert_eq!(sfi.offset, 4);
                    sfi.send_file(&mut connection);
                    b = got.recv().unwrap();
                    assert_eq!(&b[..], b"o Wo\0\0\0\0\0\0\0\0\0");
                    assert_eq!(sfi.offset, 8);
                    sfi.send_file(&mut connection);
                    b = got.recv().unwrap();
                    assert_eq!(&b[..], b"rld!\0\0\0\0\0\0\0\0\0");
                    assert_eq!(sfi.offset, 12);
                    sfi.send_file(&mut connection);
                    b = got.recv().unwrap();
                    assert_eq!(&b[..], b"\n\0\0\0\0\0\0\0\0\0\0\0\0");
                    assert_eq!(sfi.offset, 13);
                    // no content length + blocksize > number bytes written, next should yield some
                    sfi.send_file(&mut connection);
                    tx.send(()).unwrap();
                    t.join().unwrap();
                    drop(f);
                    // connection is closed now
                    let (done, offset) = sfi.send_file(&mut connection);
                    assert!(done);
                    assert!(offset == 13);
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_send_file_updated_content_length() {
        Python::with_gil(|py| {
            let addr: SocketAddr = "127.0.0.1:0".parse().expect("Failed to parse address");
            let server = TcpListener::bind(addr).expect("Failed to bind address");
            let addr = server.local_addr().unwrap();
            debug!("Creating tempfile");
            let mut tmp = NamedTempFile::new().unwrap();
            tmp.write_all(b"Hello World!\n").unwrap();
            let mut f = tmp.reopen().unwrap();
            f.seek(std::io::SeekFrom::Start(0)).unwrap();
            let locals = PyDict::new(py);
            locals.set_item("fd", f.as_raw_fd()).unwrap();
            match py.run(
                CString::new(
                    r#"
f = open(fd)"#,
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
                        .unwrap();
                    let mut fw = FileWrapper::__new__(filelike.unbind(), Some(4));
                    fw.update_content_length(5, py);
                    let (tx, rx) = channel();
                    let (snd, got) = channel();
                    let t = thread::spawn(move || {
                        let (mut conn, _addr) = server.accept().unwrap();
                        let mut buf = [0; 13];
                        let snd = snd.clone();
                        conn.read(&mut buf).unwrap();
                        snd.send(buf).unwrap();
                        buf = [0; 13];
                        conn.read(&mut buf).unwrap();
                        snd.send(buf).unwrap();
                        rx.recv().unwrap();
                    });
                    let mut connection = TcpStream::connect(addr).expect("Failed to connect");
                    let mut sfi = fw.sendfileinfo;
                    sfi.send_file(&mut connection);
                    let mut b = got.recv().unwrap();
                    assert_eq!(&b[..], b"Hell\0\0\0\0\0\0\0\0\0");
                    assert_eq!(sfi.offset, 4);
                    sfi.send_file(&mut connection);
                    b = got.recv().unwrap();
                    assert_eq!(&b[..], b"o\0\0\0\0\0\0\0\0\0\0\0\0");
                    assert_eq!(sfi.offset, 5);
                    sfi.send_file(&mut connection);
                    drop(f);
                    debug!("Done (send_file).");
                    tx.send(()).unwrap();
                    t.join().unwrap();
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_send_file_content_length_lt_blocksize() {
        Python::with_gil(|py| {
            let addr: SocketAddr = "127.0.0.1:0".parse().expect("Failed to parse address");
            let server = TcpListener::bind(addr).expect("Failed to bind address");
            let addr = server.local_addr().unwrap();
            let mut tmp = NamedTempFile::new().unwrap();
            let mut f = tmp.reopen().unwrap();
            f.seek(std::io::SeekFrom::Start(0)).unwrap();
            let locals = PyDict::new(py);
            locals.set_item("fd", f.as_raw_fd()).unwrap();
            match py.run(
                CString::new(
                    r#"
f = open(fd)"#,
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
                        .unwrap();
                    let mut fw = FileWrapper::__new__(filelike.unbind(), Some(7));
                    fw.update_content_length(5, py);
                    let mut sfi = fw.sendfileinfo;
                    assert_eq!(sfi.blocksize, 5);
                    tmp.write_all(b"Hello World!\n").unwrap();
                    let (tx, rx) = channel();
                    let (snd, got) = channel();
                    let t = thread::spawn(move || {
                        let (mut conn, _addr) = server.accept().unwrap();
                        let mut buf = [0; 13];
                        let snd = snd.clone();
                        conn.read(&mut buf).unwrap();
                        snd.send(buf).unwrap();
                        rx.recv().unwrap();
                    });
                    let mut connection = TcpStream::connect(addr).expect("Failed to connect");
                    let res = sfi.send_file(&mut connection);
                    let b = got.recv().unwrap();
                    assert_eq!(&b[..], b"Hello\0\0\0\0\0\0\0\0");
                    assert_eq!(sfi.offset, 5);
                    sfi.send_file(&mut connection);
                    drop(f);
                    tx.send(()).unwrap();
                    t.join().unwrap();
                }
                Err(e) => {
                    e.print_and_set_sys_last_vars(py);
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_file_wrapper_new_no_args() {
        Python::with_gil(|py| {
            let fwtype = py.get_type::<FileWrapper>();
            match fwtype.call(PyTuple::empty(py), None) {
                Err(e) => {
                    assert!(e.get_type(py).name().unwrap() == "TypeError");
                }
                Ok(_) => assert!(false),
            }
        });
    }
}
