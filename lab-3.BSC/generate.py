import sys


def main(ones, output_paths):
    for p, output_path in zip(ones, output_paths):
        w = 1-p
        with open(output_path, 'w') as f:
            for i in range(256):
                one = i.bit_count()
                p_one = pow(p, one) * pow(w, (8-one))
                f.write('%d,%.8f\n' % (i, p_one))


if __name__ == "__main__":
    ones = tuple(map(float, sys.argv[-2].split(',')))
    output_paths = tuple(filter(None, map(str.strip, sys.argv[-1].split(';'))))
    main(ones, output_paths)
