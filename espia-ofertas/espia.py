#!/usr/bin/env python3
"""Espia de ofertas: daily evidence collector for the offer-modeling report.

Collects REAL public data only (nothing is generated here):
  1. Meta Ad Library (via ScrapeCreators): advertisers in the seed niches with
     >= N active ads in the source countries, their most-repeated creatives and
     the video transcripts of those creatives.
  2. Landing pages of those advertisers: title, headings, visible prices.
  3. Organic short videos in the same niche (TikTok + Instagram Reels) that
     outperform their creator's size, with transcripts.
  4. World Bank indicators for the candidate target markets.

Everything is written to <out>/dossier.json (+ raw API responses in <out>/raw/)
so every claim in the final report can be traced back to a source.
Standard library only: nothing to install.
"""
import argparse
import datetime as dt
import hashlib
import html
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

SC_BASE = os.environ.get("SCRAPECREATORS_BASE_URL", "https://api.scrapecreators.com")
WB_BASE = os.environ.get("WORLDBANK_BASE_URL", "https://api.worldbank.org")
KEY_FILE = os.path.expanduser("~/.config/espia/scrapecreators.key")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# Main language of common target markets (used only to group markets by language).
COUNTRY_LANG = {
    "US": "en", "GB": "en", "CA": "en/fr", "AU": "en", "NZ": "en", "IE": "en", "SG": "en",
    "ES": "es", "MX": "es", "CO": "es", "AR": "es", "CL": "es", "PE": "es", "UY": "es",
    "PR": "es/en", "DO": "es", "EC": "es", "CR": "es", "PA": "es", "GT": "es",
    "BR": "pt", "PT": "pt", "DE": "de", "AT": "de", "CH": "de/fr/it", "FR": "fr",
    "BE": "nl/fr", "NL": "nl", "IT": "it", "SE": "sv", "NO": "no", "DK": "da", "FI": "fi",
}
WB_INDICATORS = {
    "gdp_pc_ppp": "NY.GDP.PCAP.PP.CD",   # GDP per capita, PPP (current international $)
    "internet_pct": "IT.NET.USER.ZS",    # Individuals using the Internet (% of population)
    "population": "SP.POP.TOTL",
}
HIGH_TICKET_FUNNEL_WORDS = [
    "agenda", "agendar", "llamada", "sesión estratégica", "sesion estrategica", "aplica",
    "aplicar", "postula", "webinar", "masterclass", "clase gratuita", "clase gratis",
    "book a call", "schedule a call", "apply now", "strategy call", "free training",
    "free class", "discovery call", "mentoría", "mentoria", "programa", "coaching",
]


class BudgetExceeded(Exception):
    pass


class ApiError(Exception):
    pass


def now_ts():
    return time.time()


def log(msg):
    print(f"[{dt.datetime.now():%H:%M:%S}] {msg}", flush=True)


def load_key():
    key = os.environ.get("SCRAPECREATORS_API_KEY", "").strip()
    if not key and os.path.exists(KEY_FILE):
        key = open(KEY_FILE, encoding="utf-8").read().strip()
    if not key:
        sys.exit(f"No API key. Put it in {KEY_FILE} (chmod 600) or SCRAPECREATORS_API_KEY.")
    return key


def http_get(url, headers=None, timeout=90, retries=3):
    """GET with retries on network errors, 429 and 5xx. Returns (status, bytes)."""
    last = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            body = e.read()
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                last = f"HTTP {e.code}"
                time.sleep(2 ** (attempt + 1))
                continue
            return e.code, body
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = str(e)
            if attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
    raise ApiError(f"network error after {retries + 1} attempts: {last} ({url[:120]})")


class ScrapeCreators:
    def __init__(self, key, budget, raw_dir):
        self.key = key
        self.budget = budget
        self.raw_dir = raw_dir
        self.spent = 0
        self.calls = 0
        self.remaining = None
        os.makedirs(raw_dir, exist_ok=True)

    def get(self, path, **params):
        if self.spent >= self.budget:
            raise BudgetExceeded(f"credit budget reached ({self.spent}/{self.budget})")
        params = {k: v for k, v in params.items() if v not in (None, "")}
        url = f"{SC_BASE}{path}?{urllib.parse.urlencode(params)}"
        status, body = http_get(url, {"x-api-key": self.key, "User-Agent": "espia-ofertas/1"})
        self.calls += 1
        try:
            data = json.loads(body.decode("utf-8"))
        except ValueError:
            raise ApiError(f"{path}: HTTP {status}, non-JSON response: {body[:200]!r}")
        name = f"{self.calls:04d}_{path.strip('/').replace('/', '_')}.json"
        with open(os.path.join(self.raw_dir, name), "w", encoding="utf-8") as f:
            json.dump({"request": {"path": path, "params": params}, "status": status,
                       "response": data}, f, ensure_ascii=False)
        if status >= 400 or data.get("success") is False:
            raise ApiError(f"{path}: HTTP {status}: {str(data)[:300]}")
        charged = data.get("credits_charged")
        self.spent += charged if isinstance(charged, (int, float)) else 1
        if data.get("credits_remaining") is not None:
            self.remaining = data["credits_remaining"]
        return data


# ---------------------------------------------------------------- Meta ads

def norm_text(t):
    return re.sub(r"\s+", " ", (t or "").strip().lower())


def normalize_ad(a):
    s = a.get("snapshot") or {}
    cards = s.get("cards") or []
    card = cards[0] if cards and isinstance(cards[0], dict) else {}
    body = s.get("body")
    text = body.get("text") if isinstance(body, dict) else body
    text = text or card.get("body") or ""
    videos = s.get("videos") or []
    images = s.get("images") or []
    video_url = (videos[0].get("video_hd_url") or videos[0].get("video_sd_url")) if videos else \
        (card.get("video_hd_url") or card.get("video_sd_url"))
    preview = (videos[0].get("video_preview_image_url") if videos else None) or \
        (images[0].get("original_image_url") if images else None) or \
        card.get("video_preview_image_url") or card.get("original_image_url")
    ad_id = str(a.get("ad_archive_id") or a.get("adArchiveID") or "")
    start = a.get("start_date") or a.get("startDate")
    days = round((now_ts() - start) / 86400, 1) if isinstance(start, (int, float)) else None
    return {
        "ad_id": ad_id,
        "library_url": a.get("url") or f"https://www.facebook.com/ads/library?id={ad_id}",
        "page_id": str(a.get("page_id") or a.get("pageID") or s.get("page_id") or ""),
        "page_name": a.get("page_name") or a.get("pageName") or s.get("page_name"),
        "page_url": s.get("page_profile_uri"),
        "page_likes": s.get("page_like_count"),
        "is_active": a.get("is_active", a.get("isActive")),
        "start_date": a.get("start_date_string") or a.get("startDateString"),
        "days_running": days,
        "platforms": a.get("publisher_platform") or a.get("publisherPlatform") or [],
        "format": (s.get("display_format") or "").upper(),
        "text": text,
        "title": s.get("title") or card.get("title"),
        "link_description": s.get("link_description") or card.get("link_description"),
        "cta": s.get("cta_text") or card.get("cta_text"),
        "link_url": s.get("link_url") or card.get("link_url"),
        "extra_links": s.get("extra_links") or [],
        "video_url": video_url,
        "preview_url": preview,
        "n_cards": len(cards),
        "collation_count": a.get("collation_count"),
    }


def fingerprint(ad):
    base = norm_text(ad["text"])[:300] + "|" + norm_text(ad["title"])[:120]
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]


def landing_of(ad):
    for u in [ad.get("link_url")] + list(ad.get("extra_links") or []):
        if u and not re.search(r"(^https?://)?(www\.)?(fb\.com|facebook\.com|instagram\.com|"
                                r"fb\.me|m\.me|wa\.me|api\.whatsapp)", u):
            return u
    return None


def search_ads(sc, keyword, country, cfg):
    ads, cursor = [], None
    for _ in range(cfg["search_pages"]):
        d = sc.get("/v1/facebook/adLibrary/search/ads", query=keyword, country=country,
                   status="ACTIVE", sort_by="total_impressions",
                   search_type=cfg.get("search_type", "keyword_unordered"),
                   language=cfg.get("ad_language"), cursor=cursor)
        ads += [normalize_ad(a) for a in d.get("searchResults") or []]
        cursor = d.get("cursor")
        if not cursor:
            break
    return ads


def company_ads(sc, page_id, country, cfg):
    """Active ads of one advertiser in one country, highest impressions first."""
    ads, cursor, pages, complete = [], None, 0, False
    while pages < cfg["max_pages_per_advertiser"]:
        d = sc.get("/v1/facebook/adLibrary/company/ads", pageId=page_id, country=country,
                   status="ACTIVE", sort_by="total_impressions", cursor=cursor)
        pages += 1
        ads += [normalize_ad(a) for a in d.get("results") or []]
        cursor = d.get("cursor")
        if not cursor:
            complete = True
            break
        if len(ads) >= cfg["min_active_ads"] and cfg.get("stop_at_threshold", True):
            break
    seen, uniq = set(), []
    for a in ads:
        if a["ad_id"] not in seen:
            seen.add(a["ad_id"])
            uniq.append(a)
    return uniq, complete


def summarize_advertiser(ads, complete, cfg):
    groups = defaultdict(list)
    for rank, a in enumerate(ads):
        a["impression_rank"] = rank + 1
        groups[fingerprint(a)].append(a)
    days = sorted(a["days_running"] for a in ads if a["days_running"] is not None)
    median_days = days[len(days) // 2] if days else None
    landings = Counter(landing_of(a) for a in ads if landing_of(a))
    domains = Counter(urllib.parse.urlparse(u).netloc.lower().removeprefix("www.")
                      for u in landings.elements())
    creatives = []
    for fp, g in groups.items():
        best = min(g, key=lambda x: x["impression_rank"])
        creatives.append({
            "fingerprint": fp,
            "copies_running": len(g),
            "max_days_running": max((x["days_running"] or 0) for x in g),
            "best_impression_rank": best["impression_rank"],
            "formats": sorted({x["format"] for x in g if x["format"]}),
            "ad": best,
            "other_ad_ids": [x["ad_id"] for x in g if x is not best][:10],
        })
    creatives.sort(key=lambda c: (-c["copies_running"], c["best_impression_rank"],
                                  -c["max_days_running"]))
    n = len(ads)
    score = (min(n, 500) / 100) + ((median_days or 0) / 30) + \
        (creatives[0]["copies_running"] / 5 if creatives else 0)
    return {
        "active_ads_counted": n,
        "count_is_lower_bound": not complete,
        "meets_threshold": n >= cfg["min_active_ads"],
        "threshold_status": "cumple" if n >= cfg["min_active_ads"] else
        ("indeterminado (se alcanzó el tope de páginas; sube max_pages_per_advertiser)"
         if not complete else "no cumple"),
        "median_days_running": median_days,
        "max_days_running": days[-1] if days else None,
        "distinct_creatives": len(groups),
        "formats": dict(Counter(a["format"] or "?" for a in ads)),
        "platforms": dict(Counter(p for a in ads for p in a["platforms"])),
        "top_landings": landings.most_common(5),
        "top_domains": domains.most_common(5),
        "score": round(score, 2),
        "score_formula": "min(ads,500)/100 + median_days/30 + copies_of_top_creative/5",
        "creatives_ranked": creatives,
    }


# ---------------------------------------------------------------- landings

PRICE_RE = re.compile(
    r"(?:US\$|USD\s?|\$|€|£|R\$|MXN\s?\$?|COP\s?\$?|ARS\s?\$?|CLP\s?\$?|S/\.?\s?)\s?\d{1,3}(?:[.,\s]\d{3})*(?:[.,]\d{1,2})?"
    r"|\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?\s?(?:USD|EUR|€|dólares|dolares|euros)", re.I)


def visible_text(raw):
    raw = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()


def price_value(s):
    digits = re.sub(r"[^\d.,]", "", s)
    if re.search(r"[.,]\d{1,2}$", digits):
        digits = digits[:-3] if digits[-3] in ".," else digits[:-2]
    digits = re.sub(r"[.,]", "", digits)
    return int(digits) if digits.isdigit() else None


def capture_landing(url, save_path, cfg):
    out = {"url": url, "ok": False}
    try:
        status, body = http_get(url, {"User-Agent": UA, "Accept-Language": "es,en;q=0.8"},
                                timeout=40, retries=1)
    except ApiError as e:
        out["error"] = str(e)
        return out
    out["http_status"] = status
    raw = body.decode("utf-8", errors="replace")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(raw)
    def tags(name, limit):
        found = re.findall(rf"(?is)<{name}[^>]*>(.*?)</{name}>", raw)
        return [visible_text(x)[:200] for x in found if visible_text(x)][:limit]
    meta = re.search(r'(?is)<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)', raw)
    text = visible_text(raw)
    prices = sorted(set(m.group(0).strip() for m in PRICE_RE.finditer(text)))[:20]
    values = [v for v in (price_value(p) for p in prices) if v]
    low = text.lower()
    funnel_words = [w for w in HIGH_TICKET_FUNNEL_WORDS if w in low]
    if values and max(values) >= cfg["high_ticket_min_price"]:
        ticket = f"alto (precio visible más alto: {max(values)})"
    elif funnel_words and not values:
        ticket = "probable alto (sin precio visible; embudo de llamada/clase/aplicación)"
    elif values:
        ticket = f"bajo/medio (precio visible más alto: {max(values)})"
    else:
        ticket = "no detectado (revisar checkout a mano)"
    out.update({
        "ok": 200 <= status < 400 and len(text) > 200,
        "title": (tags("title", 1) or [None])[0],
        "meta_description": html.unescape(meta.group(1))[:300] if meta else None,
        "h1": tags("h1", 5), "h2": tags("h2", 15),
        "prices_seen": prices, "funnel_words": funnel_words,
        "ticket_guess": ticket,
        "text_excerpt": text[:cfg.get("landing_text_chars", 4000)],
        "saved_html": os.path.basename(save_path),
    })
    if not out["ok"]:
        out["note"] = "La página no devolvió texto (puede requerir JavaScript o bloquear robots)."
    return out


# ---------------------------------------------------------------- organic

def tiktok_ideas(sc, kw, cfg):
    items, cursor = [], None
    for _ in range(cfg["tiktok_pages"]):
        d = sc.get("/v1/tiktok/search/keyword", query=kw, date_posted=cfg["tiktok_date_posted"],
                   sort_by="relevance", region=cfg.get("tiktok_region"), cursor=cursor)
        for it in d.get("search_item_list") or []:
            a = it.get("aweme_info") or it
            st, au, vd = a.get("statistics") or {}, a.get("author") or {}, a.get("video") or {}
            plays = st.get("play_count") or 0
            fol = au.get("follower_count") or 0
            eng = sum(st.get(k) or 0 for k in ("digg_count", "comment_count", "share_count",
                                                 "collect_count"))
            handle = au.get("unique_id")
            vid = a.get("aweme_id")
            items.append({
                "platform": "tiktok", "keyword": kw, "id": vid,
                "url": a.get("url") or (f"https://www.tiktok.com/@{handle}/video/{vid}"
                                         if handle and vid else None),
                "caption": a.get("desc"), "language": a.get("desc_language"),
                "author": handle, "followers": fol,
                "created": dt.datetime.fromtimestamp(a["create_time"], dt.timezone.utc)
                .strftime("%Y-%m-%d") if a.get("create_time") else None,
                "duration_s": round((vd.get("duration") or 0) / 1000, 1),
                "plays": plays, "likes": st.get("digg_count"), "comments": st.get("comment_count"),
                "shares": st.get("share_count"), "saves": st.get("collect_count"),
                "engagement_rate": round(eng / plays, 4) if plays else None,
                "views_per_follower": round(plays / max(fol, 1000), 2),
                "is_ad": a.get("is_ad"),
            })
        cursor = d.get("cursor")
        if not cursor:
            break
    return items


def instagram_ideas(sc, kw, cfg):
    items = []
    for page in range(1, cfg["instagram_pages"] + 1):
        d = sc.get("/v2/instagram/reels/search", query=kw,
                   date_posted=cfg["instagram_date_posted"], page=page)
        reels = d.get("reels") or []
        for r in reels:
            ow = r.get("owner") or {}
            fol = ow.get("follower_count") or 0
            likes = r.get("like_count") or 0
            items.append({
                "platform": "instagram", "keyword": kw, "id": r.get("shortcode") or r.get("id"),
                "url": r.get("url"), "caption": (r.get("caption") or "")[:500],
                "author": ow.get("username"), "followers": fol,
                "created": (r.get("taken_at") or "")[:10], "duration_s": r.get("video_duration"),
                "likes": likes, "comments": r.get("comment_count"),
                "plays": r.get("video_play_count") or r.get("video_view_count"),
                "likes_per_follower": round(likes / max(fol, 1000), 3),
                "is_ad": r.get("is_ad"), "paid_partnership": r.get("is_paid_partnership"),
            })
        if not reels:
            break
    return items


def rank_organic(items, platform, cfg):
    seen, out = set(), []
    for it in items:
        if it["id"] in seen or it.get("is_ad"):
            continue
        seen.add(it["id"])
        out.append(it)
    if platform == "tiktok":
        out = [i for i in out if (i["plays"] or 0) >= cfg["tiktok_min_plays"]]
        out.sort(key=lambda i: (-i["views_per_follower"], -(i["plays"] or 0)))
    else:
        out = [i for i in out if (i["likes"] or 0) >= cfg["instagram_min_likes"]]
        out.sort(key=lambda i: (-i["likes_per_follower"], -(i["likes"] or 0)))
    return out


# ---------------------------------------------------------------- markets

def world_bank(countries):
    result = {c: {"country": c, "main_language": COUNTRY_LANG.get(c, "?")} for c in countries}
    for field, ind in WB_INDICATORS.items():
        url = (f"{WB_BASE}/v2/country/{';'.join(countries)}/indicator/{ind}"
               f"?format=json&mrnev=1&per_page=300")
        try:
            status, body = http_get(url, {"User-Agent": "espia-ofertas/1"}, timeout=40)
            data = json.loads(body)
            rows = data[1] if isinstance(data, list) and len(data) > 1 and data[1] else []
        except (ApiError, ValueError) as e:
            for c in countries:
                result[c][field] = None
                result[c][field + "_error"] = str(e)[:120]
            continue
        for r in rows:
            iso2 = (r.get("country") or {}).get("id")
            if iso2 in result:
                result[iso2]["name"] = r["country"].get("value")
                result[iso2][field] = round(r["value"], 1) if r.get("value") is not None else None
                result[iso2][field + "_year"] = r.get("date")
    return {"source": "World Bank WDI API (api.worldbank.org), most recent value per country",
            "indicators": WB_INDICATORS,
            "rows": sorted(result.values(), key=lambda x: -(x.get("gdp_pc_ppp") or 0))}


# ---------------------------------------------------------------- state

def load_state(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return {"advertisers": {}}


# ---------------------------------------------------------------- commands

def estimate(cfg):
    n = cfg["niches"]
    search = sum(len(x["ad_keywords"]) * len(x["source_countries"]) for x in n) * \
        cfg["search_pages"]
    adv = len(n) * cfg["advertisers_to_check"] * cfg["max_pages_per_advertiser"]
    tr = len(n) * cfg["winners_per_niche"] * cfg["creatives_per_winner"]
    org = sum(len(x.get("organic_keywords", [])) for x in n) * \
        (cfg["tiktok_pages"] + cfg["instagram_pages"])
    otr = len(n) * (cfg["tiktok_transcripts"] + cfg["instagram_transcripts"])
    return {"ad_search": search, "advertiser_pages_max": adv, "ad_transcripts_max": tr,
            "organic_search": org, "organic_transcripts_max": otr,
            "total_max": search + adv + tr + org + otr,
            "budget_cap": cfg["max_credits_per_run"]}


def cmd_estimate(args):
    cfg = json.load(open(args.config, encoding="utf-8"))
    print(json.dumps(estimate(cfg), indent=2))


def cmd_balance(args):
    key = load_key()
    status, body = http_get(f"{SC_BASE}/v1/credit/balance", {"x-api-key": key})
    print(f"HTTP {status}: {body.decode('utf-8', 'replace')[:500]}")


def cmd_scan(args):
    cfg = json.load(open(args.config, encoding="utf-8"))
    out = args.out
    os.makedirs(os.path.join(out, "landings"), exist_ok=True)
    sc = ScrapeCreators(load_key(), cfg["max_credits_per_run"], os.path.join(out, "raw"))
    state_path = os.path.join(os.path.dirname(os.path.abspath(args.config)), "state.json")
    state = load_state(state_path)
    today = dt.date.today().isoformat()
    dossier = {"generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "config": {k: v for k, v in cfg.items() if k != "niches"},
               "niches": [], "errors": [], "estimate": estimate(cfg)}
    company_cache = {}
    try:
        for niche in cfg["niches"]:
            log(f"Niche: {niche['name']}")
            nd = {"name": niche["name"], "notes": niche.get("notes"),
                  "source_countries": niche["source_countries"], "advertisers": [],
                  "organic": {"tiktok": [], "instagram": []}}
            dossier["niches"].append(nd)
            # 1) keyword search -> candidate advertisers
            hits = defaultdict(lambda: {"hits": 0, "keywords": set(), "countries": set(),
                                        "page_name": None})
            for kw in niche["ad_keywords"]:
                for c in niche["source_countries"]:
                    try:
                        ads = search_ads(sc, kw, c, cfg)
                    except ApiError as e:
                        dossier["errors"].append(f"search '{kw}' {c}: {e}")
                        continue
                    log(f"  search '{kw}' {c}: {len(ads)} ads")
                    for a in ads:
                        if not a["page_id"]:
                            continue
                        h = hits[(a["page_id"], c)]
                        h["hits"] += 1
                        h["keywords"].add(kw)
                        h["countries"].add(c)
                        h["page_name"] = a["page_name"]
            cands = sorted(hits.items(), key=lambda kv: -kv[1]["hits"])
            checked, seen_pages = 0, set()
            # 2) count active ads per advertiser
            for (page_id, country), h in cands:
                if checked >= cfg["advertisers_to_check"] or page_id in seen_pages:
                    continue
                if page_id in cfg.get("exclude_page_ids", []):
                    continue
                seen_pages.add(page_id)
                checked += 1
                try:
                    if (page_id, country) not in company_cache:
                        company_cache[(page_id, country)] = company_ads(sc, page_id, country, cfg)
                    ads, complete = company_cache[(page_id, country)]
                    ads = [dict(a) for a in ads]
                except ApiError as e:
                    dossier["errors"].append(f"company ads {page_id}: {e}")
                    continue
                summ = summarize_advertiser(ads, complete, cfg)
                prev = state["advertisers"].get(page_id)
                adv = {"page_id": page_id, "page_name": h["page_name"], "country": country,
                       "library_search_url": "https://www.facebook.com/ads/library/?active_status=active"
                       f"&ad_type=all&country={country}&view_all_page_id={page_id}",
                       "search_hits": h["hits"], "matched_keywords": sorted(h["keywords"]),
                       "first_seen": prev["first_seen"] if prev else today,
                       "is_new": prev is None, **summ}
                log(f"  {h['page_name']} ({country}): {summ['active_ads_counted']}"
                    f"{'+' if summ['count_is_lower_bound'] else ''} active ads")
                nd["advertisers"].append(adv)
            nd["advertisers"].sort(key=lambda a: (not a["meets_threshold"], -a["score"]))
            # 3) winners: landing + transcripts of the top creatives
            winners = [a for a in nd["advertisers"] if a["meets_threshold"]]
            for adv in winners[:cfg["winners_per_niche"]]:
                adv["is_winner"] = True
                if adv["top_landings"]:
                    url = adv["top_landings"][0][0]
                    adv["landing"] = capture_landing(
                        url, os.path.join(out, "landings", f"{adv['page_id']}.html"), cfg)
                for c in adv["creatives_ranked"][:cfg["creatives_per_winner"]]:
                    c["selected"] = True
                    if c["ad"]["format"] in ("VIDEO", "DCO", "DPA") or c["ad"]["video_url"]:
                        try:
                            t = sc.get("/v1/facebook/adLibrary/ad/transcript",
                                       id=c["ad"]["ad_id"], cache_max_age="7d")
                            c["transcript"] = (t.get("data") or {}).get("transcript")
                        except ApiError as e:
                            c["transcript_error"] = str(e)[:200]
                adv["creatives_ranked"] = adv["creatives_ranked"][:cfg["creatives_kept"]]
                state["advertisers"][adv["page_id"]] = {
                    "first_seen": adv["first_seen"], "last_seen": today,
                    "page_name": adv["page_name"], "ads": adv["active_ads_counted"]}
            for adv in nd["advertisers"]:
                if not adv.get("is_winner"):
                    adv["creatives_ranked"] = adv["creatives_ranked"][:1]
            # 4) organic ideas (TikTok + Instagram) for our own offer
            tk, ig = [], []
            for kw in niche.get("organic_keywords", []):
                try:
                    tk += tiktok_ideas(sc, kw, cfg)
                except ApiError as e:
                    dossier["errors"].append(f"tiktok '{kw}': {e}")
                try:
                    ig += instagram_ideas(sc, kw, cfg)
                except ApiError as e:
                    dossier["errors"].append(f"instagram '{kw}': {e}")
            tk = rank_organic(tk, "tiktok", cfg)[:cfg["organic_kept"]]
            ig = rank_organic(ig, "instagram", cfg)[:cfg["organic_kept"]]
            for it in tk[:cfg["tiktok_transcripts"]]:
                try:
                    t = sc.get("/v1/tiktok/video/transcript", url=it["url"],
                               use_ai_as_fallback="true" if (it["duration_s"] or 0) <= 120 else None)
                    it["transcript"] = t.get("transcript")
                except ApiError as e:
                    it["transcript_error"] = str(e)[:200]
            for it in ig[:cfg["instagram_transcripts"]]:
                if (it.get("duration_s") or 0) > 120:
                    it["transcript_error"] = "skipped: longer than 120 s"
                    continue
                try:
                    t = sc.get("/v2/instagram/media/transcript", url=it["url"], cache_max_age="7d")
                    it["transcript"] = " ".join(x.get("text") or "" for x in
                                                t.get("transcripts") or []).strip() or None
                except ApiError as e:
                    it["transcript_error"] = str(e)[:200]
            nd["organic"] = {"tiktok": tk, "instagram": ig}
            log(f"  organic: {len(tk)} TikTok, {len(ig)} Instagram kept")
    except BudgetExceeded as e:
        dossier["errors"].append(f"STOPPED EARLY: {e}")
        log(str(e))
    dossier["markets"] = world_bank(cfg["candidate_markets"])
    dossier["credits"] = {"spent_this_run": sc.spent, "api_calls": sc.calls,
                          "remaining_reported_by_api": sc.remaining}
    for nd in dossier["niches"]:
        for adv in nd["advertisers"]:
            for c in adv["creatives_ranked"]:
                c["ad"].pop("impression_rank", None)
    with open(os.path.join(out, "dossier.json"), "w", encoding="utf-8") as f:
        json.dump(dossier, f, ensure_ascii=False, indent=1, default=list)
    with open(os.path.join(out, "EVIDENCIA.md"), "w", encoding="utf-8") as f:
        f.write(evidence_md(dossier))
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
    log(f"Done. Credits spent: {sc.spent}. Remaining: {sc.remaining}. Out: {out}")


def fmt(n):
    return "—" if n is None else (f"{n:,.0f}" if isinstance(n, (int, float)) else str(n))


def evidence_md(d):
    L = [f"# Evidencia del espía — {d['generated_at'][:10]}", "",
         "Datos reales tomados de la Biblioteca de Anuncios de Meta, TikTok, Instagram y el "
         "Banco Mundial. Las respuestas originales están en `raw/`.", ""]
    for nd in d["niches"]:
        L += [f"## Nicho: {nd['name']}", "", "### Anunciantes revisados", "",
              "| Anunciante | País | Anuncios activos | Mediana días | Creativos distintos | "
              "Copias del top | Nuevo | Puntaje | Biblioteca |",
              "|---|---|---|---|---|---|---|---|---|"]
        for a in nd["advertisers"]:
            top = a["creatives_ranked"][0]["copies_running"] if a["creatives_ranked"] else 0
            count = f"{a['active_ads_counted']}{'+' if a['count_is_lower_bound'] else ''}"
            if a["threshold_status"].startswith("indeterminado"):
                count += " (indeterminado)"
            L.append(f"| {'★ ' if a.get('is_winner') else ''}{a['page_name']} | {a['country']} | "
                     f"{count} | "
                     f"{fmt(a['median_days_running'])} | {a['distinct_creatives']} | {top} | "
                     f"{'sí' if a['is_new'] else 'no'} | {a['score']} | "
                     f"[ver]({a['library_search_url']}) |")
        for a in [x for x in nd["advertisers"] if x.get("is_winner")]:
            L += ["", f"### ★ {a['page_name']} ({a['country']})", ""]
            lp = a.get("landing") or {}
            if lp:
                L += [f"- Landing: {lp.get('url')}", f"- Título: {lp.get('title')}",
                      f"- H1: {' / '.join(lp.get('h1') or [])}",
                      f"- Precios visibles: {', '.join(lp.get('prices_seen') or []) or 'ninguno'}",
                      f"- Ticket: {lp.get('ticket_guess')}"]
                if lp.get("error") or lp.get("note"):
                    L.append(f"- Aviso landing: {lp.get('error') or lp.get('note')}")
            for i, c in enumerate([x for x in a["creatives_ranked"] if x.get("selected")], 1):
                ad = c["ad"]
                L += ["", f"**Creativo {i}** — [{ad['ad_id']}]({ad['library_url']}) · "
                          f"{ad['format']} · {c['copies_running']} copias activas · "
                          f"hasta {fmt(c['max_days_running'])} días",
                      "", f"> {(ad['text'] or '').strip()[:1200]}", "",
                      f"- Título: {ad['title']} · CTA: {ad['cta']}",
                      f"- Transcripción: {(c.get('transcript') or c.get('transcript_error') or '—')[:2000]}"]
        L += ["", "### Ideas orgánicas", "", "| Red | Video | Vistas | Seguidores | Vistas/seguidor "
              "| Likes | Fecha |", "|---|---|---|---|---|---|---|"]
        for it in nd["organic"]["tiktok"] + nd["organic"]["instagram"]:
            ratio = it.get("views_per_follower", it.get("likes_per_follower"))
            L.append(f"| {it['platform']} | [{(it['caption'] or '')[:50]}]({it['url']}) | "
                     f"{fmt(it.get('plays'))} | {fmt(it['followers'])} | {ratio} | "
                     f"{fmt(it['likes'])} | {it['created']} |")
        L.append("")
    L += ["## Mercados (Banco Mundial)", "",
          "| País | Idioma | PIB per cápita PPA | Internet % | Población |", "|---|---|---|---|---|"]
    for r in d["markets"]["rows"]:
        L.append(f"| {r.get('name', r['country'])} | {r['main_language']} | "
                 f"{fmt(r.get('gdp_pc_ppp'))} ({r.get('gdp_pc_ppp_year', '—')}) | "
                 f"{fmt(r.get('internet_pct'))} | {fmt(r.get('population'))} |")
    L += ["", f"Créditos usados: {d['credits']['spent_this_run']} · restantes: "
              f"{d['credits']['remaining_reported_by_api']}", ""]
    if d["errors"]:
        L += ["## Errores", ""] + [f"- {e}" for e in d["errors"]]
    return "\n".join(L) + "\n"


REQUIRED_HEADINGS = ["## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6.", "## 7.", "## 8."]


def cmd_check_report(args):
    """Fail if the report is missing sections or cites ad/video ids not in the dossier."""
    d = json.load(open(os.path.join(args.run, "dossier.json"), encoding="utf-8"))
    rep = open(os.path.join(args.run, "REPORTE.md"), encoding="utf-8").read()
    known = set()
    for nd in d["niches"]:
        for a in nd["advertisers"]:
            known.add(a["page_id"])
            for c in a["creatives_ranked"]:
                known.add(c["ad"]["ad_id"])
                known.update(c.get("other_ad_ids") or [])
        for it in nd["organic"]["tiktok"] + nd["organic"]["instagram"]:
            known.add(str(it["id"]))
    problems = [f"missing section '{h}'" for h in REQUIRED_HEADINGS if h not in rep]
    for m in re.findall(r"ads/library/?\?id=(\d+)", rep):
        if m not in known:
            problems.append(f"ad id {m} cited but not in dossier")
    for m in re.findall(r"tiktok\.com/@[^/\s]+/video/(\d+)", rep):
        if m not in known:
            problems.append(f"TikTok video {m} cited but not in dossier")
    for m in re.findall(r"instagram\.com/(?:reel|p)/([A-Za-z0-9_-]+)", rep):
        if m not in known:
            problems.append(f"Instagram reel {m} cited but not in dossier")
    if problems:
        print("REPORT CHECK FAIL:\n- " + "\n- ".join(problems))
        sys.exit(1)
    print("REPORT CHECK OK")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan", help="collect today's evidence")
    s.add_argument("--config", required=True)
    s.add_argument("--out", required=True)
    s.set_defaults(fn=cmd_scan)
    e = sub.add_parser("estimate", help="max credits a scan can use with this config")
    e.add_argument("--config", required=True)
    e.set_defaults(fn=cmd_estimate)
    b = sub.add_parser("balance", help="check the API key and remaining credits")
    b.set_defaults(fn=cmd_balance)
    c = sub.add_parser("check-report", help="validate REPORTE.md against dossier.json")
    c.add_argument("--run", required=True)
    c.set_defaults(fn=cmd_check_report)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
