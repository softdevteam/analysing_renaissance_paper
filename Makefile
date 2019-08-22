PDFLATEX=pdflatex -synctex=1

.SUFFIXES: .tex .ps .dia .pdf .svg

MAIN_TEX = renaissance
BIB_FILE = bib.bib

SOFTDEVBIB_VERSION = master

TABLES = tables/b7.tex tables/b10.tex
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

${BIB_FILE}: softdevbib/softdev.bib
	softdevbib/bin/prebib softdevbib/softdev.bib > ${BIB_FILE}

softdevbib-update: softdevbib
	cd softdevbib && git pull

softdevbib/softdev.bib: softdevbib

softdevbib:
	git clone https://github.com/softdevteam/softdevbib.git

TEXMFHOME="../../share/texmf"
${MAIN_TEX}.pdf: ${DIAGRAMS} ${MAIN_TEX}.tex ${BIB_FILE} ${TABLES}
	TEXMFHOME=${TEXMFHOME} ${PDFLATEX} ${MAIN_TEX}.tex
	cd softdevbib && git checkout ${SOFTDEVBIB_VERSION}
	bibtex ${MAIN_TEX}
	TEXMFHOME=${TEXMFHOME} ${PDFLATEX} ${MAIN_TEX}.tex
	TEXMFHOME=${TEXMFHOME} ${PDFLATEX} ${MAIN_TEX}.tex
