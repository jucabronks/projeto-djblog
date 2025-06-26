#!/usr/bin/env python3
"""
🔧 Configurador Automático do GitHub Pages
Script para configurar o GitHub Pages com zero esforço humano
"""

import requests
import json
import os
import subprocess


def run_git_command(command):
    """Executa comando git e retorna o resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def get_github_repo_info():
    """Obtém informações do repositório GitHub"""
    success, output, error = run_git_command("git remote get-url origin")
    if not success:
        return None, None

    # Extrair owner e repo da URL
    # Formatos: https://github.com/owner/repo.git ou
    # git@github.com:owner/repo.git
    url = output.replace('.git', '')
    if 'github.com/' in url:
        parts = url.split('github.com/')[-1].split('/')
        if len(parts) >= 2:
            return parts[0], parts[1]

    return None, None


def create_github_pages_config():
    """Cria configuração do GitHub Pages"""
    print("🔧 Configurando GitHub Pages...")

    # Verificar se já existe configuração
    if os.path.exists('.github/workflows/deploy-site.yml'):
        print("✅ Workflow do GitHub Actions já existe!")
    else:
        print("❌ Workflow não encontrado. Execute este script após criar o arquivo!")
        return False

    # Verificar repositório
    owner, repo = get_github_repo_info()
    if not owner or not repo:
        print("❌ Não foi possível identificar o repositório GitHub")
        return False

    print(f"📋 Repositório identificado: {owner}/{repo}")

    # Criar arquivo de configuração para GitHub Pages
    github_pages_config = {
        "source": {
            "branch": "gh-pages",
            "path": "/"
        }
    }

    # Salvar configurações
    with open('.github-pages-config.json', 'w') as f:
        json.dump(github_pages_config, f, indent=2)

    print("✅ Configuração do GitHub Pages criada!")
    return True


def setup_secrets_instructions():
    """Cria instruções para configurar secrets"""
    owner, repo = get_github_repo_info()
    if not owner or not repo:
        print("❌ Não foi possível identificar o repositório")
        return

    secrets_needed = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_REGION",
        "DYNAMODB_TABLE_NAME"
    ]

    instructions = """
🔐 CONFIGURAÇÃO DE SECRETS DO GITHUB

Para o site funcionar automaticamente, configure os seguintes secrets:

🌐 URL: https://github.com/{owner}/{repo}/settings/secrets/actions

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
   https://{owner}.github.io/{repo}

📊 MONITORAMENTO AUTOMÁTICO:

- Site é atualizado automaticamente diariamente às 7:00 UTC
- Relatório de saúde disponível em: https://{owner}.github.io/{repo}/health.json
- Logs de deploy em: https://github.com/{owner}/{repo}/actions

"""

    with open('GITHUB_PAGES_SETUP.md', 'w', encoding='utf-8') as f:
        f.write(instructions)

    print("📄 Instruções salvas em: GITHUB_PAGES_SETUP.md")
    print("\n" + instructions)


def create_health_check_page():
    """Cria página de monitoramento automático"""
    html_content = """<!DOCTYPE html>"
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍 Monitor do Sistema</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        .status-card {
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #ddd;
        }
        .status-up {
            background: #d4edda;
            border-left-color: #28a745;
        }
        .status-down {
            background: #f8d7da;
            border-left-color: #dc3545;
        }
        .status-unknown {
            background: #fff3cd;
            border-left-color: #ffc107;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
        }
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        .timestamp {
            text-align: center;
            color: #666;
            margin-top: 1rem;
        }
        pre {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Monitor do Sistema</h1>
            <p>Status em tempo real do DJBlog</p>
            <button class= (
                "refresh-btn" onclick="loadHealth()">🔄 Atualizar</button>
            )
        </div>

        <div id="health-status">
            <p>📡 Carregando dados...</p>
        </div>

        <div class="timestamp">
            <p>🕒 Última atualização: <span id="last-update">--</span></p>
        </div>
    </div>

    <script>
        async function loadHealth() {
            try {
                const response = await fetch('./health.json');
                const data = await response.json();
                displayHealth(data);
            } catch (error) {
                document.getElementById('health-status').innerHTML = `
                    <div class="status-card status-down">
                        <h3>❌ Erro ao carregar dados</h3>
                        <p>Não foi possível carregar o relatório de saúde.</p>
                        <pre>${error.message}</pre>
                    </div>
                `;
            }
        }

        function displayHealth(data) {
            let html = '<div class="status-grid">';

            // Status dos websites
            if (data.websites) {
                for (const [url, status] of Object.entries(data.websites)) {
                    const statusClass = (
                        status.status === 'UP' ? 'status-up' : 'status-down';
                    )
                    const emoji = status.status === 'UP' ? '✅' : '❌';
                    html += `
                        <div class="status-card ${statusClass}">
                            <h3>${emoji} Website</h3>
                            <p><strong>URL:</strong> ${url}</p>
                            <p><strong>Status:</strong> ${status.status}</p>
                            ${status.response_time ? `<p><strong>Tempo:</strong> ${status.response_time.toFixed(2)}s</p>` : ''}
                        </div>
                    `;
                }
            }

            // Status do DynamoDB
            if (data.dynamodb) {
                const statusClass = (
                    data.dynamodb.status = (
                        == 'UP' ? 'status-up' : 'status-down';
                    )
                )
                const emoji = data.dynamodb.status === 'UP' ? '✅' : '❌';
                html += `
                    <div class="status-card ${statusClass}">
                        <h3>${emoji} DynamoDB</h3>
                        <p><strong>Status:</strong> ${data.dynamodb.status}</p>
                        ${data.dynamodb.table_name ? `<p><strong>Tabela:</strong> ${data.dynamodb.table_name}</p>` : ''}
                    </div>
                `;
            }

            // Status das Lambda Functions
            if (data.lambda_functions && typeof data.lambda_functions = (
                == 'object') {
            )
                for (const [funcName, status] of Object.entries(data.lambda_functions)) {
                    if (typeof status === 'object' && status.status) {
                        const statusClass = (
                            status.status = (
                                == 'UP' ? 'status-up' : 'status-down';
                            )
                        )
                        const emoji = status.status === 'UP' ? '✅' : '❌';
                        html += `
                            <div class="status-card ${statusClass}">
                                <h3>${emoji} ${funcName}</h3>
                                <p><strong>Status:</strong> ${status.status}</p>
                            </div>
                        `;
                    }
                }
            }

            html += '</div>';
            document.getElementById('health-status').innerHTML = html;
            document.getElementById('last-update').textContent = (
                new Date(data.timestamp).toLocaleString('pt-BR');
            )
        }

        // Carregar dados inicialmente
        loadHealth();

        // Atualizar a cada 5 minutos
        setInterval(loadHealth, 5 * 60 * 1000);
    </script>
</body>
</html>"""

    with open('monitor.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("📊 Página de monitoramento criada: monitor.html")


def main():
    """Função principal"""
    print("🚀 CONFIGURADOR AUTOMÁTICO DO GITHUB PAGES")
    print("=" * 50)

    try:
        # Configurar GitHub Pages
        if create_github_pages_config():
            print("✅ GitHub Pages configurado!")

        # Criar instruções
        setup_secrets_instructions()

        # Criar página de monitoramento
        create_health_check_page()

        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Configure os secrets conforme instruções em GITHUB_PAGES_SETUP.md")
        print("2. Faça push do código para GitHub")
        print("3. Configure GitHub Pages para usar GitHub Actions")
        print("4. O site será atualizado automaticamente!")

        return 0

    except Exception as e:
        print(f"💥 ERRO: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
