use libc;
use pyo3::Python;
use pyruvate;
use std::thread;
use std::time::Duration;

#[test]
fn test_serve() {
    thread::spawn(move || {
        thread::sleep(Duration::from_secs_f32(0.5));
        unsafe {
            libc::raise(libc::SIGINT);
        }
    });
    // serve in main thread
    Python::with_gil(|py| {
        match pyruvate::serve(
            py,
            py.None(),
            Some("localhost:0".to_string()),
            2,
            16,
            true,
            false,
            0,
            0,
            None,
            60,
        ) {
            Ok(_) => (),
            Err(_) => assert!(false),
        }
    });
}
