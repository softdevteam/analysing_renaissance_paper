#!/usr/bin/env python2.7

import os
import sys
from warmup.krun_results import parse_krun_file_with_changepoints
from warmup.summary_statistics import collect_summary_statistics

DATA_DIR = "data"
QUALITY = "LOW"


def process_delta(delta_dir, delta):
    result_files = os.listdir(delta_dir)

    # The number of no steady state process executions.
    nss_count = 0
    pexec_count = 0

    for fl in result_files:
        path = os.path.join(delta_dir, fl)
        classifier, data = parse_krun_file_with_changepoints([path])
        summaries = collect_summary_statistics(data, classifier['delta'],
                                               classifier['steady'],
                                               quality=QUALITY)

        for mach, mach_data in summaries['machines'].items():
            for vm, vm_data in mach_data.items():
                for bench, cs in vm_data.items():
                    nss_count += \
                        cs["detailed_classification"]["no steady state"]
                    pexec_count += sum(cs["detailed_classification"].values())

    return nss_count, pexec_count


def main(data_dir):
    cached_pexec_count = None

    with open("nss_counts.csv","w") as out_file:
        for delta in os.listdir(data_dir):
            delta_dir = os.path.join(data_dir, delta)
            nss_count, pexec_count = process_delta(delta_dir, float(delta))

            # Should have seen the same number of pexecs for all deltas.
            if cached_pexec_count is None:
                cached_pexec_count = pexec_count
            else:
                assert pexec_count == cached_pexec_count

            out_file.write("%s,%s\n" % (delta, nss_count))


if __name__ == "__main__":
    main(DATA_DIR)
