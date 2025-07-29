# Rune-512: Compact Binary Encoding

[![PyPI version](https://badge.fury.io/py/rune-512.svg)](https://badge.fury.io/py/rune-512)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Rune-512** is a binary-to-text encoding scheme designed to safely and compactly embed arbitrary binary data in environments with strict character limits but also support a wide range of Unicode characters, such as social media bios (like Bluesky, Twitter).

It uses a carefully selected 512-character symbolic unicode alphabet that is not visually distracting and can represent data more densely than traditional encodings like Base64, packing 9 bits of data into a single character.

For example, here's 32 random bytes:

```
ᛝ⠅┯⡊⡋⢜⢴⣗▮⢌▟⣣┘▊⡼╋⢱⣜▧⣎━▋◰╾╧□⠜◡⢎⣙⠴▀
```

Here's the string `"the fox jumped over the lazy dog"`:

```
ᛝ⠟ ⡋⡑◣┦◻⢥┇⡖⠑⢡┇◗╊◞┪┹⢦◈◠┍⡬⢅⣇┤⡻⠶⠡⠨⡳⢿◣⡂◎◱⢩▵⣡⢊⣛⡉⣖⠔┭⣣○⣛┃⢒┯⡫╧⠲▊◃▲⣷⠹⢠
```

## Features

- **Compact:** Encodes 9 bits per character, offering significant space savings over Base64.
- **Reliable:** Uses a CRC-16 checksum to detect data corruption.
- **Safe:** The alphabet consists of Unicode codepoints with wide compatibility across common platforms.
- **Easy to Use:** Provides a simple command-line interface and a straightforward Python library.

## Installation

Install `rune-512` from PyPI:

```bash
pip install rune-512
```

## Usage

### Command-Line Interface

The package provides a CLI for easy encoding and decoding from your terminal.

#### Encoding

To encode a string:
```bash
python -m rune_512 encode "hello world"
# Output: ᛝ⠻◈□┫⣆▍◈⠻╯⣤▱┠
```

To encode a hex string, use the `--hex` flag:
```bash
python -m rune_512 encode --hex "deadbeef"
# Output: ᛝ⣄⢯╺╭◮◠
```

You can also pipe data from stdin:
```bash
echo "some data" | python -m rune_512 encode
# Output: ᛝ⠘⡴◍╻⣖⢤⠙⠰╴⣂
```

#### Decoding

To decode a `rune-512` string:
```bash
python -m rune_512 decode "ᛝ⠻◈□┫⣆▍◈⠻╯⣤▱┠"
# Output: hello world
```

To decode to a hex string, use the `--hex` flag:
```bash
python -m rune_512 decode --hex "ᛝ⣄⢯╺╭◮◠"
# Output: deadbeef
```

### Library

You can also use `rune-512` as a library in your Python projects.

#### Encoding

To encode a byte string:

```python
from rune_512 import encode

payload = b'hello world'
encoded_string = encode(payload)
print(encoded_string)
# Output: ᛝ⠻◈□┫⣆▍◈⠻╯⣤▱┠
```

#### Decoding

To decode a string:

```python
from rune_512 import decode

encoded_string = 'ᛝ⠻◈□┫⣆▍◈⠻╯⣤▱┠'
try:
    payload, codepoints_consumed = decode(encoded_string)
    print(payload)
    # Output: b'hello world'
    print(f"Consumed {codepoints_consumed} codepoints.")
    # Output: Consumed 13 codepoints.
except ValueError as e:
    print(f"Decoding failed: {e}")
```

The `decode` function returns a tuple containing the decoded `bytes` and the number of Unicode codepoints consumed from the input string. This is useful for parsing data from streams or larger text blocks that may contain other information. Since the payload length is not encoded in the data, `rune-512` is designed for stream-based decoding. The decoder reads characters until it encounters one outside its alphabet, and the returned count helps you know how much of the input was part of the encoded data.

## How It Works

A `rune-512` encoded string consists of three parts:

1.  **Magic Prefix (`ᛝ`):** A special character that identifies the string as `rune-512` encoded data. In practice, you can scan for this prefix to find the potential start of a `rune-512` encoded sequence in a larger text. The library exports this value as `MAGIC_PREFIX`.
2.  **Header:** A 17-bit section containing a 16-bit CRC-16/XMODEM checksum of the original payload and a parity bit for padding disambiguation.
3.  **Payload:** The binary data, packed into 9-bit chunks.

Each 9-bit chunk is mapped to a character in the 512-character alphabet. This structure ensures that the data is both compact and verifiable.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
