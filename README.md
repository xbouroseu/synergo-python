# [Synergo2Python]() - Convert Synergo algorithmic flowcharts to Python code

## Purpose:
1. Easily convert any complex flowchart to python code.
2. Helps educators to check more efficiently for errors.

## Installation & Usage:
### Requirements
- Windows
- Python3

#### Clone repository
```sh
git clone https://github.com/xbouroseu/synergo-python.git
cd synergo-python
```

### Usage
Download Synergo software [here](https://synergo.software.informer.com/download/).
Synergo works properly only in Windows currently. There are example models provided which you can open and modify.

#### Run conversion on `input_file_path` and produce `output_file_basename.py` if provided or else `input_file_basename.py`
``` sh
py convert.py input_file_path [output_file_basename]
```
