"""Interfaz de linea de comandos.

Uso basico:
    python nicho.py "finanzas personales"

Opciones:
    python nicho.py "recetas keto" --profundidad 2 --max 30 --pais es --idioma es
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from typing import Any, Dict

from .analyzer import normalizar
from .scraper import InvestigadorDeNicho
from .serpapi_client import SerpApiClient, SerpApiError


def _slug(texto: str) -> str:
    base = normalizar(texto).replace(" ", "_")
    return "".join(c for c in base if c.isalnum() or c == "_")[:40] or "nicho"


def guardar_csv(resultado: Dict[str, Any], ruta: str) -> None:
    with open(ruta, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["#", "pregunta", "frecuencia", "tipo"])
        for i, fila in enumerate(resultado["ranking_preguntas"], 1):
            writer.writerow([i, fila["pregunta"], fila["frecuencia"], fila["tipo"]])


def guardar_json(resultado: Dict[str, Any], ruta: str) -> None:
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(resultado, fh, ensure_ascii=False, indent=2)


def imprimir_resumen(resultado: Dict[str, Any], top: int = 20) -> None:
    print()
    print("=" * 64)
    print(f"NICHO: {resultado['nicho']}")
    print(
        f"Busquedas: {resultado['busquedas_realizadas']} | "
        f"Preguntas unicas: {resultado['preguntas_unicas']} "
        f"(de {resultado['total_preguntas_encontradas']} encontradas)"
    )
    print("=" * 64)

    print(f"\nTOP {top} PREGUNTAS DE LA AUDIENCIA (las mas repetidas):")
    for i, fila in enumerate(resultado["ranking_preguntas"][:top], 1):
        print(f"  {i:>2}. ({fila['frecuencia']}x) {fila['pregunta']}  ->  {fila['tipo']}")

    if resultado["subtemas"]:
        print("\nSUB-TEMAS / SUB-NICHOS DETECTADOS (palabras mas recurrentes):")
        linea = ", ".join(
            f"{t['tema']} ({t['menciones']})" for t in resultado["subtemas"]
        )
        print(f"  {linea}")

    if resultado["ai_overviews"]:
        ov = resultado["ai_overviews"][0]
        texto = ov.get("texto", "")
        if texto:
            print("\nAI OVERVIEW (resumen de Google) — extracto:")
            print(f"  {texto[:500]}{'...' if len(texto) > 500 else ''}")

    if resultado["busquedas_relacionadas"]:
        print("\nBUSQUEDAS RELACIONADAS:")
        print("  " + ", ".join(resultado["busquedas_relacionadas"][:20]))
    print()


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="nicho",
        description="Investiga un nicho con Google AI Overviews + preguntas de la audiencia.",
    )
    p.add_argument("nicho", help='El nicho o palabra semilla, ej: "finanzas para jovenes"')
    p.add_argument("--profundidad", type=int, default=1,
                   help="Niveles de expansion de preguntas (0=solo la semilla). Def: 1")
    p.add_argument("--max", type=int, default=25, dest="max_busquedas",
                   help="Tope de busquedas para cuidar tu cuota. Def: 25")
    p.add_argument("--idioma", default="es", help="Idioma (hl). Def: es")
    p.add_argument("--pais", default="mx", help="Pais (gl), ej: mx, es, ar, us. Def: mx")
    p.add_argument("--pausa", type=float, default=1.0,
                   help="Segundos de pausa entre busquedas. Def: 1.0")
    p.add_argument("--salida", default="salidas",
                   help="Carpeta donde guardar CSV/JSON. Def: salidas")
    return p


def main(argv=None) -> int:
    args = construir_parser().parse_args(argv)

    try:
        client = SerpApiClient(hl=args.idioma, gl=args.pais)
    except SerpApiError as exc:
        print(f"\n[!] {exc}\n", file=sys.stderr)
        return 2

    investigador = InvestigadorDeNicho(
        client=client,
        profundidad=args.profundidad,
        max_busquedas=args.max_busquedas,
        pausa_seg=args.pausa,
        log=lambda m: print(m, file=sys.stderr),
    )

    try:
        resultado = investigador.investigar(args.nicho)
    except SerpApiError as exc:
        print(f"\n[!] Error con SerpApi: {exc}\n", file=sys.stderr)
        return 3

    imprimir_resumen(resultado)

    os.makedirs(args.salida, exist_ok=True)
    slug = _slug(args.nicho)
    ruta_csv = os.path.join(args.salida, f"{slug}_preguntas.csv")
    ruta_json = os.path.join(args.salida, f"{slug}_completo.json")
    guardar_csv(resultado, ruta_csv)
    guardar_json(resultado, ruta_json)

    print(f"Guardado:\n  - {ruta_csv}  (preguntas para Excel/Sheets)")
    print(f"  - {ruta_json} (datos completos)\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
