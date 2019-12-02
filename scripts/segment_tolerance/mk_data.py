#!/usr/bin/env ptyhon2.7

import os
import sys
import subprocess

SCRIPT_DIR = os.getcwd()
PYTHON = sys.executable


def main(out_dir, start_delta, incr, num_incrs, relative, file_path):
    # First we annotate outliers. The result is common to all deltas.
    #
    # warmup_stats always generates the derived files alongside the orginal
    # data regardless of $CWD, so we do some symlinking magic to get files in
    # the right dirs.
    base = os.path.basename(file_path)
    symlink_target = os.path.join(out_dir, base)
    os.symlink(file_path, symlink_target)
    subprocess.check_call(["mark_outliers_in_json", symlink_target])
    os.unlink(symlink_target)

    # Grab the filename of the file we just generated.
    fls = [fl for fl in os.listdir(out_dir) if fl.endswith(".json.bz2")]
    assert len(fls) == 1
    outliers_file = os.path.abspath(os.path.join(out_dir, fls[0]))
    outliers_base = os.path.basename(outliers_file)

    for i in range(num_incrs):
        delta = str(start_delta + incr * i)
        if relative:
            delta += '%'

        wrkdir = os.path.join(out_dir, delta)
        if not os.path.exists(wrkdir):
            os.mkdir(wrkdir)

        outliers_sym = os.path.abspath(os.path.join(wrkdir, outliers_base))
        os.symlink(outliers_file, outliers_sym)
        subprocess.check_call(["mark_changepoints_in_json", "--delta",
                               delta, "--raw-deltas", outliers_sym])
        os.unlink(outliers_sym)
    os.unlink(outliers_file)


def usage():
    print("usage: mk_data.py <out-dir> <start-delta> <incr> <num-incrs> <relative?> <data-files...>")
    sys.exit(1)


if __name__ == "__main__":
    try:
        (out_dir, start_delta, incr, num_incrs, relative) = sys.argv[1:6]
        start_delta = float(start_delta)
        incr = float(incr)
        num_incrs = int(num_incrs)
        assert relative in ("0", "1")
        relative = relative == "1"
    except (IndexError, AssertionError, ValueError):
        usage()

    os.mkdir(out_dir)

    print(sys.argv[6:])
    for f in sys.argv[6:]:
        file_path = os.path.abspath(f)
        main(out_dir, start_delta, incr, num_incrs, relative, file_path)
