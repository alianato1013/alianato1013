# Traspaso: Brain Storming (fábrica de productos digitales)

Este archivo pasa el trabajo de la fábrica de productos a un chat nuevo, dedicado solo a ella. El chat anterior queda para buscar y armar repositorios.

---

## 0. Reglas para el agente que lee esto (obligatorias)

1. **Fuente única de verdad:** este archivo y el repositorio `alianato1013/alianato1013`, rama `claude/rea-repository-analysis-9eytp3`. Lo que no esté aquí ni en el repositorio **no existe**: pregunta a la dueña, no lo supongas.
2. **Primer paso, antes de hacer cualquier trabajo:**
   1. Ejecuta las verificaciones de la sección 8 y muestra el resultado.
   2. Explícale a la dueña, en un máximo de 10 líneas y en español sencillo, lo que entendiste: qué está hecho, qué decidió ella, qué falta y cuál es el siguiente paso.
   3. **Espera a que diga "correcto".** Si corrige algo, anota su corrección textual en la sección 2 de este archivo y súbelo al repositorio.
3. **Cada afirmación lleva una de estas etiquetas.** No las mezcles ni las ascienda de categoría:
   - **HECHO:** verificado, con su archivo o commit.
   - **DECISIÓN DE LA DUEÑA:** solo con su cita textual.
   - **PROPUESTA (sin aprobar):** idea del agente. No se ejecuta hasta que ella diga sí.
   - **NO VALIDADO:** hipótesis o dato sin medir.
4. **No cambies una decisión de la dueña.** Si te parece un error, díselo con tu razón y pregúntale. Ella decide.
5. **Ningún número sin fuente.** Si no hay fuente, escribe "sin dato" o "NO VALIDADO".
6. **Al terminar cada tarea:** actualiza las secciones 3 y 5 de este archivo, súbelo y dile a la dueña qué cambió.

## 1. La dueña y cómo trabajar con ella

- Habla **español**, vive en **Puerto Rico** y **no es técnica**. Usa frases cortas y pídele una sola acción a la vez, con el botón o la pantalla exactos.
- **Secretos:** nunca le pidas que pegue en el chat contraseñas, tokens ni llaves de API. Ella las escribe directamente en el servidor (`nano` o el instalador). Las llaves **públicas** SSH sí se pueden mostrar.
- **Dinero y acciones hacia afuera:** no publicas, no gastas, no creas pods ni cargas saldo sin su OK explícito. Escribir en su cuenta de ImpulTienda o de Meta también necesita su OK. Brain publica solo con "publica <ID>" y dentro de los topes.
- **El agente de la GPU** solo puede encender o apagar el pod de RunPod que **ya existe**. Nunca crea pods ni cambia la GPU sin su OK.
- **Licencias:** para contenido que se monetiza, solo modelos con licencia comercial (Qwen-Image y Wan 2.2, Apache-2.0). FLUX.2 Dev no permite uso comercial. No se copia material de la competencia ni de Etsy palabra por palabra, ni se traducen anuncios literalmente: se modela el ángulo, la estructura y la demanda.
- **Git:** trabaja y sube solo a la rama `claude/rea-repository-analysis-9eytp3`. No abras un PR si ella no lo pide. No pongas identificadores de modelo en commits ni en el código.

## 2. Decisiones de la dueña (citas textuales, no se cambian)

| Tema | Lo que dijo, tal cual |
|---|---|
| Nombre del sistema | "DISCULPA EL SISTEMA SE A A LLAMAR BRAIN STORMING" |
| Filosofía del nicho | "la idea es posicionarme en un nicho que pueda durar por años no sacar producto a producto de diferentes a ver que pega o vende. Quiero un sustema comoleto que pueda yo solo supervisar todo el trabajo y solo decirle publica." |
| Creativos por oferta | "recrea almenos 2 de ahi o instagram para completar 5 crrtivos siempre para la oferta low tick nuestra que modela la hight ticket" |
| Precio | "creo que si el producto se vende entre 17 a 23.00 esta bueno" |
| Mercados | "Al menos 20 países de mayor poder adquisitivo. Y que a nivel de estadística los productos digitales descargables sean top de ese país." |
| Campaña siguiente | "uiero la estuctura completa con el analisis que hiciste para que brain storming lo cree y sea mi proxima camapa. ya que analizaste los mercados saca el de mayr probabilidad de venta. Busca los creativos que estan funcionando en este nicho de otros paises que aun no vamdo a vender para lanzarlos en el que no esta y cambiamos el idioma , mismo angulo debe tener mismo impacto." |
| Material de Etsy | "material gratis en edsy seria bueno modelarlos como upsell o hasta orden boum. que opinas" (es una pregunta: la respuesta fue modelarlo, no copiarlo) |
| Lanzamiento en inglés | "Digamos, completa montarla. Para el mercado inglés. Tenemos 12 países que podemos probar. Ármame el plan completo. Desde cero para desarrollarla y tenerla corriendo como mínimo o mejor dicho, como máximo de tiempo en 2 días." |
| Quién hace la publicidad | "lo que quiero saber es quién crea los creativos. O las imágenes estáticas. Para poderlos poner como anuncios dentro de la campaña de Meta Ads. Luego de que se analice la estrategia de la oferta ganadora. De High Ticket a Low Ticket. Mercado e idioma. ¿Quién va a hacer esa publicidad? ¿Quién hace el marketing? ¿Quién lo analiza?" |
| Separar el chat | "¿Crees que sería bueno desvincularlo o lo dejo aquí porque ya comenzamos aquí a hablar?" → aceptó la recomendación de separarlo y pidió que el traspaso quede "exacto con la información correcta y que no se asuma, ni se cambie, ni se interprete algo diferente". |
| Verla como AYOP | "no me contestaste si es posible que yo pueda ver este sistema como está AYPO, que yo lo veo. Y me gusta, porque si tengo que ejecutar algo, pues lo ejecuto." → quiere una pantalla visual de la fábrica, como la de AYOP, desde donde ella pueda ver y ejecutar. |

**Los 12 países del inglés** son los de la propuesta del agente que ella adoptó al decir "Tenemos 12 países":
- **nativos:** US, CA, GB, IE, AU, NZ, SG;
- **de prueba:** DK, NL, NO, SE, FI.

**La oferta a validar** es la que ella subió en `Propuesta_de_negocio_descargable.html`: el binder "por si acaso" de **In Order Co.** para adultos que viven solos. Ese archivo **no está en el repositorio**; lo que se usó de él está en `brain-storming/semillas/mi-vida-en-orden/`.

## 3. Lo que está HECHO (verificado)

| Pieza | Dónde | Commit |
|---|---|---|
| Espía de ofertas (ScrapeCreators: Meta Ad Library, TikTok, Instagram) + reglas del Analista | `espia-ofertas/` | `0f6b4c9` |
| Brain Storming: motor, 4 agentes (Cazador, Bibliotecario, Estratega, Publicador), topes y publicación en Meta | `brain-storming/` | `6160173`, `5adeca6`, `5c3913d` |
| Semilla del nicho en español "Mi Vida en Orden" (cerebro investigado, evidencia y propuesta de 5 creativos `P-SEMILLA-01`) | `brain-storming/semillas/mi-vida-en-orden/` | `5c3913d`, `72f58c5`, `2ba2f49` |
| 24 mercados en la tabla diaria (top 20 por poder adquisitivo + PR, PT, MX) | `brain-storming/config.example.json` | `dcb2ffe` |
| Ahorro de tokens (rtk, ccusage, Playwright MCP, modelo por tarea) | `ahorro-tokens/` | `320ddc8` |
| Estudio GPU propio (ComfyUI + Qwen-Image en RunPod, se apaga solo) | `estudio-gpu/` | `6e916e9`, `64feb1a` |
| Guía de montaje para el Claude Code de su PC | `MONTAJE-CON-CLAUDE.md` | `e300473`, `302d935` |
| **Producto en inglés:** 3 PDFs rellenables en Letter y A4 (ver la tabla siguiente) | `lanzamiento-en/producto/salida/` | `094c51d` |
| Reporte "Cómo funciona tu sistema: agentes y flujo" | Documento en claude.ai: https://claude.ai/artifact/NcjHqGnPrJTZwQHMbN1Xkf | — |

Los PDFs del producto en inglés:

| Archivo (Letter / A4) | Páginas | Campos rellenables |
|---|---|---|
| `in-order-co-solo-binder-*` (producto principal) | 18 / 17 | 513 |
| `in-order-co-emergency-kit-*` (order bump) | 6 / 6 | 34 |
| `in-order-co-digital-legacy-*` (upsell) | 8 / 7 | 132 |

Se generan con `python3 lanzamiento-en/producto/build_binder.py`. El contenido está en `contenido.py` y las tipografías (Fraunces y Public Sans, licencia OFL) en `fonts/`.

## 4. PROPUESTAS del agente (sin aprobar: no ejecutar hasta su "sí")

| Propuesta | Detalle |
|---|---|
| Escalera de precios en inglés | Principal US$23 (A/B a US$19), bump US$9, upsell US$17. El rango US$17–23 sí es decisión suya; los precios exactos no |
| Presupuesto de prueba | ~4 días a US$40/día (≈ US$160): US$20/día para US y US$20/día para CA+GB+IE+AU+NZ+SG; los nórdicos y NL en la semana 2 |
| Reglas para cortar | CPC > US$1,50 después de US$15 → cortar; conversión de la landing < 2% después de 100 clics → arreglar la landing |
| Agente nuevo "Creativo" + motor gratis de estáticos | Produce los estáticos 1:1 y 4:5 y los videos 9:16 a partir de las páginas reales del producto, por mercado e idioma. Así el Estratega solo piensa y el Publicador solo publica. La dueña lo preguntó; aún no dijo "sí" |
| Pantalla de la fábrica "como AYOP" | Ella lo pidió (ver sección 2). Falta decidir **dónde** vive. Opción A: una sección nueva **dentro de AYOP**, con sus botones ("busca nichos", "reporte de hoy", "prepara", "publica"); necesita el código de AYOP, que no está en este repositorio. Opción B: un artefacto de claude.ai, que muestra el estado pero cuyos botones no pueden ejecutar nada en el servidor. Recomendación del agente: A, si el código de AYOP está disponible. Pregúntale antes de construir |
| Los 5 ángulos de los anuncios en inglés | 1) "When I die folder / 5 things"; 2) "You're everyone's emergency contact. Who's yours?"; 3) "do it now or leave it to the kids"; 4) mascotas; 5) "your phone is the key to your life". Modelados de los videos orgánicos de la semilla. No usar frases sobre atributos personales, como "Do you live alone?" |

## 5. PENDIENTE, en este orden

| # | Tarea | Terminado cuando |
|---|---|---|
| 1 | Confirmar con la dueña la sección 4 (precios, presupuesto, agente Creativo, tablero) | Hay una respuesta suya, citada en la sección 2 |
| 2 | 5 anuncios en inglés: estáticos 1:1 y 4:5 + videos 9:16, hechos con las páginas reales de los PDFs | Los archivos están en `lanzamiento-en/creativos/` y ella los vio |
| 3 | `lanzamiento-en/PLAN-48H.md`: validación (y lo no validado), producto y escalera, precios por país, presupuesto, configuración de Meta y compra de prueba del píxel, recuperación de carrito con Brevo, horario hora por hora (día 0, 1 y 2), KPIs y riesgos | Ella lo leyó y lo aprobó |
| 4 | `lanzamiento-en/LANDING.md` (incluye la pregunta frecuente "¿por qué pagar si hay plantillas gratis?", la garantía y su procedimiento, y el aviso legal) y `lanzamiento-en/EMAILS.md` (días 0, 2 y 5, carrito abandonado y renovación en el mes 11) | Archivos en el repositorio |
| 5 | Semilla en inglés `brain-storming/semillas/in-order-co-en/`: `nicho.json` con los 12 mercados, `cerebro/*`, `evidencia.json`, propuestas `P-SEMILLA-EN-01` (US) y `P-SEMILLA-EN-02` (Commonwealth), cada una ≤ US$20/día | `brain.py sembrar in-order-co-en` funciona y `verificar` pasa |
| 6 | Crear la tienda, los productos y el embudo en ImpulTienda | **Solo con su OK explícito.** Se usan los conectores `crear_tienda`, `crear_producto`, `fijar_precio`, `crear_embudo`, `agregar_item_embudo`, `cargar_entregable` y `precio_por_pais` |
| 7 | Montaje del servidor y de la sesión Brain en vivo | Fases 1–8 de `MONTAJE-CON-CLAUDE.md` |

## 6. NO VALIDADO (no presentarlo como hecho)

- Cuántos anuncios pagados hay del nicho **por país**: nunca se midió, porque la Biblioteca de Anuncios de Meta bloqueó la consulta. Lo mide el Cazador con ScrapeCreators.
- La marca "In Order Co." no mostró conflictos en una búsqueda web, pero **eso no es una revisión formal** en USPTO ni UKIPO. Se le recomendó hacerla.
- La conversión y el CPA reales: sin datos hasta la primera campaña.
- Si Qwen-Image da la calidad necesaria en su pod: sin probar con un pod real.
- Si ella ya tiene una tienda en ImpulTienda para esta oferta: **no verificado en este traspaso.** Pregúntale.

## 7. Estado de sus cuentas (según lo que ella contó)

| Cuenta | Estado |
|---|---|
| Servidor Contabo | Probablemente **no contratado** (un comando de servidor le falló en PowerShell). Confirmar con ella |
| RunPod | US$20 de saldo; volumen `modelos-comfyui` de 60 GB en EU-RO-1; pod configurado pero **no desplegado**; llave SSH sin agregar |
| Meta (cuenta publicitaria, píxel, token) | Sin conectar al sistema |
| ScrapeCreators, ElevenLabs, Anthropic API | Llaves sin cargar en el servidor |

## 8. Verificaciones (el agente las ejecuta primero)

```bash
git fetch origin claude/rea-repository-analysis-9eytp3
git checkout claude/rea-repository-analysis-9eytp3
git log --oneline -1                      # debe incluir este traspaso
ls espia-ofertas brain-storming ahorro-tokens estudio-gpu lanzamiento-en/producto/salida
python3 -c "
from pypdf import PdfReader; import glob
for f in sorted(glob.glob('lanzamiento-en/producto/salida/*.pdf')):
    r = PdfReader(f); print(f.split('/')[-1], len(r.pages), 'págs', len(r.get_fields() or {}), 'campos')"
python3 -m py_compile brain-storming/brain.py espia-ofertas/espia.py && echo "código OK"
```

**Resultado esperado:** los 6 PDFs con las páginas y los campos de la sección 3, y "código OK". Si algo no coincide, **detente y díselo a la dueña** antes de seguir.
