# PyTrnsys Process
[![Coverage Status](https://coveralls.io/repos/github/SPF-OST/pytrnsys_process/badge.svg)](https://coveralls.io/github/SPF-OST/pytrnsys_process)

> Post processing toolkit for `pytrnsys`

📚 [Documentation](https://pytrnsys-process.readthedocs.io/en/latest/) | 🚀 [Examples](examples)

## 🚀 Quick Start

### Prerequisites

#### Required

- [Python 3.12](https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe)
- Clone this repository:
  ```bash
  git clone https://github.com/SPF-OST/pytrnsys_process.git
  ```

#### Recommended

- [PyCharm Community IDE](https://www.jetbrains.com/pycharm/download)

### Installation

Run the following commands in your Windows Command Prompt from the `pytrnsys_process` directory:

1. Create and activate a virtual environment:
   ```bash
   py -3.12 -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   python -m pip install wheel
   python -m pip install -r requirements\dev.txt
   ```

3. You're ready to use the `pytrnsys_process` API! 🎉

### Try it out

Run the example script:

```bash
python examples/ready-to-run/processing-example.py
```

## 🧪 Testing

Run benchmarking tests:

```bash
# Run only benchmarks
pytest --benchmark-only

# Skip benchmarks
pytest --benchmark-skip
```

## 📝 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]

