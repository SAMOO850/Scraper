✨ Prospekt Scraper

🔍 Popis projektu

Tento projekt je web scraper, ktorý automaticky zbiera letáky z webovej stránky Prospektmaschine. Používa knižnice BeautifulSoup a requests na extrakciu a spracovanie údajov, ktoré sú uložené v JSON formáte.

📚 Použité technológie

Python 3

BeautifulSoup (na parsovanie HTML)

Requests (na sťahovanie obsahu webu)

JSON (na ukladanie extrahovaných údajov)

Regex (na spracovanie dátumov)

⚡ Inštalácia

Ak chceš použiť tento scraper, uisti sa, že máš nainštalovaný Python 3 a potrebné knižnice. Ak ich nemáš, nainštaluj ich pomocou:

pip install beautifulsoup4 requests python-dateutil

🔄 Ako spustiť scraper?

Naklonuj si repozitár alebo si stiahni súbor so skriptom.

Spusti Python skript:

python scraper.py

Po dokončení sa letáky uložia do súboru letaky.json.

📝 Štruktúra JSON výstupu

Každý leták bude mať nasledujúci formát:

[
  {
    "title": "Názov letáka",
    "thumbnail": "URL na náhľad",
    "shop_name": "Názov obchodu",
    "valid_from": "2025-03-17",
    "valid_to": "2025-03-22",
    "parsed_time": "2025-03-16 14:30:00"
  }
]

✨ Funkcionality

✅ Automatické prehľadanie obchodov na Prospektmaschine

✅ Extrakcia platných letákov

✅ Rozpoznanie dátumu platnosti

✅ Ukladanie výstupu do JSON formátu

🔧 Možné vylepšenia

Pridanie podpory pre ďalšie webové stránky

Export do iných formátov (CSV, PDF)

Automatizované spúšťanie cez crontab

© Licencia

Tento projekt je licencovaný pod MIT licenciou, takže ho môžeš používať, upravovať a šíriť.

📬 Ak máš otázky alebo chceš prispieť, neváhaj ma kontaktovať! ✨
