#!/usr/bin/env python2.7
import matplotlib
matplotlib.rc('xtick', labelsize=8)
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import sys


def plot(xs, ys, data_dir):
    fig, ax = plt.subplots()
    ax.set_xticks(np.arange(0, 0.1, step=0.01))
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)
    ax.set_xlim(0, 0.1)
    ax.plot(xs, ys)

    ax.set(xlabel='Delta (%)', ylabel='Number of NSS pexecs',
                  title='Impact of varying absolute segment tolerance')
    ax.grid()
    fig.savefig(os.path.join(data_dir, "plot.pdf"))
    plt.show()


def main(data_dir):
    data = []
    rel = []
    with open(os.path.join(data_dir, "nss_counts.csv")) as fh:
        for line in fh:
            line = line.strip()
            delta, count = line.split(",")

            if delta.endswith("%"):
                rel.append(True)
                data.append((delta[:-1], count))
            else:
                rel.append(False)
                data.append((delta, count))

    # There shouldn't be a mix of absolute and relative deltas
    assert rel.count(rel[0]) == len(rel)

    data = sorted(data, key=lambda t: t[0])
    xs = [t[0] for t in data]
    ys = [t[1] for t in data]
    plot(xs, ys, data_dir)


def usage():
    print("usage: plot.py <data-dir>")
    sys.exit(1)


if __name__ == "__main__":
    try:
        data_dir = sys.argv[1]
    except IndexError:
        usage()

    main(data_dir)
