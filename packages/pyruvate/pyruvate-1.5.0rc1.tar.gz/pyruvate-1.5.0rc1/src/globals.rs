use log::{debug, error};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyDictMethods, PyModule, PyString};
use std::sync::Arc;
use std::time::Duration;

use crate::transport::SharedConnectionOptions;

pub struct WSGIOptions {
    pub io_module: Py<PyModule>,
    pub wsgi_environ: Py<PyDict>,
    pub peer_addr_key: Py<PyString>,
    pub content_length_key: Py<PyString>,
    pub wsgi_input_key: Py<PyString>,
    pub chunked_transfer: bool,
    pub qmon_warn_threshold: Option<usize>,
    pub send_timeout: Duration,
}

impl WSGIOptions {
    pub fn new(
        server_name: String,
        server_port: String,
        script_name: String,
        chunked_transfer: bool,
        qmon_warn_threshold: Option<usize>,
        send_timeout: Duration,
        py: Python,
    ) -> WSGIOptions {
        // XXX work around not being able to import wsgi module from tests
        let wsgi_module = match py.import("pyruvate") {
            Ok(pyruvate) => Some(pyruvate.unbind()),
            Err(_) => {
                error!("Could not import WSGI module, so no FileWrapper");
                None
            }
        };
        let sys_module = py.import("sys").expect("Could not import module sys");
        let wsgi_environ = Self::prepare_wsgi_environ(
            &server_name,
            &server_port,
            &script_name,
            &sys_module.unbind(),
            wsgi_module.as_ref(),
            py,
        )
        .expect("Could not create wsgi environ template");
        WSGIOptions {
            io_module: py
                .import("io")
                .expect("Could not import module io")
                .unbind(),
            wsgi_environ,
            peer_addr_key: PyString::new(py, "REMOTE_ADDR").unbind(),
            content_length_key: PyString::new(py, "CONTENT_LENGTH").unbind(),
            wsgi_input_key: PyString::new(py, "wsgi.input").unbind(),
            chunked_transfer,
            qmon_warn_threshold,
            send_timeout,
        }
    }

    fn prepare_wsgi_environ(
        server_name: &str,
        server_port: &str,
        script_name: &str,
        sys: &Py<PyModule>,
        wsgi: Option<&Py<PyModule>>,
        py: Python,
    ) -> PyResult<Py<PyDict>> {
        let environ = PyDict::new(py);
        environ.set_item("SERVER_NAME", server_name)?;
        environ.set_item("SERVER_PORT", server_port)?;
        environ.set_item("SCRIPT_NAME", script_name)?;
        environ.set_item("wsgi.errors", sys.getattr(py, "stderr")?)?;
        environ.set_item("wsgi.version", (1, 0))?;
        environ.set_item("wsgi.multithread", false)?;
        environ.set_item("wsgi.multiprocess", true)?;
        environ.set_item("wsgi.run_once", false)?;
        environ.set_item("wsgi.url_scheme", "http")?;
        if let Some(wsgi) = wsgi {
            debug!("Setting FileWrapper in environ");
            environ.set_item("wsgi.file_wrapper", wsgi.getattr(py, "FileWrapper")?)?;
        }
        Ok(environ.into())
    }
}

pub type SharedWSGIOptions = Arc<WSGIOptions>;

pub fn shared_wsgi_options(
    server_name: String,
    server_port: String,
    script_name: String,
    chunked_transfer: bool,
    qmon_warn_threshold: Option<usize>,
    send_timeout: Duration,
    py: Python,
) -> SharedWSGIOptions {
    Arc::new(WSGIOptions::new(
        server_name,
        server_port,
        script_name,
        chunked_transfer,
        qmon_warn_threshold,
        send_timeout,
        py,
    ))
}

pub struct ServerOptions {
    pub num_workers: usize,
    pub max_number_headers: usize,
    pub connection_options: SharedConnectionOptions,
    pub wsgi_options: SharedWSGIOptions,
}

#[cfg(test)]
mod tests {
    use crate::globals::WSGIOptions;
    use log::debug;
    use pyo3::types::{PyDictMethods, PyModuleMethods, PyString};
    use pyo3::{Bound, Python};
    use std::time::Duration;

    #[test]
    fn test_creation() {
        Python::with_gil(|py| {
            let sn = String::from("127.0.0.1");
            let sp = String::from("7878");
            let script = String::from("/foo");
            let pypath = py.import("sys").unwrap().dict().get_item("path").unwrap();
            debug!("sys.path: {:?}", pypath);
            let got = WSGIOptions::new(
                sn.clone(),
                sp.clone(),
                script.clone(),
                false,
                None,
                Duration::from_secs(60),
                py,
            );
            match got.wsgi_environ.bind(py).get_item("SERVER_NAME").unwrap() {
                Some(pyob) => {
                    assert!(
                        pyob.unbind()
                            .extract::<Bound<PyString>>(py)
                            .unwrap()
                            .to_string()
                            == sn
                    )
                }
                None => assert!(false),
            }
            match got.wsgi_environ.bind(py).get_item("SERVER_PORT").unwrap() {
                Some(pyob) => {
                    assert!(
                        pyob.unbind()
                            .extract::<Bound<PyString>>(py)
                            .unwrap()
                            .to_string()
                            == sp
                    )
                }
                None => assert!(false),
            }
            match got.wsgi_environ.bind(py).get_item("SCRIPT_NAME").unwrap() {
                Some(pyob) => {
                    assert!(
                        pyob.unbind()
                            .extract::<Bound<PyString>>(py)
                            .unwrap()
                            .to_string()
                            == script
                    )
                }
                None => assert!(false),
            }
        });
    }
}
