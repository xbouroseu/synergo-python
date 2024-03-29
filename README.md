# Synergo2Python
## Convert Synergo algorithmic flowcharts to Python code

### Purpose:
1. Easily convert any complex flowchart to python code.
2. Helps educators to check more efficiently for errors.

## Installation & Usage:
### Requirements
- Python3

#### 1. (Optional) Download Synergo client
Download Synergo client software [here](https://synergo.software.informer.com/download/).
Synergo currently works properly only in **Windows**. There are example models included here which you can open and modify.

#### 2. Clone repository
```sh
git clone https://github.com/xbouroseu/synergo-python.git
cd synergo-python
```

#### 3. Run conversion on `input_file_path` and produce `./output_file_basename.py` if provided or else `./input_file_basename.py`
``` sh
python convert.py input_file_path [output_file_basename]
```
### Example
Running for `examples/model2.synergo` which looks like this:

![alt text](https://github.com/xbouroseu/synergo-python/blob/master/examples/model2.png)

Produces the following:
```python
x = int(input("Give x: "))
y = int(input("Give y: "))
z = int(input("Give z: "))
w = 0
if x>0:
    w = x + y + z
    if w > 20:
        w = 2*w + 1
    else:
        w = w*w
else:
    w = x - y - z
print("W: ", w)
```
