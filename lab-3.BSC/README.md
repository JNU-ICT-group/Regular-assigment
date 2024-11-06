# `byteChannel`

A program to calculate information contents and parameters for a Binary Symmetric Channel (BSC).

## Environment

- Python 3.x
- argparse
- numpy
- pathlib
- csv

## Usage

- Basic usage

```help
python byteChannel.py INPUT NOISE OUTPUT
  INPUT           path to the channel input file
  NOISE           Error transmission probability of BSC
  OUTPUT          path to the channel output file
```

For example:
`calcBSCInfo "data/p=0.2.dat" "data/p0=0.7.dat" "data/out.csv"`

- Show this help message and exit.
  `python byteChannel.py --help,-h`

- Base directory path

  `python byteChannel.py -d DIR, --dir DIR`

- Full prompt output

  `python byteChannel.py -O`

- Weak prompt output

  `python byteChannel.py -S ` 

- Check test flow and state

  ``python byteChannel.py --test,-t``

- Show version information

  ``python byteChannel.py --version,-v`` 

## Unit testing

- Run the script `unit-test.cmd` (by double-clicking or from a command prompt).
- Open `unit-test/results.csv` and `unit-test/results.expect.csv` in a spreadsheet software to compare the results.

## Included files

- `README.md`/`README.html`
  This file.
  
- `byteChannel.py`
  Source code of this program.
  
- `unit-test.cmd`
  Unit test for this program.
  
- `run-exp.cmd`
  
  Run this program.
  
- `unit-test/`
  Directory for data used by unit test.
  - `DMS.*.dat`
    Output files from Discrete Memoryless Sources.
    
  - `BSC.*.dat`
    Output files from Binary Symmetric Channels.
    
  - `results.expect.csv`
    Expecting results from unit test.
    
  - `results.csv`
  
    Results from unit test

