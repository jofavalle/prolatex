"""El eje de estilos de citas, sobre los dos formatos."""

import pytest

import generarproyecto as g

CLAVES = list(g.ESTILOS_CITAS.keys())


@pytest.mark.parametrize("clave", CLAVES)
@pytest.mark.parametrize("formato", ["hep", "clasico"])
def test_estilo_y_sorting_llegan_a_biblatex(generar, clave, formato):
    info = g.ESTILOS_CITAS[clave]
    _, tex = generar(citas=clave, formato=formato)
    assert f"style={info['estilo']}" in tex
    assert f"sorting={info['sorting']}" in tex


def test_el_defecto_es_aip(generar):
    """AIP (phys, orden de aparición) es lo que usan las revistas de física."""
    assert g.CITAS_DEFAULT == "aip"
    _, tex = generar()
    assert "style=phys" in tex
    assert "sorting=none" in tex


@pytest.mark.parametrize("formato", ["hep", "clasico"])
def test_backend_biber_en_ambos_formatos(generar, formato):
    _, tex = generar(formato=formato)
    assert "backend=biber" in tex
    assert "\\addbibresource{referencias.bib}" in tex


def test_los_seis_estilos_estan_declarados():
    """Si se añade uno, la tabla del README también debe crecer."""
    assert len(CLAVES) == 6
