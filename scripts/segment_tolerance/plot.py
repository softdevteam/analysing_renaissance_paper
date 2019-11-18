#!/usr/bin/env python2.7
import matplotlib
matplotlib.rc('xtick', labelsize=5)
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np



def plot(xs, ys):
    fig, ax = plt.subplots()
    ax.set_xticks(np.arange(0, 0.1005, step=0.005))
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)
    ax.set_xlim(0, 0.1)
    ax.plot(xs, ys)

    ax.set(xlabel='Delta (seconds)', ylabel='Number of NSS pexecs',
                  title='Impact of varying absolute segment tolerance')
    ax.grid()
    fig.savefig("plot.pdf")
    plt.show()


if __name__ == "__main__":
    data = []
    with open("nss_counts.csv") as fh:
        for line in fh:
            line = line.strip()
            delta, count = line.split(",")
            data.append((delta, count))

    data = sorted(data, key=lambda t: t[0])
    xs = [t[0] for t in data]
    ys = [t[1] for t in data]
    plot(xs, ys)

    #for point in data:
    #    print(point)
