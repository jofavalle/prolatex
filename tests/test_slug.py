"""Funciones puras: no tocan disco ni entorno."""

import pytest

import generarproyecto as g


@pytest.mark.parametrize("entrada, esperado", [
    ("Mi artículo sobre IA", "mi-articulo-sobre-ia"),
    ("Análisis de datos", "analisis-de-datos"),
    ("ÉXITO Rotundo", "exito-rotundo"),
    ("El Niño y la señal", "el-nino-y-la-senal"),
    ("Espacios    múltiples", "espacios-multiples"),
    ("Puntuación: ¿qué pasa?", "puntuacion-que-pasa"),
    ("guiones---repetidos", "guiones-repetidos"),
    ("  bordes  ", "bordes"),
    ("snake_case_texto", "snake-case-texto"),
])
def test_slugify(entrada, esperado):
    assert g.slugify(entrada) == esperado


def test_slugify_no_deja_barras():
    """El slug nombra un directorio: una barra lo convertiría en una ruta."""
    assert "/" not in g.slugify("carpeta/subcarpeta")


def test_sustituir_placeholders_reemplaza():
    plantilla = "Título: {{TITULO}}, autor: {{AUTOR}}"
    resultado = g.sustituir_placeholders(
        plantilla, {"TITULO": "Medida", "AUTOR": "Joe"}
    )
    assert resultado == "Título: Medida, autor: Joe"


def test_sustituir_placeholders_admite_valor_vacio():
    """Los campos institucionales del formato hep van vacíos por defecto."""
    resultado = g.sustituir_placeholders(
        "\\newcommand{\\lainstitucion}{{{INSTITUCION}}}", {"INSTITUCION": ""}
    )
    assert resultado == "\\newcommand{\\lainstitucion}{}"


def test_sustituir_placeholders_deja_intacto_lo_desconocido():
    plantilla = "{{TITULO}} y {{NO_DEFINIDO}}"
    resultado = g.sustituir_placeholders(plantilla, {"TITULO": "X"})
    assert resultado == "X y {{NO_DEFINIDO}}"
