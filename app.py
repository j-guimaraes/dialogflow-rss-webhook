import json
from flask import Flask, request, jsonify
import feedparser

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
    feed = feedparser.parse(feed_info["url"])
    itens = feed.entries[:3]

    if not itens:
        resposta = f"Não encontrei atualizações em: {feed_info['descricao']}."
    else:
        lista = "\n".join([f"- {item.title}: {item.link}" for item in itens])
        resposta = f"{feed_info['descricao']}:\n{lista}"

    return jsonify({"fulfillmentText": resposta})

if __name__ == '__main__':
    app.run()

