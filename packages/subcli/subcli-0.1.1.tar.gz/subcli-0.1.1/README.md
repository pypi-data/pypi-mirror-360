# SubCLI – Subtitle Downloader from SubtitleCat

**SubCLI** is a Python command-line tool that helps you quickly search and download movie subtitles from [subtitlecat.com](https://subtitlecat.com), all from your terminal.

---

## Features

- Search for subtitles by movie name  
- Choose from available language options  
- Download selected subtitle as a `.srt`  
- Simple, interactive CLI with arrow-key navigation  
- Clean terminal interface using [Click](https://palletsprojects.com/p/click/) and [InquirerPy](https://github.com/kazhala/InquirerPy)

---

## Installation

> Requires **Python 3.6+**

### 1. Clone the project

```bash
git clone https://github.com/yourusername/subcli.git
cd subcli
````

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install CLI locally

```bash
pip install .
```

---

## Usage

Once installed, you can run:

```bash
subcli "John Wick 4"
```

### What it does:

1. Searches SubtitleCat for results
2. Shows you a list of subtitle versions
3. Lets you pick a language
4. Downloads the subtitle `.zip` to the current folder

---

## Example

```bash
$ subcli "The Matrix"

Found 12 subtitles for 'The Matrix':
? Select a subtitle result: (Use arrow keys)
=> The Matrix 1999 BluRay x264 YIFY
   The Matrix 1999 DVDRip
   The Matrix Reloaded 2003

? Select a subtitle language: (Use arrow keys)
=> English
   Portuguese
   Spanish

 You selected: English
 File downloaded as: The.Matrix.1999.YIFY.English.zip
```

---

## Project Structure

```
subcli/
├── subcli/
│   ├── __init__.py
│   ├── cli.py               # CLI entrypoint
│   └── get_subtitle.py      # Core logic for scraping & downloading
├── setup.py
├── README.md
└── requirements.txt
```

---

## Disclaimer

This tool scrapes content from [subtitlecat.com](https://subtitlecat.com). Use it responsibly and respect subtitle licensing where applicable.

---

## Author

Developed by yannickRafael – feel free to fork or contribute.

---

## License

MIT License

```