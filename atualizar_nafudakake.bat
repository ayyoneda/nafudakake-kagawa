@echo off
chcp 65001 > nul
title Nafudakake Digital - Atualizar Dados e Publicar
echo =======================================================
echo   NAFUDAKAKE DIGITAL - ASSOCIAÇÃO KAGAWA DE KENDO
echo   1. Conectando ao Google Sheets e gerando arquivos...
echo =======================================================
echo.

python src/Nafudakake.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Ocorreu uma falha ao gerar o Nafudakake.
    echo Verifique sua conexão com a internet ou as credenciais.
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo =======================================================
echo   2. Verificando alterações e publicando no GitHub...
echo =======================================================
echo.

git status --porcelain > nul 2>&1
for /f %%i in ('git status --porcelain') do set HAS_CHANGES=1

if defined HAS_CHANGES (
    git add .
    git commit -m "Atualizacao automatica de dados: %date% %time%"
    git push origin main
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo =======================================================
        echo   ✅ SUCESSO!
        echo   O Nafudakake foi atualizado e publicado no GitHub!
        echo   Em ~1 minuto o Datastudio refletira os novos dados.
        echo =======================================================
    ) else (
        echo.
        echo [AVISO] Os arquivos foram gerados, mas houve falha no git push.
    )
) else (
    echo [INFO] Nenhuma alteração detectada na planilha. Os arquivos já estavam atualizados.
)

echo.
pause
