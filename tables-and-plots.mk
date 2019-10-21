DATA_B7 = renaissance_linux1_1240v5-0.1.json.bz2
DATA_B7_URL = https://archive.org/download/softdev_renaissance_analysis/runs/v0.1/linux1_1240v5/graal_and_hotspot/${DATA_B7}
DATA_B7_OUTLIERS = renaissance_linux1_1240v5-0.1_outliers_w200.json.bz2
DATA_B7_OUTLIERS_CPTS = renaissance_linux1_1240v5-0.1_outliers_w200_changepoints.json.bz2

DATA_B10 = renaissance_linux2_1240v6-0.1.json.bz2
DATA_B10_URL = https://archive.org/download/softdev_renaissance_analysis/runs/v0.1/linux2_1240v6/graal_and_hotspot/${DATA_B10}
DATA_B10_OUTLIERS = renaissance_linux2_1240v6-0.1_outliers_w200.json.bz2
DATA_B10_OUTLIERS_CPTS = renaissance_linux2_1240v6-0.1_outliers_w200_changepoints.json.bz2

# The OpenJ9 results were collected separately, so they are in their own results files.
DATA_J9_B7 = renaissance_j9_linux1_1240v5-0.1.json.bz2
DATA_J9_B7_URL = https://archive.org/download/softdev_renaissance_analysis/runs/v0.1/linux1_1240v5/openj9/${DATA_J9_B7}
DATA_J9_B7_OUTLIERS = renaissance_j9_linux1_1240v5-0.1_outliers_w200.json.bz2
DATA_J9_B7_OUTLIERS_CPTS = renaissance_j9_linux1_1240v5-0.1_outliers_w200_changepoints.json.bz2

DATA_J9_B10 = renaissance_j9_linux2_1240v6-0.1.json.bz2
DATA_J9_B10_URL = https://archive.org/download/softdev_renaissance_analysis/runs/v0.1/linux2_1240v6/openj9/${DATA_J9_B10}
DATA_J9_B10_OUTLIERS = renaissance_j9_linux2_1240v6-0.1_outliers_w200.json.bz2
DATA_J9_B10_OUTLIERS_CPTS = renaissance_j9_linux2_1240v6-0.1_outliers_w200_changepoints.json.bz2

-include common.mk

all: ${TABLES} ${PLOTS}

#
# Table generation.
#

warmup_stats:
	git clone https://github.com/softdevteam/warmup_stats
	cd warmup_stats && sh build.sh

.PHONY: tables
tables: ${TABLES}

data:
	mkdir -p data
	cd data && wget --no-use-server-timestamps ${DATA_B7_URL} && \
		../warmup_stats/bin/mark_outliers_in_json ${DATA_B7} && \
		../warmup_stats/bin/mark_changepoints_in_json ${DATA_B7_OUTLIERS}
	cd data && \
		wget --no-use-server-timestamps ${DATA_B10_URL} && \
		../warmup_stats/bin/mark_outliers_in_json ${DATA_B10} && \
		../warmup_stats/bin/mark_changepoints_in_json ${DATA_B10_OUTLIERS}
	cd data && wget --no-use-server-timestamps ${DATA_J9_B7_URL} && \
		../warmup_stats/bin/mark_outliers_in_json ${DATA_J9_B7} && \
		../warmup_stats/bin/mark_changepoints_in_json ${DATA_J9_B7_OUTLIERS}
	cd data && \
		wget --no-use-server-timestamps ${DATA_J9_B10_URL} && \
		../warmup_stats/bin/mark_outliers_in_json ${DATA_J9_B10} && \
		../warmup_stats/bin/mark_changepoints_in_json ${DATA_J9_B10_OUTLIERS}

${TABLE_B7_GRAAL_CE}: ${TABLE_B7_GRAAL_CE_HOTSPOT}
	warmup_stats/bin/table_classification_summaries_others -o $@ \
		--only-vms graal-ce --without-preamble \
		data/${DATA_B7_OUTLIERS_CPTS}
	sed -i'.orig' 's/\\end{longtable}/\\caption{\\captionbsevengraalce}\n\\label{tab:b7graalce}\n\\end{longtable}/g' $@

${TABLE_B7_GRAAL_CE_HOTSPOT}: data
	warmup_stats/bin/table_classification_summaries_others -o $@ \
		--only-vms graal-ce-hotspot --without-preamble \
		data/${DATA_B7_OUTLIERS_CPTS}
	sed -i'.orig' 's/\\end{longtable}/\\caption{\\captionbsevengraalcehs}\n\\label{tab:b7graalcehs}\n\\end{longtable}/g' $@

${TABLE_B10_GRAAL_CE}: ${TABLE_B10_GRAAL_CE_HOTSPOT}
	warmup_stats/bin/table_classification_summaries_others -o $@ \
		--only-vms graal-ce --without-preamble \
		data/${DATA_B10_OUTLIERS_CPTS}
	sed -i'.orig' 's/\\end{longtable}/\\caption{\\captionbtengraalce}\n\\label{tab:b10graalce}\n\\end{longtable}/g' $@

${TABLE_B10_GRAAL_CE_HOTSPOT}: data
	warmup_stats/bin/table_classification_summaries_others -o $@ \
		--only-vms graal-ce-hotspot --without-preamble \
		data/${DATA_B10_OUTLIERS_CPTS}
	sed -i'.orig' 's/\\end{longtable}/\\caption{\\captionbtengraalcehs}\n\\label{tab:b10graalcehs}\n\\end{longtable}/g' $@

${TABLE_B7_J9}: data
	warmup_stats/bin/table_classification_summaries_others -o $@ \
		--only-vms openj9 --without-preamble \
		data/${DATA_J9_B7_OUTLIERS_CPTS}
	sed -i'.orig' 's/\\end{longtable}/\\caption{\\captionbsevenjnine}\n\\label{tab:b7j9}\n\\end{longtable}/g' $@

${TABLE_B10_J9}: data
	warmup_stats/bin/table_classification_summaries_others -o $@ \
		--only-vms openj9 --without-preamble \
		data/${DATA_J9_B10_OUTLIERS_CPTS}
	sed -i'.orig' 's/\\end{longtable}/\\caption{\\captionbtenjnine}\n\\label{tab:b10j9}\n\\end{longtable}/g' $@

#
# Plot generation
#

plots/slowdown1.pdf: warmup_stats data
	mkdir -p plots
	warmup_stats/bin/plot_krun_results --with-outliers --with-changepoints -o $@ \
		-b bencher7:akka-uct:graal-ce-hotspot:default-ext:6 data/${DATA_B7_OUTLIERS_CPTS}

plots/no-steady1.pdf: warmup_stats data
	mkdir -p plots
	warmup_stats/bin/plot_krun_results --with-outliers --with-changepoints -o $@ \
		-b bencher7:log-regression:graal-ce:default-ext:5 data/${DATA_B7_OUTLIERS_CPTS}

plots/no-steady2.pdf: warmup_stats data
	mkdir -p plots
	warmup_stats/bin/plot_krun_results --with-outliers --with-changepoints -o $@ \
		-b bencher10:scala-kmeans:graal-ce-hotspot:default-ext:1 data/${DATA_B10_OUTLIERS_CPTS}

plots/cycles1.pdf: warmup_stats data
	mkdir -p plots
	warmup_stats/bin/plot_krun_results --with-outliers --with-changepoints -o $@ \
		-b bencher7:mnemonics:graal-ce:default-ext:8 data/${DATA_B7_OUTLIERS_CPTS}

plots/outliers1.pdf: warmup_stats data
	mkdir -p plots
	warmup_stats/bin/plot_krun_results --with-outliers --with-changepoints -o $@ \
		-b bencher10:future-genetic:graal-ce-hotspot:default-ext:9 data/${DATA_B10_OUTLIERS_CPTS}

plots/fastearly1.pdf: warmup_stats data
	mkdir -p plots
	warmup_stats/bin/plot_krun_results --with-outliers --with-changepoints -o $@ \
		-b bencher7:fj-kmeans:graal-ce-hotspot:default-ext:8 data/${DATA_B7_OUTLIERS_CPTS}

plots/steps1.pdf: warmup_stats data
	mkdir -p plots
	warmup_stats/bin/plot_krun_results --with-outliers --with-changepoints -o $@ \
		-b bencher7:scrabble:graal-ce:default-ext:5 data/${DATA_B7_OUTLIERS_CPTS}

plots/leak.pdf: warmup_stats data
	mkdir -p plots
	warmup_stats/bin/plot_krun_results --with-outliers --with-changepoints -o $@ \
		-b bencher7:als:openj9:default-ext:2 data/${DATA_J9_B7_OUTLIERS_CPTS}
