#!/usr/bin/env python3
"""
generarproyecto - Generador de proyectos LaTeX

Crea la estructura de un proyecto LaTeX a partir de plantillas predefinidas.

Uso:
    generarproyecto --nombre "Mi artículo" --tipo art
    generarproyecto --nombre "Mi ensayo" --tipo ens
    generarproyecto --nombre "Mi presentación" --tipo pres
    generarproyecto --nombre "Mi artículo" --tipo art --autor "Juan Pérez"

Tipos disponibles:
    art   → Artículo (documentclass: article)
    ens   → Ensayo (documentclass: report)
    pres  → Presentación (documentclass: beamer)
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ============================================================================
# Configuración
# ============================================================================

# Directorio donde viven las plantillas.
# Por defecto busca en ~/.latex-templates/
# Puedes sobreescribirlo con la variable de entorno LATEX_TEMPLATES_DIR
TEMPLATES_DIR = Path(
    os.environ.get(
        "LATEX_TEMPLATES_DIR",
        Path.home() / ".latex-templates"
    )
)

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

# Autor por defecto. Puedes cambiarlo aquí o usar la variable de entorno
# LATEX_AUTOR, o pasar --autor en la línea de comandos.
AUTOR_DEFAULT = os.environ.get("LATEX_AUTOR", "Tu Nombre")


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
        print("Para instalar las plantillas, ejecuta:")
        print(f"  mkdir -p {TEMPLATES_DIR}")
        print(f"  cp plantillas/* {TEMPLATES_DIR}/")
        print()
        print("O define LATEX_TEMPLATES_DIR apuntando a tu directorio de plantillas.")
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

def crear_proyecto(nombre: str, tipo: str, autor: str, directorio_base: Path):
    """Crea la estructura completa del proyecto LaTeX."""

    if tipo not in TIPOS:
        print(f"Error: Tipo '{tipo}' no reconocido.")
        print(f"Tipos disponibles: {', '.join(TIPOS.keys())}")
        sys.exit(1)

    verificar_plantillas()

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

    # Variables para sustituir en las plantillas
    variables = {
        "TITULO": nombre,
        "AUTOR": autor,
        "FECHA": fecha,
        "NOMBRE_ARCHIVO": slug,
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
            "Ejemplos:\n"
            "  generarproyecto --nombre 'Análisis de datos' --tipo art\n"
            "  generarproyecto -n 'Ética en IA' -t ens --autor 'María López'\n"
            "  generarproyecto -n 'Avances en ML' -t pres\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-n", "--nombre",
        required=True,
        help="Título del proyecto (se usará también para nombrar el directorio)"
    )

    parser.add_argument(
        "-t", "--tipo",
        required=True,
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
        "--listar",
        action="store_true",
        help="Muestra los tipos de proyecto disponibles y sale"
    )

    args = parser.parse_args()

    if args.listar:
        print("Tipos de proyecto disponibles:")
        print()
        for clave, info in TIPOS.items():
            print(f"  {clave:6s} → {info['descripcion']}")
        print()
        sys.exit(0)

    crear_proyecto(
        nombre=args.nombre,
        tipo=args.tipo,
        autor=args.autor,
        directorio_base=Path(args.directorio).resolve(),
    )


if __name__ == "__main__":
    main()
