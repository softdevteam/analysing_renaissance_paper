#!/usr/bin/env ptyhon2.7

import os
import sys
import subprocess

START_DELTA = 0.0
NUM_INCRS = 1000
INCR = 0.0001
SCRIPT_DIR = os.getcwd()
PYTHON = sys.executable
DATA_DIR = os.path.join(SCRIPT_DIR, "data")


def main(file_path):
    # First we annotate outliers. The result is common to all deltas.
    #
    # warmup_stats always generates the derived files alongside the orginal
    # data regardless of $CWD, so we do some symlinking magic to get files in
    # the right dirs.
    base = os.path.basename(file_path)
    symlink_target = os.path.join(DATA_DIR, base)
    os.symlink(file_path, symlink_target)
    subprocess.check_call(["mark_outliers_in_json", symlink_target])
    os.unlink(symlink_target)

    # Grab the filename of the file we just generated.
    fls = [fl for fl in os.listdir(DATA_DIR) if fl.endswith(".json.bz2")]
    assert len(fls) == 1
    outliers_file = os.path.join(DATA_DIR, fls[0])
    outliers_base = os.path.basename(outliers_file)

    for i in range(NUM_INCRS):
        delta = START_DELTA + INCR * i
        wrkdir = os.path.join(DATA_DIR, str(delta))
        if not os.path.exists(wrkdir):
            os.mkdir(wrkdir)

        outliers_sym = os.path.join(wrkdir, outliers_base)
        os.symlink(outliers_file, outliers_sym)
        subprocess.check_call(["mark_changepoints_in_json", "--delta",
                               str(delta), outliers_sym])
        os.unlink(outliers_sym)
    os.unlink(outliers_file)


if __name__ == "__main__":
    os.mkdir("data")
    for f in sys.argv[1:]:
        file_path = os.path.abspath(f)
        main(file_path)
