@echo off
chcp 65001 > nul
title Nafudakake Digital - Atualizar Dados e Artefatos
echo =======================================================
echo   NAFUDAKAKE DIGITAL - ASSOCIAÇÃO KAGAWA DE KENDO
echo   Atualizando dados do Google Sheets e gerando imagens...
echo =======================================================
echo.

python src/Nafudakake.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCESSO] Plaquetas, SVGs e PNGs gerados com sucesso!
    echo.
    echo Para publicar as alterações no Looker Studio / GitHub Pages:
    echo   git add .
    echo   git commit -m "Atualização do Nafudakake"
    echo   git push origin main
    echo.
) else (
    echo.
    echo [ERRO] Ocorreu uma falha ao gerar o Nafudakake.
    echo.
)

pause
