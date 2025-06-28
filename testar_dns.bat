@echo off
echo 🔄 Testando propagação DNS do noticiasontem.com.br
echo.
echo 📋 Testando domínio principal:
nslookup noticiasontem.com.br
echo.
echo 📋 Testando subdomínio www:
nslookup www.noticiasontem.com.br
echo.
echo ✅ Se aparecer "cloudfront" nos resultados = DNS OK!
echo ❌ Se não aparecer = aguarde mais alguns minutos
pause
