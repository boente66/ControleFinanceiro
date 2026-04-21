#!/bin/bash

echo "🧹 Limpando build..."
rm -rf build dist __pycache__

echo "🚀 Gerando executável..."

pyinstaller run.py \
--onedir \
--windowed \
--name FinanceApp \
--add-data "assets:assets" \
--add-data "core:core" \
--add-data "views:views" \
--add-data "controllers:controllers" \
--add-data "services:services" \
--add-data "utilitarios:utilitarios" \
--hidden-import matplotlib \
--hidden-import matplotlib.backends.backend_qt5agg \
--hidden-import sqlite3 \
--hidden-import PyQt5.sip

echo "✅ Build finalizado!"
echo "📦 Local: dist/FinanceApp/"
