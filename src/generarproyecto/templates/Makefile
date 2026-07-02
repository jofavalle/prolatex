# ============================================================================
# Makefile para compilar proyecto LaTeX
# Uso:
#   make          → Compila el documento completo (con bibliografía)
#   make quick    → Compilación rápida (sin bibliografía)
#   make clean    → Elimina archivos auxiliares
#   make purge    → Elimina auxiliares + PDF
#   make watch    → Compilación continua (requiere latexmk)
# ============================================================================

MAIN = {{NOMBRE_ARCHIVO}}
TEX  = pdflatex
BIB  = biber
FLAGS = -interaction=nonstopmode -halt-on-error

.PHONY: all quick clean purge watch

all:
	$(TEX) $(FLAGS) $(MAIN).tex
	$(BIB) $(MAIN)
	$(TEX) $(FLAGS) $(MAIN).tex
	$(TEX) $(FLAGS) $(MAIN).tex

quick:
	$(TEX) $(FLAGS) $(MAIN).tex

clean:
	rm -f $(MAIN).{aux,bbl,bcf,blg,log,nav,out,run.xml,snm,toc,vrb,fdb_latexmk,fls,synctex.gz}

purge: clean
	rm -f $(MAIN).pdf

watch:
	latexmk -pdf -pvc -interaction=nonstopmode $(MAIN).tex
