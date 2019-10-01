PDFLATEX=pdflatex -synctex=1

.SUFFIXES: .tex .ps .dia .pdf .svg

MAIN_TEX = renaissance
BIB_FILE = bib.bib

SOFTDEVBIB_VERSION = master

DATA_B7 = renaissance_linux1_1240v5-0.1.json.bz2
DATA_B7_URL = https://archive.org/download/softdev_renaissance_analysis/runs/v0.1/linux1_1240v5/${DATA_B7}
DATA_B7_OUTLIERS = renaissance_linux1_1240v5-0.1_outliers_w200.json.bz2
DATA_B7_OUTLIERS_CPTS = renaissance_linux1_1240v5-0.1_outliers_w200_changepoints.json.bz2

DATA_B10 = renaissance_linux2_1240v6-0.1.json.bz2
DATA_B10_URL = https://archive.org/download/softdev_renaissance_analysis/runs/v0.1/linux2_1240v6/${DATA_B10}
DATA_B10_OUTLIERS = renaissance_linux2_1240v6-0.1_outliers_w200.json.bz2
DATA_B10_OUTLIERS_CPTS = renaissance_linux2_1240v6-0.1_outliers_w200_changepoints.json.bz2

-include common.mk

DIAGRAMS =

BASE_CLEANFILES =	aux bbl blg dvi log ps pdf toc out snm nav vrb \
			vtc synctex.gz
OTHER_CLEANFILES =	${BIB_FILE} texput.log ${DIFF}.tex

all: ${MAIN_TEX}.pdf ${BIB_FILE}

.svg.pdf:
	inkscape --export-pdf=$@ $<

.PHONY: clean
clean:
	for i in ${BASE_CLEANFILES}; do rm -f ${MAIN_TEX}.$${i}; done
	rm -f ${OTHER_CLEANFILES}
	rm -f tables/*.orig
	rm -rf data

${BIB_FILE}: softdevbib/softdev.bib
	softdevbib/bin/prebib softdevbib/softdev.bib > ${BIB_FILE}

softdevbib-update: softdevbib
	cd softdevbib && git pull

softdevbib/softdev.bib: softdevbib

softdevbib:
	git clone https://github.com/softdevteam/softdevbib.git

TEXMFHOME="../../share/texmf"
${MAIN_TEX}.pdf: ${DIAGRAMS} ${MAIN_TEX}.tex ${BIB_FILE} ${TABLES} ${PLOTS}
	TEXMFHOME=${TEXMFHOME} ${PDFLATEX} ${MAIN_TEX}.tex
	cd softdevbib && git checkout ${SOFTDEVBIB_VERSION}
	bibtex ${MAIN_TEX}
	TEXMFHOME=${TEXMFHOME} ${PDFLATEX} ${MAIN_TEX}.tex
	TEXMFHOME=${TEXMFHOME} ${PDFLATEX} ${MAIN_TEX}.tex
