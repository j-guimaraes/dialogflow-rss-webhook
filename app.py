import json
from flask import Flask, request, jsonify
import feedparser
import requests
from datetime import datetime

app = Flask(__name__)

# Feeds para RSS (exemplo, carrega do JSON se quiseres)
feeds = {
    "exemplo": {
        "url": "https://news.google.com/rss/search?q=kiwi",
        "descricao": "Notícias recentes sobre kiwis"
    }
}

# Dados das empresas para o webhook "empresas"
empresas_info = {
    "zespri": {
        "summary": "Zespri é a maior exportadora mundial de kiwis, com sede na Nova Zelândia.",
        "localizacao": "Te Puke, Nova Zelândia",
        "contactos": "Telefone: +64 7 573 2000 | Website: https://www.zespri.com"
    },
    "associacao portuguesa de kiwicultores": {
        "summary": "Associação que representa os produtores portugueses de kiwi.",
        "localizacao": "Portugal",
        "contactos": "Email: info@apkiwi.pt | Website: https://www.apkiwi.pt"
    },
    "kiwi vine health": {
        "summary": "Organização dedicada à saúde e pesquisa da vinha de kiwi na Nova Zelândia.",
        "localizacao": "Te Puke, Nova Zelândia",
        "contactos": "Website: https://www.kiwivinehealth.org.nz"
    }
}

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    
    # Pega a intenção (intent) e parâmetros do Dialogflow
    intent = req.get("queryResult", {}).get("intent", {}).get("displayName")
    parametros = req.get("queryResult", {}).get("parameters", {})
    
    # Se for pedido de notícias via parâmetro "fonte"
    if "fonte" in parametros:
        fonte = parametros.get("fonte")
        if fonte not in feeds:
            return jsonify({"fulfillmentText": "Fonte não reconhecida. Tenta perguntar por outra fonte de informação."})

        feed_info = feeds[fonte]

        try:
            resp = requests.get(feed_info["url"], timeout=3)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
        except requests.exceptions.Timeout:
            return jsonify({"fulfillmentText": "O sistema está um pouco lento agora. Por favor, tenta outra vez daqui a pouco."})
        except Exception:
            return jsonify({"fulfillmentText": "Desculpa, ocorreu um erro ao buscar as informações. Tenta novamente mais tarde."})
        
        itens = feed.entries[:3]
        if not itens:
            resposta = f"Não encontrei atualizações em: {feed_info['descricao']}."
        else:
            lista = []
            for item in itens:
                data_str = "Data desconhecida"
                if 'published_parsed' in item and item.published_parsed:
                    try:
                        dt = datetime(*item.published_parsed[:6])
                        data_str = dt.strftime('%d/%m/%Y')
                    except:
                        pass
                lista.append(f"🔹 <a href='{item.link}'>{item.title}</a> (Artigo do dia: {data_str})")
            resposta = f"{feed_info['descricao']}:\n" + "\n".join(lista)
        return jsonify({"fulfillmentText": resposta, "payload": {"telegram": {"text": resposta, "parse_mode": "HTML"}}})
    
    # Se for pergunta sobre empresa (intents específicas ou parâmetro "empresa")
    empresa = parametros.get("empresa")
    if empresa:
        empresa = empresa.lower()
        if empresa in empresas_info:
            info = empresas_info[empresa]
            texto = (f"📌 <b>{empresa.title()}</b>\n\n"
                     f"{info['summary']}\n"
                     f"📍 Localização: {info['localizacao']}\n"
                     f"📞 Contactos: {info['contactos']}")
            return jsonify({"fulfillmentText": texto, "payload": {"telegram": {"text": texto, "parse_mode": "HTML"}}})
        else:
            return jsonify({"fulfillmentText": "Desculpa, não tenho informações sobre essa empresa."})

    # Resposta padrão
    return jsonify({"fulfillmentText": "Desculpa, não entendi. Podes reformular?"})

if __name__ == '__main__':
    app.run()


