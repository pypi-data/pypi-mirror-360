# 📦 reqbuddy – Python Requirement File Helper

![PyPI](https://img.shields.io/pypi/v/reqbuddy?color=blue)
![Python](https://img.shields.io/pypi/pyversions/reqbuddy)
![License](https://img.shields.io/github/license/AstinOfficial/reqbuddy)


A lightweight Python utility for managing `requirements.txt` files and discovering installed packages. It includes both a Python API and CLI for convenience.

📌 **Available on PyPI**: [https://pypi.org/project/reqbuddy/](https://pypi.org/project/reqbuddy/)


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

## 🛠️ For Developers: Automated Releasing

This project includes a helpful script: `release.sh`

### ✨ What it does:

- ✅ Bumps the version in `pyproject.toml`
- 📝 Updates `CHANGELOG.md` with your message
- 🏷 Creates a Git tag (e.g., `v0.1.7`)
- 🚀 Pushes the tag and code to GitHub
- 📦 Triggers GitHub Actions to publish to PyPI
- 📢 Creates a GitHub Release page
- ✅ Confirms the new version is live on PyPI

### 🧪 How to use it

```bash
./release.sh 0.1.7 "Add CLI command and improve requirement detection"
   ```
Make sure:

- You’ve installed the GitHub CLI
- You’re authenticated (`gh auth login`)




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

