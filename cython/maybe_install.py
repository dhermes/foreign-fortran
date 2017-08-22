import os
import subprocess
import sys

try:
    import example
except ImportError:
    example = None

if example is None:
    bin_dir, bin_name = sys.executable.rsplit(os.path.sep, 1)
    assert bin_name == 'python'
    pip_bin = os.path.join(bin_dir, 'pip')
    subprocess.call([
        pip_bin,
        'install',
        os.path.join('cython', 'package'),
    ])
