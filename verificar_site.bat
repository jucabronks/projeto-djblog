@echo off
:: 🚀 Script de Verificação Rápida do DJBlog para Windows
:: Uso: verificar_site.bat [--quick|--open|--deploy]

echo 🚀 DJBlog - Verificação Rápida
echo ================================

:: Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

:: Verifica o argumento
set ACTION=%1
if "%ACTION%"=="--quick" goto QUICK
if "%ACTION%"=="--open" goto OPEN
if "%ACTION%"=="--deploy" goto DEPLOY
if "%ACTION%"=="--help" goto HELP

:: Verificação padrão
echo 🔍 Executando verificação completa...
python verificar_site.py
goto END

:QUICK
echo ⚡ Verificação super rápida...
python verificar_site.py --quick
goto END

:OPEN
echo 🌐 Verificando e abrindo site...
python verificar_site.py --open
goto END

:DEPLOY
echo 🚀 Iniciando deploy completo...
python deploy_oneclick.py
goto END

:HELP
echo.
echo 🚀 DJBlog - Script de Verificação
echo.
echo Uso:
echo   verificar_site.bat          Verificação completa
echo   verificar_site.bat --quick  Verificação rápida
echo   verificar_site.bat --open   Abrir site no navegador
echo   verificar_site.bat --deploy Deploy completo
echo   verificar_site.bat --help   Esta ajuda
echo.
goto END

:END
echo.
echo 💡 Dica: Use 'verificar_site.bat --quick' para verificação rápida
pause
