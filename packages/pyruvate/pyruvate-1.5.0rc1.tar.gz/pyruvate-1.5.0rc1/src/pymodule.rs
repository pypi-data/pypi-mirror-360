use cfg_if::cfg_if;
use mio::net::{TcpListener, UnixListener};
use pyo3::exceptions::{PyIOError, PyValueError};
use pyo3::prelude::*;
use pyo3::{PyObject, PyResult, Python};
use std::time::Duration;

use crate::filewrapper::FileWrapper;
use crate::globals::{shared_wsgi_options, ServerOptions};
use crate::pyutils::{async_logger, sync_logger};
use crate::server::Server;
use crate::startresponse::StartResponse;
use crate::transport::{parse_server_info, shared_connection_options};

#[cfg(target_os = "linux")]
use crate::transport::SocketActivation;

macro_rules! server_loop {
    ($L:ty, $application: ident, $listener: ident, $server_options: ident, $async_logging: ident, $py: ident) => {
        match Server::<$L>::new($application, $listener, $server_options, $py) {
            Ok(mut server) => {
                let res = if $async_logging {
                    async_logger($py, "pyruvate")
                } else {
                    sync_logger($py, "pyruvate")
                };
                match res {
                    Ok(_) => match server.serve($py) {
                        Ok(_) => Ok($py.None()),
                        Err(_) => Err(PyIOError::new_err("Error encountered during event loop")),
                    },
                    Err(_) => Err(PyIOError::new_err("Could not setup logging")),
                }
            }
            Err(e) => Err(PyIOError::new_err(format!(
                "Could not create server: {e:?}"
            ))),
        }
    };
}

#[allow(clippy::too_many_arguments)]
#[pyfunction]
#[pyo3(signature=(application, addr, num_workers, max_number_headers=32, async_logging=true, chunked_transfer=false, max_reuse_count=0, keepalive_timeout=60, qmon_warn_threshold=None, send_timeout=60))]
pub fn serve(
    py: Python,
    application: PyObject,
    addr: Option<String>,
    num_workers: usize,
    max_number_headers: usize,
    async_logging: bool,
    chunked_transfer: bool,
    max_reuse_count: u8,
    keepalive_timeout: u8,
    qmon_warn_threshold: Option<usize>,
    send_timeout: u8,
) -> PyResult<PyObject> {
    if num_workers < 1 {
        return Err(PyValueError::new_err("Need at least 1 worker"));
    }
    // addr can be a TCP or Unix domain socket address
    // or None when using a systemd socket.
    let (sockaddr, server_name, server_port) = parse_server_info(addr.clone());
    let server_options = ServerOptions {
        num_workers,
        max_number_headers,
        connection_options: shared_connection_options(
            max_reuse_count,
            Duration::from_secs(keepalive_timeout.into()),
        ),
        wsgi_options: shared_wsgi_options(
            server_name.clone(),
            server_port,
            String::new(),
            chunked_transfer,
            qmon_warn_threshold,
            Duration::from_secs(send_timeout.into()),
            py,
        ),
    };
    match addr {
        Some(_) => {
            match sockaddr {
                Some(sockaddr) => match TcpListener::bind(sockaddr) {
                    Ok(listener) => server_loop!(
                        TcpListener,
                        application,
                        listener,
                        server_options,
                        async_logging,
                        py
                    ),
                    Err(e) => Err(PyIOError::new_err(format!("Could not bind socket: {e:?}"))),
                },
                None => {
                    // fallback to UnixListener
                    match UnixListener::bind(server_name) {
                        Ok(listener) => server_loop!(
                            UnixListener,
                            application,
                            listener,
                            server_options,
                            async_logging,
                            py
                        ),
                        Err(e) => Err(PyIOError::new_err(format!(
                            "Could not bind unix domain socket: {e:?}"
                        ))),
                    }
                }
            }
        }
        None => {
            cfg_if! {
                if #[cfg(target_os = "linux")] {
                    // try systemd socket activation
                    match TcpListener::from_active_socket() {
                        Ok(listener) => server_loop!(
                            TcpListener,
                            application,
                            listener,
                            server_options,
                            async_logging,
                            py
                        ),
                        Err(_) => {
                            // fall back to UnixListener
                            match UnixListener::from_active_socket() {
                                Ok(listener) => server_loop!(
                                    UnixListener,
                                    application,
                                    listener,
                                    server_options,
                                    async_logging,
                                    py
                                ),
                                Err(e) => Err(PyIOError::new_err(
                                    format!("Socket activation: {e}"),
                                )),
                            }
                        }
                    }
                } else {
                    Err(PyIOError::new_err(
                        "Could not bind socket.",
                    ))
                }
            }
        }
    }
}

#[pymodule(name = "_pyruvate")]
fn _pyruvate(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__doc__", "Pyruvate WSGI server")?;
    m.add_class::<StartResponse>()?;
    m.add_class::<FileWrapper>()?;
    m.add_function(wrap_pyfunction!(serve, m)?)
}
