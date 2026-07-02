#requires -Version 5.1
<#
    Instalador de generarproyecto (Windows / PowerShell)

    Uso:
        powershell -ExecutionPolicy Bypass -File instalar.ps1

    Alternativas:
        - Linux/macOS: bash instalar.sh
        - Cualquier SO con pip: pip install .  /  pipx install .
#>

$ErrorActionPreference = "Stop"

$ScriptDir       = Split-Path -Parent $MyInvocation.MyCommand.Path
$TemplatesSource = Join-Path $ScriptDir "src\generarproyecto\templates"
$TemplatesDest   = Join-Path $env:USERPROFILE ".latex-templates"
$BinDest         = Join-Path $env:LOCALAPPDATA "Programs\generarproyecto"

Write-Host ""
Write-Host "  Instalando generarproyecto..."
Write-Host "  -----------------------------"
Write-Host ""

# 1. Copiar plantillas
Write-Host "  -> Instalando plantillas en $TemplatesDest\"
New-Item -ItemType Directory -Force -Path $TemplatesDest | Out-Null
Copy-Item -Path (Join-Path $TemplatesSource "*") -Destination $TemplatesDest -Recurse -Force
Get-ChildItem $TemplatesDest | ForEach-Object { Write-Host "     $($_.Name)" }
Write-Host ""

# 2. Instalar el script y un shim .bat que lo invoque
Write-Host "  -> Instalando script en $BinDest\"
New-Item -ItemType Directory -Force -Path $BinDest | Out-Null
Copy-Item -Path (Join-Path $ScriptDir "src\generarproyecto\__init__.py") -Destination (Join-Path $BinDest "generarproyecto.py") -Force

$ShimPath = Join-Path $BinDest "generarproyecto.bat"
@"
@echo off
python "%~dp0generarproyecto.py" %*
"@ | Set-Content -Path $ShimPath -Encoding ASCII
Write-Host ""

# 3. Verificar que BinDest esté en el PATH del usuario
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$BinDest*") {
    Write-Host "  ! $BinDest no está en tu PATH de usuario."
    Write-Host ""
    Write-Host "  Para agregarlo, ejecuta en PowerShell:"
    Write-Host ""
    Write-Host "    [Environment]::SetEnvironmentVariable('Path', `$env:Path + ';$BinDest', 'User')"
    Write-Host ""
    Write-Host "  Luego cierra y vuelve a abrir la terminal."
    Write-Host ""
} else {
    Write-Host "  OK: $BinDest ya está en tu PATH."
}

# 4. Sugerencia de configuración del autor
Write-Host ""
Write-Host "  -----------------------------"
Write-Host "  Instalación completada"
Write-Host ""
Write-Host "  Configuración opcional:"
Write-Host "  Para definir tu nombre de autor por defecto, ejecuta:"
Write-Host ""
Write-Host "    [Environment]::SetEnvironmentVariable('LATEX_AUTOR', 'Tu Nombre Completo', 'User')"
Write-Host ""
Write-Host "  Uso:"
Write-Host "    generarproyecto --nombre 'Mi articulo' --tipo art"
Write-Host "    generarproyecto -n 'Mi ensayo' -t ens --autor 'Juan Perez'"
Write-Host "    generarproyecto -n 'Mi presentacion' -t pres"
Write-Host "    generarproyecto -n 'Mi articulo' -t art -l    # numeracion de lineas"
Write-Host "    generarproyecto --listar"
Write-Host ""
Write-Host "  Nota: requiere Python 3.9+ disponible en el PATH (comando 'python')."
Write-Host ""
