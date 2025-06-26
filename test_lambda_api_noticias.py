from lambda_api_noticias import lambda_handler

# Simulando um evento e contexto vazios (como a AWS faz)
event = {}
context = None

response = lambda_handler(event, context)
print(response) 