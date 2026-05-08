@echo off
echo Configurando ContextWordlist v1.0...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python no esta instalado o no esta en el PATH.
    pause
    exit /b 1
)

if not exist "venv\" (
    echo Creando entorno virtual...
    python -m venv venv
)

echo Instalando dependencias (rich)...
venv\Scripts\pip install rich

if not exist "reports\" (
    mkdir reports
    echo Directorio reports\ creado.
)

echo.
echo Setup completado con exito!
echo Ejemplos de uso:
echo   venv\Scripts\python contextwordlist.py -i
echo   venv\Scripts\python contextwordlist.py --name Juan --company Acme --export all
echo.
pause