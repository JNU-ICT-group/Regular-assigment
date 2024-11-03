import sys


def main(errors, output_paths):
    for error, output_path in zip(errors, output_paths):
        with open(output_path, 'w') as f:
            f.writelines(['0,%f\n' % (1-error), '1,%f\n' % error])


if __name__ == "__main__":
    errors = tuple(map(float, sys.argv[-2].split(',')))
    output_paths = tuple(filter(None, map(str.strip, sys.argv[-1].split(';'))))
    main(errors, output_paths)
