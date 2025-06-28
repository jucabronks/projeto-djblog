# 🌐 Guia Completo: Deploy em Produção com Domínio Próprio

## 🎯 **Objetivo: Do GitHub Pages para Domínio Profissional**

Transformar seu projeto de `jucabronks.github.io/projeto-djblog` para `seudominio.com.br` com infraestrutura profissional.

---

## 📋 **OPÇÃO 1: AWS S3 + CloudFront (Recomendado)**

### **🏆 Vantagens:**
- ✅ **Custo baixo:** $2-5/mês
- ✅ **Performance global:** CDN AWS
- ✅ **SSL automático:** HTTPS gratuito
- ✅ **Escalabilidade infinita**
- ✅ **Integração perfeita** com suas Lambdas

### **📋 Passos:**

#### **1. Registrar Domínio:**
```bash
# Opções recomendadas:
# 1. Registro.br (oficial .com.br) - https://registro.br
# 2. Route 53 AWS (qualquer TLD) - console.aws.amazon.com/route53
# 3. Cloudflare (com DNS gratuito) - cloudflare.com

# Sugestões de nomes:
✅ noticiasdigitais.com.br
✅ portalbrasil24.com.br  
✅ infocentral.com.br
✅ digestnacional.com.br
✅ noticiasagil.com.br
```

#### **2. Configurar S3 para Site Estático:**
```bash
# Executar no projeto:
cd c:\Users\dgajr\OneDrive\Área de Trabalho\projeto-djblog
python scripts/setup_s3_website.py
```

#### **3. Configurar CloudFront + SSL:**
```bash
# Configurar CDN e certificado:
python scripts/setup_cloudfront_ssl.py
```

#### **4. Configurar DNS:**
```bash
# Apontar domínio para CloudFront:
python scripts/setup_dns_route53.py
```

---

## 📋 **OPÇÃO 2: Vercel (Mais Simples)**

### **🏆 Vantagens:**
- ✅ **Deploy automático:** Git push = site atualizado
- ✅ **SSL automático:** HTTPS configurado
- ✅ **CDN global:** Edge computing
- ✅ **Domínio grátis:** `.vercel.app`
- ✅ **Plano grátis generoso**

### **📋 Passos Vercel:**

#### **1. Instalar Vercel CLI:**
```powershell
npm install -g vercel
```

#### **2. Configurar projeto:**
```powershell
# Na pasta do projeto:
cd c:\Users\dgajr\OneDrive\Área de Trabalho\projeto-djblog
vercel login
vercel --prod
```

#### **3. Configurar domínio próprio:**
```powershell
# Se você tem um domínio:
vercel domains add seudominio.com.br
vercel alias set meu-projeto-vercel.vercel.app seudominio.com.br
```

---

## 📋 **OPÇÃO 3: Netlify (Alternativa Simples)**

### **🏆 Vantagens:**
- ✅ **Interface visual** super fácil
- ✅ **Deploy contínuo** via GitHub
- ✅ **Forms handling** gratuito
- ✅ **SSL automático**
- ✅ **Branch previews**

### **📋 Passos Netlify:**

#### **1. Conectar repositório:**
1. Acesse: https://netlify.com
2. **"New site from Git"**
3. Conecte seu repositório GitHub
4. **Build command:** `python generate_static_site.py`
5. **Publish directory:** `./`

#### **2. Configurar domínio:**
1. **Site settings** > **Domain management**
2. **Add custom domain:** `seudominio.com.br`
3. Configurar DNS conforme instruções

---

## 📋 **SCRIPTS AUTOMATIZADOS (Vou Criar)**

Vou criar scripts para automatizar cada opção:

### **🔧 Scripts AWS (Opção 1):**
- `scripts/deploy_aws_s3.py` - Deploy para S3
- `scripts/setup_cloudfront.py` - CDN + SSL
- `scripts/setup_route53.py` - DNS management

### **🔧 Scripts Vercel (Opção 2):**
- `scripts/deploy_vercel.py` - Deploy automatizado
- `scripts/setup_vercel_domain.py` - Configurar domínio

### **🔧 Scripts Netlify (Opção 3):**
- `scripts/deploy_netlify.py` - Deploy via API
- `scripts/setup_netlify_domain.py` - Configurar domínio

---

## 💰 **Comparação de Custos (Mensal)**

| Opção | Custo Base | Domínio .com.br | SSL | CDN | Total/mês |
|-------|------------|-----------------|-----|-----|-----------|
| **AWS S3+CloudFront** | $1-3 | $15/ano | Grátis | Incluído | **$2-4** |
| **Vercel Pro** | $20 | $15/ano | Grátis | Incluído | **$21** |
| **Netlify Pro** | $19 | $15/ano | Grátis | Incluído | **$20** |
| **GitHub Pages** | Grátis | $15/ano | Grátis | Limitado | **$1.25** |

**🏆 Recomendação:** AWS S3 + CloudFront para produção profissional

---

## 🚀 **Próximos Passos**

### **Para AWS (Recomendado):**
1. Confirme se tem conta AWS configurada
2. Escolha um nome de domínio
3. Execute scripts automatizados que vou criar

### **Para Vercel (Mais Simples):**
1. Instale Vercel CLI
2. Execute deploy automatizado
3. Configure domínio próprio

### **Para Netlify (Visual):**
1. Conecte repositório na interface
2. Configure build automático
3. Adicione domínio customizado

---

## 📞 **Suporte**

Escolha uma opção e eu criarei todos os scripts automatizados necessários para deploy em produção com seu domínio próprio!

## 🛠️ **Scripts Criados e Prontos**

### **🔧 Para AWS S3 + CloudFront:**
```powershell
# Deploy completo AWS
python scripts/deploy_aws_production.py
```

### **🔧 Para Vercel (Mais Simples):**
```powershell
# Deploy no Vercel
python scripts/deploy_vercel.py
```

### **🔧 Para Configurar DNS (Cloudflare):**
```powershell
# Configurar DNS automaticamente
python scripts/setup_cloudflare_dns.py
```

---

## 🚀 **Execução Rápida**

### **Opção 1: Vercel (Mais Fácil)**
```powershell
# 1. Deploy no Vercel
python scripts/deploy_vercel.py

# 2. Configurar DNS (se tem domínio próprio)
python scripts/setup_cloudflare_dns.py
```

### **Opção 2: AWS (Mais Profissional)**
```powershell
# 1. Deploy AWS completo
python scripts/deploy_aws_production.py

# 2. DNS automático incluído (Route 53)
# ou usar Cloudflare:
python scripts/setup_cloudflare_dns.py
```

---

**Qual opção prefere?**
- � **Vercel** (5 minutos, automático) → `python scripts/deploy_vercel.py`
- 🥈 **AWS S3** (Profissional, $2/mês) → `python scripts/deploy_aws_production.py`
- 🥉 **Só DNS** (já tem site) → `python scripts/setup_cloudflare_dns.py`
