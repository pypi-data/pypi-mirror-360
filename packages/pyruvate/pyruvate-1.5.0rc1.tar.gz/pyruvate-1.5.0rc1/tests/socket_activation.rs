use log::debug;
use mio::net::{TcpListener, UnixListener};
#[cfg(target_os = "linux")]
use pyruvate::SocketActivation;
use rand::prelude::IndexedRandom;
use std::env::{remove_var, set_var, var};
use std::fs::remove_file;
use std::os::fd::{AsRawFd, IntoRawFd};
use std::process::id;

fn random_filename() -> String {
    let mut rng = &mut rand::rng();
    (b'0'..=b'z')
        .map(|c| c as char)
        .filter(|c| c.is_alphanumeric())
        .collect::<Vec<_>>()
        .choose_multiple(&mut rng, 7)
        .collect()
}

#[cfg(target_os = "linux")]
#[test]
fn socket_activation() {
    // TCP sockets
    // no systemd environment
    if var("LISTEN_FDS").is_ok() {
        remove_var("LISTEN_FDS");
    }
    if var("LISTEN_PID").is_ok() {
        remove_var("LISTEN_PID");
    }
    match TcpListener::from_active_socket() {
        Ok(_) => assert!(false),
        Err(e) => debug!("No systemd environment, error (expected): {:?}", e),
    }
    // no file descriptors
    set_var("LISTEN_FDS", "0");
    set_var("LISTEN_PID", format!("{}", id()));
    match TcpListener::from_active_socket() {
        Ok(_) => assert!(false),
        Err(e) => debug!("No file descriptors, error (expected): {:?}", e),
    }
    // file descriptor is not a socket
    set_var("LISTEN_FDS", "1");
    set_var("LISTEN_PID", format!("{}", id()));
    match TcpListener::from_active_socket() {
        Ok(_) => assert!(false),
        Err(e) => debug!("File descriptor not a socket, error (expected): {:?}", e),
    }
    // Success
    let si = "127.0.0.1:0".parse().unwrap();
    let listener = TcpListener::bind(si).unwrap();
    // must be >= 3 (SD_LISTEN_FDS_START)
    // see libsystemd.activation for how this works
    let rl = listener.into_raw_fd();
    debug!("listener fd: {rl:?}");
    set_var("LISTEN_FDS", "1");
    set_var("LISTEN_PID", format!("{}", id()));
    match TcpListener::from_active_socket() {
        Ok(sock) => {
            assert!(sock.as_raw_fd() == 3);
        }
        Err(e) => {
            debug!("from_active_socket failed: {e}");
            assert!(false);
        }
    }
    // Unix domain sockets
    // no file descriptors
    set_var("LISTEN_FDS", "0");
    set_var("LISTEN_PID", format!("{}", id()));
    match UnixListener::from_active_socket() {
        Ok(_) => assert!(false),
        Err(e) => debug!("Error: {:?}", e),
    }
    // file descriptor is not a socket
    set_var("LISTEN_FDS", "1");
    set_var("LISTEN_PID", format!("{}", id()));
    match UnixListener::from_active_socket() {
        Ok(_) => assert!(false),
        Err(e) => debug!("Error: {:?}", e),
    }
    // Success
    let socketfile = "/tmp/".to_owned() + &random_filename() + ".socket";
    let listener = UnixListener::bind(&socketfile).unwrap();
    let rl = listener.into_raw_fd();
    debug!("listener fd: {rl:?}");
    set_var("LISTEN_FDS", "1");
    set_var("LISTEN_PID", format!("{}", id()));
    match UnixListener::from_active_socket() {
        Ok(sock) => {
            debug!("{:?}", sock);
            assert!(sock.as_raw_fd() == 3);
        }
        Err(e) => {
            debug!("Error: {:?}", e);
            assert!(false)
        }
    }
    remove_file(socketfile).unwrap();
}
