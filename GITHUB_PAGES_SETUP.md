
🔐 CONFIGURAÇÃO DE SECRETS DO GITHUB

Para o site funcionar automaticamente, configure os seguintes secrets:

🌐 URL: https://github.com/jucabronks/projeto-djblog/settings/secrets/actions

📋 SECRETS OBRIGATÓRIOS:

1. AWS_ACCESS_KEY_ID
   Value: sua_access_key_da_aws

2. AWS_SECRET_ACCESS_KEY  
   Value: sua_secret_key_da_aws

3. AWS_REGION
   Value: us-east-1

4. DYNAMODB_TABLE_NAME
   Value: djblog-noticias

🎯 APÓS CONFIGURAR OS SECRETS:

1. Faça um push para o repositório:
   git add .
   git commit -m "Configurar GitHub Pages automático"
   git push origin main

2. Vá para Settings → Pages no GitHub
3. Configure Source como "GitHub Actions"

4. O site estará disponível em:
   https://jucabronks.github.io/projeto-djblog

📊 MONITORAMENTO AUTOMÁTICO:

- Site é atualizado automaticamente diariamente às 7:00 UTC
- Relatório de saúde disponível em: https://jucabronks.github.io/projeto-djblog/health.json
- Logs de deploy em: https://github.com/jucabronks/projeto-djblog/actions

