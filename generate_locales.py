#!/usr/bin/env python3
"""Generate BattAI's 50 localized support and privacy pages from app strings."""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path


SITE = Path(__file__).resolve().parent
APP = SITE.parent / "45_BattAI"
RESOURCES = APP / "BattAI" / "Resources"
CONFIG = APP / "scripts" / "layout_audit" / "config" / "locales.json"
OUTPUT = SITE / "locales"
BASE_URL = "https://alice51849.github.io/battai-support"
EMAIL = "hourstag.app@gmail.com"
STRINGS_RE = re.compile(r'"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;', re.S)

KEYS = {
    "support_title": "settings.support.title",
    "support_desc": "settings.support.desc",
    "support_website": "settings.support.website",
    "privacy_title": "settings.privacy.title",
    "privacy_body": "settings.privacy.body",
    "privacy_policy": "settings.privacy.policy",
    "method_title": "methodology.title",
    "method_subtitle": "methodology.subtitle",
    "method_intro": "methodology.intro",
    "principles_title": "methodology.principles.title",
    "principles_body": "methodology.principles.body",
    "import_title": "import.title",
    "import_subtitle": "import.subtitle",
    "import_privacy": "import.privacy",
    "export_title": "export.title",
    "export_subtitle": "export.subtitle",
    "report_privacy": "report.privacy",
    "paywall_headline": "paywall.headline",
    "paywall_subheadline": "paywall.subheadline",
    "paywall_guarantee": "paywall.guarantee",
    "paywall_footnote": "paywall.footnote",
    "delete_title": "settings.delete.title",
    "delete_desc": "settings.delete.desc",
    "delete_message": "settings.delete.confirm.message",
}


def unescape(value: str) -> str:
    return (
        value.replace('\\"', '"')
        .replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace("\\\\", "\\")
    )


# 誠實鐵律:網站不得出現「永久 / lifetime / 終身 / 一生」這類無法保證的時間宣稱。
# App 內 paywall 字串目前仍寫成「一次付款. 永久使用. 無訂閱.」三段式;網站只保留
# 可兌現的事實(一次付款、無訂閱),把中間那段時間宣稱換成該語言自然的說法。
# 這是網站端的淨化層,不會改到 App 的 Localizable.strings。
GUARANTEE_HONEST = {
    "ar": "دفعة واحدة. بلا اشتراك.",
    "bn": "একবার পরিশোধ। কোনো সদস্যতা নেই।",
    "ca": "Un sol pagament. Sense subscripció.",
    "cs": "Jedna platba. Žádné předplatné.",
    "da": "Én betaling. Intet abonnement.",
    "de": "Eine Zahlung. Kein Abo.",
    "el": "Μία πληρωμή. Χωρίς συνδρομή.",
    "en": "One payment. No subscription.",
    "en-AU": "One payment. No subscription.",
    "en-CA": "One payment. No subscription.",
    "en-GB": "One payment. No subscription.",
    "es": "Pago único. Sin suscripción.",
    "es-MX": "Pago único. Sin suscripción.",
    "fi": "Yksi maksu. Ei tilausta.",
    "fr": "Achat unique. Sans abonnement.",
    "fr-CA": "Achat unique. Sans abonnement.",
    "gu": "એક ચુકવણી. કોઈ સબ્સ્ક્રિપ્શન નહીં.",
    "he": "תשלום אחד. ללא מינוי.",
    "hi": "एक भुगतान। कोई सदस्यता नहीं।",
    "hr": "Jedno plaćanje. Bez pretplate.",
    "hu": "Egyszeri fizetés. Nincs előfizetés.",
    "id": "Sekali bayar. Tanpa langganan.",
    "it": "Un pagamento. Nessun abbonamento.",
    "ja": "支払いは一度だけ。サブスクリプションなし。",
    "kn": "ಒಂದು ಪಾವತಿ. ಚಂದಾದಾರಿಕೆ ಇಲ್ಲ.",
    "ko": "한 번만 결제하면 됩니다. 구독은 없어요.",
    "ml": "ഒരു പണമടവ്. സബ്സ്ക്രിപ്ഷൻ ഇല്ല.",
    "mr": "एकच पेमेंट. सदस्यता नाही.",
    "ms": "Satu bayaran. Tiada langganan.",
    "nl": "Eén betaling. Geen abonnement.",
    "no": "Én betaling. Ikke noe abonnement.",
    "or": "ଗୋଟିଏ ଦେୟ। କୌଣସି ସବସ୍କ୍ରିପସନ୍ ନାହିଁ।",
    "pa": "ਇਕ ਭੁਗਤਾਨ। ਕੋਈ ਗਾਹਕੀ ਨਹੀਂ।",
    "pl": "Jedna płatność. Bez subskrypcji.",
    "pt-BR": "Um pagamento. Sem assinatura.",
    "pt-PT": "Um pagamento. Sem subscrição.",
    "ro": "O singură plată. Fără abonament.",
    "ru": "Один платёж. Без подписки.",
    "sk": "Jedna platba. Žiadne predplatné.",
    "sl-SI": "Eno plačilo. Brez naročnine.",
    "sv": "En betalning. Ingen prenumeration.",
    "ta": "ஒரே கட்டணம். சந்தா இல்லை.",
    "te": "ఒక్క చెల్లింపు. సభ్యత్వం లేదు.",
    "th": "จ่ายครั้งเดียว ไม่มีการสมัครสมาชิก",
    "tr": "Tek ödeme. Abonelik yok.",
    "uk": "Один платіж. Без підписки.",
    "ur": "ایک ادائیگی۔ کوئی سبسکرپشن نہیں۔",
    "vi": "Thanh toán một lần. Không đăng ký",
    "zh-Hans": "只付一次，绝无订阅。",
    "zh-Hant": "只付一次，絕無訂閱。",
}


def load_strings(code: str) -> dict[str, str]:
    path = RESOURCES / f"{code}.lproj" / "Localizable.strings"
    table = {
        unescape(key): unescape(value)
        for key, value in STRINGS_RE.findall(path.read_text(encoding="utf-8"))
    }
    missing = [key for key in KEYS.values() if key not in table]
    if missing:
        raise RuntimeError(f"{code} is missing localized web keys: {missing}")
    localized = {name: table[key] for name, key in KEYS.items()}
    localized["app_name"] = "BattAI"
    honest = GUARANTEE_HONEST.get(code)
    if honest is None:
        raise RuntimeError(f"{code} has no honest paywall guarantee copy for the web")
    localized["paywall_guarantee"] = honest
    return localized


def e(value: str) -> str:
    return html.escape(value, quote=True)


def alternates(locales: list[dict], page: str) -> str:
    links = []
    for locale in locales:
        code = locale["code"]
        suffix = "" if page == "index.html" else page
        url = f"{BASE_URL}/locales/{code}/{suffix}"
        links.append(
            f'  <link rel="alternate" hreflang="{e(code)}" href="{e(url)}">'
        )
    root = "" if page == "index.html" else page
    links.append(
        f'  <link rel="alternate" hreflang="x-default" href="{BASE_URL}/{root}">'
    )
    return "\n".join(links)


def shell(
    *,
    locale: dict,
    strings: dict[str, str],
    locales: list[dict],
    page: str,
    title: str,
    description: str,
    body: str,
) -> str:
    code = locale["code"]
    direction = "rtl" if locale.get("rtl") else "ltr"
    canonical_suffix = "" if page == "index.html" else page
    canonical = f"{BASE_URL}/locales/{code}/{canonical_suffix}"
    return f"""<!doctype html>
<html lang="{e(code)}" dir="{direction}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)} — {e(strings["app_name"])}</title>
  <meta name="description" content="{e(description)}">
  <link rel="canonical" href="{e(canonical)}">
{alternates(locales, page)}
  <link rel="icon" type="image/png" href="../../assets/favicon.png">
  <link rel="apple-touch-icon" href="../../assets/icon.png">
  <link rel="stylesheet" href="../../style.css">
  <meta name="theme-color" content="#F4FAFC" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#071B25" media="(prefers-color-scheme: dark)">
</head>
<body>
<div class="bg"></div>
<header>
  <div class="wrap nav">
    <a class="brand" href="index.html"><img src="../../assets/icon.png" alt=""><span>{e(strings["app_name"])}</span></a>
    <nav class="nav-links" aria-label="{e(strings["support_title"])}">
      <a href="index.html"{' aria-current="page"' if page == 'index.html' else ''}>{e(strings["support_title"])}</a>
      <a href="privacy.html"{' aria-current="page"' if page == 'privacy.html' else ''}>{e(strings["privacy_title"])}</a>
      <a href="../../languages.html" lang="en">Languages</a>
    </nav>
  </div>
</header>
<main>
{body}
</main>
<footer>
  <div class="wrap foot">
    <span>{e(strings["app_name"])}</span>
    <nav>
      <a href="index.html">{e(strings["support_title"])}</a>
      <a href="privacy.html">{e(strings["privacy_title"])}</a>
      <a href="mailto:{EMAIL}">{EMAIL}</a>
    </nav>
  </div>
</footer>
</body>
</html>
"""


def support_page(locale: dict, strings: dict[str, str], locales: list[dict]) -> str:
    body = f"""
  <section class="hero wrap">
    <img class="app-icon" src="../../assets/icon.png" alt="">
    <span class="eyebrow">{e(strings["support_title"])}</span>
    <h1>{e(strings["app_name"])}</h1>
    <p class="tagline">{e(strings["support_desc"])}</p>
    <div class="badges">
      <span class="pill"><span class="mark"></span>{e(strings["privacy_title"])}</span>
      <span class="pill"><span class="mark"></span>{e(strings["paywall_guarantee"])}</span>
    </div>
  </section>
  <section class="wrap">
    <div class="section-head">
      <h2>{e(strings["method_title"])}</h2>
      <p>{e(strings["method_subtitle"])}</p>
    </div>
    <div class="card"><p>{e(strings["method_intro"])}</p></div>
  </section>
  <section class="wrap">
    <div class="grid">
      <div class="card feature"><h3>{e(strings["import_title"])}</h3><p>{e(strings["import_subtitle"])}</p></div>
      <div class="card feature"><h3>{e(strings["export_title"])}</h3><p>{e(strings["export_subtitle"])}</p></div>
      <div class="card feature"><h3>{e(strings["paywall_headline"])}</h3><p>{e(strings["paywall_subheadline"])}</p></div>
      <div class="card feature"><h3>{e(strings["privacy_title"])}</h3><p>{e(strings["privacy_body"])}</p></div>
    </div>
  </section>
  <section class="wrap">
    <div class="card contact-card">
      <span class="eyebrow">{e(strings["support_title"])}</span>
      <h2>{e(strings["support_desc"])}</h2>
      <a class="mail" href="mailto:{EMAIL}">{EMAIL}</a>
    </div>
  </section>
"""
    return shell(
        locale=locale,
        strings=strings,
        locales=locales,
        page="index.html",
        title=strings["support_title"],
        description=strings["support_desc"],
        body=body,
    )


def privacy_page(locale: dict, strings: dict[str, str], locales: list[dict]) -> str:
    body = f"""
  <section class="hero wrap">
    <span class="eyebrow">{e(strings["privacy_policy"])}</span>
    <h1>{e(strings["privacy_title"])}</h1>
    <p class="updated"><time datetime="2026-08-11">2026-08-11</time> · {e(strings["app_name"])}</p>
    <p class="tagline">{e(strings["privacy_body"])}</p>
  </section>
  <section class="wrap doc">
    <div class="card">
      <div class="callout"><p>{e(strings["privacy_body"])}</p></div>
      <h2>{e(strings["principles_title"])}</h2>
      <p>{e(strings["principles_body"])}</p>
      <h2>{e(strings["import_title"])}</h2>
      <p>{e(strings["import_privacy"])}</p>
      <h2>{e(strings["export_title"])}</h2>
      <p>{e(strings["export_subtitle"])}</p>
      <p>{e(strings["report_privacy"])}</p>
      <h2>{e(strings["paywall_headline"])}</h2>
      <p>{e(strings["paywall_guarantee"])}</p>
      <p>{e(strings["paywall_footnote"])}</p>
      <h2>{e(strings["delete_title"])}</h2>
      <p>{e(strings["delete_desc"])}</p>
      <p>{e(strings["delete_message"])}</p>
      <h2>{e(strings["support_title"])}</h2>
      <p>{e(strings["support_desc"])}</p>
      <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
    </div>
  </section>
"""
    return shell(
        locale=locale,
        strings=strings,
        locales=locales,
        page="privacy.html",
        title=strings["privacy_title"],
        description=strings["privacy_body"],
        body=body,
    )


def languages_page(locales: list[dict]) -> str:
    cards = "\n".join(
        f'      <a class="card language-card" href="locales/{e(locale["code"])}/" '
        f'lang="{e(locale["code"])}" dir="{"rtl" if locale.get("rtl") else "ltr"}">'
        f'{e(locale["name"])}</a>'
        for locale in locales
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Languages — BattAI</title>
  <meta name="description" content="BattAI support and privacy information in all 50 supported Apple locales.">
  <link rel="canonical" href="{BASE_URL}/languages.html">
  <link rel="icon" type="image/png" href="assets/favicon.png">
  <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="bg"></div>
<main>
  <section class="hero wrap">
    <img class="app-icon" src="assets/icon.png" alt="">
    <span class="eyebrow">BattAI</span>
    <h1>Languages</h1>
    <p class="tagline">Support and privacy information in all 50 supported Apple locales.</p>
  </section>
  <section class="wrap">
    <div class="language-grid">
{cards}
    </div>
  </section>
</main>
</body>
</html>
"""


def sitemap(locales: list[dict]) -> str:
    urls = [f"{BASE_URL}/", f"{BASE_URL}/privacy.html", f"{BASE_URL}/languages.html"]
    for locale in locales:
        code = locale["code"]
        urls.extend(
            [
                f"{BASE_URL}/locales/{code}/",
                f"{BASE_URL}/locales/{code}/privacy.html",
            ]
        )
    entries = "\n".join(f"  <url><loc>{e(url)}</loc></url>" for url in urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n"
    )


def main() -> None:
    locales = json.loads(CONFIG.read_text(encoding="utf-8"))["locales"]
    if len(locales) != 50:
        raise RuntimeError(f"Expected 50 locales, found {len(locales)}")

    shutil.rmtree(OUTPUT, ignore_errors=True)
    for locale in locales:
        code = locale["code"]
        strings = load_strings(code)
        destination = OUTPUT / code
        destination.mkdir(parents=True)
        (destination / "index.html").write_text(
            support_page(locale, strings, locales), encoding="utf-8"
        )
        (destination / "privacy.html").write_text(
            privacy_page(locale, strings, locales), encoding="utf-8"
        )

    (SITE / "languages.html").write_text(languages_page(locales), encoding="utf-8")
    (SITE / "sitemap.xml").write_text(sitemap(locales), encoding="utf-8")
    print(f"Generated {len(locales)} support pages + {len(locales)} privacy pages")


if __name__ == "__main__":
    main()
