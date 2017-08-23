from __future__ import print_function
from __future__ import unicode_literals

import os
import subprocess
import sys


LIBRARY_PREFIX = 'libraries: ='
ERR_MSG = 'Fortran search default library path not found.'
BAD_PATH = 'Path {} is not a directory.'


def main():
    cmd = ('gfortran', '-print-search-dirs')
    cmd_output = subprocess.check_output(cmd)
    cmd_output = cmd_output.decode('utf-8')

    search_lines = cmd_output.strip().split('\n')
    library_lines = [
        line[len(LIBRARY_PREFIX):]
        for line in search_lines
        if line.startswith(LIBRARY_PREFIX)
    ]
    if len(library_lines) != 1:
        print(ERR_MSG, file=sys.stderr)
        sys.exit(1)

    library_line = library_lines[0]
    accepted = []
    for part in library_line.split(':'):
        full_path = os.path.abspath(part)

        if not os.path.exists(full_path):
            continue

        if not os.path.isdir(full_path):
            msg = BAD_PATH.format(full_path)
            print(msg, file=sys.stderr)
            sys.exit(1)

        accepted.append('-L' + full_path)

    print(' '.join(accepted))


if __name__ == '__main__':
    main()
