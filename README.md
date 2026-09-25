# BiletFinder

TCDD e-bilet sitesindeki **ekonomi (Y1)** koltuklarını sürekli kontrol eder. Boş yer çıkınca **Telegram**’a mesaj atar.

Script bilgisayarda çalışır; telefon sadece bildirim almak içindir.

---

## 1. Bilgisayara kurulum

Python 3 lazım. Sonra proje klasöründe:

```bash
pip install requests curl_cffi
```

Windows’ta Python yolu farklıysa:

```bash
python -m pip install requests curl_cffi
```

---

## 2. Telegram (telefonda)

### Bot oluştur

1. Telegram’da **@BotFather**’ı aç.
2. `/newbot` yaz.
3. Bota bir isim ve kullanıcı adı ver (kullanıcı adı `...bot` ile bitmeli).
4. BotFather sana bir **token** verir. Örnek: `123456:ABC-DEF...`
5. Bu değeri `tcdd_monitor.py` içindeki `TELEGRAM_BOT_TOKEN` satırına yapıştır.

### Chat ID al

1. Az önce oluşturduğun bota Telegram’dan **Start** / **Başlat** de (en az bir mesaj at).
2. Telefondan şu adresi aç (TOKEN yerine bot token’ını yaz):

   `https://api.telegram.org/botTOKEN/getUpdates`

3. Açılan metinde `"chat":{"id": 123456789` gibi bir sayı görürsün. Bu **chat id**.
4. Bu sayıyı `TELEGRAM_CHAT_ID` satırına yaz.

Bot sana mesaj atamazsa genelde sebep: bota hiç `/start` atılmamış olmasıdır.

Telegram’ın çalıştığını denemek için:

```bash
python tcdd_monitor.py --test-notify
```

Telefona test mesajı gelmeli.

---

## 3. Kodda değiştirilecek yerler

Hepsi dosyanın en üstündeki **CONFIG** bloğunda:

```python
TELEGRAM_BOT_TOKEN = "..."          # BotFather token
TELEGRAM_CHAT_ID = "..."            # kendi chat id'n

DEPARTURE_STATION_ID = 1325
DEPARTURE_STATION_NAME = "İSTANBUL(SÖĞÜTLÜÇEŞME)"
ARRIVAL_STATION_ID = 98
ARRIVAL_STATION_NAME = "ANKARA GAR"

DEPARTURE_DATE = "09-09-2026 00:00:00"   # GG-AA-YYYY SS:DD:SS

POLL_INTERVAL_SECONDS = 5                 # kaç saniyede bir tarasın
MAX_NOTIFICATIONS_PER_WINDOW = 2          # aynı sefer doluyken max kaç mesaj
SEND_STARTUP_TELEGRAM = True              # başlarken "Arama başladı" mesajı
```

`BEARER_TOKEN` satırını normalde elleme. TCDD misafir token’ı dosyada duruyor. 401/403 alırsan script yeni token ister.

### Rota değiştirmek

İsim ve ID birlikte değişmeli. Bilinen istasyonlar:

| İstasyon | ID |
|----------|----|
| ANKARA GAR | 98 |
| İSTANBUL(SÖĞÜTLÜÇEŞME) | 1325 |

**İstanbul → Ankara**

```python
DEPARTURE_STATION_ID = 1325
DEPARTURE_STATION_NAME = "İSTANBUL(SÖĞÜTLÜÇEŞME)"
ARRIVAL_STATION_ID = 98
ARRIVAL_STATION_NAME = "ANKARA GAR"
```

**Ankara → İstanbul**

```python
DEPARTURE_STATION_ID = 98
DEPARTURE_STATION_NAME = "ANKARA GAR"
ARRIVAL_STATION_ID = 1325
ARRIVAL_STATION_NAME = "İSTANBUL(SÖĞÜTLÜÇEŞME)"
```

### Tarih

Format: `GG-AA-YYYY 00:00:00`  
Saat kısmını `00:00:00` bırak; günün tüm seferleri taranır.

---

## 4. Çalıştırma

Proje klasöründe:

```bash
python -u tcdd_monitor.py
```

Durdurmak için `Ctrl+C`.

Bilgisayar açık ve script çalışırken Telegram’a bildirim gelir. Script kapanınca tarama da durur.
