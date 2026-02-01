@echo off
echo Stopping AI Interview Assistant on port 8000...
powershell -Command "$p = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue; if($p) { Stop-Process -Id $p.OwningProcess -Force; echo 'Server stopped.' } else { echo 'Server is not running on port 8000.' }"
pause
