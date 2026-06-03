import requests
import json

def test_api():
    url = "https://api.mercadolivre.com/sites/MLB/search?q=smartphone&limit=5"
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"Produtos encontrados: {len(results)}")
            for p in results:
                print(f"- {p.get('title')} (R$ {p.get('price')})")
        else:
            print(f"Erro na API: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    test_api()
