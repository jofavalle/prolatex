#!/usr/bin/env python3
"""
generarproyecto - Generador de proyectos LaTeX

Crea la estructura de un proyecto LaTeX a partir de plantillas predefinidas.

Uso:
    generarproyecto --nombre "Mi artículo" --tipo art
    generarproyecto --nombre "Mi artículo" --tipo art --citas apa
    generarproyecto --nombre "Mi ensayo" --tipo ens
    generarproyecto --nombre "Mi presentación" --tipo pres
    generarproyecto --nombre "Mi artículo" --tipo art --autor "Juan Pérez"
    generarproyecto --nombre "Mi artículo" --tipo art -l
    generarproyecto --nombre "Mi ensayo" --tipo ens -l --lineas-lado derecha --lineas-modulo 5

Tipos disponibles:
    art   → Artículo (documentclass: article)
    ens   → Ensayo (documentclass: report)
    pres  → Presentación (documentclass: beamer)

Estilos de citas:
    aip        → AIP (American Institute of Physics) [por defecto]
    apa        → APA 7.ª edición
    ieee       → IEEE
    nature     → Nature
    numeric    → Numérico genérico
    authoryear → Autor-año genérico

Numeración de líneas (solo art/ens):
    -l, --numeracion-lineas   Activa el paquete `lineno` (envíos a revisión)
    --lineas-lado             izquierda [por defecto] | derecha
    --lineas-modulo           Muestra el número cada N líneas (default: 1)
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from importlib import resources
from pathlib import Path

# En consolas de Windows (cmd.exe) sin code page UTF-8, imprimir los símbolos
# usados en los mensajes (✓, →, ─, ⚠) puede lanzar UnicodeEncodeError. Se
# reconfigura la salida a UTF-8 de forma defensiva cuando el intérprete lo
# permite (Python 3.7+).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


# ============================================================================
# Configuración
# ============================================================================

def _plantillas_embebidas():
    """
    Devuelve la ruta a las plantillas empaquetadas dentro del propio paquete
    (disponibles cuando se instala vía `pip install .` / `pipx install .`),
    o None si no se pueden resolver (ej. ejecutando el script suelto).
    """
    try:
        recurso = resources.files("generarproyecto") / "templates"
        if recurso.is_dir():
            return Path(recurso)
    except (ModuleNotFoundError, FileNotFoundError, TypeError):
        pass
    return None


def resolver_templates_dir() -> Path:
    """
    Resuelve el directorio de plantillas a usar, en este orden de prioridad:
      1. Variable de entorno LATEX_TEMPLATES_DIR.
      2. ~/.latex-templates si existe (instalado con instalar.sh / instalar.ps1).
      3. Plantillas embebidas en el paquete (instalación vía pip/pipx).
      4. ~/.latex-templates por defecto (aunque no exista aún), para que los
         mensajes de error de verificar_plantillas() sean consistentes.
    """
    env_dir = os.environ.get("LATEX_TEMPLATES_DIR")
    if env_dir:
        return Path(env_dir)

    dir_usuario = Path.home() / ".latex-templates"
    if dir_usuario.exists():
        return dir_usuario

    embebidas = _plantillas_embebidas()
    if embebidas is not None:
        return embebidas

    return dir_usuario


# Directorio donde viven las plantillas (ver resolver_templates_dir() para
# el orden de prioridad).
TEMPLATES_DIR = resolver_templates_dir()

# Mapeo de tipos cortos a nombres de plantilla y descripciones
TIPOS = {
    "art": {
        "plantilla": "articulo.tex",
        "descripcion": "Artículo (article)",
        "clase": "article",
    },
    "ens": {
        "plantilla": "ensayo.tex",
        "descripcion": "Ensayo (report)",
        "clase": "report",
    },
    "pres": {
        "plantilla": "presentacion.tex",
        "descripcion": "Presentación (beamer)",
        "clase": "beamer",
    },
}

# Estilos de citas disponibles (relevantes para Física)
# Cada entrada: clave → (estilo biblatex, sorting, descripción)
ESTILOS_CITAS = {
    "aip": {
        "estilo": "phys",
        "sorting": "none",
        "descripcion": "AIP (American Institute of Physics) — numérico, orden de aparición",
    },
    "apa": {
        "estilo": "apa",
        "sorting": "nyt",
        "descripcion": "APA 7.ª edición — autor-año, orden alfabético",
    },
    "ieee": {
        "estilo": "ieee",
        "sorting": "none",
        "descripcion": "IEEE — numérico, orden de aparición",
    },
    "nature": {
        "estilo": "nature",
        "sorting": "none",
        "descripcion": "Nature — numérico, orden de aparición",
    },
    "numeric": {
        "estilo": "numeric",
        "sorting": "none",
        "descripcion": "Numérico genérico — orden de aparición",
    },
    "authoryear": {
        "estilo": "authoryear",
        "sorting": "nyt",
        "descripcion": "Autor-año genérico — orden alfabético",
    },
}

CITAS_DEFAULT = "aip"

# Autor por defecto. Puedes cambiarlo aquí o usar la variable de entorno
# LATEX_AUTOR, o pasar --autor en la línea de comandos.
AUTOR_DEFAULT = os.environ.get("LATEX_AUTOR", "Tu Nombre")

# Tipos de documento que admiten numeración de líneas (revisión de revistas).
# No aplica a presentaciones (beamer).
TIPOS_CON_NUMERACION_LINEAS = ("art", "ens")

# Mapeo de --lineas-lado a la opción del paquete `lineno` que se añade a
# \usepackage[...]{lineno}. "izquierda" es el comportamiento por defecto del
# paquete (sin opción extra).
LADOS_LINEA = {
    "izquierda": "",
    "derecha": "right",
}

LINEAS_LADO_DEFAULT = "izquierda"
LINEAS_MODULO_DEFAULT = 1


# ============================================================================
# Funciones auxiliares
# ============================================================================

def slugify(texto: str) -> str:
    """
    Convierte un texto a un nombre de archivo seguro.
    "Mi artículo sobre IA" → "mi-articulo-sobre-ia"
    """
    # Reemplazos de caracteres acentuados
    reemplazos = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
        "ñ": "n", "Ñ": "N", "ü": "u", "Ü": "U",
    }
    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)

    # Convertir a minúsculas, reemplazar espacios y caracteres no alfanuméricos
    texto = texto.lower().strip()
    texto = re.sub(r"[^\w\s-]", "", texto)
    texto = re.sub(r"[\s_]+", "-", texto)
    texto = re.sub(r"-+", "-", texto)
    return texto.strip("-")


def sustituir_placeholders(contenido: str, variables: dict) -> str:
    """Reemplaza los placeholders {{CLAVE}} en el contenido."""
    for clave, valor in variables.items():
        contenido = contenido.replace(f"{{{{{clave}}}}}", valor)
    return contenido


def copiar_plantilla(origen: Path, destino: Path, variables: dict):
    """Copia un archivo de plantilla sustituyendo los placeholders."""
    contenido = origen.read_text(encoding="utf-8")
    contenido = sustituir_placeholders(contenido, variables)
    destino.write_text(contenido, encoding="utf-8")


def verificar_plantillas():
    """Verifica que el directorio de plantillas existe y tiene los archivos."""
    if not TEMPLATES_DIR.exists():
        print(f"Error: No se encontró el directorio de plantillas: {TEMPLATES_DIR}")
        print()
        print("Para instalar las plantillas, ejecuta el instalador incluido:")
        print("  bash instalar.sh          (Linux/macOS)")
        print("  ./instalar.ps1            (Windows, PowerShell)")
        print()
        print("O instala el paquete con pip/pipx (usa plantillas embebidas, sin pasos extra):")
        print("  pip install .")
        print("  pipx install .")
        print()
        print("También puedes definir LATEX_TEMPLATES_DIR apuntando a tu propio directorio de plantillas.")
        sys.exit(1)

    archivos_necesarios = ["articulo.tex", "ensayo.tex", "presentacion.tex",
                           "referencias.bib", "Makefile"]
    faltantes = [a for a in archivos_necesarios if not (TEMPLATES_DIR / a).exists()]

    if faltantes:
        print(f"Advertencia: Faltan plantillas en {TEMPLATES_DIR}:")
        for f in faltantes:
            print(f"  - {f}")
        print()


# ============================================================================
# Función principal
# ============================================================================

def crear_proyecto(
    nombre: str,
    tipo: str,
    autor: str,
    citas: str,
    directorio_base: Path,
    numeracion_lineas: bool = False,
    lineas_lado: str = LINEAS_LADO_DEFAULT,
    lineas_modulo: int = LINEAS_MODULO_DEFAULT,
):
    """Crea la estructura completa del proyecto LaTeX."""

    if tipo not in TIPOS:
        print(f"Error: Tipo '{tipo}' no reconocido.")
        print(f"Tipos disponibles: {', '.join(TIPOS.keys())}")
        sys.exit(1)

    verificar_plantillas()

    # La numeración de líneas no aplica a presentaciones (beamer)
    if numeracion_lineas and tipo not in TIPOS_CON_NUMERACION_LINEAS:
        print(
            f"Advertencia: la numeración de líneas no aplica al tipo '{tipo}' "
            "(solo 'art' y 'ens'). Se ignorará."
        )
        numeracion_lineas = False

    # Generar nombre del directorio y archivo
    slug = slugify(nombre)
    info_tipo = TIPOS[tipo]
    # Meses en español (evita depender del locale del sistema)
    meses_es = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
    }
    hoy = datetime.now()
    fecha = f"{hoy.day} de {meses_es[hoy.month]} de {hoy.year}"

    # Estilo de citas
    info_citas = ESTILOS_CITAS[citas]

    # Numeración de líneas (paquete `lineno`), opcional
    if numeracion_lineas:
        opcion_lado = LADOS_LINEA[lineas_lado]
        opciones_paquete = f"[{opcion_lado}]" if opcion_lado else ""
        lineno_paquete = (
            "% --- Numeración de líneas (revisión) ---\n"
            f"\\usepackage{opciones_paquete}{{lineno}}"
        )
        lineno_activar = "\\linenumbers"
        if lineas_modulo > 1:
            lineno_activar += f"\n\\modulolinenumbers[{lineas_modulo}]"
    else:
        lineno_paquete = ""
        lineno_activar = ""

    # Variables para sustituir en las plantillas
    variables = {
        "TITULO": nombre,
        "AUTOR": autor,
        "FECHA": fecha,
        "NOMBRE_ARCHIVO": slug,
        "ESTILO_CITAS": info_citas["estilo"],
        "SORTING_CITAS": info_citas["sorting"],
        "LINENO_PAQUETE": lineno_paquete,
        "LINENO_ACTIVAR": lineno_activar,
    }

    # Crear directorio del proyecto
    dir_proyecto = directorio_base / slug
    if dir_proyecto.exists():
        print(f"Error: El directorio '{dir_proyecto}' ya existe.")
        print("Elige otro nombre o elimina el directorio existente.")
        sys.exit(1)

    dir_proyecto.mkdir(parents=True)
    (dir_proyecto / "figuras").mkdir()

    # Copiar y procesar la plantilla principal
    plantilla_origen = TEMPLATES_DIR / info_tipo["plantilla"]
    archivo_tex = dir_proyecto / f"{slug}.tex"

    if plantilla_origen.exists():
        copiar_plantilla(plantilla_origen, archivo_tex, variables)
    else:
        print(f"Advertencia: No se encontró {plantilla_origen}")
        print(f"Creando archivo .tex mínimo...")
        archivo_tex.write_text(
            f"\\documentclass{{{info_tipo['clase']}}}\n"
            f"\\title{{{nombre}}}\n"
            f"\\author{{{autor}}}\n"
            f"\\date{{{fecha}}}\n"
            f"\\begin{{document}}\n"
            f"\\maketitle\n\n"
            f"\\end{{document}}\n",
            encoding="utf-8"
        )

    # Copiar referencias.bib
    bib_origen = TEMPLATES_DIR / "referencias.bib"
    if bib_origen.exists():
        copiar_plantilla(bib_origen, dir_proyecto / "referencias.bib", variables)
    else:
        (dir_proyecto / "referencias.bib").write_text(
            "% Referencias bibliográficas\n", encoding="utf-8"
        )

    # Copiar Makefile
    makefile_origen = TEMPLATES_DIR / "Makefile"
    if makefile_origen.exists():
        copiar_plantilla(makefile_origen, dir_proyecto / "Makefile", variables)

    # Crear .gitignore para LaTeX
    gitignore_contenido = """# LaTeX auxiliares
*.aux
*.bbl
*.bcf
*.blg
*.log
*.nav
*.out
*.run.xml
*.snm
*.toc
*.vrb
*.fdb_latexmk
*.fls
*.synctex.gz

# PDF generado (descomenta si no quieres versionarlo)
# *.pdf
"""
    (dir_proyecto / ".gitignore").write_text(gitignore_contenido, encoding="utf-8")

    # Resumen final
    print()
    print(f"  ✓ Proyecto creado exitosamente")
    print(f"  ─────────────────────────────────────")
    print(f"  Tipo:      {info_tipo['descripcion']}")
    print(f"  Título:    {nombre}")
    print(f"  Autor:     {autor}")
    print(f"  Citas:     {info_citas['descripcion']}")
    if numeracion_lineas:
        print(f"  Líneas:    numeradas ({lineas_lado}, módulo {lineas_modulo})")
    print(f"  Directorio: {dir_proyecto}/")
    print()
    print(f"  Archivos generados:")
    print(f"    {slug}.tex         ← Documento principal")
    print(f"    referencias.bib    ← Bibliografía")
    print(f"    Makefile           ← Compilación")
    print(f"    figuras/           ← Directorio para imágenes")
    print(f"    .gitignore         ← Exclusiones de Git")
    print()
    print(f"  Para compilar:")
    print(f"    cd {dir_proyecto}")
    print(f"    make               # Compilación completa")
    print(f"    make quick         # Solo pdflatex (sin bibliografía)")
    print(f"    make watch         # Compilación continua (requiere latexmk)")
    print()


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        prog="generarproyecto",
        description="Genera la estructura de un proyecto LaTeX a partir de plantillas.",
        epilog=(
            "Tipos disponibles:\n"
            "  art   → Artículo (article)\n"
            "  ens   → Ensayo (report)\n"
            "  pres  → Presentación (beamer)\n"
            "\n"
            "Estilos de citas:\n"
            "  aip        → AIP (por defecto)\n"
            "  apa        → APA 7.ª edición\n"
            "  ieee       → IEEE\n"
            "  nature     → Nature\n"
            "  numeric    → Numérico genérico\n"
            "  authoryear → Autor-año genérico\n"
            "\n"
            "Ejemplos:\n"
            "  generarproyecto --nombre 'Análisis de datos' --tipo art\n"
            "  generarproyecto -n 'Ética en IA' -t ens --citas apa\n"
            "  generarproyecto -n 'Avances en ML' -t pres --autor 'María López'\n"
            "  generarproyecto -n 'Revisión de pares' -t art -l\n"
            "  generarproyecto -n 'Revisión de pares' -t ens -l --lineas-lado derecha --lineas-modulo 5\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-n", "--nombre",
        help="Título del proyecto (se usará también para nombrar el directorio)"
    )

    parser.add_argument(
        "-t", "--tipo",
        choices=list(TIPOS.keys()),
        help="Tipo de documento: art (artículo), ens (ensayo), pres (presentación)"
    )

    parser.add_argument(
        "-a", "--autor",
        default=AUTOR_DEFAULT,
        help=f"Nombre del autor (default: '{AUTOR_DEFAULT}' o variable LATEX_AUTOR)"
    )

    parser.add_argument(
        "-d", "--directorio",
        default=".",
        help="Directorio base donde crear el proyecto (default: directorio actual)"
    )

    parser.add_argument(
        "-c", "--citas",
        default=CITAS_DEFAULT,
        choices=list(ESTILOS_CITAS.keys()),
        help=f"Estilo de citas bibliográficas (default: '{CITAS_DEFAULT}')"
    )

    parser.add_argument(
        "--listar",
        action="store_true",
        help="Muestra los tipos de proyecto disponibles y sale"
    )

    parser.add_argument(
        "-l", "--numeracion-lineas",
        action="store_true",
        help=(
            "Activa numeración de líneas (paquete lineno), útil para envíos a "
            "revisión en revistas científicas. Solo aplica a 'art' y 'ens'."
        )
    )

    parser.add_argument(
        "--lineas-lado",
        default=LINEAS_LADO_DEFAULT,
        choices=list(LADOS_LINEA.keys()),
        help=(
            f"Margen donde aparece la numeración de líneas (default: "
            f"'{LINEAS_LADO_DEFAULT}'). Solo tiene efecto con -l/--numeracion-lineas."
        )
    )

    parser.add_argument(
        "--lineas-modulo",
        type=int,
        default=LINEAS_MODULO_DEFAULT,
        help=(
            f"Muestra el número de línea cada N líneas (default: "
            f"{LINEAS_MODULO_DEFAULT} = todas). Solo tiene efecto con -l/--numeracion-lineas."
        )
    )

    args = parser.parse_args()

    if args.listar:
        print("Tipos de proyecto disponibles:")
        print()
        for clave, info in TIPOS.items():
            print(f"  {clave:6s} → {info['descripcion']}")
        print()
        print("Estilos de citas disponibles:")
        print()
        for clave, info in ESTILOS_CITAS.items():
            print(f"  {clave:12s} → {info['descripcion']}")
        print()
        sys.exit(0)

    # Validar argumentos requeridos cuando no se usa --listar
    if not args.nombre:
        parser.error("el argumento -n/--nombre es requerido")
    if not args.tipo:
        parser.error("el argumento -t/--tipo es requerido")
    if args.lineas_modulo < 1:
        parser.error("--lineas-modulo debe ser un entero >= 1")

    crear_proyecto(
        nombre=args.nombre,
        tipo=args.tipo,
        autor=args.autor,
        citas=args.citas,
        directorio_base=Path(args.directorio).resolve(),
        numeracion_lineas=args.numeracion_lineas,
        lineas_lado=args.lineas_lado,
        lineas_modulo=args.lineas_modulo,
    )


if __name__ == "__main__":
    main()
