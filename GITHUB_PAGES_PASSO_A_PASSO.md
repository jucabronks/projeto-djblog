# 🌐 Passo a Passo: Habilitar GitHub Pages

## 🎯 **OBJETIVO: Ativar o site automático em 5 minutos**

---

## 📋 **PASSO 1: Configurar GitHub Secrets (OBRIGATÓRIO)**

### **1.1 - Abrir configuração de Secrets:**
1. Vá para: https://github.com/jucabronks/projeto-djblog
2. Clique em **"Settings"** (no topo da página)
3. No menu lateral esquerdo, clique em **"Secrets and variables"**
4. Clique em **"Actions"**

### **1.2 - Adicionar os 4 Secrets obrigatórios:**

**🔑 SECRET 1:**
- Clique em **"New repository secret"**
- **Name:** `AWS_ACCESS_KEY_ID`
- **Secret:** `sua_access_key_da_aws`
- Clique em **"Add secret"**

**🔑 SECRET 2:**
- Clique em **"New repository secret"**
- **Name:** `AWS_SECRET_ACCESS_KEY`
- **Secret:** `sua_secret_key_da_aws`
- Clique em **"Add secret"**

**🔑 SECRET 3:**
- Clique em **"New repository secret"**
- **Name:** `AWS_REGION`
- **Secret:** `us-east-1`
- Clique em **"Add secret"**

**🔑 SECRET 4:**
- Clique em **"New repository secret"**
- **Name:** `DYNAMODB_TABLE_NAME`
- **Secret:** `djblog-noticias`
- Clique em **"Add secret"**

---

## 📋 **PASSO 2: Habilitar GitHub Pages**

### **2.1 - Abrir configuração do Pages:**
1. No mesmo repositório: https://github.com/jucabronks/projeto-djblog
2. Clique em **"Settings"** (no topo da página)
3. No menu lateral esquerdo, role para baixo e clique em **"Pages"**

### **2.2 - Configurar a fonte:**
1. Em **"Source"**, selecione: **"GitHub Actions"**
2. ✅ Pronto! Não precisa configurar mais nada

---

## 📋 **PASSO 3: Executar o Deploy (Opcional)**

### **3.1 - Executar manualmente (para testar):**
1. Vá para: https://github.com/jucabronks/projeto-djblog/actions
2. Clique no workflow **"🌐 Deploy Site Estático"**
3. Clique em **"Run workflow"**
4. Clique no botão azul **"Run workflow"**

### **3.2 - Aguardar execução:**
- O workflow demora cerca de **2-3 minutos**
- Acompanhe o progresso na página Actions
- ✅ Quando terminar, aparecerá um ✅ verde

---

## 📋 **PASSO 4: Verificar se funcionou**

### **4.1 - Verificar URL do site:**
1. Aguarde **1-2 minutos** após o workflow terminar
2. Acesse: https://jucabronks.github.io/projeto-djblog
3. ✅ O site deve estar funcionando!

### **4.2 - Se o site não carregar:**
- Aguarde mais 5 minutos (pode demorar para propagar)
- Verifique se todos os 4 secrets foram adicionados corretamente
- Verifique se o Source está como "GitHub Actions"

---

## � **PASSO 5: Configurar Domínio Customizado (OPCIONAL)**

### **5.1 - Requisitos para domínio próprio:**
- Possuir um domínio registrado (ex: `meublog.com.br`)
- Acesso ao painel DNS do domínio (Cloudflare, GoDaddy, etc.)

### **5.2 - Configurar DNS (no seu provedor):**
**Para subdomínio (ex: blog.meusite.com):**
```
CNAME blog.meusite.com → jucabronks.github.io
```

**Para domínio principal (ex: meusite.com):**
```
A meusite.com → 185.199.108.153
A meusite.com → 185.199.109.153
A meusite.com → 185.199.110.153
A meusite.com → 185.199.111.153
```

### **5.3 - Configurar no GitHub Pages:**
1. Vá para: https://github.com/jucabronks/projeto-djblog/settings/pages
2. Em **"Custom domain"**, digite seu domínio: `blog.meusite.com`
3. Clique em **"Save"**
4. ✅ Aguarde validação DNS (5-15 minutos)
5. ✅ Marque **"Enforce HTTPS"** quando disponível

### **5.4 - Criar arquivo CNAME (automático):**
- O GitHub criará automaticamente o arquivo `CNAME` no repositório
- ✅ Não é necessário fazer nada manual

### **5.5 - Verificar domínio customizado:**
- Aguarde **15-30 minutos** para propagação DNS
- Acesse seu domínio customizado
- ✅ O site deve estar funcionando com SSL!

---

## �🔄 **AUTOMAÇÃO APÓS CONFIGURAÇÃO:**

### **✅ O que acontece automaticamente:**
- **04:00 (BRT) todo dia** - Site é atualizado automaticamente
- **21:00 (BRT) todo dia** - Notícias são coletadas automaticamente
- **Zero manutenção** necessária

### **📊 URLs importantes:**
- **Site GitHub:** https://jucabronks.github.io/projeto-djblog
- **Site customizado:** (seu domínio, se configurado)
- **Logs:** https://github.com/jucabronks/projeto-djblog/actions
- **Health Check:** https://jucabronks.github.io/projeto-djblog/health.json

---

## 🆘 **RESOLUÇÃO DE PROBLEMAS:**

### **❌ Site não carrega (404):**
1. Verifique se GitHub Pages está configurado como "GitHub Actions"
2. Verifique se todos os 4 secrets foram adicionados
3. Execute o workflow manualmente nos Actions
4. Aguarde 5-10 minutos para propagação

### **❌ Workflow falha:**
1. Verifique se as credenciais AWS estão corretas
2. Verifique se a região AWS está como "us-east-1"
3. Verifique os logs de erro nos Actions

### **❌ Site carrega mas sem conteúdo:**
- É normal! As notícias serão coletadas automaticamente às 21:00 (BRT)
- Para testar imediatamente, execute o workflow manualmente

### **❌ Domínio customizado não funciona:**
1. Verifique se os registros DNS foram configurados corretamente
2. Aguarde **24-48 horas** para propagação completa do DNS
3. Use ferramentas como https://www.whatsmydns.net para verificar propagação
4. Certifique-se de que o DNS aponta para `jucabronks.github.io` (CNAME) ou IPs corretos (A)

### **❌ Certificado SSL não carrega:**
- Aguarde **1-2 horas** após validação DNS bem-sucedida
- O GitHub ativa HTTPS automaticamente quando DNS está correto
- Marque "Enforce HTTPS" apenas depois que o certificado estiver ativo

---

## 🎉 **RESULTADO FINAL:**

✅ **Site funcionando:** https://jucabronks.github.io/projeto-djblog  
✅ **Domínio customizado:** (se configurado)  
✅ **Atualização automática** todo dia às 04:00 (BRT)  
✅ **Zero manutenção** necessária  
✅ **Custo:** $3-5/mês na AWS (GitHub Pages é gratuito)  
✅ **SSL/HTTPS:** Incluído gratuitamente  

**🎯 Pronto para produção!**

## 💡 **PRÓXIMOS PASSOS OPCIONAIS:**

1. **🎨 Customizar nome do blog:** Editar `config.py` e fazer commit
2. **📊 Analytics:** Adicionar Google Analytics no template HTML
3. **🎯 SEO:** Configurar Google Search Console
4. **📧 Notificações:** Configurar alertas de falha do deploy
5. **📈 Monitoramento:** Usar AWS CloudWatch para métricas detalhadas
