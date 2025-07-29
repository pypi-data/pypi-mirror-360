# brickdetector

**brickdetector** is a lightweight Python package that detects the presence of the word "brick" in any form (e.g., "Brick", "bricked", "bricking") within a given text input.

## Features

- Detects all variants of the word "brick" (case-insensitive, including prefixes and suffixes as well as unicode characters resembling characters in the word "brick")
- Easy-to-use
- Lightweight

## Installation

```bash
$ pip install brickdetector
```

## Usage

```py
from brickdetector import brickbasher

# w -- string. word to check
brickbasher(w)
```