# `calcBSCInfo`

A program to calculate information contents and parameters for a Binary Symmetric Channel (BSC).

## Environment

- Python 3.x
- argparse
- numpy
- pathlib
- csv

## Usage

- Basic usage ( byteChannel.py )

```help
python byteChannel.py INPUT NOISE OUTPUT
  INPUT           path to the channel input file
  NOISE           Error transmission probability of BSC
  OUTPUT          path to the channel output file
```

For example:
`python byteChannel.py "data/p=0.2.dat" "data/p0=0.7.dat" "data/out.csv"`

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
  
  
  
- Basic usage ( calcBSCInfo.py )

  ```help
  python calcBSCInfo.py X Y OUTPUT
    X                  path to the channel input file
    Y                  path to the channel output file
    OUTPUT             path to the output file to append results
  ```
  
  For example:
  
  `python calcBSCInfo.py X.dat Y.dat OUTPUT.csv`
  
- Show this help message and exit.

  `python calcBSCInfo.py --help,-h`
  
- Path to the output file to append expect results

  `python calcBSCInfo.py --export [EXPORT]`
  
- Display detailed messages

  `python calcBSCInfo.py --verbose,-v`

## Unit testing

- Run the script `unit-test.cmd` (by double-clicking or from a command prompt).
- Open `unit-test/results.csv` and `unit-test/results.expect.csv` in a spreadsheet software to compare the results.

## Included files

- `README.md`/`README.html`
  This file.
  
- `byteChannel.py`
  Source code of this program.
  
- `byteSource.py`
  
  Generate random sequences
  
- `calcBSCInfo.py`
  
  Calculated measured and theoretical values
  
- `generate.py`

  Generate specified binary probability auxiliary files

- `parse_cmdline.py`

  Assist in parsing command-line parameters

- `unit-test.cmd`
  Unit test for this program.

- `run-exp.cmd`

  Run this program.

- `【实验3.1】实验报告.docx`

  Experiment report

- `【实验3.1】系统开发计划.html/【实验3.1】系统开发计划.md`

  System development plan

- `副本理论计算.xlsx`

  Theoretical computational model

- `input/`

  generate的二元随机信源8次扩展概率空间配置csv文件，和噪声源dat文件

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
