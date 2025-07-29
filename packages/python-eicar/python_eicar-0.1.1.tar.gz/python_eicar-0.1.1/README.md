# python-eicar

**python-eicar** is a Python package designed to assist in testing antivirus (AV) detection mechanisms for potentially malicious packages and dependencies. It provides simple methods to generate and use the standardized [EICAR test string](https://en.wikipedia.org/wiki/EICAR_test_file), a harmless file used to verify AV software behavior.

This tool can be especially helpful for security engineers, SOC analysts, and developers looking to assess how their security stack responds to simulated malicious PyPI packages — a growing vector of supply chain attacks.

## 🚨 Disclaimer

> This package is **not malicious** and contains only the official [EICAR test string](https://www.eicar.org/download-anti-malware-testfile/), which is recognized as safe by design and used by antivirus vendors for testing.  
> It is intended for **educational and testing purposes only**. Use responsibly and at your own risk.  

---

## 🔧 Installation

Install from [PyPI](https://pypi.org/project/python-eicar):

```bash
pip install python-eicar
```

---

## ⚙️ Usage

### As a CLI tool

After installation, you can use the command-line utility:

```bash
eicar-print
```

This will print the EICAR test string to the console.

### In Python code

Import the package and use its two core functions:

```python
from python_eicar.main import eicar_print, write_eicar_in_file

# Print the EICAR string to the console
eicar_print()

# Write the EICAR string to a file
write_eicar_in_file("eicar_test_file.txt")
```

---

## 📆 API

### `eicar_print() -> bool`

Prints the EICAR test string to the console.

Returns `True` on success or `False` on failure.

---

### `write_eicar_in_file(file_path: str) -> bool`

Writes the EICAR test string to the specified file.

Returns `True` on success or `False` on failure.

```python
write_eicar_in_file("test/eicar.txt")
```

---

## ✅ Purpose

The primary goal of this project is to **simulate a benign but AV-detectable Python package**. It helps security teams test their defenses against:

- Malicious packages from PyPI
- Supply chain threats
- Runtime string inspection and detection
- Package install-time triggers

With AV and endpoint solutions now inspecting Python environments more aggressively, this tool is a **safe way to validate** that detection and response controls are working as expected.

---

## 📁 Project Structure

```
python-eicar/
├── python_eicar/
│   └── main.py
├── setup.py
├── pyproject.toml
├── README.md
└── ...
```

---

## 🛡️ Legal & Ethical Use

Use this package **only in environments you own or have permission to test**. Misuse of tools that trigger AV responses can result in unintended disruptions or legal consequences.

---

## 📜 License

MIT License – see [LICENSE](LICENSE) file for details.

---

## 🙋 Contributing

Contributions, ideas, and improvements are welcome! Open an issue or submit a pull request.

---

## ✉️ Contact

Created by [Khalid Al-Amri](https://www.linkedin.com/in/khalidwalamri/) — for security research and defensive testing.
