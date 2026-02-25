# generarproyecto

Herramienta CLI para generar proyectos LaTeX a partir de plantillas predefinidas.

## Instalación

```bash
git clone <este-repo> && cd latexgen
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

# Crear en un directorio específico
generarproyecto -n "Mi artículo" -t art -d ~/proyectos/

# Listar tipos disponibles
generarproyecto --listar
```

## Tipos de proyecto

| Código | Tipo | Clase LaTeX |
|--------|------|-------------|
| `art` | Artículo | `article` |
| `ens` | Ensayo | `report` |
| `pres` | Presentación | `beamer` |

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

## Requisitos

- Python 3.6+
- Una distribución LaTeX (TeX Live, MiKTeX)
- `biber` (para bibliografía con biblatex)
- `latexmk` (opcional, para `make watch`)
- Para presentaciones con tema Metropolis: `sudo tlmgr install beamertheme-metropolis`
