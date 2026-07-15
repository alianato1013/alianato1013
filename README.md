# 🔎 Investigador de Nichos — Google AI Overviews + Preguntas de la Audiencia

Herramienta para **descubrir el nicho perfecto para tu canal**. Le das una palabra
o tema, y te devuelve **las preguntas que más se hace la gente** sobre eso (sacadas
de Google), rankeadas por frecuencia. También te trae el **AI Overview** de Google
y los **sub-temas / sub-nichos** que están calientes.

Justo lo que pediste: *"sacar una data por nicho regresando las preguntas más
generadas por la audiencia"* para **cubrir necesidades reales de las personas**.

---

## 🧠 ¿De dónde salen los datos?

- **People Also Ask** ("La gente también pregunta") → las preguntas reales de la audiencia.
- **AI Overview** → el resumen que genera Google con IA.
- **Related searches** → búsquedas relacionadas (más ideas de contenido).

Todo esto lo obtenemos a través de **SerpApi**, un servicio que consulta Google por
nosotros de forma **estable y legal** (resuelve captchas/proxies y nos da JSON limpio).
Scrapear Google directo es frágil y se rompe seguido; por eso usamos SerpApi.

---

## 🚀 Instalación (una sola vez)

### 1. Instala las dependencias
```bash
pip install -r requirements.txt
```

### 2. Consigue tu clave GRATIS de SerpApi
- Entra a 👉 https://serpapi.com/manage-api-key
- Regístrate (el plan gratis da **100 búsquedas al mes**, suficiente para probar).
- Copia tu API key.

### 3. Guarda tu clave
```bash
cp .env.example .env
```
Abre el archivo `.env` y pega tu clave:
```
SERPAPI_KEY=tu_clave_real_aqui
```
> El archivo `.env` está en `.gitignore`, así que tu clave **nunca** se sube a GitHub.

---

## ▶️ Cómo usarlo

Lo más simple:
```bash
python nicho.py "finanzas personales"
```

Con más potencia (expande preguntas 2 niveles, hasta 30 búsquedas, audiencia de España):
```bash
python nicho.py "recetas keto" --profundidad 2 --max 30 --pais es --idioma es
```

### Opciones
| Opción | Qué hace | Default |
|---|---|---|
| `--profundidad` | Cuántos niveles de preguntas expandir (más = más preguntas, más cuota) | `1` |
| `--max` | Tope de búsquedas para cuidar tu cuota | `25` |
| `--pais` | País de la audiencia (`mx`, `es`, `ar`, `us`, `co`...) | `mx` |
| `--idioma` | Idioma de los resultados | `es` |
| `--pausa` | Segundos entre búsquedas | `1.0` |
| `--salida` | Carpeta donde guardar resultados | `salidas` |

---

## 📂 Qué obtienes

En pantalla ves un resumen con el **TOP de preguntas**. Además se guardan 2 archivos:

- `salidas/<nicho>_preguntas.csv` → las preguntas rankeadas, **listo para abrir en
  Excel o Google Sheets** (columnas: `#`, `pregunta`, `frecuencia`, `tipo`).
- `salidas/<nicho>_completo.json` → todos los datos (preguntas, sub-temas, AI Overview,
  búsquedas relacionadas y fuentes).

La columna **`tipo`** clasifica cada pregunta (tutorial, definición, comparación,
cifras...) — te sirve para decidir el **formato de video**.

---

## 💡 Cómo usar esto para elegir nicho de canal

1. Corre 5-10 temas que te interesen y compara **cuántas preguntas únicas** genera cada uno
   (más preguntas = más hambre de contenido = más videos posibles).
2. Mira los **sub-temas detectados**: ahí están los sub-nichos menos saturados.
3. Las preguntas con **frecuencia alta** son tus primeros títulos de video casi garantizados.

### 🔗 Combínalo con NexLev (lo tienes conectado)
Esta herramienta te dice **QUÉ pregunta la audiencia**. Para saber si el nicho
**paga bien y tiene demanda en YouTube**, cruza los resultados con NexLev:
- Google (esta tool) → demanda de información / ideas de títulos.
- NexLev → RPM del nicho, canales outlier, si funciona en formato *faceless*.

El nicho ideal = **muchas preguntas sin responder** (Google) **+ RPM alto y outliers
recientes** (NexLev).

---

## 🧪 Pruebas

La lógica de extracción/ranking se puede probar sin gastar cuota de API:
```bash
python tests/test_analyzer.py
```

---

## ❓ Problemas comunes

- **"No encontré tu clave de SerpApi"** → no creaste el `.env` o la variable está vacía.
- **Error 429** → te quedaste sin búsquedas del mes o vas muy rápido (sube `--pausa`).
- **No aparece AI Overview** → Google no siempre lo muestra para todas las consultas; las
  preguntas (People Also Ask) casi siempre sí aparecen.
