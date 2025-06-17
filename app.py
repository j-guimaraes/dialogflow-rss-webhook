import json
from flask import Flask, request, jsonify
import feedparser
import requests

app = Flask(__name__)

# Carrega feeds de um ficheiro externo
with open("feeds.json", "r", encoding="utf-8") as f:
    feeds = json.load(f)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    fonte = req.get("queryResult", {}).get("parameters", {}).get("fonte")

    if fonte not in feeds:
        return jsonify({
            "fulfillmentText": "Fonte não reconhecida. Tenta perguntar por outra fonte de informação."
        })

    feed_info = feeds[fonte]
    
    try:
        resp = requests.get(feed_info["url"], timeout=3)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
    except requests.exceptions.Timeout:
        return jsonify({
            "fulfillmentText": "O sistema está um pouco lento agora. Por favor, tenta outra vez daqui a pouco."
        })
    except Exception as e:
        return jsonify({
            "fulfillmentText": "Desculpa, ocorreu um erro ao buscar as informações. Tenta novamente mais tarde."
        })
        
    itens = feed.entries[:3]

    if not itens:
        resposta = f"Não encontrei atualizações em: {feed_info['descricao']}."
    else:
        lista = []
        for item in itens:
            if hasattr(item, 'published'):
                try:
                    dt = datetime(*item.published_parsed[:6])
                    data_str = dt.strftime('%d/%m/%Y')
                except Exception:
                    data_str = "Data desconhecida"
            else:
                data_str = "Data desconhecida"
            lista.append(f"- {item.title} (Artigo do dia: {data_str}): {item.link}")
        resposta = f"{feed_info['descricao']}:\n" + "\n".join(lista)

    return jsonify({"fulfillmentText": resposta})

if __name__ == '__main__':
    app.run()

