#!/bin/bash
# ============================================================================
# Instalador de generarproyecto
# Uso: bash instalar.sh
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATES_DEST="$HOME/.latex-templates"
BIN_DEST="$HOME/.local/bin"

echo ""
echo "  Instalando generarproyecto..."
echo "  ─────────────────────────────"
echo ""

# 1. Crear directorio de plantillas
echo "  → Instalando plantillas en $TEMPLATES_DEST/"
mkdir -p "$TEMPLATES_DEST"
cp -v "$SCRIPT_DIR/templates/"* "$TEMPLATES_DEST/"
echo ""

# 2. Instalar el script
echo "  → Instalando script en $BIN_DEST/"
mkdir -p "$BIN_DEST"
cp "$SCRIPT_DIR/generarproyecto.py" "$BIN_DEST/generarproyecto"
chmod +x "$BIN_DEST/generarproyecto"
echo ""

# 3. Verificar que el PATH incluya ~/.local/bin
if [[ ":$PATH:" != *":$BIN_DEST:"* ]]; then
    echo "  ⚠ $BIN_DEST no está en tu PATH."
    echo ""
    echo "  Agrega esta línea a tu ~/.bashrc o ~/.zshrc:"
    echo ""
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "  Luego ejecuta: source ~/.bashrc  (o source ~/.zshrc)"
    echo ""
else
    echo "  ✓ $BIN_DEST ya está en tu PATH."
fi

# 4. Sugerencia de configuración del autor
echo ""
echo "  ─────────────────────────────"
echo "  ✓ Instalación completada"
echo ""
echo "  Configuración opcional:"
echo "  Para definir tu nombre de autor por defecto, agrega a tu ~/.bashrc:"
echo ""
echo "    export LATEX_AUTOR=\"Tu Nombre Completo\""
echo ""
echo "  Uso:"
echo "    generarproyecto --nombre 'Mi artículo' --tipo art"
echo "    generarproyecto -n 'Mi ensayo' -t ens --autor 'Juan Pérez'"
echo "    generarproyecto -n 'Mi presentación' -t pres"
echo "    generarproyecto --listar"
echo ""
