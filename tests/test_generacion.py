"""Generación de proyectos: estructura y contenido de lo que sale."""

import re

import pytest

import generarproyecto as g
from conftest import entornos_desbalanceados, placeholders_sin_sustituir

TIPOS = ["art", "ens", "pres"]

PATRON_CLASE = re.compile(r"\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}")


@pytest.mark.parametrize("tipo", TIPOS)
def test_estructura_generada(generar, tipo):
    destino, _ = generar(tipo=tipo)
    assert (destino / "proyecto-de-prueba.tex").is_file()
    assert (destino / "referencias.bib").is_file()
    assert (destino / "Makefile").is_file()
    assert (destino / ".gitignore").is_file()
    assert (destino / "figuras").is_dir()


@pytest.mark.parametrize("tipo, clase", [
    ("art", "article"),
    ("ens", "report"),
    ("pres", "beamer"),
])
def test_clase_de_documento(generar, tipo, clase):
    _, tex = generar(tipo=tipo)
    encontrada = PATRON_CLASE.search(tex)
    assert encontrada is not None, "no se encontró \\documentclass"
    assert encontrada.group(1) == clase


@pytest.mark.parametrize("tipo", TIPOS)
def test_no_quedan_placeholders(generar, tipo):
    """
    Invariante que vale por muchos tests: si alguien añade un placeholder a una
    plantilla y olvida cablearlo en crear_proyecto(), esto lo caza sin que haya
    que escribir un test específico para ese placeholder.
    """
    destino, _ = generar(tipo=tipo)
    for archivo in destino.rglob("*"):
        if not archivo.is_file():
            continue
        contenido = archivo.read_text(encoding="utf-8")
        assert not placeholders_sin_sustituir(contenido), (
            f"{archivo.name} conserva placeholders sin sustituir"
        )


@pytest.mark.parametrize("tipo", TIPOS)
def test_entornos_latex_balanceados(generar, tipo):
    """Proxy estructural de compilabilidad: cada \\begin tiene su \\end."""
    _, tex = generar(tipo=tipo)
    assert entornos_desbalanceados(tex) == []


@pytest.mark.parametrize("tipo", TIPOS)
def test_metadatos_sustituidos(generar, tipo):
    _, tex = generar(nombre="Medida de precisión", tipo=tipo, autor="Ada Lovelace")
    assert "Medida de precisión" in tex
    assert "Ada Lovelace" in tex


def test_makefile_apunta_al_documento(generar):
    destino, _ = generar(nombre="Mi trabajo")
    makefile = (destino / "Makefile").read_text(encoding="utf-8")
    assert "MAIN = mi-trabajo" in makefile


def test_tipo_invalido_sale_con_error(tmp_path):
    with pytest.raises(SystemExit) as excinfo:
        g.crear_proyecto(
            nombre="X", tipo="inexistente", autor="A",
            citas=g.CITAS_DEFAULT, directorio_base=tmp_path,
        )
    assert excinfo.value.code == 1


def test_directorio_existente_sale_con_error(generar, tmp_path):
    generar(nombre="Colision")
    with pytest.raises(SystemExit) as excinfo:
        g.crear_proyecto(
            nombre="Colision", tipo="art", autor="A",
            citas=g.CITAS_DEFAULT, directorio_base=tmp_path,
        )
    assert excinfo.value.code == 1
