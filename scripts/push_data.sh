#!/bin/bash
REPO_DIR="/home/dietpi/dashboard_citizen"
LOG_FILE="/home/dietpi/dashboard_sync.log"
cd $REPO_DIR

# 1. Rotación de Logs (Mantenemos solo las últimas 1000 líneas)
tail -n 1000 $LOG_FILE > ${LOG_FILE}.tmp && mv ${LOG_FILE}.tmp $LOG_FILE

# 2. Limpieza de archivos temporales de Python
find . -type d -name "__pycache__" -exec rm -rf {} +

# 3. Recolección de datos
/usr/bin/python3 $REPO_DIR/scripts/harvester.py

# 4. Sincronización con GitHub
git add .
git commit -m "Auto-update: $(date +'%Y-%m-%d %H:%M')"
git push origin main
