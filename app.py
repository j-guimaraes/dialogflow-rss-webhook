from flask import Flask, request, jsonify
import feedparser

app = Flask(__name__)

# Dicionário de fontes
feeds = {
    "polinizacao": {
        "url": "https://news.google.com/news/rss/search?q=kiwifruit%20pollination&hl=en",
        "descricao": "Notícias recentes sobre polinização de kiwis"
    },
    "zespri": {
        "url": "https://rss.app/feeds/waxKIY1WgCjtxLEs.xml",
        "descricao": "Atualizações do Kiwiflier da Zespri"
    },
    "apkiwi": {
        "url": "https://morss.it/:clip:items=%7C%7C*%5Bclass=fs-1%5D/https://www.comunicamaiskiwi.apk.com.pt/artigos",
        "descricao": "Novos artigos dos APKiwicultores"
    },
    "canopy": {
        "url": "https://www.google.com/alerts/feeds/15846699374716510861/18443315587638399243",
        "descricao": "Novos documentos publicados no Zespri Canopy"
    },
    "bioseguranca": {
        "url": "https://www.google.com/alerts/feeds/15846699374716510861/15614409539590136616",
        "descricao": "Novidades da Kiwi Vine Health sobre biosegurança do kiwi"
    },
    "kiwiko": {
        "url": "https://rss.app/feeds/sFMbornI2qY1K91A.xml",
        "descricao": "Novos posts da Kiwiko sobre desenvolvimento de variedades de kiwi"
    }
}

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
