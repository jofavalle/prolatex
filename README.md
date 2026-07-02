# Generador de Proyectos LaTeX

Herramienta CLI para generar proyectos LaTeX a partir de plantillas predefinidas, orientada a proyectos de física.

## Instalación

### Linux / macOS

```bash
git clone <este-repo> && cd prolatex
bash instalar.sh
```

Esto copia las plantillas a `~/.latex-templates/` y el script a `~/.local/bin/`.

### Windows (PowerShell)

```powershell
git clone <este-repo>; cd prolatex
powershell -ExecutionPolicy Bypass -File instalar.ps1
```

Esto copia las plantillas a `%USERPROFILE%\.latex-templates\` y el script (junto a un shim `generarproyecto.bat`) a `%LOCALAPPDATA%\Programs\generarproyecto\`. Requiere Python 3.9+ en el PATH.

### Alternativa multiplataforma: pip / pipx

```bash
git clone <este-repo> && cd prolatex
pip install .
# o, para una instalación aislada:
pipx install .
```

Esta opción funciona igual en Linux, macOS y Windows: instala el comando `generarproyecto` con las plantillas embebidas en el paquete, sin necesidad de ejecutar `instalar.sh`/`instalar.ps1`. Sigue siendo posible personalizar las plantillas copiándolas a `~/.latex-templates` (o `%USERPROFILE%\.latex-templates` en Windows) o definiendo `LATEX_TEMPLATES_DIR`; esas rutas tienen prioridad sobre las plantillas embebidas.

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

# Activar numeración de líneas (envío a revisión de revista)
generarproyecto -n "Mi artículo" -t art -l
generarproyecto -n "Mi ensayo" -t ens -l --lineas-lado derecha --lineas-modulo 5

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

## Numeración de líneas

Para los tipos `art` (artículo) y `ens` (ensayo) puedes activar numeración de líneas continua, útil cuando se envía un manuscrito a revisión en una revista científica. Usa el paquete `lineno` y se activa desde el inicio del cuerpo del documento (justo antes de la primera sección/capítulo).

| Opción | Descripción | Default |
|--------|-------------|---------|
| `-l`, `--numeracion-lineas` | Activa la numeración de líneas | Desactivada |
| `--lineas-lado` | Margen donde aparece el número: `izquierda` o `derecha` | `izquierda` |
| `--lineas-modulo` | Muestra el número cada N líneas (entero ≥ 1) | `1` (todas) |

```bash
generarproyecto -n "Mi artículo" -t art -l
generarproyecto -n "Mi ensayo" -t ens -l --lineas-lado derecha --lineas-modulo 5
```

No aplica al tipo `pres` (beamer); si se combina con `-l`, se ignora con una advertencia.

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

### Compilar en Windows

El `Makefile` generado usa `make` y `rm`, que no vienen incluidos por defecto en Windows. Opciones para poder usar `make`:

- **MSYS2**: `pacman -S make` y compila desde la terminal MSYS2/MinGW.
- **Chocolatey**: `choco install make`.
- **WSL**: instala una distribución Linux y compila desde ahí.

`latexmk` (usado por `make watch`) viene incluido con MiKTeX, así que `make watch` funciona igual una vez que `make` esté disponible por alguna de las vías anteriores.

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

Las plantillas viven en `~/.latex-templates/` (`%USERPROFILE%\.latex-templates` en Windows) cuando se instalan con `instalar.sh`/`instalar.ps1`. Si instalaste con `pip`/`pipx` y no has copiado plantillas propias, se usan las plantillas embebidas en el paquete. Puedes editar tu copia en `~/.latex-templates/` directamente para ajustar paquetes, estilos o estructura a tus necesidades; esa ruta tiene prioridad sobre las plantillas embebidas.

Los placeholders disponibles son:

- `{{TITULO}}` — Título del proyecto
- `{{AUTOR}}` — Nombre del autor
- `{{FECHA}}` — Fecha de creación
- `{{NOMBRE_ARCHIVO}}` — Slug del nombre (para el Makefile)
- `{{ESTILO_CITAS}}` — Estilo de biblatex seleccionado (ej. `phys`, `apa`, `ieee`)
- `{{SORTING_CITAS}}` — Método de ordenación de la bibliografía (ej. `none`, `nyt`)
- `{{LINENO_PAQUETE}}` — Carga del paquete `lineno` (vacío si no se usa `-l`)
- `{{LINENO_ACTIVAR}}` — Comandos `\linenumbers`/`\modulolinenumbers` (vacío si no se usa `-l`)

## Bibliografía

Las plantillas usan `biblatex` con backend `biber`. El estilo de citas se configura al crear el proyecto con la opción `--citas` (ver [Estilos de citas](#estilos-de-citas)). Por defecto se usa el estilo **AIP** (`phys`), que sigue el formato de revistas AIP/APS (Physical Review, Journal of Applied Physics, etc.).

Para agregar referencias, edita el archivo `referencias.bib` con entradas BibTeX y cítalas en el documento con `\cite{clave}`.

## Requisitos

- Python 3.9+
- Una distribución LaTeX (TeX Live, MiKTeX) con soporte para `biblatex`/`biber` y el paquete `lineno`
- `latexmk` (opcional, para `make watch`)
- En Windows, además: `make` (vía MSYS2, Chocolatey o WSL) para poder usar el `Makefile` generado (ver [Compilar en Windows](#compilar-en-windows))

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

### Instalación de dependencias LaTeX en Windows

```powershell
# MiKTeX incluye pdflatex, biber y latexmk, e instala paquetes faltantes (como lineno o biblatex-phys) automáticamente la primera vez que se usan
choco install miktex

# Alternativamente, descarga el instalador desde https://miktex.org/download
```

Para `make`, instala alguna de las opciones descritas en [Compilar en Windows](#compilar-en-windows).

