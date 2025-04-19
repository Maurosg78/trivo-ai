import json
import requests

url = 'http://localhost:8081/api/generate-recipe'
payload = {'user_text': 'quiero una pizza napolitana con mucho queso'}
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        data = response.json()
        print('Receta generada con éxito!')
        print(f'Nombre: {data["recipe"]["nombre"]}')
        print(f'Descripción: {data["recipe"]["descripcion"]}')
        print('\nIngredientes:')
        for ing in data["recipe"]["ingredientes"]:
            print(f'- {ing["name"]}: {ing["amount"]} {ing["unit"]}')
        print('\nMétodo de preparación:')
        for i, paso in enumerate(data["recipe"]["metodo"]):
            print(f'{i+1}. {paso}')
        print('\nConsejo profesional:')
        print(data["key_tip"])
    else:
        print(f'Error: {response.status_code}')
        print(response.text)
except Exception as e:
    print(f'Error: {e}') 