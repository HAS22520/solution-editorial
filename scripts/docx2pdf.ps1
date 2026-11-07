# docx2pdf.ps1 — 用本机 Office/WPS COM 把 .docx 导出为 .pdf
#
# 用法：
#   powershell -ExecutionPolicy Bypass -File docx2pdf.ps1 -Docx "D:\x\a.docx" [-Pdf "D:\x\a.pdf"]
#
# 退出码：0 成功；1 参数/文件问题；2 没有可用的 COM 引擎；3 导出失败（文件可能被占用）

param(
    [Parameter(Mandatory = $true)][string]$Docx,
    [string]$Pdf
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Docx)) {
    Write-Error "找不到文件：$Docx"
    exit 1
}
$src = (Resolve-Path -LiteralPath $Docx).Path
if (-not $Pdf) { $Pdf = [System.IO.Path]::ChangeExtension($src, '.pdf') }
$dst = [System.IO.Path]::GetFullPath($Pdf)

$wdExportFormatPDF = 17
$engines = @('Word.Application', 'Kwps.Application', 'wps.Application')
$app = $null
$engineName = $null

foreach ($name in $engines) {
    try {
        $app = New-Object -ComObject $name
        $engineName = $name
        break
    } catch {
        $app = $null
    }
}

if (-not $app) {
    Write-Error "没有可用的 Office/WPS COM 引擎（试过：$($engines -join ', ')）"
    exit 2
}

$doc = $null
try {
    $app.Visible = $false
    try { $app.DisplayAlerts = 0 } catch { }
    # ReadOnly 打开，避免改动源文件
    $doc = $app.Documents.Open($src, $false, $true)
    $doc.ExportAsFixedFormat($dst, $wdExportFormatPDF)
    Write-Output "✓ $engineName 导出成功：$dst"
    exit 0
} catch {
    Write-Error "导出失败（文件可能被 Word/WPS 占用）：$($_.Exception.Message)"
    exit 3
} finally {
    if ($doc) { try { $doc.Close(0) } catch { } }
    if ($app) { try { $app.Quit() } catch { } }
    if ($doc) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) }
    if ($app) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) }
    [GC]::Collect()
}
