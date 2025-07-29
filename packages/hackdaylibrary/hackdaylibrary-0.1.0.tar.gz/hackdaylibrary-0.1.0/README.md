````markdown
# hackday

**hackday** is a powerful Python library for ethical hacking and cybersecurity. It contains over 30 modules with extensive functionality for network security testing, web application analysis, data processing, cryptography, OSINT, and many other tasks.

---

## What is it for?

- Conducting ethical penetration testing and security audits  
- Automating information gathering (reconnaissance)  
- Network analysis, vulnerability scanning, SQLi and XSS testing  
- Working with cameras, microphones, and network devices  
- Cryptoanalysis and working with hashes and passwords  
- Web page parsing and OSINT data collection  
- Tools for Docker container inspection and much more  

---

## Installation

```bash
pip install hackday
````

---

## How to use

Import the modules you need in your code:

```python
from hackday import network, wifi, camera, bruteforce, osint

# Example: Scan open ports on a host
open_ports = network.scan_ports("192.168.1.1")
print(open_ports)

# Example: Get a list of Wi-Fi networks
networks = wifi.scan_wifi_networks()
print(networks)

# Example: Record audio from the microphone
#mic.record_audio(duration=5, output_file="test.wav")

# Example: Generate all possible 4-digit PIN codes
pins = bruteforce.generate_pin_codes(length=4)
print(pins[:10])

# Example: Gather basic OSINT information
info = osint.get_basic_info("example.com")
print(info)
```

---

## Documentation

Detailed documentation for each module and function will be added soon.

---

## License

This project is licensed under the MIT License — feel free to use, modify, and distribute.

---

## Warning

The tools included in `hackday` are intended **only for ethical hacking** and security testing on your own or authorized systems. Any use of these tools for illegal activities is prohibited by law and may result in criminal charges.

---

## Contact

If you have ideas, suggestions, or want to contribute to the library’s development — please open issues or pull requests on GitHub.

---

Thank you for using `hackday`!
Be responsible and keep security first.

```
```
