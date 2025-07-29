# opencc_purepy

[![PyPI version](https://img.shields.io/pypi/v/opencc-purepy)](https://pypi.org/project/opencc-purepy/)
[![License](https://img.shields.io/github/license/laisuk/opencc_pyo3)](https://github.com/laisuk/opencc_pyo3/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/personalized-badge/opencc-purepy?period=month&units=international_system&left_color=black&right_color=orange&left_text=Downloads)](https://pepy.tech/project/opencc-purepy)
[![Build & Release](https://github.com/laisuk/opencc_purepy/actions/workflows/release.yml/badge.svg)](https://github.com/laisuk/opencc_purepy/actions/workflows/release.yml)

**opencc_purepy** is a **pure Python** implementation of [OpenCC (Open Chinese Convert)](https://github.com/BYVoid/OpenCC), supporting conversion between Simplified, Traditional, Hong Kong, Taiwan, and Japanese Kanji.  
It uses dictionary-based segmentation and mapping logic inspired by the original OpenCC.

---

## 🚩 Features

- **Pure Python** – no native dependencies
- **Multiple Chinese locale conversions** (Simplified, Traditional, HK, TW, JP)
- **Punctuation style conversion** (optional)
- **Automatic code detection** (Simplified/Traditional)
- **CLI** with Office document support (`.docx`, `.xlsx`, `.pptx`, `.odt`, `.ods`, `.odp`, `.epub`)

> 🐍 `opencc_purepy` core library is compatible with **Python 2.7+** if used as an import module.  
The CLI tool `opencc-purepy` requires **Python 3.7 or later** (due to `f-string` usage).

---

## 🔁 Supported Conversion Configs

| Code    | Description                                    |
|---------|------------------------------------------------|
| `s2t`   | Simplified → Traditional                       |
| `t2s`   | Traditional → Simplified                       |
| `s2tw`  | Simplified → Traditional (Taiwan)              |
| `tw2s`  | Traditional (Taiwan) → Simplified              |
| `s2twp` | Simplified → Traditional (Taiwan) with idioms  |
| `tw2sp` | Traditional (Taiwan) → Simplified with idioms  |
| `s2hk`  | Simplified → Traditional (Hong Kong)           |
| `hk2s`  | Traditional (Hong Kong) → Simplified           |
| `t2tw`  | Traditional → Traditional (Taiwan)             |
| `tw2t`  | Traditional (Taiwan) → Traditional             |
| `t2twp` | Traditional → Traditional (Taiwan) with idioms |
| `tw2tp` | Traditional (Taiwan) → Traditional with idioms |
| `t2hk`  | Traditional → Traditional (Hong Kong)          |
| `hk2t`  | Traditional (Hong Kong) → Traditional          |
| `t2jp`  | Japanese Kyojitai → Shinjitai                  |
| `jp2t`  | Japanese Shinjitai → Kyojitai                  |

---

## 📦 Installation

```bash
pip install opencc-purepy
```

---

## 🚀 Usage

### Python

```python
from opencc_purepy import OpenCC

text = "“春眠不觉晓，处处闻啼鸟。”"
opencc = OpenCC("s2t")
converted = opencc.convert(text, punctuation=True)
print(converted)  # 「春眠不覺曉，處處聞啼鳥。」
```

### CLI

#### Text File Conversion

```sh
python -m opencc_purepy convert -i input.txt -o output.txt -c s2t -p
# or, if installed as a script:
opencc-purepy convert -i input.txt -o output.txt -c s2t -p
```

#### Office Document Conversion (`--office`)

Supports: `.docx`, `.xlsx`, `.pptx`, `.odt`, `.ods`, `.odp`, `.epub`

```sh
# Convert Word document with font preservation
opencc-purepy convert --office -i example.docx -c t2s --keep-font

# Convert EPUB and auto-detect output name
opencc-purepy convert --office -i book.epub -c s2t --auto-ext

# Convert Excel and specify output path and format
opencc-purepy convert --office -i sheet.xlsx -o result.xlsx -c s2tw --format xlsx
```

> ℹ️ When `--office` is enabled, the input is processed as an Office or EPUB document and OpenCC conversion is applied internally.

---

## 🧩 API Reference

### `OpenCC` class

- `OpenCC(config: str = "s2t")`  
  Create a converter with the specified config.
- `convert(input: str, punctuation: bool = False) -> str`  
  Convert text with optional punctuation conversion.
- `zho_check(input: str) -> int`  
  Detect the code of the input text:  
  &nbsp;&nbsp;1 - Traditional, 2 - Simplified, 0 - Others

---

## 🛠 Development

- Python bindings: [`opencc_purepy/__init__.py`](https://github.com/laisuk/opencc_purepy/blob/master/opencc_purepy/__init__.py), [`opencc_purepy/opencc_purepy.pyi`](https://github.com/laisuk/opencc_purepy/blob/master/opencc_purepy/opencc_purepy.pyi)
- CLI: [`opencc_purepy/__main__.py`](https://github.com/laisuk/opencc_purepy/blob/master/opencc_purepy/__main__.py)

---

## ⚡ Benchmark

> Measured on a local machine using the default "s2t" configuration.  
> Each test averaged over 20 runs with preloaded dictionaries.

| Input Size        | Avg. Time (ms) |
|-------------------|---------------:|
| **100 chars**     |        0.15 ms |
| **1,000 chars**   |        0.93 ms |
| **10,000 chars**  |        8.76 ms |
| **100,000 chars** |       86.05 ms |

*Timings exclude initialization; focus is on pure conversion speed.*

---

## 📄 License

This project is licensed under the [MIT License](https://github.com/laisuk/opencc_purepy/blob/master/LICENSE).

---

Powered by Pure Python and OpenCC Lexicons.