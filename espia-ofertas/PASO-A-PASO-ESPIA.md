# El Espía de ofertas: paso a paso

**Qué hace cada día, solo:**

```
1. BUSCA      Biblioteca de Anuncios de Meta (país de origen, p. ej. EE. UU.)
              → anunciantes de tu nicho con 100 anuncios activos o más
2. DESARMA    Los 3 creativos que más copias activas tienen, con su transcripción
              + la landing (título, promesa, precios visibles)
3. ORGÁNICO   TikTok + Instagram Reels del mismo nicho, en el idioma de tu oferta:
              los videos que superan el tamaño de su creador, con transcripción
4. MERCADOS   Banco Mundial: poder adquisitivo, internet y población de tus países candidatos
5. ANALIZA    Claude escribe el reporte con reglas fijas (ANALISTA.md):
              oferta modelo → mercados → nuestra oferta low ticket → branding gemelo
              → 5 creativos (3 del modelo + 2 de TikTok/Instagram)
6. VERIFICA   Rechaza el reporte si cita un anuncio o video que no está en los datos
7. ENTREGA    Google Drive / Espia / <fecha> /
```

**Archivos:**

| Archivo | Para qué sirve |
|---|---|
| `espia.py` | Recoge los datos (solo Python estándar: **no instala nada**) |
| `config.example.json` | Tus nichos, palabras clave, países y límites |
| `ANALISTA.md` | Las reglas inmutables del reporte |
| `run-daily.sh` | La corrida diaria completa |

---

## Paso 1: Crear la cuenta de ScrapeCreators (5 min, en tu PC)

1. Entra a **scrapecreators.com** → **Sign up** (con Google o correo). Te regalan **100 créditos** para probar, sin tarjeta.
2. En el panel (**Dashboard**), copia tu **API key** (empieza con `sk_` o similar).
3. **No la pegues en el chat** ni en ningún archivo del repositorio. Solo va en el servidor (paso 3).
4. **Todavía no compres nada.** Primero haz la prueba del paso 5. Si te convence, compra **Freelance (USD 47 por 25.000 créditos, no vencen)**. El precio venía en fuentes de 2026; confírmalo en su página antes de pagar.

## Paso 2: Entrar al servidor

Usa el mismo servidor del Editor Supremo (`PASO-A-PASO-NUBE.md`).
- Si todavía no lo creaste, haz antes los pasos 1, 2, 3 y 5 de esa guía, y en el paso 6 inicia sesión en Claude Code una vez.
- El Espía no necesita GPU ni espacio: guarda solo JSON y HTML pequeños, **no descarga videos**.

```powershell
ssh editor@IP
```
```bash
cd ~/alianato1013 && git pull
cd ~/alianato1013/espia-ofertas
```

## Paso 3: Guardar la llave de forma segura (2 min)

```bash
mkdir -p ~/.config/espia
nano ~/.config/espia/scrapecreators.key
```
Pega la llave (una sola línea) y guarda: **Ctrl+O → Enter → Ctrl+X**. Después:
```bash
chmod 600 ~/.config/espia/scrapecreators.key
python3 espia.py balance
```
Tiene que responder `HTTP 200` con tus créditos. Si dice 401, la llave está mal copiada.

## Paso 4: Configurar tus nichos (10 min)

```bash
cp config.example.json config.json
nano config.json
```

**Lo que tienes que cambiar:**

| Campo | Qué poner | Ejemplo |
|---|---|---|
| `niches[].name` | Nombre del nicho y para qué tienda | "Relaciones de pareja (Entre Vínculos)" |
| `niches[].source_countries` | País o países **de origen** del high ticket (código de 2 letras) | `["US"]` |
| `niches[].ad_keywords` | 2–4 palabras **en el idioma del país de origen**, como las buscaría un cliente high ticket | `"save your marriage"` |
| `niches[].organic_keywords` | 1–3 palabras **en el idioma de tu oferta**, para TikTok e Instagram | `"apego ansioso"` |
| `candidate_markets` | Países donde podrías vender | `["US","PR","ES","MX",…]` |
| `drive_folder` | Carpeta de Drive (déjala así si ya configuraste rclone) | `"gdrive:Espia"` |

**Lo que normalmente no tocas:**

| Campo | Qué controla |
|---|---|
| `min_active_ads` (100) | El umbral de anuncios activos para considerar que una oferta está escalando |
| `high_ticket_min_price` (97) | El precio desde el que se considera high ticket |
| `advertisers_to_check` (6) | Cuántos anunciantes revisa por nicho |
| `max_pages_per_advertiser` (5) | Cuántas páginas de anuncios lee por anunciante |
| `max_credits_per_run` (150) | **El tope de gasto diario.** Al llegar, se detiene y lo dice |

Calcula el gasto máximo de tu configuración:
```bash
python3 espia.py estimate --config config.json
```
`total_max` es el peor caso. En la práctica gasta menos, porque deja de leer a un anunciante cuando pasa de 100 anuncios.

## Paso 5: Primera corrida de prueba (10–20 min)

**Con los 100 créditos gratis**, deja un solo nicho en `config.json` y pon `"max_credits_per_run": 90`. Después:
```bash
bash run-daily.sh
```

**Qué revisar:**

1. **En la terminal:** cada búsqueda dice cuántos anuncios encontró, y cada anunciante, cuántos anuncios activos tiene.
2. **`runs/<fecha>/EVIDENCIA.md`:** los datos crudos ordenados. Abre 2 o 3 enlaces "ver" para comprobar que coinciden con la Biblioteca de Anuncios real.
3. **`runs/<fecha>/REPORTE.md`:** el reporte de Claude. Si existe `NO-VERIFICADO.txt`, el verificador lo rechazó dos veces; no lo uses y avísame.
4. **En Google Drive:** la carpeta `Espia/<fecha>/` con todo.

**Si algo sale raro:**

| Lo que ves | Qué hacer |
|---|---|
| Un anunciante aparece como "indeterminado" | Sube `max_pages_per_advertiser` (a 8, por ejemplo) |
| `search ... 0 ads` | Prueba otras palabras clave o quita el filtro de idioma (`ad_language: ""`) |
| Ningún anunciante llega a 100 | Es información real: en ese nicho y país hoy no hay ofertas escalando. Prueba otro país de origen o palabras más amplias |
| Errores `HTTP 4xx` en `errors` | Envíame el archivo `runs/<fecha>.log` |

## Paso 6: Programarlo cada 24 horas (2 min)

```bash
crontab -e
```
Si te pregunta el editor, elige `1` (nano). Añade esta línea al final:
```
40 10 * * * /home/editor/alianato1013/espia-ofertas/run-daily.sh >/dev/null 2>&1
```
- El servidor usa hora UTC: **10:40 UTC = 6:40 a. m. en Puerto Rico**. Al despertar tienes el reporte del día en Drive.
- Guarda con **Ctrl+O → Enter → Ctrl+X**.
- Compruébalo con `crontab -l`.

## Paso 7: Usar el reporte

Abre **Drive → Espia → <fecha> → REPORTE.md**. Tiene siempre estas 8 secciones:

1. **Resumen del día**
2. **Oferta modelo (high ticket):**
   - idioma original, dolor, promesa y mecanismo;
   - enlace a la Biblioteca y landing;
   - precio y señales de escala.
3. **Los 3 creativos ganadores**, con la estructura completa (gancho → problema → agitación → mecanismo → prueba → oferta → CTA) y por qué funcionaron.
4. **Extrapolación a otros mercados:**
   - datos del Banco Mundial e idioma (océano azul);
   - top 3 países;
   - enlace para validar la competencia en cada país.
5. **Nuestra oferta low ticket (el gemelo):**
   - mismo avatar y dolor, solución más corta y concreta, resultado rápido;
   - precio, order bump, upsell y garantía.
6. **Branding gemelo:**
   - nombre e historia ("la misma historia, con nuestras palabras");
   - tono, paleta y tipografías.
7. **Nuestros 5 creativos:**
   - **1–3** convertidos de los 3 creativos del modelo;
   - **4–5** recreados de videos que están funcionando en TikTok e Instagram.

   Cada uno trae guion por segundos, texto en pantalla, copy del anuncio y prompt de producción.
8. **Fuentes y límites**

Los guiones de la sección 7 los puedes producir con el Editor Supremo o con Higgsfield.

**¿Quieres cambiar una regla del reporte?** Escríbeme: *"cambia las reglas del analista: …"*.

---

## Costos aproximados

| Concepto | Costo |
|---|---|
| ScrapeCreators | Con la configuración de ejemplo, ~40–100 créditos por día. El paquete de USD 47 (25.000 créditos) dura unos **8–20 meses** |
| Banco Mundial | Gratis |
| Claude (el análisis) | Usa tu suscripción de Claude en el servidor (una sesión corta al día) |
| Servidor | El mismo del Editor Supremo; no suma costo |

Estas cifras son estimaciones. El gasto real de cada día aparece al final de `EVIDENCIA.md` ("Créditos usados").

## Seguridad

- **No instala nada:** solo usa Python y Claude Code, que el servidor ya tiene.
- **Solo lee datos públicos:**
  - la Biblioteca de Anuncios, TikTok e Instagram (a través de ScrapeCreators);
  - las landings;
  - el Banco Mundial.
- **No toca tus cuentas:** ni tu cuenta de Meta, ni tus anuncios, ni tus tiendas.
- **La llave vive solo en el servidor**, con permisos privados (`chmod 600`).
- **Claude, en la corrida automática, solo puede leer y escribir archivos.** No tiene acceso a la terminal ni a internet.

## Lo que tienes que saber (límites reales)

- **Ya probado (con un servidor de ScrapeCreators simulado):**
  - la corrida completa: búsqueda, conteo, creativos, transcripciones, landing, orgánicos, mercados, reporte, verificador y reintento;
  - el rechazo de reportes incompletos o con datos inventados.
- **Todavía sin probar con tu llave real:** desde este entorno no se puede llegar a la API de ScrapeCreators. Los nombres de los campos los tomé de los ejemplos de su documentación oficial. **La corrida del paso 5 es la prueba real.** Si algo no cuadra, el archivo `raw/` guarda cada respuesta original para corregirlo rápido.
- **"Más de 100 anuncios activos" es una señal de escala, no una prueba de ganancias.** Meta no publica el gasto ni las ventas. El sistema lo combina con los días activos y las copias del mismo creativo; aun así, el reporte lo marca como señal.
- **Precios:** muchas ofertas high ticket esconden el precio (llamada o webinar). En ese caso el reporte dice "probable alto" y te pide revisar el checkout a mano.
- **Instagram:** la búsqueda de reels usa lo que Google tiene indexado. Es "lo mejor posible", no completa, y no trae vistas (solo likes y comentarios).
- **Transcripciones:** solo de videos de 2 minutos o menos (más largos cuestan más créditos y están desactivados).
- **Tamaño del público en Meta:** todavía no está incluido. Necesita tu token de la API de Meta; es el siguiente paso cuando quieras.
