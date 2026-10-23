#!/usr/bin/env python3
"""Brain Storming: niche-expert operating system built on top of the Espia.

One niche, one avatar, many products and markets over the years. This tool does the
deterministic part (collect real data, keep the brain's history, compute metrics and
rules, validate proposals, publish to Meta within hard caps). The judgment part
(write the brain, propose products/creatives/markets) is done by Claude following
roles/*.md, and nothing is published without the owner's "publica <ID>".

Standard library only. Data lives OUTSIDE the repo (default ~/brain-data), versioned
with a local git repository and backed up to Google Drive.
"""
import argparse
import base64
import datetime as dt
import json
import math
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "espia-ofertas"))
import espia  # noqa: E402

DATA = os.path.expanduser(os.environ.get("BRAIN_DATA", "~/brain-data"))
META_TOKEN_FILE = os.path.expanduser("~/.config/brain/meta_token")
GRAPH_BASE = os.environ.get("GRAPH_BASE_URL", "https://graph.facebook.com")
GRAPH_VIDEO_BASE = os.environ.get("GRAPH_VIDEO_BASE_URL", "https://graph-video.facebook.com")
PURCHASE_TYPES = ["offsite_conversion.fb_pixel_purchase", "purchase", "omni_purchase"]
CTA_TYPES = {"LEARN_MORE", "SHOP_NOW", "SIGN_UP", "BUY_NOW", "GET_OFFER", "DOWNLOAD", "ORDER_NOW"}
PROPOSAL_TYPES = {"nuevo_producto", "variante_producto", "nuevo_mercado", "nuevos_creativos",
                  "escalar", "apagar", "ajuste_tienda"}
log = espia.log


# ---------------------------------------------------------------- helpers

def today():
    return dt.date.today().isoformat()


def jload(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def jsave(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def config():
    cfg = jload(os.path.join(DATA, "config.json"))
    if cfg is None:
        sys.exit(f"No config. Run: python3 brain.py init   (data dir: {DATA})")
    return cfg


def niche_dir(cfg, slug=None):
    slug = slug or cfg.get("nicho_activo")
    if not slug:
        sys.exit("No active niche. Use: python3 brain.py fijar-nicho ...")
    d = os.path.join(DATA, "cerebro", slug)
    if not os.path.isdir(d):
        sys.exit(f"Niche folder missing: {d}")
    return d


def niche(cfg):
    d = niche_dir(cfg)
    return d, jload(os.path.join(d, "nicho.json"))


def git_commit(msg):
    if not os.path.isdir(os.path.join(DATA, ".git")):
        return
    subprocess.run(["git", "-C", DATA, "add", "-A"], check=False)
    subprocess.run(["git", "-C", DATA, "commit", "-q", "-m", msg], check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def sc_client(cfg, budget, raw_dir):
    return espia.ScrapeCreators(espia.load_key(), budget, raw_dir)


# ---------------------------------------------------------------- init / niche

def cmd_init(args):
    os.makedirs(os.path.join(DATA, "cerebro"), exist_ok=True)
    os.makedirs(os.path.join(DATA, "nichos"), exist_ok=True)
    if not os.path.exists(os.path.join(DATA, "config.json")):
        shutil.copy(os.path.join(HERE, "config.example.json"), os.path.join(DATA, "config.json"))
        log("config.json created: edit it")
    if not os.path.exists(os.path.join(DATA, "candidatos.json")):
        shutil.copy(os.path.join(HERE, "candidatos.example.json"),
                    os.path.join(DATA, "candidatos.json"))
    shutil.copy(os.path.join(HERE, "plantillas", "CLAUDE.md"), os.path.join(DATA, "CLAUDE.md"))
    with open(os.path.join(DATA, ".gitignore"), "w") as f:
        f.write("**/raw/\n**/raw-seguimiento/\n**/landings/\n**/assets/\n*.tmp\n")
    if not os.path.isdir(os.path.join(DATA, ".git")):
        subprocess.run(["git", "init", "-q", DATA], check=True)
        subprocess.run(["git", "-C", DATA, "config", "user.name", "Brain Storming"], check=True)
        subprocess.run(["git", "-C", DATA, "config", "user.email", "brain@localhost"], check=True)
    git_commit("init")
    log(f"Ready: {DATA}")


def cmd_nichos(args):
    """Score candidate niches with real data (ad volume, longevity, blue-ocean ratio, organic)."""
    cfg = config()
    cand = jload(args.candidatos or os.path.join(DATA, "candidatos.json"))
    out = os.path.join(DATA, "nichos", today())
    os.makedirs(out, exist_ok=True)
    sc = sc_client(cfg, cfg["cazador"]["max_creditos"], os.path.join(out, "raw"))
    origin = cand["pais_origen"]
    rows = []
    try:
        for c in cand["candidatos"]:
            log(f"Candidate: {c['nombre']}")
            r = {"nombre": c["nombre"], "avatar": c.get("avatar"), "origen": origin,
                 "keywords_origen": c["keywords_origen"], "destinos": {}, "errores": []}
            days, advertisers, total = [], set(), 0
            for kw in c["keywords_origen"]:
                try:
                    d = sc.get("/v1/facebook/adLibrary/search/ads", query=kw, country=origin,
                               status="ACTIVE", sort_by="total_impressions")
                except espia.ApiError as e:
                    r["errores"].append(str(e)[:200])
                    continue
                total = max(total, d.get("searchResultsCount") or 0)  # keywords overlap: no sum
                for a in map(espia.normalize_ad, d.get("searchResults") or []):
                    advertisers.add(a["page_id"])
                    if a["days_running"] is not None:
                        days.append(a["days_running"])
            days.sort()
            r["origen_anuncios_activos"] = total
            r["origen_anunciantes_en_muestra"] = len(advertisers)
            r["origen_mediana_dias"] = days[len(days) // 2] if days else None
            r["origen_pct_mas_90_dias"] = round(sum(x >= 90 for x in days) / len(days), 2) \
                if days else None
            for iso, kws in c.get("destinos", {}).items():
                dtotal, dadv = 0, set()
                for kw in kws:
                    try:
                        d = sc.get("/v1/facebook/adLibrary/search/ads", query=kw, country=iso,
                                   status="ACTIVE", sort_by="total_impressions")
                    except espia.ApiError as e:
                        r["errores"].append(str(e)[:200])
                        continue
                    dtotal = max(dtotal, d.get("searchResultsCount") or 0)
                    dadv |= {a.get("page_id") for a in d.get("searchResults") or []}
                r["destinos"][iso] = {"keywords": kws, "anuncios_activos": dtotal,
                                      "anunciantes_en_muestra": len(dadv - {None}),
                                      "ratio_origen_destino": round((total + 1) / (dtotal + 1), 1)}
            plays, big = 0, 0
            for kw in c.get("organic_keywords", []):
                try:
                    items = espia.tiktok_ideas(sc, kw, {"tiktok_pages": 1,
                                                        "tiktok_date_posted": "last-6-months"})
                except espia.ApiError as e:
                    r["errores"].append(str(e)[:200])
                    continue
                plays += sum(i["plays"] or 0 for i in items)
                big += sum((i["plays"] or 0) >= 100000 for i in items)
            r["tiktok_vistas_muestra"] = plays
            r["tiktok_videos_100k"] = big
            best_ratio = max([v["ratio_origen_destino"] for v in r["destinos"].values()] or [1])
            parts = {
                "demanda": round(math.log10(1 + total), 2),
                "longevidad": round(3 * (r["origen_pct_mas_90_dias"] or 0) +
                                    min((r["origen_mediana_dias"] or 0) / 90, 2), 2),
                "oceano_azul": round(math.log10(best_ratio), 2),
                "organico": round(math.log10(1 + plays) / 2, 2),
            }
            r["puntaje_partes"] = parts
            r["puntaje"] = round(sum(parts.values()), 2)
            rows.append(r)
    except espia.BudgetExceeded as e:
        log(str(e))
    rows.sort(key=lambda x: -x["puntaje"])
    res = {"fecha": today(), "pais_origen": origin, "candidatos": rows,
           "formula": "demanda=log10(anuncios origen, máx. entre palabras) + longevidad=3*pct>90d + min(mediana/90,2) "
                      "+ oceano_azul=log10(mejor ratio origen/destino) + organico=log10(vistas TikTok)/2",
           "nota": "searchResultsCount puede venir topado (p. ej. 50001 = 50.000+).",
           "creditos": {"usados": sc.spent, "restantes": sc.remaining}}
    jsave(os.path.join(out, "scorecard.json"), res)
    L = [f"# Scorecard de nichos — {today()} (origen {origin})", "",
         "| # | Nicho | Puntaje | Anuncios origen | Mediana días | % >90 días | Mejor destino (ratio) "
         "| TikTok vistas |", "|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        best = max(r["destinos"].items(), key=lambda kv: kv[1]["ratio_origen_destino"],
                   default=(None, {}))
        L.append(f"| {i} | {r['nombre']} | {r['puntaje']} | {espia.fmt(r['origen_anuncios_activos'])}"
                 f" | {espia.fmt(r['origen_mediana_dias'])} | {r['origen_pct_mas_90_dias']} | "
                 f"{best[0]} ({best[1].get('ratio_origen_destino')}) | "
                 f"{espia.fmt(r['tiktok_vistas_muestra'])} |")
    L += ["", f"Fórmula: {res['formula']}", "", f"Nota: {res['nota']}",
          f"Créditos usados: {sc.spent}"]
    open(os.path.join(out, "SCORECARD.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    log(f"Scorecard: {out}/SCORECARD.md")


def cmd_fijar_nicho(args):
    cfg = config()
    sc_path = os.path.join(DATA, "nichos", args.fecha, "scorecard.json")
    card = jload(sc_path)
    if not card:
        sys.exit(f"No scorecard at {sc_path}")
    match = [c for c in card["candidatos"] if c["nombre"] == args.nombre]
    if not match:
        sys.exit("Candidate name not found. Options: " +
                 ", ".join(c["nombre"] for c in card["candidatos"]))
    c = match[0]
    cand = {x["nombre"]: x for x in jload(os.path.join(DATA, "candidatos.json"))["candidatos"]}
    src = cand.get(c["nombre"], {})
    slug = args.slug
    d = os.path.join(DATA, "cerebro", slug)
    if os.path.exists(d):
        sys.exit(f"{d} already exists")
    shutil.copytree(os.path.join(HERE, "plantillas", "cerebro"), d)
    for sub in ("diario", "propuestas", "assets", "historial"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    nj = {
        "slug": slug, "nombre": c["nombre"], "avatar": c.get("avatar"),
        "fijado": today(), "scorecard": os.path.relpath(sc_path, DATA),
        "origen": {"paises": [card["pais_origen"]], "keywords": c["keywords_origen"]},
        "organic_keywords": src.get("organic_keywords", []),
        "mercados": {iso: {"keywords": v["keywords"], "estado": "pendiente",
                           "idioma": espia.COUNTRY_LANG.get(iso, "?")}
                     for iso, v in c["destinos"].items()},
        "seguimiento_page_ids": [], "excluir_page_ids": [],
        "tienda": {"store_id": "", "nombre": ""},
        "meta": {"ad_account_id": "", "page_id": "", "pixel_id": "", "instagram_user_id": ""},
        "cpa_objetivo_usd": cfg["reglas"]["cpa_objetivo_usd_por_defecto"],
    }
    jsave(os.path.join(d, "nicho.json"), nj)
    cfg["nicho_activo"] = slug
    jsave(os.path.join(DATA, "config.json"), cfg)
    with open(os.path.join(d, "DECISIONES.md"), "a", encoding="utf-8") as f:
        f.write(f"\n- {today()} · Nicho fijado: **{c['nombre']}** (puntaje {c['puntaje']}, "
                f"scorecard `{nj['scorecard']}`).\n")
    git_commit(f"fijar nicho {slug}")
    log(f"Active niche: {slug} -> {d}. Complete tienda/meta in nicho.json.")


# ---------------------------------------------------------------- daily intel

def espia_config(cfg, nj):
    e = dict(cfg["espia"])
    e["niches"] = [{"name": nj["nombre"], "notes": nj.get("avatar"),
                    "source_countries": nj["origen"]["paises"],
                    "ad_keywords": nj["origen"]["keywords"],
                    "organic_keywords": nj.get("organic_keywords", [])}]
    e["candidate_markets"] = sorted(set(nj["mercados"]) | set(cfg.get("mercados_extra", [])))
    e["exclude_page_ids"] = nj.get("excluir_page_ids", []) + \
        ([nj["meta"]["page_id"]] if nj["meta"].get("page_id") else [])
    e["drive_folder"] = ""
    return e


def track(history_path, key, row, meta):
    h = jload(history_path, {})
    item = h.setdefault(key, {**meta, "historial": []})
    item.update(meta)
    item["historial"] = [x for x in item["historial"] if x["fecha"] != row["fecha"]] + [row]
    jsave(history_path, h)
    return item


def trend(hist, field, days=7):
    pts = [x for x in hist if x.get(field) is not None][-days:]
    if len(pts) < 2:
        return None
    return pts[-1][field] - pts[0][field]


def cmd_diario(args):
    cfg = config()
    d, nj = niche(cfg)
    day = os.path.join(d, "diario", args.fecha or today())
    os.makedirs(day, exist_ok=True)
    # 1) Espia scan for the fixed niche
    ecfg_path = os.path.join(d, "espia-config.json")
    jsave(ecfg_path, espia_config(cfg, nj))
    espia.cmd_scan(argparse.Namespace(config=ecfg_path, out=day))
    dossier = jload(os.path.join(day, "dossier.json"))
    # 2) competitor + market history
    sc = sc_client(cfg, cfg["seguimiento"]["max_creditos"], os.path.join(day, "raw-seguimiento"))
    comp_path = os.path.join(d, "COMPETIDORES.json")
    fecha = args.fecha or today()
    seen = set()
    for nd in dossier["niches"]:
        for a in nd["advertisers"]:
            seen.add(a["page_id"])
            track(comp_path, a["page_id"], {
                "fecha": fecha, "anuncios_activos": a["active_ads_counted"],
                "es_minimo": a["count_is_lower_bound"], "mediana_dias": a["median_days_running"],
                "creativos_distintos": a["distinct_creatives"]},
                {"nombre": a["page_name"], "pais": a["country"],
                 "biblioteca": a["library_search_url"]})
    errors = []
    try:
        for pid in nj.get("seguimiento_page_ids", []):
            if pid in seen:
                continue
            country = nj["origen"]["paises"][0]
            try:
                ads, complete = espia.company_ads(sc, pid, country, cfg["espia"])
            except espia.ApiError as e:
                errors.append(f"seguimiento {pid}: {e}")
                continue
            s = espia.summarize_advertiser(ads, complete, cfg["espia"])
            track(comp_path, pid, {"fecha": fecha, "anuncios_activos": s["active_ads_counted"],
                                   "es_minimo": s["count_is_lower_bound"],
                                   "mediana_dias": s["median_days_running"],
                                   "creativos_distintos": s["distinct_creatives"]},
                  {"nombre": ads[0]["page_name"] if ads else pid, "pais": country,
                   "biblioteca": "https://www.facebook.com/ads/library/?active_status=active&ad_type=all"
                                 f"&country={country}&view_all_page_id={pid}"})
        mk_path = os.path.join(d, "MERCADOS.json")
        for iso, m in nj["mercados"].items():
            for kw in m["keywords"][:cfg["seguimiento"]["keywords_por_mercado"]]:
                try:
                    r = sc.get("/v1/facebook/adLibrary/search/ads", query=kw, country=iso,
                               status="ACTIVE", sort_by="total_impressions")
                except espia.ApiError as e:
                    errors.append(f"mercado {iso} '{kw}': {e}")
                    continue
                ads = [espia.normalize_ad(a) for a in r.get("searchResults") or []]
                names = defaultdict(int)
                for a in ads:
                    names[a["page_name"]] += 1
                track(mk_path, f"{iso}|{kw}", {
                    "fecha": fecha, "anuncios_activos": r.get("searchResultsCount"),
                    "anunciantes_en_muestra": len(names),
                    "top_anunciantes": sorted(names.items(), key=lambda kv: -kv[1])[:5]},
                    {"pais": iso, "keyword": kw, "estado": m.get("estado"),
                     "biblioteca": "https://www.facebook.com/ads/library/?active_status=active"
                                   f"&ad_type=all&country={iso}&q={urllib.parse.quote(kw)}"})
    except espia.BudgetExceeded as e:
        errors.append(f"seguimiento detenido: {e}")
    # 3) own results (Meta) + rules -> automatic proposals
    met = None
    if nj["meta"].get("ad_account_id") and os.path.exists(META_TOKEN_FILE):
        try:
            met = metrics(cfg, nj, d, day, fecha)
        except Exception as e:  # keep the daily run alive; report the error
            errors.append(f"metricas Meta: {e}")
    else:
        errors.append("metricas Meta: sin configurar (nicho.json meta.ad_account_id + token)")
    jsave(os.path.join(day, "seguimiento.json"), {
        "errores": errors, "creditos_seguimiento": sc.spent,
        "creditos_espia": dossier.get("credits"), "metricas": bool(met)})
    write_summary(cfg, nj, d, day, fecha, errors)
    git_commit(f"diario {nj['slug']} {fecha}")
    log(f"Daily data ready: {day}")


def write_summary(cfg, nj, d, day, fecha, errors):
    comp = jload(os.path.join(d, "COMPETIDORES.json"), {})
    mk = jload(os.path.join(d, "MERCADOS.json"), {})
    L = [f"# Datos del día — {nj['nombre']} — {fecha}", "",
         "Generado por `brain.py diario`. Todo sale de `dossier.json`, `COMPETIDORES.json`, "
         "`MERCADOS.json`, `metricas.json` y `senales.json`.", "",
         "## Competidores (historial)", "",
         "| Anunciante | País | Anuncios hoy | Cambio 7 días | Mediana días | Biblioteca |",
         "|---|---|---|---|---|---|"]
    for pid, c in sorted(comp.items(), key=lambda kv: -(kv[1]["historial"][-1]["anuncios_activos"]
                                                        or 0)):
        last = c["historial"][-1]
        if last["fecha"] != fecha:
            continue
        t = trend(c["historial"], "anuncios_activos")
        L.append(f"| {c['nombre']} | {c['pais']} | {last['anuncios_activos']}"
                 f"{'+' if last['es_minimo'] else ''} | {'—' if t is None else f'{t:+}'} | "
                 f"{espia.fmt(last['mediana_dias'])} | [ver]({c['biblioteca']}) |")
    L += ["", "## Competencia por mercado de destino", "",
          "| Mercado | Palabra | Estado | Anuncios activos | Cambio 7 días | Anunciantes en muestra "
          "| Biblioteca |", "|---|---|---|---|---|---|---|"]
    for k, m in mk.items():
        last = m["historial"][-1]
        if last["fecha"] != fecha:
            continue
        t = trend(m["historial"], "anuncios_activos")
        L.append(f"| {m['pais']} | {m['keyword']} | {m.get('estado')} | "
                 f"{espia.fmt(last['anuncios_activos'])} | {'—' if t is None else f'{t:+}'} | "
                 f"{last['anunciantes_en_muestra']} | [ver]({m['biblioteca']}) |")
    met = jload(os.path.join(day, "metricas.json"))
    L += ["", "## Nuestros resultados (Meta, últimos 7 días)", ""]
    if met:
        t = met["totales_7d"]
        L += [f"- Gasto: {t['gasto']} · Compras: {t['compras']} · Ingresos atribuidos: "
              f"{t['ingresos']} · CPA: {t['cpa']} · ROAS: {t['roas']} (moneda de la cuenta: "
              f"{met.get('moneda')})", "",
              "| Anuncio | Ángulo | Mercado | Gasto 7d | Compras 7d | CPA | CTR % | Gancho % |",
              "|---|---|---|---|---|---|---|---|"]
        for a in met["anuncios"]:
            L.append(f"| {a['ad_name'].replace('|', ' / ')} | {a['angulo']} | {a['mercado']} | "
                     f"{a['gasto']} | {a['compras']:g} | {'—' if a['cpa'] is None else a['cpa']} | {a['ctr']} | "
                     f"{a['hook_rate']} |")
    else:
        L.append("Sin métricas de Meta hoy (ver errores).")
    sen = jload(os.path.join(day, "senales.json"), [])
    L += ["", "## Señales automáticas (reglas fijas de config.json)", ""]
    L += [f"- **{s['accion'].upper()}** {s['objeto']} — {s['motivo']} → propuesta {s['propuesta']}"
          for s in sen] or ["- Ninguna."]
    if os.path.exists(os.path.join(d, "ESTADISTICAS.md")):
        L += ["", "Estadísticas acumuladas por ángulo / mercado / producto: `ESTADISTICAS.md`."]
    if errors:
        L += ["", "## Errores", ""] + [f"- {e}" for e in errors]
    open(os.path.join(day, "DATOS-DEL-DIA.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


# ---------------------------------------------------------------- Meta Graph API

class Meta:
    def __init__(self, cfg, dry_run=False, logf=None):
        self.version = cfg["meta"]["graph_version"]
        self.dry_run = dry_run
        self.logf = logf
        try:
            self.token = open(META_TOKEN_FILE, encoding="utf-8").read().strip()
        except OSError:
            sys.exit(f"Missing Meta token: {META_TOKEN_FILE}")

    def _record(self, method, path, params, result):
        if self.logf:
            safe = {k: v for k, v in params.items() if k not in ("access_token", "bytes")}
            with open(self.logf, "a", encoding="utf-8") as f:
                f.write(json.dumps({"t": dt.datetime.now().isoformat(timespec="seconds"),
                                    "method": method, "path": path, "params": safe,
                                    "result": result}, ensure_ascii=False) + "\n")

    def _call(self, method, path, params, base=None):
        url = f"{base or GRAPH_BASE}/{self.version}/{path.lstrip('/')}"
        params = {k: (json.dumps(v) if isinstance(v, (dict, list, bool)) else v)
                  for k, v in params.items() if v is not None}
        params["access_token"] = self.token
        if method == "GET":
            req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params))
        else:
            req = urllib.request.Request(url, data=urllib.parse.urlencode(params).encode(),
                                         method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                out = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            raise RuntimeError(f"Meta {method} {path}: HTTP {e.code}: {body[:400]}")
        return out

    def get(self, path, **params):
        return self._call("GET", path, params)

    def get_all(self, path, **params):
        out, data = [], self._call("GET", path, params)
        while True:
            out += data.get("data", [])
            nxt = (data.get("paging") or {}).get("next")
            if not nxt:
                return out
            with urllib.request.urlopen(nxt, timeout=120) as r:
                data = json.loads(r.read().decode())

    def post(self, path, **params):
        if self.dry_run:
            fake = {"id": f"DRYRUN-{uuid.uuid4().hex[:8]}"}
            self._record("POST(dry-run)", path, params, fake)
            return fake
        res = self._call("POST", path, params)
        self._record("POST", path, params, res)
        return res

    def upload_video(self, account, path, name):
        if self.dry_run:
            return {"id": f"DRYRUN-video-{uuid.uuid4().hex[:6]}"}
        boundary = uuid.uuid4().hex
        body = []
        for k, v in (("access_token", self.token), ("name", name)):
            body += [f"--{boundary}", f'Content-Disposition: form-data; name="{k}"', "", v]
        head = "\r\n".join(body + [f"--{boundary}",
                                   f'Content-Disposition: form-data; name="source"; '
                                   f'filename="{os.path.basename(path)}"',
                                   f"Content-Type: {mimetypes.guess_type(path)[0] or 'video/mp4'}",
                                   "", ""]).encode()
        data = head + open(path, "rb").read() + f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(
            f"{GRAPH_VIDEO_BASE}/{self.version}/{account}/advideos", data=data, method="POST",
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                res = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Meta video upload: HTTP {e.code}: {e.read()[:400]!r}")
        self._record("POST", f"{account}/advideos", {"name": name}, res)
        return res


def ad_name_parts(name):
    """Naming convention BS|<proposal>|<angle>|<market>|<product>|<creative>."""
    p = (name or "").split("|")
    if len(p) >= 6 and p[0] == "BS":
        return {"propuesta": p[1], "angulo": p[2], "mercado": p[3], "producto": p[4],
                "creativo": p[5]}
    return {"propuesta": "-", "angulo": "(sin convención)", "mercado": "-", "producto": "-",
            "creativo": "-"}


def first_action(actions, types):
    by = {a.get("action_type"): float(a.get("value") or 0) for a in actions or []}
    for t in types:
        if t in by:
            return by[t]
    return 0.0


def rnd(x, n=2):
    return None if x is None else round(x, n)


def metrics(cfg, nj, d, day, fecha):
    m = Meta(cfg)
    acct = nj["meta"]["ad_account_id"]
    info = m.get(acct, fields="currency,name,account_status")
    rows = m.get_all(f"{acct}/insights", level="ad", date_preset="last_7d", time_increment=1,
                     limit=500, fields="date_start,ad_id,ad_name,adset_id,campaign_id,spend,"
                     "impressions,inline_link_clicks,actions,action_values")
    perf_path = os.path.join(d, "RENDIMIENTO.json")
    perf = jload(perf_path, {})
    for r in rows:
        item = perf.setdefault(r["ad_id"], {"ad_name": r.get("ad_name"), "adset_id": r.get("adset_id"),
                                            "campaign_id": r.get("campaign_id"), "dias": {}})
        item["ad_name"] = r.get("ad_name")
        item["dias"][r["date_start"]] = {
            "gasto": float(r.get("spend") or 0), "impresiones": int(r.get("impressions") or 0),
            "clics": int(r.get("inline_link_clicks") or 0),
            "compras": first_action(r.get("actions"), PURCHASE_TYPES),
            "ingresos": first_action(r.get("action_values"), PURCHASE_TYPES),
            "vistas_3s": first_action(r.get("actions"), ["video_view"])}
    jsave(perf_path, perf)
    cutoff7 = (dt.date.fromisoformat(fecha) - dt.timedelta(days=7)).isoformat()
    cutoff3 = (dt.date.fromisoformat(fecha) - dt.timedelta(days=3)).isoformat()

    def agg(days, since):  # [since, fecha): last_7d insights end yesterday
        s = defaultdict(float)
        for k, v in days.items():
            if since <= k < fecha:
                for f, x in v.items():
                    s[f] += x
        return s

    ads, tot = [], defaultdict(float)
    for ad_id, item in perf.items():
        s7, s3 = agg(item["dias"], cutoff7), agg(item["dias"], cutoff3)
        life = defaultdict(float)
        for v in item["dias"].values():
            for f, x in v.items():
                life[f] += x
        if not s7["impresiones"]:
            continue
        parts = ad_name_parts(item["ad_name"])
        a = {"ad_id": ad_id, "ad_name": item["ad_name"], "adset_id": item["adset_id"], **parts,
             "gasto": rnd(s7["gasto"]), "compras": s7["compras"], "ingresos": rnd(s7["ingresos"]),
             "cpa": rnd(s7["gasto"] / s7["compras"]) if s7["compras"] else None,
             "ctr": rnd(100 * s7["clics"] / s7["impresiones"]),
             "hook_rate": rnd(100 * s7["vistas_3s"] / s7["impresiones"]),
             "impresiones": int(s7["impresiones"]),
             "gasto_3d": rnd(s3["gasto"]), "compras_3d": s3["compras"],
             "gasto_total": rnd(life["gasto"]), "compras_total": life["compras"]}
        ads.append(a)
        for f in ("gasto", "compras", "ingresos"):
            tot[f] += s7[f]
    totals = {"gasto": rnd(tot["gasto"]), "compras": tot["compras"], "ingresos": rnd(tot["ingresos"]),
              "cpa": rnd(tot["gasto"] / tot["compras"]) if tot["compras"] else None,
              "roas": rnd(tot["ingresos"] / tot["gasto"]) if tot["gasto"] else None}
    met = {"fecha": fecha, "cuenta": info.get("name"), "moneda": info.get("currency"),
           "estado_cuenta": info.get("account_status"), "totales_7d": totals,
           "anuncios": sorted(ads, key=lambda a: -(a["gasto"] or 0))}
    jsave(os.path.join(day, "metricas.json"), met)
    stats_md(perf, d)
    signals(cfg, nj, d, day, fecha, met)
    return met


def stats_md(perf, d):
    """Lifetime performance grouped by angle / market / product: what the brain learns from."""
    groups = {"angulo": defaultdict(lambda: defaultdict(float)),
              "mercado": defaultdict(lambda: defaultdict(float)),
              "producto": defaultdict(lambda: defaultdict(float))}
    for item in perf.values():
        parts = ad_name_parts(item["ad_name"])
        for day in item["dias"].values():
            for g in groups:
                for f, x in day.items():
                    groups[g][parts[g]][f] += x
    L = ["# Estadísticas acumuladas (toda la vida, de RENDIMIENTO.json)", "",
         "Generado por `brain.py`. No editar a mano.", ""]
    for g, rows in groups.items():
        L += [f"## Por {g}", "", f"| {g} | Gasto | Compras | CPA | Ingresos | ROAS | CTR % |",
              "|---|---|---|---|---|---|---|"]
        for k, s in sorted(rows.items(), key=lambda kv: -kv[1]["gasto"]):
            cpa = rnd(s["gasto"] / s["compras"]) if s["compras"] else "—"
            roas = rnd(s["ingresos"] / s["gasto"]) if s["gasto"] else "—"
            ctr = rnd(100 * s["clics"] / s["impresiones"]) if s["impresiones"] else "—"
            L.append(f"| {k} | {rnd(s['gasto'])} | {s['compras']:g} | {cpa} | "
                     f"{rnd(s['ingresos'])} | {roas} | {ctr} |")
        L.append("")
    open(os.path.join(d, "ESTADISTICAS.md"), "w", encoding="utf-8").write("\n".join(L))


def signals(cfg, nj, d, day, fecha, met):
    r = cfg["reglas"]
    target = nj.get("cpa_objetivo_usd") or r["cpa_objetivo_usd_por_defecto"]
    out = []
    pending, done = set(), {}
    for p in proposals(d):
        if p["tipo"] in ("apagar", "escalar"):
            if p["estado"] in ("pendiente", "preparada", "error"):
                pending.add((p.get("objeto"), p["tipo"]))
            elif p["estado"] in ("publicada", "rechazada"):
                key = (p.get("objeto"), p["tipo"])
                done[key] = max(done.get(key, ""), (p.get("resultado") or {}).get("fecha", "")[:10]
                                or (p.get("rechazo") or {}).get("fecha", "") or p.get("creada", ""))
    since3 = (dt.date.fromisoformat(fecha) - dt.timedelta(days=3)).isoformat()
    for a in met["anuncios"]:
        reason = None
        if a["compras_total"] == 0 and a["gasto_total"] >= r["apagar_sin_compras_x_cpa"] * target:
            reason = (f"gastó {a['gasto_total']} (≥ {r['apagar_sin_compras_x_cpa']}× CPA objetivo "
                      f"{target}) sin compras")
            action = "apagar"
        elif a["cpa"] and a["gasto"] >= r["apagar_cpa_alto_min_gasto_x_cpa"] * target and \
                a["cpa"] > r["apagar_cpa_alto_x"] * target:
            reason = f"CPA 7d {a['cpa']} > {r['apagar_cpa_alto_x']}× objetivo {target}"
            action = "apagar"
        elif a["compras_3d"] >= r["escalar_min_compras_3d"] and a["gasto_3d"] and \
                a["gasto_3d"] / a["compras_3d"] <= target:
            reason = (f"{a['compras_3d']:g} compras en 3 días con CPA "
                      f"{rnd(a['gasto_3d'] / a['compras_3d'])} ≤ objetivo {target}")
            action = "escalar"
        if not reason:
            continue
        objeto = a["ad_id"] if action == "apagar" else a["adset_id"]
        if (objeto, action) in pending:
            continue
        if action == "apagar" and (objeto, "apagar") in done:
            continue  # already paused (or the owner said no): never ask again
        if action == "escalar" and done.get((objeto, "escalar"), "") >= since3:
            continue  # scaled or rejected in the last 3 days: let it stabilize
        pid = new_proposal_id(d)
        prop = {"id": pid, "tipo": action, "estado": "pendiente", "creada": fecha,
                "origen": "regla automática", "objeto": objeto,
                "resumen": f"{action.upper()} {a['ad_name']}: {reason}",
                "evidencia": [f"metricas.json {fecha}: ad {a['ad_id']}"],
                "meta": {"escalar_pct": r["escalar_pct"]} if action == "escalar" else {}}
        jsave(os.path.join(d, "propuestas", f"{pid}.json"), prop)
        pending.add((objeto, action))
        out.append({"accion": action, "objeto": f"{a['ad_name']} ({objeto})", "motivo": reason,
                    "propuesta": pid})
    jsave(os.path.join(day, "senales.json"), out)


# ---------------------------------------------------------------- proposals

def proposals(d):
    pdir = os.path.join(d, "propuestas")
    out = []
    for f in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
        if f.endswith(".json"):
            p = jload(os.path.join(pdir, f))
            if p:
                out.append(p)
    return out


def new_proposal_id(d):
    base = "P-" + dt.date.today().strftime("%Y%m%d")
    nums = [int(m.group(1)) for p in proposals(d)
            for m in [re.fullmatch(re.escape(base) + r"-(\d+)", p["id"])] if m]
    return f"{base}-{max(nums, default=0) + 1:02d}"


def load_proposal(d, pid):
    path = os.path.join(d, "propuestas", f"{pid}.json")
    p = jload(path)
    if not p:
        sys.exit(f"Proposal not found: {pid}")
    return path, p


def validate_proposal(cfg, nj, p, known_ids):
    errs = []
    if p.get("tipo") not in PROPOSAL_TYPES:
        errs.append(f"tipo inválido: {p.get('tipo')}")
    for k in ("id", "estado", "resumen", "evidencia"):
        if not p.get(k):
            errs.append(f"falta '{k}'")
    lim = cfg["limites"]
    meta = p.get("meta") or {}
    if p.get("tipo") in ("nuevo_producto", "variante_producto", "nuevo_mercado", "nuevos_creativos"):
        if not meta.get("anuncios"):
            errs.append("faltan meta.anuncios")
        if not meta.get("paises"):
            errs.append("faltan meta.paises")
        for iso in meta.get("paises", []):
            if iso not in nj["mercados"] and iso not in nj["origen"]["paises"]:
                errs.append(f"país {iso} no está en los mercados del nicho")
        b = meta.get("presupuesto_diario_usd", 0)
        if not 0 < b <= lim["max_presupuesto_diario_por_conjunto_usd"]:
            errs.append(f"presupuesto_diario_usd {b} fuera de (0, "
                        f"{lim['max_presupuesto_diario_por_conjunto_usd']}]")
        for i, a in enumerate(meta.get("anuncios", [])):
            for k in ("angulo", "creativo", "texto", "titulo", "cta", "formato"):
                if not a.get(k):
                    errs.append(f"anuncio {i + 1}: falta '{k}'")
            if a.get("cta") and a["cta"] not in CTA_TYPES:
                errs.append(f"anuncio {i + 1}: cta {a['cta']} no permitido {sorted(CTA_TYPES)}")
            for k in ("angulo", "creativo"):
                if "|" in (a.get(k) or ""):
                    errs.append(f"anuncio {i + 1}: '{k}' no puede llevar '|'")
    text = json.dumps(p, ensure_ascii=False)
    for m in re.findall(r"ads/library/?\?id=(\d+)", text):
        if m not in known_ids:
            errs.append(f"cita el anuncio {m}, que no está en los datos")
    for m in re.findall(r"tiktok\.com/@[^/\s\"]+/video/(\d+)", text):
        if m not in known_ids:
            errs.append(f"cita el TikTok {m}, que no está en los datos")
    for m in re.findall(r"instagram\.com/(?:reel|p)/([A-Za-z0-9_-]+)", text):
        if m not in known_ids:
            errs.append(f"cita el reel {m}, que no está en los datos")
    return errs


def known_ids_for(d):
    ids = set()
    ddir = os.path.join(d, "diario")
    for day in os.listdir(ddir) if os.path.isdir(ddir) else []:
        ds = jload(os.path.join(ddir, day, "dossier.json"))
        if not ds:
            continue
        for nd in ds["niches"]:
            for a in nd["advertisers"]:
                ids.add(a["page_id"])
                for c in a["creatives_ranked"]:
                    ids.add(c["ad"]["ad_id"])
                    ids.update(c.get("other_ad_ids") or [])
            for it in nd["organic"]["tiktok"] + nd["organic"]["instagram"]:
                ids.add(str(it["id"]))
    return ids


def cmd_verificar(args):
    """Validate today's proposals and report: sections, schema, caps, cited evidence."""
    cfg = config()
    d, nj = niche(cfg)
    fecha = args.fecha or today()
    day = os.path.join(d, "diario", fecha)
    known = known_ids_for(d)
    problems = []
    rep_path = os.path.join(day, "REPORTE.md")
    if not os.path.exists(rep_path):
        problems.append("falta REPORTE.md")
    else:
        rep = open(rep_path, encoding="utf-8").read()
        for h in ["## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."]:
            if h not in rep:
                problems.append(f"REPORTE.md: falta la sección '{h}'")
        problems += [f"REPORTE.md: {e}" for e in validate_proposal(
            cfg, nj, {"id": "x", "tipo": "ajuste_tienda", "estado": "x", "resumen": "x",
                      "evidencia": ["x"], "texto": rep}, known) if "cita" in e]
    todays = [p for p in proposals(d) if p.get("creada") == fecha and p.get("origen") != "regla automática"]
    if len(todays) > cfg["limites"]["max_propuestas_por_dia"]:
        problems.append(f"{len(todays)} propuestas hoy (máx. {cfg['limites']['max_propuestas_por_dia']})")
    for p in todays:
        problems += [f"{p.get('id')}: {e}" for e in validate_proposal(cfg, nj, p, known)]
    if problems:
        print("VERIFICACION FAIL:\n- " + "\n- ".join(problems))
        sys.exit(1)
    print(f"VERIFICACION OK ({len(todays)} propuestas)")


def cmd_cola(args):
    cfg = config()
    d, nj = niche(cfg)
    ps = [p for p in proposals(d) if args.todas or p["estado"] in ("pendiente", "preparada", "error")]
    if not ps:
        print("No hay propuestas pendientes.")
    for p in ps:
        meta = p.get("meta") or {}
        falta = [a.get("creativo") for a in meta.get("anuncios", []) if not a.get("media")]
        print(f"{p['id']} [{p['estado']}] {p['tipo']}: {p['resumen']}"
              + (f" · presupuesto {meta.get('presupuesto_diario_usd')}/día en {meta.get('paises')}"
                 if meta.get("paises") else "")
              + (f" · sin medios: {', '.join(falta)}" if falta else ""))


def cmd_rechaza(args):
    cfg = config()
    d, nj = niche(cfg)
    path, p = load_proposal(d, args.id)
    p["estado"] = "rechazada"
    p["rechazo"] = {"fecha": today(), "motivo": args.motivo}
    jsave(path, p)
    with open(os.path.join(d, "DECISIONES.md"), "a", encoding="utf-8") as f:
        f.write(f"\n- {today()} · RECHAZADA {p['id']} ({p['tipo']}: {p['resumen']}). "
                f"Motivo del dueño: {args.motivo}\n")
    git_commit(f"rechaza {p['id']}")
    print(f"{p['id']} rechazada. El motivo quedó en DECISIONES.md para que el cerebro aprenda.")


def cmd_set(args):
    """Record data produced while publishing: landing link, media files, ImpulTienda ids."""
    cfg = config()
    d, nj = niche(cfg)
    path, p = load_proposal(d, args.id)
    meta = p.setdefault("meta", {})
    if args.link:
        if not args.link.startswith("https://"):
            sys.exit("link must be https://")
        meta["link"] = args.link
    if args.media:
        idx, fpath = args.media
        fpath = os.path.abspath(fpath)
        if not os.path.exists(fpath):
            sys.exit(f"media file not found: {fpath}")
        meta["anuncios"][int(idx) - 1]["media"] = fpath
    if args.tienda:
        p.setdefault("resultado", {})["impultienda"] = json.loads(args.tienda)
    if args.estado:
        p["estado"] = args.estado
    jsave(path, p)
    print(json.dumps({k: p.get(k) for k in ("id", "estado")} | {"link": meta.get("link")},
                     ensure_ascii=False))


# ---------------------------------------------------------------- publish (Meta)

def cmd_publica(args):
    cfg = config()
    d, nj = niche(cfg)
    path, p = load_proposal(d, args.id)
    if p["estado"] in ("publicada", "rechazada"):
        sys.exit(f"{p['id']} is already {p['estado']}")
    errs = validate_proposal(cfg, nj, p, known_ids_for(d)) if p.get("origen") != "regla automática" \
        else []
    if errs:
        sys.exit("Proposal invalid:\n- " + "\n- ".join(errs))
    logf = os.path.join(d, "propuestas", f"{p['id']}.meta-log.jsonl")
    m = Meta(cfg, dry_run=args.dry_run, logf=logf)
    acct = nj["meta"]["ad_account_id"]
    if args.dry_run:  # simulate on a throwaway copy: fake ids must never be saved
        p = json.loads(json.dumps(p))
    res = p.setdefault("resultado", {})
    res.pop("error", None)
    try:
        if p["tipo"] == "apagar":
            m.post(p["objeto"], status="PAUSED")
            res["apagado"] = p["objeto"]
        elif p["tipo"] == "escalar":
            cur = m.get(p["objeto"], fields="daily_budget,name")
            old = int(cur.get("daily_budget") or 0)
            cap = int(cfg["limites"]["max_presupuesto_diario_por_conjunto_usd"] * 100)
            new = min(int(old * (1 + p["meta"]["escalar_pct"] / 100)), cap)
            if new <= old:
                raise RuntimeError(f"budget already at cap ({old / 100} USD)")
            m.post(p["objeto"], daily_budget=new)
            res["presupuesto"] = {"antes": old / 100, "ahora": new / 100}
        else:
            publish_campaign(cfg, nj, d, p, m, acct, res)
        p["estado"] = "publicada" if not args.dry_run else p["estado"]
        res["fecha"] = dt.datetime.now().isoformat(timespec="seconds")
        if args.dry_run:
            res["dry_run"] = True
    except Exception as e:
        if args.dry_run:
            sys.exit(f"DRY-RUN ERROR: {e}")
        p["estado"] = "error"
        res["error"] = str(e)[:600]
        jsave(path, p)
        sys.exit(f"PUBLISH ERROR: {e}\n(created objects so far are saved in {path}; "
                 f"rerun 'publica' to resume)")
    if args.dry_run:
        print("DRY-RUN OK (nothing was created or saved)")
    else:
        jsave(path, p)
        with open(os.path.join(d, "DECISIONES.md"), "a", encoding="utf-8") as f:
            f.write(f"\n- {today()} · PUBLICADA {p['id']} ({p['tipo']}: {p['resumen']}).\n")
        git_commit(f"publica {p['id']}")
    print(json.dumps({"id": p["id"], "estado": p["estado"], "resultado": res}, ensure_ascii=False,
                     indent=1))


def publish_campaign(cfg, nj, d, p, m, acct, res):
    meta, lim = p["meta"], cfg["limites"]
    if not meta.get("link"):
        raise RuntimeError("falta meta.link (el link del embudo/landing). "
                           "Usa: brain.py set <ID> --link https://...")
    missing = [a["creativo"] for a in meta["anuncios"] if not a.get("media")]
    if missing:
        raise RuntimeError(f"faltan medios para: {', '.join(missing)} (usa 'prepara' primero)")
    info = m.get(acct, fields="currency") if not m.dry_run else {"currency": "USD"}
    if info.get("currency") != "USD":
        raise RuntimeError(f"la cuenta usa {info.get('currency')}; los topes están en USD. "
                           "Ajusta config.limites a esa moneda y 'moneda_cuenta'.")
    active = sum(x.get("meta", {}).get("presupuesto_diario_usd", 0) for x in proposals(d)
                 if x["estado"] == "publicada" and x["id"] != p["id"]
                 and (x.get("resultado") or {}).get("fecha", "")[:10] == today())
    if active + meta["presupuesto_diario_usd"] > lim["max_presupuesto_nuevo_por_dia_usd"]:
        raise RuntimeError(f"supera el tope de presupuesto nuevo por día "
                           f"({active} + {meta['presupuesto_diario_usd']} > "
                           f"{lim['max_presupuesto_nuevo_por_dia_usd']} USD)")
    mercado = "-".join(meta["paises"])
    producto = meta.get("producto", "core")
    if "campaign_id" not in res:
        res["campaign_id"] = m.post(f"{acct}/campaigns", name=f"BS|{p['id']}|{producto}|{mercado}",
                                    objective="OUTCOME_SALES", status="PAUSED",
                                    special_ad_categories=[], buying_type="AUCTION")["id"]
    if "adset_id" not in res:
        targeting = {"geo_locations": {"countries": meta["paises"]},
                     "age_min": meta.get("edad_min", 18), "age_max": meta.get("edad_max", 65)}
        if meta.get("generos"):
            targeting["genders"] = meta["generos"]
        res["adset_id"] = m.post(
            f"{acct}/adsets", name=f"BS|{p['id']}|{mercado}", campaign_id=res["campaign_id"],
            daily_budget=int(round(meta["presupuesto_diario_usd"] * 100)),
            billing_event="IMPRESSIONS", optimization_goal="OFFSITE_CONVERSIONS",
            bid_strategy="LOWEST_COST_WITHOUT_CAP", is_adset_budget_sharing_enabled=False,
            promoted_object={"pixel_id": nj["meta"]["pixel_id"], "custom_event_type": "PURCHASE"},
            targeting=targeting, status="PAUSED")["id"]
    res.setdefault("anuncios", {})
    for i, a in enumerate(meta["anuncios"], 1):
        key = str(i)
        r = res["anuncios"].setdefault(key, {})
        name = f"BS|{p['id']}|{a['angulo']}|{mercado}|{producto}|{a['creativo']}"
        spec = {"page_id": nj["meta"]["page_id"]}
        if nj["meta"].get("instagram_user_id"):
            spec["instagram_user_id"] = nj["meta"]["instagram_user_id"]
        cta = {"type": a["cta"], "value": {"link": meta["link"]}}
        is_video = a["media"].lower().endswith((".mp4", ".mov", ".m4v"))
        if "creative_id" not in r:
            if is_video:
                if "video_id" not in r:
                    r["video_id"] = m.upload_video(acct, a["media"], name)["id"]
                thumb = wait_video(m, r["video_id"])
                spec["video_data"] = {"video_id": r["video_id"], "image_url": thumb,
                                      "message": a["texto"], "title": a["titulo"],
                                      "call_to_action": cta}
            else:
                if "image_hash" not in r:
                    b64 = base64.b64encode(open(a["media"], "rb").read()).decode()
                    up = m.post(f"{acct}/adimages", bytes=b64)
                    r["image_hash"] = (next(iter(up.get("images", {}).values()), {}).get("hash")
                                       or up.get("hash") or up.get("id"))
                spec["link_data"] = {"image_hash": r["image_hash"], "link": meta["link"],
                                     "message": a["texto"], "name": a["titulo"],
                                     "call_to_action": cta}
            r["creative_id"] = m.post(f"{acct}/adcreatives", name=name,
                                      object_story_spec=spec)["id"]
        if "ad_id" not in r:
            r["ad_id"] = m.post(f"{acct}/ads", name=name, adset_id=res["adset_id"],
                                creative={"creative_id": r["creative_id"]}, status="PAUSED")["id"]
    # everything created paused; now switch on (the owner already said "publica")
    for obj in [res["campaign_id"], res["adset_id"]] + [r["ad_id"] for r in res["anuncios"].values()]:
        m.post(obj, status="ACTIVE")
    res["activado"] = True


def wait_video(m, video_id, timeout=600):
    if m.dry_run:
        return "https://example.invalid/thumb.jpg"
    t0 = time.time()
    while time.time() - t0 < timeout:
        v = m.get(video_id, fields="status,picture")
        st = (v.get("status") or {}).get("video_status")
        if st == "ready" and v.get("picture"):
            return v["picture"]
        if st == "error":
            raise RuntimeError(f"Meta could not process video {video_id}")
        time.sleep(15)
    raise RuntimeError(f"video {video_id} not ready after {timeout}s; rerun 'publica' later")


def cmd_meta_check(args):
    cfg = config()
    d, nj = niche(cfg)
    m = Meta(cfg)
    me = m.get("me", fields="id,name")
    acct = m.get(nj["meta"]["ad_account_id"], fields="name,currency,account_status,timezone_name")
    page = m.get(nj["meta"]["page_id"], fields="name") if nj["meta"].get("page_id") else {}
    pixel = m.get(nj["meta"]["pixel_id"], fields="name,last_fired_time") \
        if nj["meta"].get("pixel_id") else {}
    print(json.dumps({"token_de": me, "cuenta": acct, "pagina": page, "pixel": pixel},
                     ensure_ascii=False, indent=1))
    if acct.get("account_status") != 1:
        print("ATENCION: account_status != 1 (la cuenta no está activa)")


def cmd_estado(args):
    cfg = config()
    print(f"Datos: {DATA}")
    if not cfg.get("nicho_activo"):
        print("Sin nicho activo. Siguiente paso: 'busca nichos'.")
        return
    d, nj = niche(cfg)
    print(f"Nicho activo: {nj['nombre']} (desde {nj['fijado']})")
    print("Mercados: " + ", ".join(f"{k}={v['estado']}" for k, v in nj["mercados"].items()))
    ddir = os.path.join(d, "diario")
    days = sorted(os.listdir(ddir)) if os.path.isdir(ddir) else []
    if days:
        last = os.path.join(ddir, days[-1])
        flags = [f for f in ("REPORTE.md", "NO-VERIFICADO.txt") if os.path.exists(os.path.join(last, f))]
        print(f"Último día: {days[-1]} ({', '.join(flags) or 'sin reporte'})")
        met = jload(os.path.join(last, "metricas.json"))
        if met:
            print(f"Meta 7d: {met['totales_7d']} {met.get('moneda')}")
        ds = jload(os.path.join(last, "dossier.json"))
        if ds:
            print(f"Créditos ScrapeCreators restantes: {ds['credits']['remaining_reported_by_api']}")
    pend = [p for p in proposals(d) if p["estado"] in ("pendiente", "preparada", "error")]
    print(f"Propuestas esperando tu decisión: {len(pend)}")
    for p in pend:
        print(f"  {p['id']} [{p['estado']}] {p['tipo']}: {p['resumen']}")


def main():
    p = argparse.ArgumentParser(description="Brain Storming")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init").set_defaults(fn=cmd_init)
    s = sub.add_parser("nichos")
    s.add_argument("--candidatos")
    s.set_defaults(fn=cmd_nichos)
    s = sub.add_parser("fijar-nicho")
    s.add_argument("--fecha", required=True)
    s.add_argument("--nombre", required=True)
    s.add_argument("--slug", required=True)
    s.set_defaults(fn=cmd_fijar_nicho)
    s = sub.add_parser("diario")
    s.add_argument("--fecha")
    s.set_defaults(fn=cmd_diario)
    s = sub.add_parser("verificar")
    s.add_argument("--fecha")
    s.set_defaults(fn=cmd_verificar)
    s = sub.add_parser("cola")
    s.add_argument("--todas", action="store_true")
    s.set_defaults(fn=cmd_cola)
    s = sub.add_parser("rechaza")
    s.add_argument("id")
    s.add_argument("motivo")
    s.set_defaults(fn=cmd_rechaza)
    s = sub.add_parser("set")
    s.add_argument("id")
    s.add_argument("--link")
    s.add_argument("--media", nargs=2, metavar=("N_ANUNCIO", "ARCHIVO"))
    s.add_argument("--tienda", help="JSON with ImpulTienda ids created")
    s.add_argument("--estado", choices=["pendiente", "preparada"])
    s.set_defaults(fn=cmd_set)
    s = sub.add_parser("publica")
    s.add_argument("id")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_publica)
    sub.add_parser("meta-check").set_defaults(fn=cmd_meta_check)
    sub.add_parser("estado").set_defaults(fn=cmd_estado)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
