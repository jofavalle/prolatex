"""
Configuración común de los tests.

El aislamiento de plantillas de este archivo NO es opcional. El módulo
`generarproyecto` congela el directorio de plantillas en tiempo de import:

    TEMPLATES_DIR = resolver_templates_dir()   # nivel de módulo

y `resolver_templates_dir()` da prioridad a `~/.latex-templates` sobre las
plantillas embebidas en el paquete. En una máquina donde se haya ejecutado
`instalar.sh` alguna vez, los tests correrían en silencio contra las plantillas
del usuario y no contra las del repositorio, dando resultados que no dicen nada
sobre el código bajo prueba.

Por eso el entorno se fija aquí, a nivel de módulo: pytest importa `conftest.py`
antes que cualquier módulo de test, así que esto ocurre antes del import.
"""

import importlib
import os
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
PLANTILLAS = RAIZ / "src" / "generarproyecto" / "templates"

os.environ["LATEX_TEMPLATES_DIR"] = str(PLANTILLAS)
os.environ.pop("LATEX_AUTOR", None)

# Red de seguridad: si algún plugin importó el paquete antes que este archivo,
# se recarga para que tome el entorno recién fijado.
if "generarproyecto" in sys.modules:
    importlib.reload(sys.modules["generarproyecto"])


# Patrón de placeholder real de las plantillas: {{NOMBRE_EN_MAYUSCULAS}}.
# No vale buscar "{{" a secas, porque `\graphicspath{{figuras/}}` es LaTeX
# legítimo y daría un falso positivo.
PLACEHOLDER = re.compile(r"\{\{[A-Z_]+\}\}")

ENTORNO = re.compile(r"\\(begin|end)\{([^}]+)\}")


def placeholders_sin_sustituir(texto: str):
    """Devuelve la lista de placeholders que quedaron sin resolver."""
    return PLACEHOLDER.findall(texto)


def entornos_desbalanceados(texto: str):
    """
    Comprueba que cada \\begin{X} tiene su \\end{X} en el orden correcto.

    No sustituye a compilar el documento, pero caza el error más probable al
    editar una plantilla a mano. Las líneas comentadas se ignoran: las
    plantillas traen ejemplos de figura y tabla comentados.
    """
    pila = []
    errores = []
    for numero, linea in enumerate(texto.splitlines(), 1):
        if linea.lstrip().startswith("%"):
            continue
        for accion, entorno in ENTORNO.findall(linea):
            if accion == "begin":
                pila.append((entorno, numero))
            else:
                if not pila:
                    errores.append(f"linea {numero}: \\end{{{entorno}}} sin apertura")
                elif pila[-1][0] != entorno:
                    abierto, linea_abierto = pila.pop()
                    errores.append(
                        f"linea {numero}: \\end{{{entorno}}} cierra "
                        f"\\begin{{{abierto}}} abierto en la linea {linea_abierto}"
                    )
                else:
                    pila.pop()
    errores.extend(
        f"linea {n}: \\begin{{{e}}} sin cerrar" for e, n in pila
    )
    return errores


@pytest.fixture
def plantillas():
    """Directorio de plantillas contra el que corren los tests."""
    return PLANTILLAS


@pytest.fixture
def generar(tmp_path):
    """
    Genera un proyecto en un directorio temporal.

    Devuelve una tupla (directorio del proyecto, contenido del .tex principal).
    """
    def _generar(nombre="Proyecto de prueba", tipo="art", **kwargs):
        import generarproyecto as g

        kwargs.setdefault("autor", "Autora de Prueba")
        kwargs.setdefault("citas", g.CITAS_DEFAULT)
        g.crear_proyecto(
            nombre=nombre,
            tipo=tipo,
            directorio_base=tmp_path,
            **kwargs,
        )
        slug = g.slugify(nombre)
        destino = tmp_path / slug
        return destino, (destino / f"{slug}.tex").read_text(encoding="utf-8")

    return _generar
