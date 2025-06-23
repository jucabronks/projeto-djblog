"""
Módulo para resumir textos usando a API do OpenAI (ChatGPT).

Como usar:
1. Instale a biblioteca openai:
   pip install openai
2. Obtenha uma chave de API em https://platform.openai.com/api-keys
3. Use a função resumir_com_ia(texto, api_key)

Exemplo:
from summarize_ai import resumir_com_ia
resumo = resumir_com_ia("Seu texto aqui", "SUA_CHAVE_OPENAI")
print(resumo)
"""

import openai
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def resumir_com_ia(texto, api_key):
    """Resume texto usando OpenAI GPT-3.5-turbo"""
    try:
        client = openai.OpenAI(api_key=api_key)
        prompt = f"Resuma o texto a seguir em 3 frases objetivas e curtas:\n\n{texto}"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Erro ao resumir com IA: {e}")
        return texto[:200] + ("..." if len(texto) > 200 else "")

def traduzir_com_ia(texto, api_key, idioma_destino):
    """Traduz texto usando OpenAI GPT-3.5-turbo"""
    try:
        client = openai.OpenAI(api_key=api_key)
        prompt = f"Traduza o texto a seguir para o idioma {idioma_destino} de forma natural e jornalística, mantendo o sentido original.\n\nTexto:\n{texto}"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Erro ao traduzir com IA: {e}")
        return texto

def resumir_texto(texto):
    """Resume texto de forma simples (fallback)"""
    try:
        return texto[:200] + ("..." if len(texto) > 200 else "")
    except Exception as e:
        logger.error(f"Erro ao resumir texto: {e}")
        return texto

# Exemplo de uso
if __name__ == "__main__":
    texto = "O ChatGPT é um modelo de linguagem natural desenvolvido pela OpenAI. Ele pode responder perguntas, gerar textos e ajudar em tarefas de automação. Sua aplicação é ampla em diversos setores."
    api_key = "SUA_CHAVE_OPENAI"
    # print(resumir_com_ia(texto, api_key))  # Descomente após inserir sua chave 