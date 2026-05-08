#!/bin/bash
echo "Configurando ContextWordlist v1.0..."

# Verificar Python 3.10+
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 no está instalado."
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual (venv)..."
    python3 -m venv venv
fi

# Activar e instalar dependencias
source venv/bin/activate
echo "Instalando dependencias (rich)..."
pip install rich

# Crear directorio de reportes
mkdir -p reports
echo "Directorio reports/ creado."

echo ""
echo "¡Setup completado con éxito!"
echo "Ejemplos de uso:"
echo "  ./venv/bin/python contextwordlist.py -i"
echo "  ./venv/bin/python contextwordlist.py --name Juan --company Acme --export all"
echo ""

read -p "¿Quieres correr el modo interactivo ahora? (s/N): " run_now
if [[ "$run_now" =~ ^[sS]$ ]]; then
    python contextwordlist.py -i
fi