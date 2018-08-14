# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from __future__ import unicode_literals

import collections
import os
import subprocess
import sys


LIBRARY_PREFIX = "libraries: ="
ERR_MSG = "Fortran search default library path not found."
BAD_PATH = "Path {} is not a directory."


def main():
    cmd = ("gfortran", "-print-search-dirs")
    cmd_output = subprocess.check_output(cmd)
    cmd_output = cmd_output.decode("utf-8")

    search_lines = cmd_output.strip().split("\n")
    library_lines = [
        line[len(LIBRARY_PREFIX) :]
        for line in search_lines
        if line.startswith(LIBRARY_PREFIX)
    ]
    if len(library_lines) != 1:
        print(ERR_MSG, file=sys.stderr)
        sys.exit(1)

    library_line = library_lines[0]
    accepted = collections.OrderedDict()  # Like an ordered set.
    for part in library_line.split(":"):
        full_path = os.path.abspath(part)

        if not os.path.exists(full_path):
            continue

        if not os.path.isdir(full_path):
            msg = BAD_PATH.format(full_path)
            print(msg, file=sys.stderr)
            sys.exit(1)

        accepted["-L" + full_path] = True

    print(" ".join(accepted.keys()))


if __name__ == "__main__":
    main()
