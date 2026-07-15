"""Pruebas de la logica de extraccion/ranking usando una respuesta simulada de SerpApi.

Se pueden correr sin clave de API:  python -m pytest  (o)  python tests/test_analyzer.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nicho_research import analyzer  # noqa: E402

RESPUESTA_SIMULADA = {
    "ai_overview": {
        "text_blocks": [
            {"snippet": "El ayuno intermitente consiste en alternar periodos de comida y ayuno."},
            {"list": [{"snippet": "Ayuda a controlar calorias."}, {"snippet": "Puede mejorar la energia."}]},
        ],
        "references": [
            {"title": "Clinica X", "link": "https://ejemplo.com/x"},
        ],
    },
    "related_questions": [
        {"question": "¿Qué es el ayuno intermitente?"},
        {"question": "¿Cómo empezar el ayuno intermitente?"},
        {"question": "que es el ayuno intermitente"},  # duplicado (acentos/mayus)
        {"question": "¿Cuánto peso se baja con ayuno intermitente?"},
    ],
    "related_searches": [
        {"query": "ayuno intermitente 16/8"},
        {"query": "ayuno intermitente resultados"},
    ],
}


def test_extraer_preguntas():
    preguntas = analyzer.extraer_preguntas(RESPUESTA_SIMULADA)
    assert len(preguntas) == 4


def test_ranking_deduplica_por_acentos_y_mayus():
    preguntas = analyzer.extraer_preguntas(RESPUESTA_SIMULADA)
    ranking = analyzer.rankear_preguntas(preguntas)
    # "¿Qué es...?" y "que es..." deben colapsar en 1 con frecuencia 2.
    assert len(ranking) == 3
    top = ranking[0]
    assert top["frecuencia"] == 2
    assert "ayuno intermitente" in analyzer.normalizar(top["pregunta"])


def test_clasificacion_de_tipos():
    assert analyzer.clasificar_pregunta("¿Cómo empezar?") == "tutorial / paso a paso"
    assert analyzer.clasificar_pregunta("¿Qué es X?") == "definicion / explicacion"
    assert analyzer.clasificar_pregunta("¿Cuánto cuesta?") == "cifras / cantidades"


def test_ai_overview_texto_y_fuentes():
    ov = analyzer.extraer_ai_overview(RESPUESTA_SIMULADA)
    assert "ayuno intermitente" in ov["texto"].lower()
    assert "controlar calorias" in ov["texto"].lower()  # aplano listas anidadas
    assert ov["fuentes"][0]["url"] == "https://ejemplo.com/x"


def test_related_searches():
    rel = analyzer.extraer_related_searches(RESPUESTA_SIMULADA)
    assert "ayuno intermitente 16/8" in rel


def test_subtemas():
    preguntas = analyzer.extraer_preguntas(RESPUESTA_SIMULADA)
    subtemas = analyzer.detectar_subtemas(preguntas)
    temas = {t["tema"] for t in subtemas}
    assert "ayuno" in temas and "intermitente" in temas


if __name__ == "__main__":
    fallos = 0
    for nombre, fn in sorted(globals().items()):
        if nombre.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"OK   {nombre}")
            except AssertionError as exc:
                fallos += 1
                print(f"FAIL {nombre}: {exc}")
    print(f"\n{'Todo bien' if not fallos else str(fallos) + ' fallo(s)'}")
    raise SystemExit(1 if fallos else 0)
