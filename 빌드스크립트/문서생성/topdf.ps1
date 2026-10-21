param([string]$InDir, [string]$OutDir)
# Word로 docx → pdf (화면 확인용)
New-Item -ItemType Directory -Force $OutDir | Out-Null
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
  Get-ChildItem -Path $InDir -Filter *.docx | ForEach-Object {
    $doc = $w.Documents.Open($_.FullName, $false, $true)
    [string]$pdf = [System.IO.Path]::Combine($OutDir, $_.BaseName + '.pdf')
    $doc.ExportAsFixedFormat($pdf, 17)
    $doc.Close([ref]0)
    Write-Output ("pdf " + $_.BaseName)
  }
} finally { $w.Quit() }
