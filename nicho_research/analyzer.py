"""Extraccion y analisis: de la respuesta cruda de Google a insights de nicho."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, Iterable, List, Optional

# Palabras de arranque que indican el "tipo" de pregunta (util para formatos de video).
QUESTION_TYPES = {
    "como": "tutorial / paso a paso",
    "que": "definicion / explicacion",
    "cual": "comparacion / eleccion",
    "cuanto": "cifras / cantidades",
    "cuando": "momento / timing",
    "donde": "lugar / recurso",
    "por que": "razones / motivacion",
    "porque": "razones / motivacion",
    "para que": "beneficio / utilidad",
    "quien": "personas / referentes",
    "es": "duda de si/no",
    "vale la pena": "duda de si/no",
    "sirve": "duda de si/no",
}

# Palabras vacias que ignoramos al detectar sub-temas.
STOPWORDS = {
    "de", "la", "el", "en", "y", "a", "los", "las", "un", "una", "por", "con",
    "para", "que", "como", "cual", "cuales", "es", "se", "del", "al", "lo", "su",
    "sus", "mas", "o", "u", "e", "the", "of", "to", "in", "and", "for", "on",
    "mi", "mis", "me", "te", "tu", "tus", "hay", "puedo", "puede", "si", "no",
}


def normalizar(texto: str) -> str:
    """Minusculas, sin acentos y sin espacios extra, para comparar/deduplicar."""
    texto = texto.lower().strip()
    reemplazos = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u", "ñ": "n"}
    for a, b in reemplazos.items():
        texto = texto.replace(a, b)
    # Quitamos signos de puntuacion (¿ ? ¡ ! . , : ; " ') para deduplicar bien.
    texto = re.sub(r"[¿?¡!.,:;\"'()]+", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def clasificar_pregunta(pregunta: str) -> str:
    """Devuelve el tipo/intencion aproximada de una pregunta."""
    n = normalizar(pregunta)
    for prefijo, etiqueta in QUESTION_TYPES.items():
        if n.startswith(prefijo + " ") or prefijo in n[:20]:
            return etiqueta
    return "otra"


# -------------------- Extraccion desde la respuesta de SerpApi --------------------

def extraer_preguntas(data: Dict[str, Any]) -> List[str]:
    """Saca las preguntas de 'People Also Ask' (related_questions)."""
    preguntas: List[str] = []
    for item in data.get("related_questions", []) or []:
        q = item.get("question")
        if q:
            preguntas.append(q.strip())
    return preguntas


def extraer_tokens_paa(data: Dict[str, Any]) -> List[str]:
    """Devuelve los textos de PAA que sirven como nuevas semillas para expandir."""
    return extraer_preguntas(data)


def extraer_related_searches(data: Dict[str, Any]) -> List[str]:
    busquedas: List[str] = []
    for item in data.get("related_searches", []) or []:
        q = item.get("query")
        if q:
            busquedas.append(q.strip())
    return busquedas


def extraer_ai_overview(data: Dict[str, Any]) -> Dict[str, Any]:
    """Devuelve {texto, fuentes, page_token} del AI Overview si existe."""
    overview = data.get("ai_overview") or {}
    resultado: Dict[str, Any] = {"texto": "", "fuentes": [], "page_token": None}

    if overview.get("page_token"):
        # Overview colapsado: hay que pedirlo aparte con su token.
        resultado["page_token"] = overview["page_token"]

    bloques = overview.get("text_blocks") or []
    partes: List[str] = []
    for bloque in bloques:
        _aplanar_bloque(bloque, partes)
    resultado["texto"] = "\n".join(p for p in partes if p).strip()

    for ref in overview.get("references", []) or []:
        resultado["fuentes"].append(
            {"titulo": ref.get("title", ""), "url": ref.get("link", "")}
        )
    return resultado


def _aplanar_bloque(bloque: Dict[str, Any], acc: List[str]) -> None:
    """Los text_blocks del AI Overview pueden anidar listas; los aplanamos a texto."""
    if not isinstance(bloque, dict):
        return
    if bloque.get("snippet"):
        acc.append(str(bloque["snippet"]).strip())
    for lista in bloque.get("list", []) or []:
        _aplanar_bloque(lista, acc)
    for sub in bloque.get("text_blocks", []) or []:
        _aplanar_bloque(sub, acc)


# -------------------- Agregacion / ranking --------------------

def rankear_preguntas(todas: Iterable[str]) -> List[Dict[str, Any]]:
    """Deduplica preguntas (ignorando acentos/mayus) y las ordena por frecuencia."""
    conteo: Counter = Counter()
    original_por_norma: Dict[str, str] = {}
    for q in todas:
        clave = normalizar(q)
        if not clave:
            continue
        conteo[clave] += 1
        # Guardamos la primera forma "bonita" que vimos.
        original_por_norma.setdefault(clave, q.strip())

    ranking: List[Dict[str, Any]] = []
    for clave, veces in conteo.most_common():
        pregunta = original_por_norma[clave]
        ranking.append(
            {
                "pregunta": pregunta,
                "frecuencia": veces,
                "tipo": clasificar_pregunta(pregunta),
            }
        )
    return ranking


def detectar_subtemas(preguntas: Iterable[str], top: int = 15) -> List[Dict[str, Any]]:
    """Cuenta palabras/temas recurrentes para revelar sub-nichos dentro del nicho."""
    conteo: Counter = Counter()
    for q in preguntas:
        for palabra in normalizar(q).split():
            if len(palabra) < 4 or palabra in STOPWORDS:
                continue
            conteo[palabra] += 1
    return [
        {"tema": palabra, "menciones": veces}
        for palabra, veces in conteo.most_common(top)
    ]
