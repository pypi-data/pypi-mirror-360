# download_retry.py

A simple Python command-line tool to repeatedly attempt downloading a binary file from a URL until successful or until a timeout is reached.

## Features

- Downloads binary data from a given URL
- Skips SSL certificate validation by default (`--insecure true`)
- Retries every `delta_t` seconds until `max_t` seconds have elapsed
- Saves the result to a specified output file
- Returns exit code `0` on success, `1` on failure

---

## Requirements

- Python 3.6+
- `requests` package

Install dependencies using:

pip install -r requirements.txt

---

## Usage

python download_retry.py --url <URL> --delta_t <seconds> --max_t <seconds> --out <output_filename> [--insecure true|false]

### Arguments

| Argument      | Description                                      | Example                         |
|---------------|--------------------------------------------------|---------------------------------|
| `--url`       | The URL to download from                         | `https://example.com/file.bin` |
| `--delta_t`   | Time between retries in seconds                  | `5`                             |
| `--max_t`     | Maximum total wait time in seconds               | `60`                            |
| `--out`       | Output filename                                  | `file.bin`                      |
| `--insecure`  | Skip SSL verification (`true` by default)        | `true` or `false`               |

---

## Examples

### Default (insecure=True):

Skips SSL certificate verification:

python download_retry.py \
  --url "https://my.server.local/firmware.bin" \
  --delta_t 3 \
  --max_t 60 \
  --out firmware.bin

### Enforce SSL certificate verification (insecure=False):

python download_retry.py \
  --url "https://secure.example.com/file.bin" \
  --delta_t 3 \
  --max_t 60 \
  --out secure.bin \
  --insecure false

---

## Exit Codes

- `0`: File downloaded successfully
- `1`: Failed to download within time limit

---

## Testing

To run tests:

1. Install test requirements:

pip install pytest

2. Run tests:

pytest tests/

---

## Build and Install

To build source and wheel distributions:

python -m build

If you don't have the build tool installed:

pip install build

To install the package locally:

pip install .

To upload to PyPI (optional):

pip install twine
twine upload dist/*

---

## Warning

By default, SSL certificate validation is **disabled** using `--insecure true`. This may expose you to **man-in-the-middle attacks**. Use `--insecure false` to enforce SSL verification when downloading from public or sensitive endpoints.

---

## License

MIT License

## Version

0.1.0
