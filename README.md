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
# Crear un artículo (formato hep por defecto)
generarproyecto --nombre "Análisis de redes neuronales" --tipo art

# Crear un artículo con el formato académico general
generarproyecto -n "Trabajo de curso" -t art --formato clasico

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

## Formatos de documento

La opción `-f` / `--formato` elige la tipografía y la estructura del documento. Es un eje
independiente del tipo y del estilo de citas: se combinan libremente.

| Código | Formato | Descripción |
|--------|---------|-------------|
| `hep` | Física de altas energías | Tipografía de paper de colaboración: 12pt sobre A4, márgenes de una pulgada, `upgreek` para notación de partículas, portada con resumen centrado. **Por defecto** |
| `clasico` | Académico general | El formato original: márgenes de 2.5 cm, índice, encabezados y entornos de teorema |

```bash
generarproyecto -n "Medida de la fracción de ramificación" -t art          # hep, por defecto
generarproyecto -n "Trabajo de curso" -t art --formato clasico
generarproyecto -n "Mi artículo" -t art --formato hep --citas apa -l       # se combinan
```

Por ahora solo el tipo `art` tiene variante propia para el formato `hep`. Los tipos `ens` y
`pres` usan su plantilla de siempre sea cual sea el formato elegido.

### Portada del formato `hep`

El formato `hep` reproduce la estructura de portada de un paper de colaboración, con tres
campos **vacíos por defecto**:

| Opción | Qué rellena |
|--------|-------------|
| `--institucion` | Encabezado institucional en la parte superior |
| `--num-informe` | Número de informe interno, alineado a la derecha |
| `--publicado-en` | Línea de publicación al pie de la portada |

Cada bloque se omite del documento si su campo va vacío. Rellénalos solo si el documento
pertenece de verdad a esa institución: un documento personal con un encabezado institucional
ajeno induce a error sobre su procedencia.

> El formato `hep` es una reproducción de los ajustes tipográficos habituales en los papers
> de física de altas energías, no la plantilla oficial de ninguna colaboración. Como
> referencia de cómo se ve el resultado publicado puede consultarse `arXiv:2509.15873`.

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
- Una distribución LaTeX (TeX Live, MiKTeX) con soporte para `biblatex`/`biber` y los paquetes `lineno` y `upgreek` (este último lo usa el formato `hep`)
- `latexmk` (opcional, para `make watch`)
- En Windows, además: `make` (vía MSYS2, Chocolatey o WSL) para poder usar el `Makefile` generado (ver [Compilar en Windows](#compilar-en-windows))

### Instalación de dependencias LaTeX en Debian/Ubuntu

```bash
# Paquetes esenciales (compilador, biber y estilos bibliográficos incluyendo biblatex-phys)
sudo apt-get install texlive-latex-recommended texlive-bibtex-extra biber

# Soporte para español
sudo apt-get install texlive-lang-spanish

# Tema Metropolis para presentaciones beamer, y upgreek para el formato hep
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

