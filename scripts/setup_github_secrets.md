# 🔐 Configuração de Secrets no GitHub

## 📋 **Passo a Passo**

### **1. Acessar Secrets do Repositório**
1. Vá para seu repositório no GitHub
2. Clique em **Settings** (Configurações)
3. No menu lateral, clique em **Secrets and variables** → **Actions**
4. Clique em **New repository secret**

### **2. Secrets Obrigatórios**

#### **AWS Credentials**
```
Name: AWS_ACCESS_KEY_ID
Value: AKIA... (sua AWS Access Key)

Name: AWS_SECRET_ACCESS_KEY  
Value: ... (sua AWS Secret Key)
```

#### **MongoDB Atlas**
```
Name: MONGO_URI
Value: mongodb+srv://projeto-vm-user:senha-forte-123!@projeto-vm-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

#### **WordPress**
```
Name: WP_URL
Value: https://seu-site.com

Name: WP_USER
Value: admin

Name: WP_APP_PASSWORD
Value: senha-app-wordpress
```

#### **Email para Alertas**
```
Name: ALARM_EMAIL
Value: seu@email.com
```

### **3. Secrets Opcionais**

#### **OpenAI (para resumos com IA)**
```
Name: OPENAI_API_KEY
Value: sk-... (deixe vazio se não usar)
```

#### **Datadog (para monitoramento avançado)**
```
Name: DD_API_KEY
Value: ... (deixe vazio se não usar)
```

#### **Copyscape (para verificação de plágio)**
```
Name: COPYS_API_USER
Value: ... (deixe vazio se não usar)

Name: COPYS_API_KEY
Value: ... (deixe vazio se não usar)
```

## 🔧 **Como Obter as Credenciais**

### **AWS Credentials**
1. Acesse AWS Console
2. IAM → Users → Create User
3. Permissions: `AdministratorAccess` (ou políticas específicas)
4. Create Access Key
5. Guarde Access Key ID e Secret Access Key

### **WordPress App Password**
1. WordPress Admin → Users → Profile
2. Scroll down para "Application Passwords"
3. Add New Application Password
4. Nome: "projeto-vm-lambda"
5. Copie a senha gerada

## ✅ **Verificação**

Após configurar todos os secrets:

1. **Teste o Deploy**:
   - Vá para Actions no GitHub
   - Clique em "Deploy to AWS"
   - Clique em "Run workflow"

2. **Verifique os Logs**:
   - Monitore a execução do workflow
   - Verifique se não há erros de autenticação

3. **Confirme o Email**:
   - Verifique seu email para confirmar inscrição no SNS
   - Clique no link de confirmação

## 🚨 **Segurança**

- ✅ Nunca commite secrets no código
- ✅ Use IAM roles com permissões mínimas
- ✅ Rotacione as credenciais periodicamente
- ✅ Monitore o uso das credenciais

## 📞 **Suporte**

Se houver problemas:
1. Verifique os logs do GitHub Actions
2. Confirme se todos os secrets estão configurados
3. Teste as credenciais localmente 