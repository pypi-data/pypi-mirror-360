# HTTP Status Checker CLI

A fast, concurrent Python-based CLI tool to check the HTTP status codes.

---

## 🚀 Features

- ✅ Supports URL input via CLI or file
- ✅ Displays status codes and errors clearly
- ✅ Concurrent requests for fast performance
- ✅ Optional output to a result file
- ✅ Easy to extend, test, and package

---

## 📦 Installation

Clone the repo:

```bash
git clone 
cd http-status-checker
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🧪 Usage

### Check multiple URLs:

```bash
python main.py --urls https://google.com https://example.com
```

### Check from a file:

```bash
python main.py --file urls.txt
```

### Output to a file:

```bash
python main.py --file urls.txt --output results.txt
```

---

## 📄 Sample Output

```bash
[200] https://google.com
[404] https://example.com/missing
[ERR] https://notarealsite.fake (Name or service not known)
```

---

## 🔧 Tech Stack

- Python 3.7+
    - I am using Python 3.11
- `requests`
- `argparse`
- `concurrent.futures`

---

## ✅ Roadmap

- [ ] Color-coded CLI output
- [ ] Async implementation (`aiohttp`)
- [ ] Docker support
- [ ] PyPI package
- [ ] Configurable timeout and retries

---

## 🤝 Contributing

Pull requests and feature suggestions welcome! Open an issue to start a discussion.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---