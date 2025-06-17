import json
from flask import Flask, request, jsonify
import feedparser
import requests
from datetime import datetime
import html

app = Flask(__name__)

# Carrega feeds de um ficheiro externo
with open("feeds.json", "r", encoding="utf-8") as f:
    feeds = json.load(f)

def escape_markdown(text):
    # Escapa os caracteres especiais para MarkdownV2 (Telegram)
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + c if c in escape_chars else c for c in text])

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    fonte = req.get("queryResult", {}).get("parameters", {}).get("fonte")
    
    if fonte not in feeds:
        return jsonify({
            "fulfillmentText": "❌ Fonte não reconhecida. Tenta perguntar por outra fonte de informação."
        })
    
    feed_info = feeds[fonte]
    
    try:
        resp = requests.get(feed_info["url"], timeout=3)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
    except requests.exceptions.Timeout:
        return jsonify({
            "fulfillmentText": "⏰ O sistema está um pouco lento agora\\. Por favor, tenta outra vez daqui a pouco\\."
        })
    except Exception as e:
        return jsonify({
            "fulfillmentText": "❌ Desculpa, ocorreu um erro ao buscar as informações\\. Tenta novamente mais tarde\\."
        })
    
    itens = feed.entries[:3]
    
    if not itens:
        resposta = f"📭 Não encontrei atualizações recentes em:\n*{escape_markdown(feed_info['descricao'])}*"
    else:
        lista = []
        for i, item in enumerate(itens, 1):
            data_str = "Data desconhecida"
            if 'published_parsed' in item and item.published_parsed:
                try:
                    dt = datetime(*item.published_parsed[:6])
                    data_str = dt.strftime('%d/%m/%Y às %H:%M')
                except Exception:
                    pass
            elif 'updated_parsed' in item and item.updated_parsed:
                try:
                    dt = datetime(*item.updated_parsed[:6])
                    data_str = dt.strftime('%d/%m/%Y às %H:%M')
                except Exception:
                    pass
            
            titulo = escape_markdown(item.title)
            link = item.link
            
            # Layout melhorado para cada notícia
            linha = f"📰 *{i}\\.*  [{titulo}]({link})\n⏰ {escape_markdown(data_str)}"
            lista.append(linha)
        
        # Cabeçalho melhorado com separador visual
        cabecalho = f"🗞️ *{escape_markdown(feed_info['descricao'])}*\n{'─' * 30}"
        resposta = f"{cabecalho}\n\n" + "\n\n".join(lista)
        
        # Rodapé com informação adicional
        resposta += f"\n\n📊 A mostrar as {len(itens)} notícias mais recentes"
    
    return jsonify({
        "fulfillmentText": resposta,
        "payload": {
            "telegram": {
                "text": resposta,
                "parse_mode": "MarkdownV2"
            }
        }
    })

if __name__ == '__main__':
    app.run()
