@echo off
chcp 65001 > nul
title Nafudakake Digital - Servidor Local
echo =======================================================
echo   NAFUDAKAKE DIGITAL - ASSOCIAÇÃO KAGAWA DE KENDO
echo   Iniciando servidor interativo em http://localhost:5050
echo =======================================================
echo.

start http://localhost:5050
python src/server.py

pause
