# 📦 reqbuddy – Python Requirement File Helper

![PyPI](https://img.shields.io/pypi/v/reqbuddy?color=blue)
![Python](https://img.shields.io/pypi/pyversions/reqbuddy)
![License](https://img.shields.io/github/license/astin-biju/reqbuddy)
![Downloads](https://img.shields.io/pypi/dm/reqbuddy?label=pip%20downloads)

A lightweight Python utility for managing `requirements.txt` files and discovering installed packages. It includes both a Python API and CLI for convenience.


## ✨ Features

- **🔍 Read & clean `requirements.txt`**
- **📄 Generate requirements.txt from the current environment**
- **🧹 Strip version constraints if needed**
- **🖥️ CLI support: `reqbuddy get`, `reqbuddy find`**
- **♻️ Remove duplicate entries**

## 🔧 Installation
  ```bash
   pip install reqbuddy
   ```
## 🚀 CLI Usage
  ```bash
 # Generate requirements.txt from current environment
reqbuddy find

# Read and print requirements
reqbuddy get

   ```
## 🧑‍💻 Python Usage
  ```bash
from reqbuddy import find_requirement, get_requirement

# Generate requirements.txt
genreqs = find_requirement(strip=False, save=True)
print(genreqs)

# Read existing requirements.txt
reqs = get_requirement(strip=True)
print(reqs)
   ```

## ✅ Requirements
- Python 3.8+

## 📝 License
MIT License

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request


## 🙋‍♂️ Author
Astin Biju <br>
Feel free to connect on <a href="https://www.linkedin.com/in/astin-biju/">LinkedIn</a> or message me for questions or collaboration.

