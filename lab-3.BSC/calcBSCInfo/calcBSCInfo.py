""" Calculate information contents and parameters of a BSC.

This program is intended for used in course, Principle of Information and Coding Theory.
Usage details can be displayed by passing command line argument `--help`.

Note: All information contents calculated are bit-wise, i.e. in (information-)bit per (binary-)bit.
"""

# Standard library
import sys
import argparse
import time
import csv
from pathlib import Path

# Non-standard library
import numpy as np

__author__ = "Guo, Jiangling"
__email__ = "tguojiangling@jnu.edu.cn"
__version__ = "20201014.1050"

def main():
    """Entry point of this program."""
    args = parse_sys_args()
    workflow(args.X, args.Y, args.OUTPUT, verbose=args.verbose)

###
# The main work flow
###
def workflow(x_file_name, y_file_name, out_file_name, verbose=False):
    """The main workflow."""

    # Number of binary bits in one symbol.
    N = 8

    x = read_file_as_bytes(x_file_name)
    y = read_file_as_bytes(y_file_name)

    ## --- Core computation: begin
    start_time = time.time()

    joint_p_xy = calc_joint_p_xy(x, y)
    H_x = calc_H_p(calc_p_x(joint_p_xy)) / N
    H_y = calc_H_p(calc_p_y(joint_p_xy)) / N
    joint_H_xy = calc_joint_H_xy(joint_p_xy) / N
    cond_H_xy = calc_cond_H_xy(joint_p_xy) / N
    cond_H_yx = calc_cond_H_yx(joint_p_xy) / N
    I_xy = H_x - cond_H_xy

    # Calculate error probability of the BSC.
    err = np.bitwise_xor(x, y)
    p_BSC = count_binary_1(err) / (x.size * N)

    elapsed_time = time.time() - start_time
    ## --- Core computation: end

    if verbose:
        p_x0 = 1 - (count_binary_1(x) / (x.size * N))
        p_y0 = 1 - (count_binary_1(y) / (y.size * N))
        print('Computation Time: %.5f sec' % (elapsed_time))
        print('  BSC input  (X): %d bytes, "%s"' % (x.size, x_file_name))
        print('  BSC output (Y): %d bytes, "%s"' % (y.size, y_file_name))
        print('  H(X) =', H_x, 'bit/bit, p(x=0) =', p_x0)
        print('  H(Y) =', H_y, 'bit/bit, p(y=0) =', p_y0)
        print(' H(XY) =', joint_H_xy, 'bit/2-bit')
        print('H(X|Y) =', cond_H_xy, 'bit/bit')
        print('H(Y|X) =', cond_H_yx, 'bit/bit')
        print('I(X;Y) =', I_xy, 'bit/bit')
        print('(BSC)p =', p_BSC)

    write_results(out_file_name, [x_file_name, y_file_name, H_x, H_y, joint_H_xy, cond_H_xy, cond_H_yx, I_xy, p_BSC])

    return H_x

###
# Computation functions
###

def calc_joint_p_xy(x, y):
    (joint_p_xy, xedges, yedges) = np.histogram2d(x, y, bins=range(257), density=True)
    return joint_p_xy

def calc_p_y(joint_p_xy):
    """Calculate p(y)."""
    return np.sum(joint_p_xy, axis=0)

def calc_p_x(joint_p_xy):
    """Calculate p(x)."""
    return np.sum(joint_p_xy, axis=1)

def calc_I_p(P):
    """Calculate self-information from given probability distribution."""
    P = replace_0_with_eps(P)
    return -np.log2(P)

def calc_H_p(P):
    """Compute entropy from given probability distribution."""
    return np.sum(P*calc_I_p(P))

def calc_joint_H_xy(joint_p_xy):
    """Calculate joint entropy H(XY)."""
    return np.sum(joint_p_xy * calc_I_p(joint_p_xy))

def calc_cond_H_xy(joint_p_xy):
    """Calculate conditional entropy H(X|Y)."""
    p_y = calc_p_y(joint_p_xy)
    p_y = replace_0_with_eps(p_y)

    # Extend p_y vertically to 255 rows:
    # p_y_matrix =
    # [ [ p(y_0), p(y_1), ..., p(y_255) ],
    #   [ p(y_0), p(y_1), ..., p(y_255) ],
    #   ...
    #   [ p(y_0), p(y_1), ..., p(y_255) ] ]
    p_y_matrix = np.repeat([p_y], joint_p_xy.shape[0], axis=0)

    return np.sum(joint_p_xy * calc_I_p(joint_p_xy / p_y_matrix))

def calc_cond_H_yx(joint_p_xy):
    """Calculate conditional entropy H(Y|X)."""
    p_x = calc_p_x(joint_p_xy)
    p_x = replace_0_with_eps(p_x)

    # Transpose p_x and extend it horizontally to 255 columns:
    # p_x_matrix = 
    # [ [ p(x_0), p(x_0), ..., p(x_0) ],
    #   [ p(x_1), p(x_1), ..., p(x_1) ],
    #   ...
    #   [ p(x_255), p(x_255), ..., p(x_255) ] ]
    p_x_matrix = np.repeat(np.array([p_x]).T,joint_p_xy.shape[1] , axis=1)

    return np.sum(joint_p_xy * calc_I_p(joint_p_xy / p_x_matrix))

def count_binary_1(x):
    # Create a Look-Up Table for number of binary '1' in each byte.
    LUT_num_of_1 = np.array([bin(byte).count("1") for byte in range(256)])
    num_of_1 = np.sum(LUT_num_of_1[x])
    return num_of_1

def replace_0_with_eps(P):
    """Replace zeros with the smallest numbers."""
    # For probabilities, it makes virtually no difference, but for computation it can prevent some undesired results such as 0*log2(0)=nan.
    return np.where(P==0, np.spacing(1), P)

###
# I/O
###

def read_file_as_bytes(in_file_name):
    """Read a file as bytes and return a uint8 array."""
    return np.fromfile(in_file_name, dtype='uint8')

def write_results(out_file_name, data):
    """Write a row of data into a CSV file."""

    # Write the header for all columns, if the output file does not exist.
    if not Path(out_file_name).is_file():
        with open(out_file_name, 'w', newline='') as out_file:
            csvwriter = csv.writer(out_file, quoting=csv.QUOTE_ALL)
            csvwriter.writerow(['X', 'Y', 'H(X)', 'H(Y)', 'H(XY)', 'H(X|Y)', 'H(Y|X)', 'I(X;Y)', 'p'])

    with open(out_file_name, 'a', newline='') as out_file:
        csvwriter = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        csvwriter.writerow(data)

###
# Parse command line arguments.
###
def parse_sys_args():
    """Parse command line arguments."""

    # Define syntax for command line arguments.
    parser = argparse.ArgumentParser(description='Calculate information for BSC.')
    parser.add_argument('X', help='path to the channel input file')
    parser.add_argument('Y', help='path to the channel output file')
    parser.add_argument('OUTPUT', help='path to the output file to append results')
    parser.add_argument('-v', '--verbose', action='store_true', help='display detailed messages')

    if len(sys.argv)==1:
        # No arguments specified.
        parser.print_help()
        parser.exit()
    else:
        args = parser.parse_args()

    return args

if __name__ == '__main__':
    main()
