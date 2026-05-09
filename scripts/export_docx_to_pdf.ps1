param(
    [Parameter(Mandatory = $true)]
    [string]$DocxPath,
    [Parameter(Mandatory = $true)]
    [string]$PdfPath
)

$resolvedDocx = (Resolve-Path $DocxPath).Path
$resolvedPdf = [System.IO.Path]::GetFullPath($PdfPath)

$word = $null
$document = $null

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0

    $document = $word.Documents.Open($resolvedDocx, $false, $true)
    $document.ExportAsFixedFormat($resolvedPdf, 17)
}
finally {
    if ($document -ne $null) {
        $document.Close([ref]$false)
    }
    if ($word -ne $null) {
        $word.Quit()
    }
}
