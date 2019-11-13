#!/bin/sh
#
# You will need warmup_stats in you PYTHONPATH.

python misc_tables.py \
    renaissance_linux1_1240v5-0.1_outliers_w200_changepoints.json.bz2 \
    renaissance_j9_linux1_1240v5-0.1_outliers_w200_changepoints.json.bz2 \
    renaissance_linux2_1240v6-0.1_outliers_w200_changepoints.json.bz2 \
    renaissance_j9_linux2_1240v6-0.1_outliers_w200_changepoints.json.bz2
