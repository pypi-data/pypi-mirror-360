<p align="center">
  <img src="logo.png" alt="datadocket logo" width="100%"/>
</p>

# datadocket

A simple data loading and saving utility library for Python without bloat, no pandas, no numpy, no bs. Just vanilla Python.

## Installation

Install from the root of the repository:

```bash
pip install datadocket
```

## Usage

This is a function-based library. In an unconventional and controversial move, I've decided to name the functions with an upper case initial
so it looks better. I know upper cases are supposed to be for classes... I don't care.

```python
import datadocket as dd

data = dd.load.Csv('file.csv')
dd.save.Csv('out.csv', data)
```

## Available modules:
- `dd.load`: Loading functions for txt, json, csv
- `dd.save`: Saving functions for txt, json, csv
- `dd.utils`: Utility functions
- `dd.zip`: Zip file utilities
