#!/usr/bin/env python2.7

import sys
from warmup.krun_results import parse_krun_file_with_changepoints
from warmup.summary_statistics import collect_summary_statistics


GREEN = "#9fffa8"
WHITE = '#ffffff'
ORANGE = '#f1ca6d'
RED = '#ff7878'
REALLY_RED = '#ff0000'

LATE_STEADY_ITER = 50

# Quality of statistics. LOW or HIGH.
QUALITY = 'HIGH'

HTML_HEADER = """<html>
        <head>
        <title>Renaissance Grids</title>
        <style>
        .rotate {
            transform: rotate(-90.0deg);
            white-space: nowrap;
            width: 2em;
        }
        td {
            border: 1px solid;
            height: 3em;
            overflow: hidden;
            font-size: x-small;
        }
        .mean_steady_iter {
            width: 50px;
        }
        table {
            width: 100%;
            table-layout: fixed;
            padding-top: 10em;
        }
        </style>
        </head>
        <body>\n\n"""


def range_from_mean_and_ci(mean, ci):
    """Make a (lo, hi) tuple from a mean and confidence interval"""
    return mean - ci, mean + ci


def ranges_overlap(r1, r2):
    """Does range tuple `r1` overlap range tuple `r2`?"""

    # If they "not distinct", then they are overlapping.
    return not (r1[1] <= r2[0] or r2[0] >= r1[1])


def process(data, dimensions):
    """Convert raw data into table row data"""

    tables = {}
    process_perf_comp_validity(data, dimensions, tables)
    process_nss(data, dimensions, tables)
    process_steady_iters(data, dimensions, tables)
    return tables


def process_nss(data, dimensions, tables):
    tables["nss-pexecs"] = {}
    shade_delta = 200.0 / dimensions["num_pexecs"]

    for mach in dimensions["machines"]:
        tables["nss-pexecs"][mach] = {}
        for vm in dimensions["vms"]:
            tables["nss-pexecs"][mach][vm] = {}
            for bench in dimensions["benchmarks"]:
                try:
                    cs = data["classifications"][mach][vm][bench]
                except KeyError:
                    num_nss = None
                else:
                    if len(cs) == 0:
                        num_nss = None
                    else:
                        num_nss = len(list(filter(
                            lambda c: c == "no steady state", cs)))

                if num_nss is None:
                    td = "-", WHITE
                elif num_nss == 0:
                    td = "0", GREEN
                else:
                    val = (dimensions["num_pexecs"] - num_nss) * shade_delta
                    val = int(val)
                    gb = "{0:02x}".format(val)
                    col = "#ff%s%s" % (gb, gb)
                    td = str(num_nss), col
                tables["nss-pexecs"][mach][vm][bench] = td


def process_steady_iters(data, dimensions, tables):
    tables["steady-iters"] = {}
    shade_delta = 200.0 / dimensions["num_iters"]

    for mach in dimensions["machines"]:
        tables["steady-iters"][mach] = {}
        for vm in dimensions["vms"]:
            tables["steady-iters"][mach][vm] = {}
            for bench in dimensions["benchmarks"]:
                try:
                    summs = data["summaries"][mach][vm][bench]
                except KeyError:
                    summs = None
                else:
                    if len(summs) == 0:
                        summs = None

                if summs is None:
                    td = "-", WHITE
                elif summs['classification'] == "flat":
                    td = "f", GREEN
                elif summs['classification'] == "no steady state":
                    td = ">", REALLY_RED
                else:
                    si = summs["steady_state_iteration"]
                    if si is None:
                        assert summs['classification'] == "bad inconsistent"
                        td = "?", REALLY_RED
                    elif si < LATE_STEADY_ITER:
                        td = str(si), GREEN
                    else:
                        # A shade of red.
                        val = int((dimensions["num_iters"] - si) * shade_delta)
                        gb = "{0:02x}".format(val)
                        col = "#ff%s%s" % (gb, gb)
                        td = str(si), col
                tables["steady-iters"][mach][vm][bench] = td


def process_perf_comp_validity(data, dimensions, tables):
    tables["perf-comp-valid"] = {}
    for mach in dimensions["machines"]:
        tables["perf-comp-valid"][mach] = {}
        for bench in dimensions["benchmarks"]:
            present_vms = {}
            for vm in ["graal-ce", "graal-ce-hotspot"]:
                try:
                    times = data["wallclock_times"][mach][vm][bench]
                except KeyError:
                    break
                else:
                    if len(times) > 0:
                        classifications = \
                            data["classifications"][mach][vm][bench]
                        if "no steady state" in classifications:
                            present_vms[vm] = "nss"
                        else:
                            summs = data["summaries"][mach][vm][bench]
                            present_vms[vm] = (summs['steady_state_time'],
                                               summs['steady_state_time_ci'])

            if len(present_vms) != 2:
                # One or other vm data was missing.
                td_text = "-"
                td_col = WHITE
            else:
                vals = present_vms.values()
                if "nss" in vals:
                    td_text = "nss"
                    td_col = RED
                else:
                    assert all([type(x) is tuple for x in vals])
                    # Compute ranges from mean and CI.
                    r1 = range_from_mean_and_ci(vals[0][0], vals[0][1])
                    r2 = range_from_mean_and_ci(vals[1][0], vals[1][1])

                    # Do they overlap?
                    if ranges_overlap(r1, r2):
                        td_text = "ci"
                        td_col = ORANGE
                    else:
                        # Ranges are distinct (non-overlapping).
                        td_text = ""
                        td_col = GREEN
            assert bench not in tables["perf-comp-valid"][mach]
            tables["perf-comp-valid"][mach][bench] = (td_text, td_col)


def render_count_matrix(html, dimensions, table):
    html.write("<table>")

    # Columns are the benchmarks.
    html.write("<tr><th></th>")
    for bench in dimensions["benchmarks"]:
        html.write("<th><div class='rotate'>%s</div></th>" % bench)
    html.write("</tr>\n")

    # Rows are VMs.
    for vm in dimensions["vms"]:
        html.write("<tr><td>%s</td>" % vm)
        for bench in dimensions["benchmarks"]:
            td = table[vm][bench]
            html.write("<td style='background-color: %s'>%s</td>" %
                       (td[1], td[0]))
        html.write("</tr>\n")
    html.write("</table>")


def render_perf_comparison_matrix(html, dimensions, tables):
    table_data = tables["perf-comp-valid"]

    html.write("<table>")

    # Columns are the benchmarks.
    html.write("<tr><th></th>")
    for bmark in dimensions["benchmarks"]:
        html.write("<th><div class='rotate'>%s</div></th>" % bmark)
    html.write("</tr>\n")

    # Rows are machines.
    for mach in dimensions["machines"]:
        html.write("<tr><td>%s</td>" % mach)
        for bmark in dimensions["benchmarks"]:
            td_text, td_col = table_data[mach][bmark]
            html.write("<td style='background-color: %s'>%s</td>" %
                       (td_col, td_text))

    html.write("</tr>\n")
    html.write("</table>")


def main(files):
    # All of the data merged into one nested dictionary.
    merged_data = {
        "classifications": {},
        "wallclock_times": {},
        "summaries": {},
    }

    # The dimensions of the data.
    # When generating tables, iterate over these (not the keys of
    # `merged_data`) to ensure that the same vms/benchmarks/machines
    # consistently appear.
    dimensions = {
        "vms": set(),
        "benchmarks": set(),
        "machines": set(),
        "num_pexecs": 0,
        "num_iters": 0,
    }

    the_classifier = None
    for file in files:
        classifier, data = parse_krun_file_with_changepoints([file])

        # All classification parameters should be the same.
        if the_classifier:
            assert classifier == the_classifier
        else:
            the_classifier = classifier

        # There is exactly one machine per file.
        assert len(data.keys()) == 1
        mach = data.keys()[0]

        # Merge in classifications.
        for k, v in data[mach]["classifications"].items():
            if mach not in merged_data["classifications"]:
                merged_data["classifications"][mach] = {}
            bench, vm, _ = k.split(":")
            if vm not in merged_data["classifications"][mach]:
                merged_data["classifications"][mach][vm] = {}
            assert bench not in merged_data["classifications"][mach][vm]
            merged_data["classifications"][mach][vm][bench] = v

        # Merge in summaries.
        summaries = collect_summary_statistics(data, classifier['delta'],
                                               classifier['steady'],
                                               quality=QUALITY)
        for vm, vm_v in summaries['machines'][mach].items():
            if mach not in merged_data["summaries"]:
                merged_data["summaries"][mach] = {}
            if vm not in merged_data["summaries"][mach]:
                merged_data["summaries"][mach][vm] = {}
            for bench, bench_v in vm_v.items():
                assert bench not in merged_data["summaries"][mach][vm]
                merged_data["summaries"][mach][vm][bench] = bench_v

        # Merge in wallclock times and update the dimensions.
        for k, v in data[mach]["wallclock_times"].items():
            if mach not in merged_data["wallclock_times"]:
                merged_data["wallclock_times"][mach] = {}
            bench, vm, _ = k.split(":")
            if vm not in merged_data["wallclock_times"][mach]:
                merged_data["wallclock_times"][mach][vm] = {}
            assert bench not in merged_data["wallclock_times"][mach][vm]
            merged_data["wallclock_times"][mach][vm][bench] = v

            dimensions["benchmarks"].add(bench)
            dimensions["vms"].add(vm)
            dimensions["machines"].add(mach)

            # Check we have the same number of pexecs (or none) for everything.
            if dimensions["num_pexecs"] == 0 and len(v) != 0:
                dimensions["num_pexecs"] = len(v)
            else:
                assert len(v) == dimensions["num_pexecs"] or len(v) == 0

            # Check we have the same number of in-process iterations per
            # process execution.
            for iters in v:
                assert type(v) is list
                if dimensions["num_iters"] == 0:
                    dimensions["num_iters"] = len(iters)
                else:
                    assert len(iters) == dimensions["num_iters"]

    assert dimensions["num_pexecs"] > 0
    assert dimensions["num_iters"] > 0
    assert len(dimensions["vms"]) > 0
    assert len(dimensions["benchmarks"]) > 0
    assert len(dimensions["machines"]) > 0

    dimensions["benchmarks"] = list(sorted(dimensions["benchmarks"]))
    dimensions["vms"] = list(sorted(dimensions["vms"]))
    dimensions["machines"] = list(sorted(dimensions["machines"]))

    # Now process the data into tables row data.
    tables = process(merged_data, dimensions)

    # Write a HTML page.
    with open("out.html", "w") as html:
        html.write(HTML_HEADER)

        html.write("<h1>Number of proc. execs not reaching"
                   "a steady state</h1>\n")
        for mach in dimensions["machines"]:
            html.write("<h2>%s</h2>\n" % mach)
            render_count_matrix(html, dimensions, tables["nss-pexecs"][mach])

        html.write("<h1>Mean Steady State Iteration</h1>\n")
        html.write("<p>Red threshold: %s iterations</p>\n" % LATE_STEADY_ITER)
        html.write("<p>'&gt;': consistently NSS\n</p>")
        html.write("<p>'?': bad inconsistent\n</p>")
        html.write("<p>'f': flat (i.e. 0)\n</p>")
        for mach in dimensions["machines"]:
            html.write("<h2>%s</h2>\n" % mach)
            render_count_matrix(html, dimensions, tables["steady-iters"][mach])

        html.write("<h1>Performance Comparison Validity "
                   "(Graal CE vs Hotspot)</h1>\n")
        html.write("<p>ci: confidence intervals overlap</p>\n")
        html.write("<p>nss: one and/or other vm had "
                   "&gt;=1 no-steady-state pexec</p>\n")
        render_perf_comparison_matrix(html, dimensions, tables)

        html.write("</body></html>")


if __name__ == "__main__":
    main(sys.argv[1:])
