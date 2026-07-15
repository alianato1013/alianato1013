"""Orquestador: dado un nicho, recolecta y expande las preguntas de la audiencia.

Estrategia (embudo de descubrimiento):
  1. Buscamos la(s) palabra(s) semilla del nicho en Google (via SerpApi).
  2. Guardamos AI Overview + People Also Ask + busquedas relacionadas.
  3. EXPANDIMOS: cada pregunta de "People Also Ask" se vuelve una nueva semilla
     (hasta la profundidad indicada), porque al abrir una pregunta Google revela
     mas preguntas. Asi salen decenas/cientos de dudas reales de la gente.
  4. Deduplicamos y rankeamos por frecuencia -> "las mas generadas por la audiencia".
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional, Set

from . import analyzer
from .serpapi_client import SerpApiClient


class InvestigadorDeNicho:
    def __init__(
        self,
        client: SerpApiClient,
        profundidad: int = 1,
        max_busquedas: int = 25,
        pausa_seg: float = 1.0,
        log: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.client = client
        self.profundidad = profundidad      # cuantos niveles de expansion de PAA
        self.max_busquedas = max_busquedas  # tope de consultas (cuida tu cuota)
        self.pausa_seg = pausa_seg
        self.log = log or (lambda _m: None)

        self._consultadas: Set[str] = set()
        self._busquedas_hechas = 0

    def investigar(self, nicho: str) -> Dict[str, Any]:
        preguntas_crudas: List[str] = []
        related_searches: List[str] = []
        ai_overviews: List[Dict[str, Any]] = []

        # Cola de (termino, nivel) para el recorrido por niveles.
        cola: List[tuple] = [(nicho, 0)]

        while cola and self._busquedas_hechas < self.max_busquedas:
            termino, nivel = cola.pop(0)
            clave = analyzer.normalizar(termino)
            if clave in self._consultadas:
                continue
            self._consultadas.add(clave)

            self.log(f"[{self._busquedas_hechas + 1}/{self.max_busquedas}] Buscando: {termino}")
            data = self.client.search(termino)
            self._busquedas_hechas += 1

            # People Also Ask -> preguntas de la audiencia
            nuevas = analyzer.extraer_preguntas(data)
            preguntas_crudas.extend(nuevas)

            # Busquedas relacionadas
            related_searches.extend(analyzer.extraer_related_searches(data))

            # AI Overview (solo lo guardamos para la semilla original y nivel 0)
            if nivel == 0:
                ov = analyzer.extraer_ai_overview(data)
                if ov.get("page_token") and not ov.get("texto"):
                    try:
                        detalle = self.client.ai_overview_by_token(ov["page_token"])
                        ov = analyzer.extraer_ai_overview({"ai_overview": detalle.get("ai_overview", detalle)})
                        self._busquedas_hechas += 1
                    except Exception as exc:  # el overview es un extra, no rompemos por el
                        self.log(f"  (no pude expandir el AI Overview: {exc})")
                if ov.get("texto") or ov.get("fuentes"):
                    ai_overviews.append({"consulta": termino, **ov})

            # Expansion: cada pregunta se vuelve semilla del siguiente nivel.
            if nivel < self.profundidad:
                for q in nuevas:
                    if analyzer.normalizar(q) not in self._consultadas:
                        cola.append((q, nivel + 1))

            if self.pausa_seg:
                time.sleep(self.pausa_seg)

        ranking = analyzer.rankear_preguntas(preguntas_crudas)
        subtemas = analyzer.detectar_subtemas(preguntas_crudas)

        return {
            "nicho": nicho,
            "busquedas_realizadas": self._busquedas_hechas,
            "total_preguntas_encontradas": len(preguntas_crudas),
            "preguntas_unicas": len(ranking),
            "ranking_preguntas": ranking,
            "subtemas": subtemas,
            "busquedas_relacionadas": sorted(set(related_searches)),
            "ai_overviews": ai_overviews,
        }
