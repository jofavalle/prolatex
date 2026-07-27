"""Numeración de líneas, la opción para envíos a revisión."""

import pytest


@pytest.mark.parametrize("formato", ["hep", "clasico"])
def test_desactivada_por_defecto(generar, formato):
    _, tex = generar(formato=formato)
    assert "{lineno}" not in tex
    assert "\\linenumbers" not in tex


@pytest.mark.parametrize("formato", ["hep", "clasico"])
def test_activada_carga_el_paquete_y_lo_enciende(generar, formato):
    _, tex = generar(numeracion_lineas=True, formato=formato)
    assert "\\usepackage{lineno}" in tex
    assert "\\linenumbers" in tex


def test_lado_derecho(generar):
    _, tex = generar(numeracion_lineas=True, lineas_lado="derecha")
    assert "\\usepackage[right]{lineno}" in tex


def test_lado_izquierdo_no_pasa_opcion(generar):
    """Izquierda es el comportamiento por defecto del paquete: sin opción."""
    _, tex = generar(numeracion_lineas=True, lineas_lado="izquierda")
    assert "\\usepackage{lineno}" in tex
    assert "[right]" not in tex


def test_modulo_mayor_que_uno(generar):
    _, tex = generar(numeracion_lineas=True, lineas_modulo=5)
    assert "\\modulolinenumbers[5]" in tex


def test_modulo_uno_no_emite_la_orden(generar):
    _, tex = generar(numeracion_lineas=True, lineas_modulo=1)
    assert "\\modulolinenumbers" not in tex


def test_ensayo_admite_numeracion(generar):
    _, tex = generar(tipo="ens", numeracion_lineas=True)
    assert "\\linenumbers" in tex


def test_presentacion_la_ignora_con_advertencia(generar, capsys):
    """Documentado en el README: con beamer no aplica y se avisa."""
    _, tex = generar(tipo="pres", numeracion_lineas=True)
    salida = capsys.readouterr().out
    assert "no aplica" in salida
    assert "\\linenumbers" not in tex
