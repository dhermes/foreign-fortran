"""Create a universal library for ``libgfortran`` and its dependencies.

Intended to be used on OS X only. It is needed because the Homebrew
installed ``libgfortran`` is ``x86_64`` only, but it also distributes
an ``i386`` version of the necessary dynamic libraries.
"""

from __future__ import print_function

import os
import shutil
import subprocess
import sys


CURR_DIR = os.path.abspath(os.path.dirname(__file__))
FRANKENSTEIN = os.path.join(CURR_DIR, 'frankenstein')
I386_DIR = '/usr/local/Cellar/gcc/7.2.0/lib/gcc/7/i386'
X86_64_DIR = '/usr/local/Cellar/gcc/7.2.0/lib/gcc/7'
LIBGFORTRAN = 'libgfortran.4.dylib'
LIBQUADMATH = 'libquadmath.0.dylib'


def make_root_dir():
    if os.path.exists(FRANKENSTEIN):
        msg = 'The directory {} already exists.'.format(FRANKENSTEIN)
        print(msg, file=sys.stderr)
        sys.exit(1)
    else:
        os.mkdir(FRANKENSTEIN)


def copy_arch(arch, lib_dir):
    sub_dir = os.path.join(FRANKENSTEIN, arch)
    os.mkdir(sub_dir)

    old_libgfortran = os.path.join(lib_dir, LIBGFORTRAN)
    arch_libgfortran = os.path.join(sub_dir, LIBGFORTRAN)
    universal_libgfortran = os.path.join(FRANKENSTEIN, LIBGFORTRAN)
    shutil.copyfile(old_libgfortran, arch_libgfortran)

    old_libquadmath = os.path.join(lib_dir, LIBQUADMATH)
    arch_libquadmath = os.path.join(sub_dir, LIBQUADMATH)
    universal_libquadmath = os.path.join(FRANKENSTEIN, LIBQUADMATH)
    shutil.copyfile(old_libquadmath, arch_libquadmath)

    # Update ``libgfortran``
    os.chmod(arch_libgfortran, 0o644)
    subprocess.check_call((
        'install_name_tool',
        '-id', universal_libgfortran,
        arch_libgfortran,
    ))
    subprocess.check_call((
        'install_name_tool',
        '-change',
        old_libquadmath, universal_libquadmath,
        arch_libgfortran,
    ))
    os.chmod(arch_libgfortran, 0o444)

    # Update ``libquadmath``
    os.chmod(arch_libquadmath, 0o644)
    subprocess.check_call((
        'install_name_tool',
        '-id', universal_libquadmath,
        arch_libquadmath,
    ))
    os.chmod(arch_libquadmath, 0o444)

    return (
        arch_libgfortran,
        universal_libgfortran,
        arch_libquadmath,
        universal_libquadmath,
    )


def combine_dylibs(i386_dylib, x86_64_dylib, universal_dylib):
    subprocess.check_call((
        'lipo',
        i386_dylib,
        x86_64_dylib,
        '-create',
        '-output',
        universal_dylib,
    ))
    curr_dir = os.getcwd()

    # Make a symlink **without** the library version.

    # NOTE: This assumes that os.path.dirname(universal_dylib) == FRANKENSTEIN.
    filename = os.path.basename(universal_dylib)
    name, _, extension = filename.split('.')
    unversioned = '{}.{}'.format(name, extension)

    os.chdir(FRANKENSTEIN)
    os.symlink(filename, unversioned)
    os.chdir(curr_dir)


def main():
    make_root_dir()
    i386_names = copy_arch('i386', I386_DIR)
    x86_64_names = copy_arch('x86_64', X86_64_DIR)

    (i386_libgfortran, universal_libgfortran,
     i386_libquadmath, universal_libquadmath) = i386_names
    x86_64_libgfortran, _, x86_64_libquadmath, _ = x86_64_names

    combine_dylibs(i386_libgfortran, x86_64_libgfortran, universal_libgfortran)
    combine_dylibs(i386_libquadmath, x86_64_libquadmath, universal_libquadmath)


if __name__ == '__main__':
    main()
