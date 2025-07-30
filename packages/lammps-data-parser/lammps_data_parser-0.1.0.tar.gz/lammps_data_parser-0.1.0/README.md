# LAMMPS Data Parser

A Python library for parsing, editing, and writing LAMMPS data files with an intuitive object-oriented interface. The library automatically handles all header updates when modifying data, ensuring file consistency.

## Note

Currently this library only supports files with atom_style 'full'.

## Requirements

 * Python 3.6+

## Installation

```bash
pip install lammps-data-parser
```

## Usage

```python
from lammps_data_parser import LammpsData


data = LammpsData("input.data")

print(f"System contains {len(data.atoms)} atoms")
print(f"Box dimensions: {data.box}")

data.atoms[0].x = 10.0  # Change position of first atom
data.bonds.append("10 1 1 2") # Add bond
# 'bonds' in header will be automatically increased 

data.write("modified.data")
```
