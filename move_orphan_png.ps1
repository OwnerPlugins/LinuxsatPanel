# ============================================================
#  LinuxsatPanel 3.0.9 - sposta le PNG orfane in D:\pnglinuxsat
#  Uso (da PowerShell):
#    cd D:\PcBeatrice\Documents\GitHub\LinuxsatPanel
#    powershell -ExecutionPolicy Bypass -File .\move_orphan_png.ps1
# ============================================================
$Repo  = "D:\PcBeatrice\Documents\GitHub\LinuxsatPanel"
$Icons = Join-Path $Repo "usr\lib\enigma2\python\Plugins\Extensions\LinuxsatPanel\LSicons2"
$Dest  = "D:\pnglinuxsat"

$orphans = @(
  "cbu","cec","chnnel-list","ciefpdishpointer_","cyrus","vhannibal2",
  "ciefp_bootlogo","ciefp_bu","ciefp_cman","ciefp_e2editor","ciefp_easysetup","ciefp_ec",
  "ciefp_epginfo","ciefp_epgshare","ciefp_ib","ciefp_mojtvepg","ciefp_oe","ciefp_opdir",
  "ciefp_opensubtitles","ciefp_piconmanager","ciefp_pictureplayer","ciefp_plugins","ciefp_satan",
  "ciefp_screengrab","ciefp_sd","ciefp_signalinfo","ciefp_sm","ciefp_sp","ciefp_sr2","ciefp_sr3",
  "ciefp_srtplayer","ciefp_ss","ciefp_subt","ciefp_t2m","ciefp_t2mpli","ciefp_tmdb",
  "ciefp_tvprogram","ciefp_tvprograma1hr","ciefp_tvprogramsbb","ciefp_tvprogramsk",
  "ciefp_tvtodayde","ciefp_vibes","ciefp_videoplayer","ciefp_webcam","ciefp_wls","ciefp_xed",
  "ciefp_youtube","csd","csm","csp","css","cssp2","cssp3","csta","cstapli","cws",
  "E2playerMOHAMED","E2playerXXX","flysat","iSettingE2","Multistalker",
  "revolution_pro","revolution_xxx","revolutionlite","SkinFHD","vavoo_maker","xclass","xklass"
)

if (-not (Test-Path $Icons)) { Write-Host "Cartella non trovata: $Icons" -ForegroundColor Red; exit 1 }
New-Item -ItemType Directory -Force -Path $Dest | Out-Null

# 1) sposta le orfane (68)
$moved = 0; $bytes = 0
foreach ($n in $orphans) {
  $f = Join-Path $Icons "$n.png"
  if (Test-Path -LiteralPath $f) {
    $bytes += (Get-Item -LiteralPath $f).Length
    Move-Item -LiteralPath $f -Destination $Dest -Force
    $moved++
  } else {
    Write-Host "  (gia' assente) $n.png" -ForegroundColor DarkGray
  }
}
Write-Host ("Spostate {0} PNG in {1} ({2:N0} KB)" -f $moved, $Dest, ($bytes/1KB)) -ForegroundColor Green

# 2) corregge maiuscole/minuscole di 3 icone (Linux e' case-sensitive).
#    Due passaggi perche' Windows non vede un rename di sole maiuscole.
$renames = @{
  "ciefpchannelhistory.png" = "CiefpChannelHistory.png"
  "ciefpkingsat.png"        = "CiefpKingSat.png"
  "titlovibrowser.png"      = "TitloviBrowser.png"
}
Push-Location $Repo
foreach ($old in $renames.Keys) {
  $new = $renames[$old]
  $actual = Get-ChildItem -LiteralPath $Icons -File | Where-Object { $_.Name -ieq $old } | Select-Object -First 1
  if ($null -eq $actual) { Write-Host "  (manca) $old" -ForegroundColor DarkGray; continue }
  if ($actual.Name -ceq $new) { Write-Host "  gia' corretto: $new" -ForegroundColor DarkGray; continue }
  $rel = "usr/lib/enigma2/python/Plugins/Extensions/LinuxsatPanel/LSicons2"
  git mv "$rel/$($actual.Name)" "$rel/_tmp_$new" 2>$null
  if ($LASTEXITCODE -ne 0) {   # git non disponibile: rename semplice
    Rename-Item -LiteralPath $actual.FullName -NewName "_tmp_$new"
    Rename-Item -LiteralPath (Join-Path $Icons "_tmp_$new") -NewName $new
  } else {
    git mv "$rel/_tmp_$new" "$rel/$new"
  }
  Write-Host "  rinominata: $($actual.Name) -> $new" -ForegroundColor Cyan
}
Pop-Location

Write-Host ""
Write-Host "Fatto. In GitHub Desktop vedrai le PNG come 'eliminate' e le 3 rinominate." -ForegroundColor Yellow
Write-Host "Le copie sono in $Dest (per rimetterne una basta ricopiarla in LSicons2)."
