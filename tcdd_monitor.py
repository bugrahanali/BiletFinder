# -*- coding: utf-8 -*-
import sys
import time
import datetime
import getpass
import requests
import curl_cffi.requests as cffi_req

# ─────────────────────────── CONFIG ────────────────────────────────────
BEARER_TOKEN = (
    "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJlVFFicDhDMmpiakp1cnUzQVk2a0ZnV196U29MQXZIMmJ5bTJ2OUg5THhRIn0."
    "eyJleHAiOjE3MjEzODQ0NzAsImlhdCI6MTcyMTM4NDQxMCwianRpIjoiYWFlNjVkNzgtNmRkZS00ZGY4LWEwZWYtYjRkNzZiYjZlODNjIiwiaXNzIjoiaHR0cDovL3l0cC1wcm9kLW1hc3RlcjEudGNkZHRhc2ltYWNpbGlrLmdvdi50cjo4MDgwL3JlYWxtcy9tYXN0ZXIiLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiMDAzNDI3MmMtNTc2Yi00OTBlLWJhOTgtNTFkMzc1NWNhYjA3IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoidG1zIiwic2Vzc2lvbl9zdGF0ZSI6IjAwYzM4NTJiLTg1YjEtNDMxNS04OGIwLWQ0MWMxMTcyYzA0MSIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiZGVmYXVsdC1yb2xlcy1tYXN0ZXIiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsInNpZCI6IjAwYzM4NTJiLTg1YjEtNDMxNS04OGIwLWQ0MWMxMTcyYzA0MSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicHJlZmVycmVkX3VzZXJuYW1lIjoid2ViIiwiZ2l2ZW5fbmFtZSI6IiIsImZhbWlseV9uYW1lIjoiIn0."
    "AIW_4Qws2wfwxyVg8dgHRT9jB3qNavob2C4mEQIQGl3urzW2jALPx-e51ZwHUb-TXB-X2RPHakonxKnWG6tDIP5aKhiidzXDcr6pDDoYU5DnQhMg1kywyOaMXsjLFjuYN5PAyGUMh6YSOVsg1PzNh-5GrJF44pS47JnB9zk03Pr08napjsZPoRB-5N4GQ49cnx7ePC82Y7YIc-gTew2baqKQPz9_v381Gbm2V38PZDH9KldlcWut7kqQYJFMJ7dkM_entPJn9lFk7R5h5j_06OlQEpWRMQTn9SQ1AYxxmZxBu5XYMKDkn4rzIIVCkdTPJNCt5PvjENjClKFeUA1DOg"
)
TELEGRAM_BOT_TOKEN = ""  # BotFather token
TELEGRAM_CHAT_ID = ""    # kendi chat id'n
DEPARTURE_STATION_ID = 1325
DEPARTURE_STATION_NAME = "İSTANBUL(SÖĞÜTLÜÇEŞME)"
ARRIVAL_STATION_ID = 98
ARRIVAL_STATION_NAME = "ANKARA GAR"
DEPARTURE_DATE = "09-09-2026 00:00:00"
POLL_INTERVAL_SECONDS = 5
MAX_NOTIFICATIONS_PER_WINDOW = 2  # koltuk açıkken max kaç Telegram mesajı
SEND_STARTUP_TELEGRAM = True  # izleme başlayınca özet mesajı
# ───────────────────────────────────────────────────────────────────────

API_URL = (
    "https://web-api-prod-ytp.tcddtasimacilik.gov.tr"
    "/tms/train/train-availability?environment=dev&userId=1"
)
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def make_headers(token):
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr",
        "Authorization": token,
        "Content-Type": "application/json",
        "Origin": "https://ebilet.tcddtasimacilik.gov.tr",
        "Referer": "https://ebilet.tcddtasimacilik.gov.tr/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/148.0.0.0 Safari/537.36"
        ),
        "unit-id": "3895",
    }


def make_payload():
    return {
        "searchRoutes": [
            {
                "departureStationId": DEPARTURE_STATION_ID,
                "departureStationName": DEPARTURE_STATION_NAME,
                "arrivalStationId": ARRIVAL_STATION_ID,
                "arrivalStationName": ARRIVAL_STATION_NAME,
                "departureDate": DEPARTURE_DATE,
            }
        ],
        "passengerTypeCounts": [{"id": 0, "count": 1}],
        "searchReservation": False,
        "blTrainTypes": ["TURISTIK_TREN"],
    }


def send_telegram(text):
    try:
        r = requests.post(
            TELEGRAM_URL,
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
            timeout=10,
        )
        if not r.ok:
            print(f"  [Telegram hata] {r.status_code}: {r.text[:200]}")
        else:
            print("  [Telegram] Mesaj gönderildi.")
    except Exception as exc:
        print(f"  [Telegram hata] {exc}")


def fetch_availability(token, verbose=False):
    """Returns (data_dict, needs_new_token). Raises on other HTTP errors."""
    r = cffi_req.post(
        API_URL,
        headers=make_headers(token),
        json=make_payload(),
        timeout=15,
        impersonate="chrome",
    )
    if verbose:
        print(f"HTTP {r.status_code}")
    if r.status_code in (401, 403):
        if verbose:
            print(r.text)
        return None, True
    r.raise_for_status()
    return r.json(), False


def _ms_to_local(ms):
    if ms is None:
        return None
    try:
        return datetime.datetime.fromtimestamp(int(ms) / 1000)
    except (TypeError, ValueError, OSError):
        return None


def train_label(train_availability):
    trains = train_availability.get("trains") or []
    if trains:
        return trains[0].get("number") or trains[0].get("name", "?")
    return train_availability.get("trainNumber", "?")


def departure_time(train_availability):
    segments = train_availability.get("trainSegments") or []
    if not segments:
        trains = train_availability.get("trains") or []
        if trains:
            segments = trains[0].get("segments") or []
    if not segments:
        return None
    return _ms_to_local(segments[0].get("departureTime"))


def _stock_containers(train_availability):
    trains = train_availability.get("trains") or []
    if trains:
        yield trains[0]
    yield train_availability


def _is_economy_cabin(cabin):
    code = (cabin.get("code") or "").upper()
    name = (cabin.get("name") or "").upper()
    return code == "Y1" or "EKONOM" in name


def find_economy_stock(train_availability):
    """Returns (count, source). count None = ekonomi satırı yok."""
    for block in _stock_containers(train_availability):
        for cca in block.get("cabinClassAvailabilities") or []:
            if _is_economy_cabin(cca.get("cabinClass") or {}):
                return cca.get("availabilityCount"), "cabinClassAvailabilities"

        for fare_family in block.get("availableFareInfo") or []:
            for cc in fare_family.get("cabinClasses") or []:
                if _is_economy_cabin(cc.get("cabinClass") or {}):
                    return cc.get("availabilityCount"), "availableFareInfo"

    return None, None


def find_economy_details(train_availability):
    """Telegram mesajı için fiyat dahil ekonomi detayı."""
    for block in _stock_containers(train_availability):
        for fare_family in block.get("availableFareInfo") or []:
            for cc in fare_family.get("cabinClasses") or []:
                if _is_economy_cabin(cc.get("cabinClass") or {}):
                    return cc

        for cca in block.get("cabinClassAvailabilities") or []:
            if _is_economy_cabin(cca.get("cabinClass") or {}):
                return {
                    "availabilityCount": cca.get("availabilityCount"),
                    "minPrice": None,
                    "minPriceCurrency": "TRY",
                }

    return None


def economy_count(train_availability):
    count, _ = find_economy_stock(train_availability)
    if count is None:
        return None
    return int(count)


def economy_has_seats(train_availability):
    count = economy_count(train_availability)
    return count is not None and count > 0
 

def sefer_saat_str(train_availability):
    dep = departure_time(train_availability)
    if not dep:
        return None
    saat = dep.strftime("%H:%M")
    if saat.startswith("0"):
        saat = saat[1:]
    return saat


def build_message(train_availability):
    saat = sefer_saat_str(train_availability)
    return f"{saat} seferi" if saat else "Sefer saati bilinmiyor"


def list_available_trips(availabilities):
    """Müsait ekonomi seferleri: (saat, tren no, koltuk sayısı)."""
    trips = []
    for ta in availabilities:
        count = economy_count(ta)
        if count is None or count <= 0:
            continue
        saat = sefer_saat_str(ta)
        if saat:
            trips.append((saat, train_label(ta), count))
    trips.sort(key=lambda x: x[0])
    return trips


def print_economy_summary(data, ts):
    legs = (data or {}).get("trainLegs") or []
    if not legs:
        print(f"[{ts}] Yanıtta trainLegs yok.")
        return

    availabilities = legs[0].get("trainAvailabilities") or []
    with_seats = 0
    no_seats = 0
    unknown = 0

    for ta in availabilities:
        label = train_label(ta)
        dep = departure_time(ta)
        dep_str = dep.strftime("%H:%M") if dep else "?"
        count, _ = find_economy_stock(ta)
        if count is None:
            unknown += 1
            print(f"  {label} {dep_str} → stok bilgisi yok")
        elif int(count) > 0:
            with_seats += 1
            print(f"  {label} {dep_str} → ekonomi {count}")
        else:
            no_seats += 1
            print(f"  {label} {dep_str} → ekonomi dolu")

    print(
        f"[{ts}] {len(availabilities)} sefer — "
        f"{with_seats} müsait, {no_seats} dolu, {unknown} bilinmiyor."
    )


def run_poll(train_states, bootstrap_done):
    """Tek poll. Returns updated bootstrap_done."""
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    data, is_401 = fetch_availability(BEARER_TOKEN)

    if is_401:
        print(f"[{ts}] 401/403 — token geçersiz veya süresi doldu.")
        return bootstrap_done, True

    legs = (data or {}).get("trainLegs") or []
    if not legs:
        print(f"[{ts}] Yanıtta trainLegs bulunamadı.")
        return bootstrap_done, False

    availabilities = legs[0].get("trainAvailabilities") or []

    if not bootstrap_done:
        print(f"[{ts}] İlk tarama — mevcut durum kaydediliyor.")
        with_seats = 0
        for ta in availabilities:
            key = train_label(ta)
            count = economy_count(ta)
            has = count is not None and count > 0
            if has:
                with_seats += 1
            train_states[key] = {
                "available": has,
                "last_count": count if count is not None else 0,
                "notif_count": 0,
            }
        print_economy_summary(data, ts)
        if SEND_STARTUP_TELEGRAM:
            send_telegram("Arama başladı")
            print(f"[{ts}] Telegram: Arama başladı")
        return True, False

    notify_cnt = 0
    for ta in availabilities:
        key = train_label(ta)
        count = economy_count(ta)
        has = count is not None and count > 0

        if key not in train_states:
            train_states[key] = {
                "available": False,
                "last_count": 0,
                "notif_count": 0,
            }

        state = train_states[key]

        if has:
            state["available"] = True
            if state["notif_count"] < MAX_NOTIFICATIONS_PER_WINDOW:
                msg = build_message(ta)
                saat = sefer_saat_str(ta) or "?"
                print(
                    f"[{ts}] BİLDİRİM → {saat} seferi ({count} koltuk, "
                    f"#{state['notif_count'] + 1}/{MAX_NOTIFICATIONS_PER_WINDOW})"
                )
                send_telegram(msg)
                state["notif_count"] += 1
                notify_cnt += 1
        else:
            if state["available"]:
                saat = sefer_saat_str(ta) or key
                print(f"[{ts}] Ekonomi doldu → {saat} seferi")
            state["available"] = False
            state["notif_count"] = 0

        state["last_count"] = count if count is not None else 0

    trips = list_available_trips(availabilities)
    if trips:
        saatler = ", ".join(f"{s} ({c})" for s, _n, c in trips)
        print(f"[{ts}] Boş ekonomi: {saatler}")
    print(
        f"[{ts}] {len(availabilities)} sefer — "
        f"{len(trips)} müsait, {notify_cnt} bildirim gönderildi."
    )
    return bootstrap_done, False


def main():
    global BEARER_TOKEN
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if "--test-notify" in sys.argv:
        send_telegram(
            "\U0001f9ea BiletFinder Telegram testi — bu mesaji goruyorsan bot calisiyor."
        )
        return

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        BEARER_TOKEN = args[0].strip()
        print("Token komut satırından alındı.")
    elif not BEARER_TOKEN:
        try:
            BEARER_TOKEN = getpass.getpass(
                "Bearer token giriniz (sadece token, 'Bearer' olmadan): "
            ).strip()
        except Exception:
            BEARER_TOKEN = input(
                "Bearer token giriniz (sadece token, 'Bearer' olmadan): "
            ).strip()

    train_states = {}
    bootstrap_done = False

    print(
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] "
        f"İzleme başladı — {DEPARTURE_STATION_NAME} → {ARRIVAL_STATION_NAME} "
        f"({DEPARTURE_DATE}), her {POLL_INTERVAL_SECONDS}s. Çıkmak: Ctrl+C"
    )

    while True:
        try:
            bootstrap_done, need_token = run_poll(train_states, bootstrap_done)
            if need_token:
                try:
                    BEARER_TOKEN = getpass.getpass(
                        "Yeni Bearer token giriniz: "
                    ).strip()
                except Exception:
                    BEARER_TOKEN = input("Yeni Bearer token giriniz: ").strip()
                bootstrap_done = False
                train_states.clear()
        except cffi_req.RequestsError as exc:
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] Ağ hatası: {exc}")
        except Exception as exc:
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] Hata: {exc}")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
