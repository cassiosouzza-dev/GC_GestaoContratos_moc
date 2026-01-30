@echo off
echo --- GERANDO EXECUTAVEL GC GESTOR ---
echo.

REM Caminho do Python Portatil (Ajuste se mudar de lugar)
set PYTHON_BIN="C:\Users\08220641622\Desktop\python-3.12.8-embed-amd64\python.exe"

REM Comando PyInstaller
%PYTHON_BIN% -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --icon="icon_gc.ico" ^
    --name="GC_Gestor_v1" ^
    --clean ^
    --hidden-import="google_auth_oauthlib" ^
    --hidden-import="googleapiclient" ^
    gestao_contratos.py

echo.
echo --- PROCESSO FINALIZADO ---
pause