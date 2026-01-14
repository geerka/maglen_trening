# Vzpieračské Cviky - Flask Aplikácia

Krásna a intuitívna webová aplikácia na správu vzpieračských cvikov s videami a opismi.

## Funkcie

✅ Pridávanie nových cvikov  
✅ Editácia existujúcich cvikov  
✅ Mazanie cvikov  
✅ Nahrávanie vlastných videí (MP4)  
✅ Integrácia s YouTube videami  
✅ Filtrovanie podľa svalových skupín a ťažkosti  
✅ Responzívny dizajn  
✅ Moderný tmavý dizajn

## Inštalácia

1. **Klon/Unzip projektu**
```bash
cd stranka
```

2. **Vytvor virtuálne prostredie** (voliteľné, ale odporúčané)
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Nainštaluj závislosti**
```bash
pip install -r requirements.txt
```

## Spustenie aplikácie

```bash
python app.py
```

Aplikácia bude dostupná na: **http://localhost:5000**

## Štruktúra projektu

```
stranka/
├── app.py                  # Hlavná Flask aplikácia
├── requirements.txt        # Python závislosti
├── exercises.json         # Databáza cvikov (vytvorí sa automaticky)
├── uploads/
│   └── videos/           # Priečinok pre nahraté videá
└── templates/
    ├── index.html         # Hlavná stránka so zoznamom cvikov
    ├── add_exercise.html  # Formulár na pridanie cviku
    ├── edit_exercise.html # Formulár na úpravu cviku
    └── view_exercise.html # Detail cviku
```

## Ako používať

### Pridanie cviku
1. Klikni na **"+ Pridať nový cvik"**
2. Vyplň podrobnosti cviku:
   - Názov
   - Svalová skupina
   - Úroveň ťažkosti
   - Popis
3. Vyber video (nahrané alebo YouTube URL)
4. Klikni **"Pridať cvik"**

### Prehliadanie cviku
- Klikni na kartu cviku alebo **"Zobraziť"** na podrobný pohľad

### Úprava cviku
- Klikni **"Upraviť"** na karte cviku

### Vymazanie cviku
- Klikni **"Vymazať"** na karte cviku

## Podporované svalové skupiny

- 💪 Hrudník
- 🔙 Chrbát
- 💪 Ramená
- 💪 Bicepsy
- 💪 Tricepsy
- 🦵 Nohy
- 🫀 Brucho
- 🙌 Predlaktie

## Úrovne ťažkosti

- 🟢 Začiatočník
- 🟡 Pokročilý
- 🔴 Expert

## Video formáty

- **Vlastné videá**: MP4 (max. 500 MB)
- **YouTube**: Vložiť URL ako `https://www.youtube.com/watch?v=xxxxx`

## Technológie

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3
- **Ukladanie**: JSON súbor
- **Video**: HTML5 Video + YouTube iFrame

## Poznámky

- Cviky sú ukladané v `exercises.json`
- Nahrané videá sú ukladané v `uploads/videos/`
- Aplikácia je optimalizovaná pre mobilné zariadenia
- Všetky dáta sú ukladané lokálne

## Licencia

Voľne dostupný projekt.
