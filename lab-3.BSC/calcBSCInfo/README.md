# `calcBSCInfo`

A program to calculate information contents and parameters for a Binary Symmetric Channel (BSC).

## Usage

- Basic usage

```help
calcBSCInfo X Y OUTPUT
  X               path to the channel input file
  Y               path to the channel output file
  OUTPUT          path to the output file to append results
```

For example:
`calcBSCInfo "data/source.dat" "data/channel-output.dat" "data/results.csv"`

- Show help messages with usage details.
`calcBSCInfo --help`

## Unit testing

- Run the script `unit-test.cmd` (by double-clicking or from a command prompt).
- Open `unit-test/results.csv` and `unit-test/results.expect.csv` in a spreadsheet software to compare the results.

## Included files

- `README.md`/`README.html`
  This file.
- `calcBSCInfo.py`
  Source code of this program.
- `unit-test.cmd`
  Unit test for this program.
- `unit-test/`
  Directory for data used by unit test.
  - `DMS.*.dat`
    Output files from Discrete Memoryless Sources.
  - `BSC.*.dat`
    Output files from Binary Symmetric Channels.
  - `results.expect.csv`
    Expecting results from unit test.
