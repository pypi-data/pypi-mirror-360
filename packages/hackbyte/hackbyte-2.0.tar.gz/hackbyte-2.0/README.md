# 🧠 HackByte - Memory Hacker CLI

A powerful Command Line Interface (CLI) tool for memory scanning, editing, and freezing — built in Python.

🎯 Designed for Linux, Termux, or Android NetHunter environments with root access.
🧠 Perfect for users who need full control over memory processes directly from the terminal.

---

## ✨ Key Features

* 🔍 Search memory values (`int`, `float`, `string`, etc.)
* ✏️ Edit memory addresses
* 📌 Freeze memory values (prevent changes)
* 🧠 Attach to process by PID or process name
* 🛠️ Interactive shell interface powered by Python `cmdloop()`

---

## 🧪 Example Usage

```bash
hackbyte
```

Then inside the interactive shell:

```
> list
> attach 1234
> scan dword 100
> edit 0 999
> freeze 0
```

---

## 🚀 Installation

### From PyPI:

```bash
pip install hackbyte
```

### From Source:

```bash
git clone https://github.com/DX4GREY/hackbyte
cd hackbyte
pip install .
```

---

## 💻 Requirements

* Python 3.6+
* Root access (Linux/Android)
* Access to `/proc/[pid]/mem` and `/proc/[pid]/maps`
* `ptrace` or `process_vm_readv` support (depending on features)

---

## 🔒 Disclaimer

This tool is provided for educational and research purposes only.
**The author is not responsible for any misuse or illegal activities.**

---

## 🙌 Credits

Created by [Dx4Grey](https://github.com/DX4GREY)
Inspired by low-level memory manipulation and reverse engineering workflows.

---
