import os
import boto3
from datetime import datetime, timedelta, timezone
from boto3.dynamodb.conditions import Key, Attr

# Configurações
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "djblog-noticias")
HTML_FILE = "index.html"
BRT = timezone(timedelta(hours=-3))  # Horário de Brasília

# Lógica de datas conforme regra do usuário
# Segunda: publica sexta, sábado, domingo
# Terça: publica segunda
# Quarta: publica terça
# Quinta: publica quarta
# Sexta: publica quinta
# Sábado e domingo: não publica


def get_periodo_publicacao(hoje=None):
    if hoje is None:
        hoje = datetime.now(BRT)
    return [(hoje - timedelta(days=1)).date()]


def buscar_noticias(datas):
    if not datas:
        return []
    
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    
    noticias = []
    for data in datas:
        inicio = datetime.combine(
            data,
            datetime.min.time(),
            tzinfo=BRT).astimezone(
            timezone.utc)
        fim = datetime.combine(
            data,
            datetime.max.time(),
            tzinfo=BRT).astimezone(
            timezone.utc)
        
        # Scan da tabela com filtro por data
        response = table.scan(
            FilterExpression=Attr('data_insercao').between(
                inicio.isoformat(),
                fim.isoformat()
            )
        )
        
        # Ordena por data de inserção (decrescente)
        items = sorted(response.get('Items', []), 
                      key=lambda x: x.get('data_insercao', ''), 
                      reverse=True)
        noticias.extend(items)
    
    return noticias


def gerar_html(noticias, datas):
    html = f"""
<!DOCTYPE html>
<html lang='pt-br'>
<head>
    <meta charset='UTF-8'>
    <title>Notícias Publicadas</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <meta name='description' content='Notícias automáticas, atualizadas e selecionadas.'>
    <!-- AdSense: Cole o código do anúncio aqui -->
    <!-- <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script> -->
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; background: #f9f9f9; }}
        .container {{ max-width: 800px; margin: 2em auto; background: #fff; padding: 2em; border-radius: 10px; box-shadow: 0 2px 16px #0002; }}
        .noticia {{ margin-bottom: 2em; padding-bottom: 1em; border-bottom: 1px solid #eee; }}
        .data {{ color: #888; font-size: 0.9em; margin-bottom: 0.2em; }}
        .titulo {{ font-size: 1.3em; margin-bottom: 0.2em; }}
        .fonte {{ font-size: 0.95em; color: #555; margin-bottom: 0.5em; }}
        .resumo {{ margin-bottom: 0.5em; }}
        .link {{ color: #1a0dab; text-decoration: none; }}
        @media (max-width: 600px) {{ .container {{ padding: 1em; }} }}
        .adsense, .afiliado {{ margin: 2em 0; text-align: center; }}
    </style>
</head>
<body>
    <div class='container'>
        <h1>Notícias publicadas</h1>
        <p>Período: {', '.join([d.strftime('%d/%m/%Y') for d in datas])}</p>
        <!-- Espaço para AdSense ou banner de afiliados -->
        <div class="adsense"><!-- Cole o bloco de anúncio aqui --></div>
        <hr/>
"""
    if not noticias:
        html += "<p><b>Nenhuma notícia encontrada para o período selecionado.</b></p>"
    else:
        for n in noticias:
            data_pub = n.get("data_insercao")
            if isinstance(data_pub, datetime):
                # Converter UTC para BRT para exibir
                data_str = data_pub.astimezone(BRT).strftime('%d/%m/%Y %H:%M')
            else:
                data_str = str(data_pub)
            html += f"""
        <div class='noticia'>
            <div class='data'>{data_str}</div>
            <div class='titulo'>{n.get('titulo', 'Sem título')}</div>
            <div class='fonte'>Fonte: {n.get('fonte', 'Desconhecida')} | Nicho: {n.get('nicho', 'N/A')}</div>
            <div class='resumo'>{n.get('resumo', '')}</div>
            <a class='link' href='{n.get('link', '#')}' target='_blank'>Ler notícia completa</a>
            <!-- Exemplo de link de afiliado:
            <div class='afiliado'><a href='SEU_LINK_AFILIADO' target='_blank'>Compre relacionado a esta notícia</a></div>
            -->
        </div>
        """
    html += """
        <hr/>
        <footer style='text-align:center; color:#aaa; font-size:0.9em;'>
            &copy; {datetime.now().year} - Gerado automaticamente
        </footer>
    </div>
</body>
</html>
"""
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Arquivo {HTML_FILE} gerado com {len(noticias)} notícias.")


def main():
    datas = get_periodo_publicacao()
    if not datas:
        print("Hoje não é dia de publicação. Nada será gerado.")
        return
    noticias = buscar_noticias(datas)
    gerar_html(noticias, datas)


if __name__ == "__main__":
    main()
