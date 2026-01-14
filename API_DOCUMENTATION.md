# API Dokumentácia - Detailné Vysvetlenie Cvikov

## Authentifikácia
Všetky POST, PUT a DELETE requesty vyžadujú admin session. Musíš sa prihlásiť cez `/admin-login` a vaša session bude obsahovať admin token.

## Endpoints

### 1. GET - Získaj detailné vysvetlenie
```
GET /api/exercise/<exercise_id>/detailed-explanation
```

**Príklad:**
```bash
curl http://localhost:5000/api/exercise/1/detailed-explanation
```

**Odpoveď (200):**
```json
{
  "exercise_id": 1,
  "exercise_name": "Bench Press",
  "detailed_explanation": [
    {
      "type": "text",
      "content": "<h2>Postup</h2><p>Ložíš sa na lavicu...</p>"
    },
    {
      "type": "image",
      "content": "20260114_120000_image.jpg",
      "caption": "Správna pozícia"
    },
    {
      "type": "video",
      "content": "https://www.youtube.com/watch?v=xxxxx"
    }
  ]
}
```

---

### 2. POST - Pridaj obsah
```
POST /api/exercise/<exercise_id>/detailed-explanation
Content-Type: application/json
```

**Typ: Text (HTML)**
```bash
curl -X POST http://localhost:5000/api/exercise/1/detailed-explanation \
  -H "Content-Type: application/json" \
  -d '{
    "type": "text",
    "content": "<h2>Nadpis</h2><p>Tvoj obsah tu...</p>"
  }'
```

**Typ: Obrázok**
```bash
curl -X POST http://localhost:5000/api/exercise/1/detailed-explanation \
  -H "Content-Type: application/json" \
  -d '{
    "type": "image",
    "content": "20260114_120000_image.jpg",
    "caption": "Popis obrázka"
  }'
```

**Typ: Video**
```bash
curl -X POST http://localhost:5000/api/exercise/1/detailed-explanation \
  -H "Content-Type: application/json" \
  -d '{
    "type": "video",
    "content": "https://www.youtube.com/watch?v=xxxxx"
  }'
```

**Odpoveď (201):**
```json
{
  "success": true,
  "message": "Content added",
  "item_index": 2
}
```

---

### 3. PUT - Uprav obsah
```
PUT /api/exercise/<exercise_id>/detailed-explanation/<item_index>
Content-Type: application/json
```

**Príklad:**
```bash
curl -X PUT http://localhost:5000/api/exercise/1/detailed-explanation/0 \
  -H "Content-Type: application/json" \
  -d '{
    "content": "<h2>Nový obsah</h2><p>Upravený text...</p>"
  }'
```

**Odpoveď (200):**
```json
{
  "success": true,
  "message": "Content updated",
  "item": {
    "type": "text",
    "content": "<h2>Nový obsah</h2><p>Upravený text...</p>"
  }
}
```

---

### 4. DELETE - Vymaž obsah
```
DELETE /api/exercise/<exercise_id>/detailed-explanation/<item_index>
```

**Príklad:**
```bash
curl -X DELETE http://localhost:5000/api/exercise/1/detailed-explanation/0
```

**Odpoveď (200):**
```json
{
  "success": true,
  "message": "Content deleted"
}
```

---

## Chybové odpovede

**401 Unauthorized** - Nie si prihlásený ako admin
```json
{"error": "Unauthorized"}
```

**404 Not Found** - Cvik neexistuje
```json
{"error": "Exercise not found"}
```

**400 Bad Request** - Chýbajúce alebo neplatné dáta
```json
{"error": "Invalid item index"}
```

---

## Príklady v Pythone

### Čítanie detailného vysvetlenia
```python
import requests

response = requests.get('http://localhost:5000/api/exercise/1/detailed-explanation')
data = response.json()

for item in data['detailed_explanation']:
    print(f"Typ: {item['type']}")
    print(f"Obsah: {item['content'][:50]}...")
```

### Pridávanie textu
```python
import requests

payload = {
    'type': 'text',
    'content': '<h2>Postup</h2><p>Ložíš sa na lavicu...</p>'
}

response = requests.post(
    'http://localhost:5000/api/exercise/1/detailed-explanation',
    json=payload,
    cookies={'session': your_session_cookie}
)

print(response.json())
```

### Úprava obsahu
```python
import requests

payload = {
    'content': '<h2>Nový nadpis</h2><p>Nový obsah</p>'
}

response = requests.put(
    'http://localhost:5000/api/exercise/1/detailed-explanation/0',
    json=payload,
    cookies={'session': your_session_cookie}
)

print(response.json())
```

### Mazanie obsahu
```python
import requests

response = requests.delete(
    'http://localhost:5000/api/exercise/1/detailed-explanation/0',
    cookies={'session': your_session_cookie}
)

print(response.json())
```

---

## Typy obsahu

| Typ | Povinné polia | Voliteľné polia | Príklad |
|-----|---|---|---|
| text | type, content | - | HTML formátovaný text |
| image | type, content | caption | filename obrázka + popis |
| video | type, content | - | YouTube URL |

---

## Poznámky
- Všetky dáta sú uložené v `exercises.json`
- Obrázky musia byť už uploadované (cez formulár alebo TinyMCE editor)
- HTML obsah je podporovaný - môžeš vkladať formátovanie
- Session cookies sú povinné pre zmeny (POST, PUT, DELETE)
