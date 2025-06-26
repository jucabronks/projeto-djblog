#!/usr/bin/env python3
"""
Gerador de site estático otimizado - Versão Corrigida
Sistema robusto de geração de HTML responsivo com fallback inteligente
"""

import json
import os
from datetime import datetime, timezone
import hashlib

# Configurações do site
SITE_CONFIG = {
    'title': 'DJBlog - Notícias Automatizadas',
    'description': 'Sistema inteligente de agregação de notícias brasileiras com tecnologia avançada',
    'language': 'pt-BR',
    'author': 'DJBlog System',
    'url': 'https://jucabronks.github.io/projeto-djblog'
}

def carregar_noticias_demo():
    """Carrega notícias demo brasileiras"""
    return [
        {
            'titulo': 'Tecnologia brasileira cresce 15% no primeiro trimestre',
            'resumo': 'Setor de tecnologia nacional apresenta crescimento significativo impulsionado por startups e investimentos em inovação.',
            'fonte': 'TechBrasil',
            'nicho': 'Tecnologia',
            'link': 'https://example.com/tech-brasil',
            'data_insercao': datetime.now().isoformat(),
            'id': 'tech001'
        },
        {
            'titulo': 'Nova descoberta médica promete revolucionar tratamentos',
            'resumo': 'Pesquisadores brasileiros desenvolvem técnica inovadora que pode transformar o tratamento de doenças crônicas.',
            'fonte': 'Saúde & Ciência',
            'nicho': 'Saúde',
            'link': 'https://example.com/saude-descoberta',
            'data_insercao': datetime.now().isoformat(),
            'id': 'saude001'
        },
        {
            'titulo': 'Economia brasileira mostra sinais de recuperação',
            'resumo': 'Indicadores econômicos apontam para melhoria gradual com crescimento do PIB e redução do desemprego.',
            'fonte': 'Economia Brasil',
            'nicho': 'Economia',
            'link': 'https://example.com/economia-recuperacao',
            'data_insercao': datetime.now().isoformat(),
            'id': 'econ001'
        }
    ]

def gerar_html_site(noticias=None):
    """Gera HTML completo do site"""
    if not noticias:
        noticias = carregar_noticias_demo()
    
    # Estatísticas
    total_noticias = len(noticias)
    nichos_unicos = len(set(n.get('nicho', 'Geral') for n in noticias))
    fontes_unicas = len(set(n.get('fonte', 'Desconhecida') for n in noticias))
    
    # Data de última atualização
    data_atualizacao = datetime.now().strftime('%d/%m/%Y às %H:%M')
    
    html = f"""<!DOCTYPE html>
<html lang="{SITE_CONFIG['language']}" prefix="og: http://ogp.me/ns#">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{SITE_CONFIG['title']}</title>
    <meta name="description" content="{SITE_CONFIG['description']}">
    <meta name="author" content="{SITE_CONFIG['author']}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{SITE_CONFIG['url']}">
    <meta property="og:title" content="{SITE_CONFIG['title']}">
    <meta property="og:description" content="{SITE_CONFIG['description']}">
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="{SITE_CONFIG['url']}">
    <meta property="twitter:title" content="{SITE_CONFIG['title']}">
    <meta property="twitter:description" content="{SITE_CONFIG['description']}">
    
    <style>
        :root {{
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --text-color: #1f2937;
            --text-light: #6b7280;
            --bg-color: #ffffff;
            --bg-secondary: #f8fafc;
            --border-color: #e5e7eb;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.15);
            --border-radius: 8px;
            --border-radius-lg: 12px;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1rem;
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 2rem 0;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        /* Stats */
        .stats {{
            background: var(--bg-secondary);
            padding: 2rem 0;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-top: 1rem;
        }}
        
        .stat-card {{
            background: white;
            padding: 1.5rem;
            border-radius: var(--border-radius-lg);
            box-shadow: var(--shadow);
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }}
        
        .stat-label {{
            color: var(--text-light);
            font-size: 0.9rem;
        }}
        
        /* News Section */
        .news-section {{
            padding: 3rem 0;
        }}
        
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }}
        
        .news-card {{
            background: white;
            border-radius: var(--border-radius-lg);
            box-shadow: var(--shadow);
            overflow: hidden;
            transition: var(--transition);
        }}
        
        .news-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }}
        
        .news-header {{
            padding: 1.5rem;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .news-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            font-size: 0.85rem;
        }}
        
        .news-date {{
            color: var(--text-light);
        }}
        
        .news-category {{
            background: var(--primary-color);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        
        .news-title {{
            font-size: 1.25rem;
            font-weight: 600;
            line-height: 1.4;
        }}
        
        .news-title a {{
            color: var(--text-color);
            text-decoration: none;
        }}
        
        .news-title a:hover {{
            color: var(--primary-color);
        }}
        
        .news-content {{
            padding: 1.5rem;
        }}
        
        .news-summary {{
            color: var(--text-light);
            margin-bottom: 1.5rem;
            line-height: 1.6;
        }}
        
        .news-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .news-source {{
            font-size: 0.85rem;
            color: var(--text-light);
        }}
        
        .news-link {{
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.9rem;
        }}
        
        .news-link:hover {{
            text-decoration: underline;
        }}
        
        /* Footer */
        .footer {{
            background: var(--text-color);
            color: white;
            padding: 3rem 0 2rem;
            margin-top: 4rem;
        }}
        
        .footer-content {{
            text-align: center;
        }}
        
        .footer h3 {{
            margin-bottom: 1rem;
        }}
        
        .footer p {{
            margin-bottom: 2rem;
            opacity: 0.8;
        }}
        
        .footer-links {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        
        .footer-links a {{
            color: white;
            text-decoration: none;
            opacity: 0.8;
        }}
        
        .footer-links a:hover {{
            opacity: 1;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .news-grid {{
                grid-template-columns: 1fr;
            }}
            
            .footer-links {{
                flex-direction: column;
                gap: 1rem;
            }}
        }}
        
        /* Utility classes */
        .text-center {{
            text-align: center;
        }}
        
        .mb-2 {{
            margin-bottom: 2rem;
        }}
        
        .loading {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="container">
            <h1>🤖 {SITE_CONFIG['title']}</h1>
            <p>{SITE_CONFIG['description']}</p>
        </div>
    </header>

    <!-- Estatísticas -->
    <section class="stats">
        <div class="container">
            <h2 class="text-center mb-2">📊 Estatísticas do Sistema</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_noticias}</div>
                    <div class="stat-label">Notícias Agregadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{nichos_unicos}</div>
                    <div class="stat-label">Nichos Cobertos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{fontes_unicas}</div>
                    <div class="stat-label">Fontes Monitoradas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">24/7</div>
                    <div class="stat-label">Coleta Automática</div>
                </div>
            </div>
        </div>
    </section>

    <!-- Seção Principal de Notícias -->
    <main class="news-section">
        <div class="container">
            <h2 class="text-center mb-2">📰 Últimas Notícias</h2>
            <p class="text-center" style="color: var(--text-light); margin-bottom: 2rem;">
                Última atualização: {data_atualizacao}
            </p>
            
            <div class="news-grid">
"""
    
    # Gerar cards de notícias
    for noticia in noticias:
        titulo = noticia.get('titulo', 'Sem título')
        resumo = noticia.get('resumo', 'Resumo não disponível')
        fonte = noticia.get('fonte', 'Fonte Externa')
        nicho = noticia.get('nicho', 'Geral')
        link = noticia.get('link', '#')
        
        # Processar data
        data_pub = noticia.get('data_insercao', '')
        try:
            if isinstance(data_pub, str):
                data_obj = datetime.fromisoformat(data_pub.replace('Z', '+00:00'))
                data_str = data_obj.strftime('%d/%m/%Y %H:%M')
            else:
                data_str = str(data_pub)
        except:
            data_str = 'Data não disponível'
        
        # Hash único para cada notícia
        noticia_id = hashlib.md5(titulo.encode()).hexdigest()[:8]
        
        html += f"""
                <article class="news-card" id="news-{noticia_id}">
                    <div class="news-header">
                        <div class="news-meta">
                            <time class="news-date" datetime="{data_pub}">{data_str}</time>
                            <span class="news-category">{nicho}</span>
                        </div>
                        <h3 class="news-title">
                            <a href="{link}" target="_blank" rel="noopener noreferrer" title="{titulo}">
                                {titulo}
                            </a>
                        </h3>
                    </div>
                    <div class="news-content">
                        <p class="news-summary">{resumo}</p>
                        <div class="news-footer">
                            <span class="news-source">📡 {fonte}</span>
                            <a href="{link}" class="news-link" target="_blank" rel="noopener noreferrer">
                                Ler mais
                            </a>
                        </div>
                    </div>
                </article>"""
    
    # Finalizar HTML
    html += """
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <h3>🤖 DJBlog - Sistema Automatizado</h3>
                <p>Agregação inteligente de notícias com tecnologia de ponta.<br>
                   Conteúdo atualizado automaticamente, sem intervenção humana.</p>
                
                <div class="footer-links">
                    <a href="#tecnologia">Tecnologia</a>
                    <a href="#saude">Saúde</a>
                    <a href="#economia">Economia</a>
                    <a href="#esportes">Esportes</a>
                </div>
                
                <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.2);">
                    <p style="opacity: 0.6; font-size: 0.9rem;">
                        © 2025 DJBlog System | Gerado automaticamente | 
                        <a href="https://github.com/jucabronks/projeto-djblog" target="_blank" style="color: #60a5fa;">
                            Código no GitHub
                        </a>
                    </p>
                </div>
            </div>
        </div>
    </footer>

    <script>
        // Analytics simples
        console.log('DJBlog loaded successfully');
        
        // Marcar tempo de carregamento
        window.addEventListener('load', function() {
            const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
            console.log('Load time:', loadTime + 'ms');
        });
        
        // Smooth scroll para links internos
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    </script>
</body>
</html>"""
    
    return html

def main():
    """Função principal"""
    try:
        print("🚀 Gerando site estático responsivo...")
        
        # Tentar carregar notícias reais, usar demo como fallback
        noticias = None
        try:
            # Aqui tentaria carregar notícias do DynamoDB
            # Por enquanto, usar sempre demo
            pass
        except:
            pass
        
        if not noticias:
            print("📝 Usando notícias demo...")
            noticias = carregar_noticias_demo()
        
        # Gerar HTML
        html_content = gerar_html_site(noticias)
        
        # Salvar arquivo
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ Site gerado com sucesso!")
        print(f"📊 Total de notícias: {len(noticias)}")
        print(f"📁 Arquivo: index.html ({len(html_content)} caracteres)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar site: {e}")
        return False

if __name__ == "__main__":
    main()
