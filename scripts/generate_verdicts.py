#!/usr/bin/env python3
import json
import os
import sys
from openai import OpenAI

# O Manus pré-configura a OpenAI com a API Key e Base URL corretas
client = OpenAI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERDICTS_PATH = os.path.join(BASE_DIR, "data", "product_verdicts.json")

def load_verdicts():
    if os.path.exists(VERDICTS_PATH):
        with open(VERDICTS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_verdicts(verdicts):
    with open(VERDICTS_PATH, "w", encoding="utf-8") as f:
        json.dump(verdicts, f, indent=2, ensure_ascii=False)

def generate_verdict(product_title):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é um especialista em curadoria de ofertas. Escreva um parágrafo curto (máximo 250 caracteres) em português sobre por que este produto é uma boa compra ou o que o destaca. Seja direto e use um tom editorial profissional."},
                {"role": "user", "content": f"Produto: {product_title}"}
            ],
            max_tokens=100
        )
        # O Manus usa a versão mais recente da biblioteca OpenAI (Pydantic models)
        if hasattr(response.choices[0].message, 'content'):
            return response.choices[0].message.content.strip()
        return None
    except Exception as e:
        print(f"Erro ao gerar veredito: {e}")
        return None

def main():
    scored_path = os.path.join(BASE_DIR, "data", "scored_products.json")
    if not os.path.exists(scored_path):
        return

    with open(scored_path, encoding="utf-8") as f:
        products = json.load(f)

    verdicts = load_verdicts()
    updated = False

    # Gerar veredito apenas para os 5 melhores produtos que ainda não possuem
    count = 0
    for p in products[:20]: # Focar nos top 20
        pid = p.get("id")
        if pid and pid not in verdicts:
            print(f"Gerando veredito para: {p.get('title')}")
            verdict = generate_verdict(p.get('title'))
            if verdict:
                verdicts[pid] = verdict
                updated = True
                count += 1
            if count >= 5: break # Limite por execução para economizar créditos e tempo

    if updated:
        save_verdicts(verdicts)
        print(f"Foram gerados {count} novos vereditos.")

if __name__ == "__main__":
    main()
