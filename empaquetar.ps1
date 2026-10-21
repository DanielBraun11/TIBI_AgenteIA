# Empaquetador de MasOrange TV Agent (TIBI)
# Genera TIBI_tv_agent.zip en la misma carpeta que este script.

$ErrorActionPreference = 'Stop'

$src  = Split-Path -Parent $MyInvocation.MyCommand.Path
$dest = Join-Path $src 'TIBI_tv_agent.zip'
$uid  = [System.Guid]::NewGuid().ToString('N').Substring(0, 8)
$tmp  = Join-Path $env:TEMP "tibi_pkg_$uid\tv_agent"

Write-Host ""
Write-Host "  Origen : $src"
Write-Host "  Destino: $dest"
Write-Host ""

# Crear estructura temporal
foreach ($d in @('.', 'app', 'tools', 'static', 'ficheros',
                 'excalibur_calls', 'Skill Agente', 'Multimedia')) {
    New-Item -ItemType Directory -Path (Join-Path $tmp $d) -Force | Out-Null
}

# Ficheros de la raiz
$rootFiles = @(
    'arquitectura_tibi.html',
    'DOCUMENTACION_TIBI.md',
    'GUIA_INSTALACION.html',
    'instalador.py',
    'instalar.bat',
    'iniciar.bat',
    'iniciar.vbs',
    'empaquetar.bat',
    'empaquetar.ps1',
    'main.py',
    'README_INSTALACION.md',
    'requirements.txt',
    'server.py'
)
foreach ($f in $rootFiles) {
    $from = Join-Path $src $f
    if (Test-Path $from) {
        Copy-Item $from (Join-Path $tmp $f) -Force
        Write-Host "  + $f"
    }
}

# Subcarpetas
$subdirs = @('app', 'tools', 'static', 'ficheros',
             'excalibur_calls', 'Skill Agente', 'Multimedia')
foreach ($d in $subdirs) {
    $srcDir = Join-Path $src $d
    if (-not (Test-Path $srcDir)) { continue }
    foreach ($file in Get-ChildItem $srcDir -File) {
        $dstFile = Join-Path $tmp "$d\$($file.Name)"
        Copy-Item $file.FullName $dstFile -Force
        Write-Host "  + $d\$($file.Name)"
    }
}

# Crear ZIP
if (Test-Path $dest) { Remove-Item $dest -Force }
Compress-Archive -Path $tmp -DestinationPath $dest -CompressionLevel Optimal

# Informe
$count = (Get-ChildItem $tmp -Recurse -File).Count
$mb    = [math]::Round((Get-Item $dest).Length / 1MB, 2)
Write-Host ""
Write-Host "  Ficheros incluidos : $count"
Write-Host "  Tamano del ZIP     : $mb MB"
Write-Host ""
Write-Host "  ZIP guardado en:"
Write-Host "  $dest"
