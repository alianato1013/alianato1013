"""Cliente para SerpApi: la fuente estable de datos de Google.

SerpApi resuelve captchas/proxies por nosotros y devuelve el resultado de Google
en JSON limpio, incluyendo:
  - ai_overview        -> el "AI Overview" (resumen generado por Google)
  - related_questions  -> "People Also Ask" (las preguntas de la audiencia)
  - related_searches   -> busquedas relacionadas

Clave gratis (100 busquedas/mes): https://serpapi.com/manage-api-key
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

import requests

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"


class SerpApiError(RuntimeError):
    """Error al hablar con SerpApi (clave invalida, sin credito, red, etc.)."""


def _load_env_file(path: str = ".env") -> None:
    """Carga variables de un archivo .env sin dependencias externas."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # No pisamos variables ya definidas en el entorno real.
            os.environ.setdefault(key, value)


class SerpApiClient:
    """Envuelve las llamadas HTTP a SerpApi con reintentos simples."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        hl: str = "es",
        gl: str = "mx",
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        _load_env_file()
        self.api_key = api_key or os.environ.get("SERPAPI_KEY", "").strip()
        if not self.api_key:
            raise SerpApiError(
                "No encontre tu clave de SerpApi.\n"
                "1) Consigue una gratis en https://serpapi.com/manage-api-key\n"
                "2) Copia .env.example a .env y pega tu clave en SERPAPI_KEY\n"
                "   (o exporta la variable: export SERPAPI_KEY=tu_clave)"
            )
        self.hl = hl  # idioma de la interfaz (es = espanol)
        self.gl = gl  # pais (mx = Mexico); cambialo segun tu audiencia
        self.timeout = timeout
        self.max_retries = max_retries

    def _get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params = {**params, "api_key": self.api_key}
        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                resp = requests.get(
                    SERPAPI_ENDPOINT, params=params, timeout=self.timeout
                )
                if resp.status_code == 401:
                    raise SerpApiError("Clave de SerpApi invalida (401).")
                if resp.status_code == 429:
                    # Sin credito o demasiadas peticiones: esperamos y reintentamos.
                    time.sleep(2 * (attempt + 1))
                    last_error = SerpApiError("Limite de peticiones alcanzado (429).")
                    continue
                resp.raise_for_status()
                data = resp.json()
                if data.get("error"):
                    raise SerpApiError(f"SerpApi respondio con error: {data['error']}")
                return data
            except requests.RequestException as exc:  # errores de red
                last_error = exc
                time.sleep(2 * (attempt + 1))
        raise SerpApiError(f"No pude contactar SerpApi tras varios intentos: {last_error}")

    def search(self, query: str) -> Dict[str, Any]:
        """Ejecuta una busqueda normal de Google y devuelve el JSON completo."""
        return self._get(
            {
                "engine": "google",
                "q": query,
                "hl": self.hl,
                "gl": self.gl,
                # Pedimos que incluya el AI Overview cuando exista.
                "no_cache": "false",
            }
        )

    def ai_overview_by_token(self, page_token: str) -> Dict[str, Any]:
        """Algunos AI Overviews vienen 'colapsados' y hay que pedirlos con su token."""
        return self._get(
            {
                "engine": "google_ai_overview",
                "page_token": page_token,
                "hl": self.hl,
                "gl": self.gl,
            }
        )
