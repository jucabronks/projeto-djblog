import json
from utils import buscar_noticias_resumidas

def lambda_handler(event, context):
    noticias = buscar_noticias_resumidas()
    publicadas = [n for n in noticias if n.get('publicado')]
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(publicadas)
    } 