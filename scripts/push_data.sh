#!/bin/bash

# Directorio del proyecto
REPO_DIR="/home/dietpi/dashboard_citizen"
cd $REPO_DIR

# 1. Ejecutar la recolección de datos
echo "Iniciando recolección de datos..."
/usr/bin/python3 $REPO_DIR/scripts/harvester.py

# 2. Verificar si el archivo CSV se generó
if [ -f "$REPO_DIR/data/cesta_compra.csv" ]; then
    echo "Datos validados. Preparando subida a GitHub..."
    
    # 3. Operaciones de Git
    git add .
    git commit -m "Auto-update: $(date +'%Y-%m-%d %H:%M') - 12k records"
    
    # Intentar subir (Asume que tienes configurado el token o SSH)
    git push origin main
    
    if [ $? -eq 0 ]; then
        echo "✅ Datos sincronizados con éxito."
    else
        echo "❌ Error al subir a GitHub. Revisa la conexión o el Token."
    fi
else
    echo "❌ Error: No se encontró el archivo de datos."
fi
