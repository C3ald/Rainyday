use std::env;
use std::net::{IpAddr, TcpStream};

fn main() {
    // Get the command-line arguments
    let args: Vec<String> = env::args().collect();

    // Verify that the IP address argument is provided
    if args.len() < 2 {
        println!("Please provide an IP address as an argument.");
        return;
    }

    // Parse the target IP address
    let target_ip: IpAddr = match args[1].parse() {
        Ok(ip) => ip,
        Err(_) => {
            println!("Invalid IP address provided.");
            return;
        }
    };

    // Determine whether a port argument is provided
    let port_arg_index = if args.len() > 2 {
        // A port argument is provided, parse it
        match args[2].parse() {
            Ok(port) => {
                // Scan a single port
                scan_port(&target_ip, port);
                return;
            }
            Err(_) => {
                println!("Invalid port provided.");
                return;
            }
        }
    } else {
        // No port argument provided, scan a range of ports
        0
    };

    // Scan ports 1 to 65535
    scan_ports(&target_ip, port_arg_index);
}

fn scan_ports(target_ip: &IpAddr, start_port: u16) {
    for port in start_port..=65535 {
        scan_port(target_ip, port);
    }
}

fn scan_port(target_ip: &IpAddr, port: u16) {
    let target_address = format!("{}:{}", target_ip, port);

    // Attempt to establish a TCP connection to the target IP and port
    match TcpStream::connect(target_address) {
        Ok(_) => {
            println!("Port {} is open", port);
        }
        Err(_) => {
            // Connection failed, port is closed or filtered
            // You can choose to omit printing closed/filtered ports
            // by removing this branch or adding a flag to control the behavior.
            // println!("Port {} is closed or filtered", port);
        }
    }
}
