"""El eje de formato: hep por defecto, clasico bajo demanda."""

import pytest

import generarproyecto as g
from conftest import entornos_desbalanceados, placeholders_sin_sustituir

# Marcas que solo aparecen en uno de los dos formatos.
MARCAS_HEP = ["top=1in", "{upgreek}", "\\newcommand{\\Bc}"]
MARCAS_CLASICO = ["top=2.5cm", "{fancyhdr}", "\\tableofcontents"]


def test_hep_es_el_defecto():
    assert g.FORMATO_DEFAULT == "hep"


def test_sin_pedir_nada_sale_el_formato_hep(generar):
    _, tex = generar()
    for marca in MARCAS_HEP:
        assert marca in tex, f"falta la marca {marca} del formato hep"
    for marca in MARCAS_CLASICO:
        assert marca not in tex, f"el formato hep no debería traer {marca}"


def test_clasico_conserva_la_plantilla_de_siempre(generar):
    _, tex = generar(formato="clasico")
    for marca in MARCAS_CLASICO:
        assert marca in tex, f"falta la marca {marca} del formato clasico"
    for marca in MARCAS_HEP:
        assert marca not in tex, f"el formato clasico no debería traer {marca}"


def test_clasico_es_identico_a_la_plantilla_del_repositorio(generar, plantillas):
    """
    El formato clasico no debe haber cambiado con la introducción del eje: es
    la plantilla original con los placeholders resueltos.
    """
    _, tex = generar(formato="clasico")
    original = (plantillas / "articulo.tex").read_text(encoding="utf-8")
    # Las líneas sin placeholders deben sobrevivir intactas.
    intactas = [
        linea for linea in original.splitlines()
        if linea.strip() and not placeholders_sin_sustituir(linea)
    ]
    faltantes = [linea for linea in intactas if linea not in tex]
    assert faltantes == [], f"la plantilla clasica perdió líneas: {faltantes[:3]}"


@pytest.mark.parametrize("formato", ["hep", "clasico"])
def test_entornos_balanceados_en_ambos_formatos(generar, formato):
    _, tex = generar(formato=formato)
    assert entornos_desbalanceados(tex) == []


# ---------------------------------------------------------------------------
# Bloque institucional de la portada
# ---------------------------------------------------------------------------

def test_campos_institucionales_vacios_por_defecto(generar):
    """
    Un documento personal no debe salir con el encabezado de una institución
    ajena. Vacíos por defecto, y el bloque no se imprime.
    """
    _, tex = generar()
    assert "\\newcommand{\\lainstitucion}{}" in tex
    assert "\\newcommand{\\elnuminforme}{}" in tex
    assert "\\newcommand{\\lapublicacion}{}" in tex


def test_campos_institucionales_se_rellenan(generar):
    _, tex = generar(
        institucion="Universidad de El Salvador",
        num_informe="FCNM-2026-001",
        publicado_en="Publicado en la Revista X",
    )
    assert "\\newcommand{\\lainstitucion}{Universidad de El Salvador}" in tex
    assert "\\newcommand{\\elnuminforme}{FCNM-2026-001}" in tex
    assert "\\newcommand{\\lapublicacion}{Publicado en la Revista X}" in tex


def test_el_bloque_condicional_sigue_presente(generar):
    """La plantilla decide en tiempo de compilación si imprime cada bloque."""
    _, tex = generar()
    assert "\\ifthenelse{\\equal{\\lainstitucion}{}}" in tex


# ---------------------------------------------------------------------------
# Resolución de plantilla y combinación de ejes
# ---------------------------------------------------------------------------

def test_resolver_plantilla_elige_la_variante_hep(plantillas):
    assert g.resolver_plantilla("art", "hep") == plantillas / "articulo-hep.tex"
    assert g.resolver_plantilla("art", "clasico") == plantillas / "articulo.tex"


@pytest.mark.parametrize("tipo, esperado", [
    ("ens", "ensayo.tex"),
    ("pres", "presentacion.tex"),
])
def test_tipos_sin_variante_caen_en_su_plantilla_base(plantillas, tipo, esperado):
    """
    'hep' solo aporta variante para 'art'. Los demás tipos deben seguir
    funcionando con el formato por defecto, no romperse.
    """
    assert g.resolver_plantilla(tipo, "hep") == plantillas / esperado


@pytest.mark.parametrize("tipo", ["ens", "pres"])
def test_el_formato_no_altera_los_tipos_sin_variante(generar, tipo):
    _, con_hep = generar(tipo=tipo, formato="hep")
    _, con_clasico = generar(nombre="Otro nombre", tipo=tipo, formato="clasico")
    assert "Proyecto de prueba" in con_hep
    assert "Otro nombre" in con_clasico


def test_los_tres_ejes_se_combinan(generar):
    """formato + citas + numeración de líneas, todo a la vez."""
    _, tex = generar(formato="hep", citas="apa", numeracion_lineas=True)
    assert "top=1in" in tex
    assert "style=apa" in tex
    assert "sorting=nyt" in tex
    assert "\\linenumbers" in tex


def test_formato_invalido_sale_con_error(tmp_path):
    with pytest.raises(SystemExit) as excinfo:
        g.crear_proyecto(
            nombre="X", tipo="art", autor="A", citas=g.CITAS_DEFAULT,
            directorio_base=tmp_path, formato="inexistente",
        )
    assert excinfo.value.code == 1
