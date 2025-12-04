


## Projektbeschreibung
Ein einfaches MCP-basiertes Tool, um Produkte per REST-API abzurufen. Integriert in die Gemini CLI.

## Setup

1. Python installieren (mind. 3.9)
2. Virtuelle Umgebung erstellen (optional)
3. Abhängigkeiten installieren:
```
pip install -r requirements.txt
```

4. Server starten:
```
python main.py
```

5. Gemini CLI starten und mit Prompts testen:
- "Show me more products"
- "Filter by Triangle"
- "Only available products"

## Hinweise
- `limit` ist auf 10 festgelegt und nicht änderbar.
- Nur `page` und `filter` sind als Parameter verfügbar.
