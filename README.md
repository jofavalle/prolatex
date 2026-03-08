# Generador de Proyectos LaTeX

Herramienta CLI para generar proyectos LaTeX a partir de plantillas predefinidas, orientada a proyectos de física.

## Instalación

```bash
git clone <este-repo> && cd prolatex
bash instalar.sh
```

Esto copia las plantillas a `~/.latex-templates/` y el script a `~/.local/bin/`.

## Uso

```bash
# Crear un artículo
generarproyecto --nombre "Análisis de redes neuronales" --tipo art

# Crear un ensayo
generarproyecto -n "Ética en la inteligencia artificial" -t ens

# Crear una presentación
generarproyecto -n "Avances en machine learning" -t pres

# Especificar autor
generarproyecto -n "Mi artículo" -t art --autor "María López"

# Especificar estilo de citas
generarproyecto -n "Mi artículo" -t art --citas apa
generarproyecto -n "Mi ensayo" -t ens -c ieee

# Crear en un directorio específico
generarproyecto -n "Mi artículo" -t art -d ~/proyectos/

# Listar tipos y estilos disponibles
generarproyecto --listar
```

## Tipos de proyecto

| Código | Tipo | Clase LaTeX |
|--------|------|-------------|
| `art` | Artículo | `article` |
| `ens` | Ensayo | `report` |
| `pres` | Presentación | `beamer` |

## Estilos de citas

Puedes elegir el estilo de citas bibliográficas con la opción `-c` / `--citas`. Por defecto se usa **AIP** (`phys`).

| Código | Estilo | Sorting | Descripción |
|--------|--------|---------|-------------|
| `aip` | `phys` | `none` | AIP (American Institute of Physics) — numérico, orden de aparición **(por defecto)** |
| `apa` | `apa` | `nyt` | APA 7.ª edición — autor-año, orden alfabético |
| `ieee` | `ieee` | `none` | IEEE — numérico, orden de aparición |
| `nature` | `nature` | `none` | Nature — numérico, orden de aparición |
| `numeric` | `numeric` | `none` | Numérico genérico — orden de aparición |
| `authoryear` | `authoryear` | `nyt` | Autor-año genérico — orden alfabético |

## Estructura generada

```
mi-articulo/
├── mi-articulo.tex    ← Documento principal
├── referencias.bib    ← Bibliografía (BibTeX)
├── Makefile           ← Comandos de compilación
├── figuras/           ← Directorio para imágenes
└── .gitignore         ← Exclusiones de Git
```

## Compilación

Dentro del directorio del proyecto:

```bash
make          # Compilación completa (pdflatex + biber + pdflatex x2)
make quick    # Solo pdflatex (sin bibliografía)
make clean    # Elimina archivos auxiliares
make purge    # Elimina auxiliares + PDF
make watch    # Compilación continua (requiere latexmk)
```

## Configuración

### Autor por defecto

Puedes definir tu nombre de autor por defecto con una variable de entorno:

```bash
# En tu ~/.bashrc o ~/.zshrc
export LATEX_AUTOR="Tu Nombre Completo"
```

### Directorio de plantillas personalizado

```bash
export LATEX_TEMPLATES_DIR="/ruta/a/tus/plantillas"
```

## Personalización de plantillas

Las plantillas viven en `~/.latex-templates/`. Puedes editarlas directamente para ajustar paquetes, estilos o estructura a tus necesidades.

Los placeholders disponibles son:

- `{{TITULO}}` — Título del proyecto
- `{{AUTOR}}` — Nombre del autor
- `{{FECHA}}` — Fecha de creación
- `{{NOMBRE_ARCHIVO}}` — Slug del nombre (para el Makefile)
- `{{ESTILO_CITAS}}` — Estilo de biblatex seleccionado (ej. `phys`, `apa`, `ieee`)
- `{{SORTING_CITAS}}` — Método de ordenación de la bibliografía (ej. `none`, `nyt`)

## Bibliografía

Las plantillas usan `biblatex` con backend `biber`. El estilo de citas se configura al crear el proyecto con la opción `--citas` (ver [Estilos de citas](#estilos-de-citas)). Por defecto se usa el estilo **AIP** (`phys`), que sigue el formato de revistas AIP/APS (Physical Review, Journal of Applied Physics, etc.).

Para agregar referencias, edita el archivo `referencias.bib` con entradas BibTeX y cítalas en el documento con `\cite{clave}`.

## Requisitos

- Python 3.6+
- Una distribución LaTeX (TeX Live, MiKTeX)
- `latexmk` (opcional, para `make watch`)

### Instalación de dependencias LaTeX en Debian/Ubuntu

```bash
# Paquetes esenciales (compilador, biber y estilos bibliográficos incluyendo biblatex-phys)
sudo apt-get install texlive-latex-recommended texlive-bibtex-extra biber

# Soporte para español
sudo apt-get install texlive-lang-spanish

# Tema Metropolis para presentaciones beamer
sudo apt-get install texlive-latex-extra

# Compilación continua (opcional)
sudo apt-get install latexmk
```

O instala todo de una vez:

```bash
sudo apt-get install texlive-full
```

> **Nota:** `texlive-full` ocupa varios GB pero incluye todo lo necesario sin preocuparte por dependencias faltantes.
