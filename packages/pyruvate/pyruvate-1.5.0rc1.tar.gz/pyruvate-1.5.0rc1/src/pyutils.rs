#![allow(non_upper_case_globals)]
use crossbeam_channel::{unbounded, Receiver, Sender};
use log::{self, set_boxed_logger, set_max_level, Level, LevelFilter, Log, Record};
use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::types::{PyAnyMethods, PyDict, PyDictMethods};
use pyo3::{PyObject, PyResult, Python};
use std::cell::RefCell;
use std::ffi::CString;
use std::thread::spawn;

pub fn close_pyobject(ob: &PyObject, py: Python) -> PyResult<()> {
    if ob.getattr(py, "close").is_ok() {
        ob.call_method0(py, "close")?;
    }
    Ok(())
}

fn clear_pyerr<F, R>(mut code: F, _py: Python)
where
    F: FnMut() -> PyResult<R>,
{
    if code().is_err() {
        log::error!("Error running python code.");
        // PyErr::fetch(py);
    }
}

// We want thread names available for Python logging.
// Therefore we store the worker name in Rust thread local storage
// and update the Python logging thread name from it
thread_local!(static PY_THREAD_NAME: RefCell<String> = RefCell::new(String::from("pyruvate-main")));

fn set_python_threadinfo(py: Python, thread_name: &str) {
    if let Ok(threading) = py.import("threading") {
        let locals = PyDict::new(py);
        if locals.set_item("threading", threading).is_ok() {
            clear_pyerr(
                || {
                    py.run(
                        CString::new(format!("threading.current_thread().name = '{thread_name}'"))
                            .expect("Could not create CString")
                            .as_c_str(),
                        None,
                        Some(&locals),
                    )
                },
                py,
            );
        }
    };
}

pub fn init_python_threadinfo(py: Python, thread_name: String) {
    set_python_threadinfo(py, &thread_name);
    PY_THREAD_NAME.with(|name| {
        *name.borrow_mut() = thread_name;
    });
}

// Notes:
//
// * Not all Python logging levels are available, only
//   those corresponding to available levels
//   in the log crate
//
// * The Rust log crate expects a global logger set *once*,
//   so it's necessary/helpful to be able to change
//   the underlying Python logger in use
fn setup_python_logger(
    py: Python,
    name: &str,
) -> PyResult<(u8, u8, u8, u8, PyObject, LevelFilter)> {
    let locals = PyDict::new(py);
    let pylogging = py.import("logging")?;
    let debug = pylogging.getattr("DEBUG")?.extract()?;
    let error = pylogging.getattr("ERROR")?.extract()?;
    let info = pylogging.getattr("INFO")?.extract()?;
    let warn = pylogging.getattr("WARN")?.extract()?;
    locals.set_item("logging", pylogging)?;
    let logger: PyObject = py
        .eval(
            CString::new(format!("logging.getLogger('{name}')"))?.as_c_str(),
            None,
            Some(&locals),
        )?
        .extract()?;
    let level = logger.call_method(py, "getEffectiveLevel", (), None)?;
    match level.extract::<u8>(py) {
        Ok(u8lvl) => {
            let filter = match u8lvl {
                lvl if lvl == debug => LevelFilter::Trace,
                lvl if lvl >= error => LevelFilter::Error,
                lvl if lvl == info => LevelFilter::Info,
                lvl if lvl == warn => LevelFilter::Warn,
                _ => LevelFilter::Off,
            };
            set_max_level(filter);
            Ok((debug, error, info, warn, logger, filter))
        }
        Err(_) => Err(PyTypeError::new_err(format!("Expected u8, got {level:?}"))),
    }
}

pub struct SyncPythonLogger {
    logger: PyObject,
    debug: u8,
    error: u8,
    info: u8,
    warn: u8,
    level: Option<Level>,
}

impl SyncPythonLogger {
    pub fn new(py: Python, name: &str) -> PyResult<Self> {
        match setup_python_logger(py, name) {
            Ok((debug, error, info, warn, logger, filter)) => Ok(Self {
                logger,
                debug,
                error,
                info,
                warn,
                level: filter.to_level(),
            }),
            Err(e) => Err(e),
        }
    }

    fn python_level(&self, level: Level) -> u8 {
        match level {
            Level::Error => self.error,
            Level::Warn => self.warn,
            Level::Info => self.info,
            Level::Debug => self.debug,
            Level::Trace => self.debug,
        }
    }
}

impl Log for SyncPythonLogger {
    fn enabled(&self, metadata: &log::Metadata) -> bool {
        self.level.is_some_and(|lvl| metadata.level() <= lvl)
    }

    fn log(&self, record: &Record) {
        Python::with_gil(|py| {
            PY_THREAD_NAME.with(|name| set_python_threadinfo(py, &name.borrow()));
            clear_pyerr(
                || {
                    self.logger.call_method(
                        py,
                        "log",
                        (
                            self.python_level(record.level()),
                            format!("{}", record.args()),
                        ),
                        None,
                    )
                },
                py,
            );
        });
    }

    fn flush(&self) {}
}

type LogRecordData = ((u8, String), String);

pub struct AsyncPythonLogger {
    records: Sender<LogRecordData>,
    debug: u8,
    error: u8,
    info: u8,
    warn: u8,
    level: Option<Level>,
}

impl AsyncPythonLogger {
    const STOPMARKER: LogRecordData = ((99, String::new()), String::new());

    pub fn new(py: Python, name: &str) -> PyResult<Self> {
        match setup_python_logger(py, name) {
            Ok((debug, error, info, warn, logger, filter)) => {
                let records = Self::create_logging_thread(logger);
                Ok(Self {
                    records,
                    debug,
                    error,
                    info,
                    warn,
                    level: filter.to_level(),
                })
            }
            Err(e) => Err(e),
        }
    }

    fn python_level(&self, level: Level) -> u8 {
        match level {
            Level::Error => self.error,
            Level::Warn => self.warn,
            Level::Info => self.info,
            Level::Debug => self.debug,
            Level::Trace => self.debug,
        }
    }

    fn create_logging_thread(pylog: PyObject) -> Sender<LogRecordData> {
        let (tx, rx): (Sender<LogRecordData>, Receiver<LogRecordData>) = unbounded();
        spawn(move || {
            Python::with_gil(|py| {
                py.allow_threads(|| {
                    while let Ok(record) = rx.recv() {
                        if record == Self::STOPMARKER {
                            break;
                        }
                        Python::with_gil(|py| {
                            set_python_threadinfo(py, &record.1);
                            clear_pyerr(|| pylog.call_method(py, "log", &record.0, None), py);
                        });
                    }
                });
            });
        });
        tx
    }
}

impl Log for AsyncPythonLogger {
    fn enabled(&self, metadata: &log::Metadata) -> bool {
        self.level.is_some_and(|lvl| metadata.level() <= lvl)
    }

    fn log(&self, record: &Record) {
        let thread_name = PY_THREAD_NAME.with(|name| String::from(&(*name.borrow())));
        self.records
            .send((
                (
                    self.python_level(record.level()),
                    format!("{}", record.args()),
                ),
                thread_name,
            ))
            .unwrap_or(());
    }

    fn flush(&self) {}
}

impl Drop for AsyncPythonLogger {
    fn drop(&mut self) {
        if self.records.send(Self::STOPMARKER).is_err() {}
    }
}

macro_rules! set_global_python_logger {
    ($L: ident, $py: ident, $name: ident) => {
        match $L::new($py, $name) {
            Ok(logging) => match set_boxed_logger(Box::new(logging)) {
                Ok(_) => Ok(()),
                Err(_) => Err(PyValueError::new_err(format!(
                    "Logging already initialized"
                ))),
            },
            Err(e) => Err(e),
        }
    };
}

pub fn async_logger(py: Python, name: &str) -> PyResult<()> {
    set_global_python_logger!(AsyncPythonLogger, py, name)
}

pub fn sync_logger(py: Python, name: &str) -> PyResult<()> {
    set_global_python_logger!(SyncPythonLogger, py, name)
}

#[cfg(test)]
mod tests {
    use log::{max_level, Level, LevelFilter, Log, Record};
    use pyo3::types::{PyAnyMethods, PyDict};
    use pyo3::Python;
    use std::ffi::CString;
    use std::fs::{remove_file, File};
    use std::io::Read;
    use std::{thread, time};

    use crate::pyutils::{
        clear_pyerr, init_python_threadinfo, AsyncPythonLogger, SyncPythonLogger,
    };

    #[test]
    fn test_async_logging() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            match py.run(
                CString::new(
                    r#"
import logging
from tempfile import mkstemp

_, logfilename = mkstemp()

# create logger
logger = logging.getLogger('foo_async')
logger.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
handler = logging.FileHandler(logfilename)
handler.setFormatter(fmt)
logger.addHandler(handler)"#,
                )
                .unwrap()
                .as_c_str(),
                None,
                Some(&locals),
            ) {
                Ok(_) => match AsyncPythonLogger::new(py, "foo_async") {
                    Ok(logger) => {
                        assert_eq!(max_level(), LevelFilter::Trace);
                        py.allow_threads(|| {
                            Python::with_gil(|_py| {
                                let record = Record::builder()
                                    .args(format_args!("debug: foo"))
                                    .level(Level::Debug)
                                    .target("pyruvate")
                                    .file(Some("pyutils.rs"))
                                    .line(Some(23))
                                    .module_path(Some("tests"))
                                    .build();
                                assert!(logger.enabled(record.metadata()));
                                logger.log(&record);
                                let record = Record::builder()
                                    .args(format_args!("Foo error encountered"))
                                    .level(Level::Error)
                                    .target("pyruvate")
                                    .file(Some("pyutils.rs"))
                                    .line(Some(23))
                                    .module_path(Some("tests"))
                                    .build();
                                assert!(logger.enabled(record.metadata()));
                                logger.log(&record);
                                let record = Record::builder()
                                    .args(format_args!("bar baz info"))
                                    .level(Level::Info)
                                    .target("pyruvate")
                                    .file(Some("pyutils.rs"))
                                    .line(Some(23))
                                    .module_path(Some("tests"))
                                    .build();
                                assert!(logger.enabled(record.metadata()));
                                logger.log(&record);
                                let record = Record::builder()
                                    .args(format_args!("tracing foo async ..."))
                                    .level(Level::Trace)
                                    .target("pyruvate")
                                    .file(Some("pyutils.rs"))
                                    .line(Some(23))
                                    .module_path(Some("tests"))
                                    .build();
                                assert!(logger.enabled(record.metadata()));
                                logger.log(&record);
                                let record = Record::builder()
                                    .args(format_args!("there's a foo!"))
                                    .level(Level::Warn)
                                    .target("pyruvate")
                                    .file(Some("pyutils.rs"))
                                    .line(Some(23))
                                    .module_path(Some("tests"))
                                    .build();
                                assert!(logger.enabled(record.metadata()));
                                logger.log(&record);
                            });
                            // yield
                            thread::sleep(time::Duration::from_millis(50));
                        });
                        let logfilename: String =
                            locals.get_item("logfilename").unwrap().extract().unwrap();
                        let mut logfile = File::open(&logfilename).unwrap();
                        let mut contents = String::new();
                        logfile.read_to_string(&mut contents).unwrap();
                        assert_eq!("DEBUG:foo_async:debug: foo\nERROR:foo_async:Foo error encountered\nINFO:foo_async:bar baz info\nDEBUG:foo_async:tracing foo async ...\nWARNING:foo_async:there's a foo!\n", contents);
                        remove_file(logfilename).unwrap();
                    }
                    Err(_) => assert!(false),
                },
                Err(_) => {
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_sync_logging() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            match py.run(
                CString::new(
                    r#"
import logging
from tempfile import mkstemp

_, logfilename = mkstemp()

# create logger
logger = logging.getLogger('foo_sync')
logger.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
handler = logging.FileHandler(logfilename)
handler.setFormatter(fmt)
logger.addHandler(handler)"#,
                )
                .unwrap()
                .as_c_str(),
                None,
                Some(&locals),
            ) {
                Ok(_) => match SyncPythonLogger::new(py, "foo_sync") {
                    Ok(logger) => {
                        assert_eq!(max_level(), LevelFilter::Trace);
                        py.allow_threads(|| {
                            let record = Record::builder()
                                .args(format_args!("debug: foo"))
                                .level(Level::Debug)
                                .target("pyruvate")
                                .file(Some("pyutils.rs"))
                                .line(Some(23))
                                .module_path(Some("tests"))
                                .build();
                            assert!(logger.enabled(record.metadata()));
                            logger.log(&record);
                            let record = Record::builder()
                                .args(format_args!("Foo error encountered"))
                                .level(Level::Error)
                                .target("pyruvate")
                                .file(Some("pyutils.rs"))
                                .line(Some(23))
                                .module_path(Some("tests"))
                                .build();
                            assert!(logger.enabled(record.metadata()));
                            logger.log(&record);
                            let record = Record::builder()
                                .args(format_args!("bar baz info"))
                                .level(Level::Info)
                                .target("pyruvate")
                                .file(Some("pyutils.rs"))
                                .line(Some(23))
                                .module_path(Some("tests"))
                                .build();
                            assert!(logger.enabled(record.metadata()));
                            logger.log(&record);
                            let record = Record::builder()
                                .args(format_args!("tracing foo sync ..."))
                                .level(Level::Trace)
                                .target("pyruvate")
                                .file(Some("pyutils.rs"))
                                .line(Some(23))
                                .module_path(Some("tests"))
                                .build();
                            assert!(logger.enabled(record.metadata()));
                            logger.log(&record);
                            let record = Record::builder()
                                .args(format_args!("there's a foo!"))
                                .level(Level::Warn)
                                .target("pyruvate")
                                .file(Some("pyutils.rs"))
                                .line(Some(23))
                                .module_path(Some("tests"))
                                .build();
                            assert!(logger.enabled(record.metadata()));
                            logger.log(&record);
                        });
                        let logfilename: String =
                            locals.get_item("logfilename").unwrap().extract().unwrap();
                        let mut logfile = File::open(&logfilename).unwrap();
                        let mut contents = String::new();
                        logfile.read_to_string(&mut contents).unwrap();
                        assert_eq!("DEBUG:foo_sync:debug: foo\nERROR:foo_sync:Foo error encountered\nINFO:foo_sync:bar baz info\nDEBUG:foo_sync:tracing foo sync ...\nWARNING:foo_sync:there's a foo!\n", contents);
                        remove_file(logfilename).unwrap();
                    }
                    Err(_) => assert!(false),
                },
                Err(_) => {
                    assert!(false);
                }
            }
        });
    }

    #[test]
    fn test_python_threadinfo() {
        Python::with_gil(|py| {
            let expected = "foo42";
            init_python_threadinfo(py, String::from(expected));
            let threading = py.import("threading").unwrap();
            let locals = PyDict::new(py);
            locals.set_item("threading", threading).unwrap();
            let got: String = py
                .eval(
                    CString::new("threading.current_thread().name")
                        .unwrap()
                        .as_c_str(),
                    None,
                    Some(&locals),
                )
                .unwrap()
                .extract()
                .unwrap();
            assert_eq!(expected, &got);
        });
    }

    #[test]
    fn test_clear_pyerr() {
        Python::with_gil(|py| {
            let locals = PyDict::new(py);
            clear_pyerr(
                || {
                    py.run(
                        CString::new("raise ValueError").unwrap().as_c_str(),
                        None,
                        Some(&locals),
                    )
                },
                py,
            );
        });
    }
}
