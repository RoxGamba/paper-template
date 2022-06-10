# make sure to use bash on Debian/Ubuntu, not dash
SHELL := /bin/bash

SRC = paper

FIGURES = 

all: $(SRC).pdf 
paper: $(SRC).pdf

%.pdf: %.tex
	pdflatex $*
	bibtex $* ; \
	pdflatex -nonstopmode $* ; \
	pdflatex -nonstopmode $*

clean:
	rm -f $(SRC).{pdf,aux,bbl,blg,dvi,log,out,toc,synctex.gz}
	rm -f *~

new: clean all

.PHONY: all clean new
