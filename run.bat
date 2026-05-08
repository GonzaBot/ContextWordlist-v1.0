@echo off
if not exist "venv\Scripts\activate.bat" (
    echo [!] Error: El entorno virtual no existe.
    echo Ejecuta setup.bat primero.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo 1. Modo Interactivo (Pregunta por pregunta)
echo 2. Modo Rapido (Flags basicos)
set /p mode="Elige una opcion (1/2): "

if "%mode%"=="1" (
    python contextwordlist.py -i
) else (
    set /p t_name="Nombre de la persona (Enter para omitir): "
    set /p t_comp="Nombre de la empresa (Enter para omitir): "
    set /p t_exp="Formato export (txt/rules/html/csv/all) [txt]: "
    
    if "%t_exp%"=="" set t_exp=txt
    
    set CMD=python contextwordlist.py --export %t_exp%
    if not "%t_name%"=="" set CMD=%CMD% --name "%t_name%"
    if not "%t_comp%"=="" set CMD=%CMD% --company "%t_comp%"
    
    %CMD%
)

echo.
set /p repeat="Generar otro wordlist? (s/N): "
if /I "%repeat%"=="s" goto :run_again
pause