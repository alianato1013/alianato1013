# Traspaso: producción de YouTube (AYOP)

Este archivo pasa la producción de los canales a un chat aparte. El chat anterior queda solo para buscar y armar repositorios.

---

## 0. Reglas para el agente que lee esto (obligatorias)

1. **Fuente única de verdad:** este archivo, el repositorio `alianato1013/alianato1013` (rama `claude/rea-repository-analysis-9eytp3`) y lo que la dueña te muestre de **AYOP**. Lo que no esté en esas fuentes **no existe**: pregúntale, no lo supongas.
2. **Primer paso, antes de hacer cualquier trabajo:**
   1. Explícale a la dueña, en un máximo de 10 líneas y en español sencillo, lo que entendiste.
   2. **Espera a que diga "correcto".** Si corrige algo, anota su corrección textual en la sección 2 de este archivo y súbelo al repositorio.
3. **Etiquetas:**
   - **HECHO:** con su fuente.
   - **DECISIÓN DE LA DUEÑA:** con su cita textual.
   - **PROPUESTA (sin aprobar):** idea del agente.
   - **NO VALIDADO:** sin comprobar.

   No asciendas nada de categoría.
4. **No cambies una decisión ni una regla de canal** sin que ella lo diga. Si te parece un error, díselo y pregunta.
5. **Las reglas de siempre:**
   - no pidas secretos en el chat;
   - no gastes dinero sin su OK;
   - solo modelos con licencia comercial;
   - no copies la narración ni la reescribas.

## 1. Qué es AYOP (lo que se sabe y lo que no)

- **HECHO** (fuente: su artefacto "Plan 14 en AYOP", https://claude.ai/artifact/CXACEoUCYQf1Te6YJppkoH, del 23 de octubre):
  - AYOP es su sistema de producción, con una página por canal y el botón "▶ Crear episodio".
  - Las etapas de un episodio son: Tema → Guion → Voz → Prompts → Generar → Ensamblar → Miniaturas → SEO → Shorts.
  - El plan de 14 semanas de Hard Times Heritage está montado dentro de AYOP: 42 videos del 26 de octubre al 29 de enero, lunes, miércoles y viernes a las 10:00 a. m. ET.
  - El video #1 (26 de octubre) es "25 "Poor Man" Money Habits 1950s Mothers Used That Seniors on Fixed Incomes Need Now".
- **HECHO:** también existe su artefacto "Plan Sumerian en AYOP" (https://claude.ai/artifact/ALrnmgXNy4U6ErQduXgVHT). **No se leyó en el chat anterior.** Léelo antes de trabajar en Sumerian Vault.
- **NO VALIDADO:**
  - dónde vive el código de AYOP (no está en este repositorio);
  - si "Job System", que ella mencionó, es AYOP;
  - qué herramientas usa AYOP hoy para la voz y las imágenes.

  Pregúntaselo.
- **Error del chat anterior, corregido aquí:** ese chat le describió las etapas del **Editor Supremo** (`editor-supremo/`, una capa sobre OpenMontage que está en este repositorio) como si fueran las de AYOP. **Son dos sistemas distintos.** El Editor Supremo nunca ha producido un video real. No mezcles los dos sin que ella decida.

## 2. Decisiones de la dueña (citas textuales)

| Tema | Lo que dijo, tal cual |
|---|---|
| Calendario | "ya el lunes tiene que salir el primer video. Del canal de HTH. Y el martes sale el de Sumerio. Así que hay que producir. Porque tiene que ser antes de febrero. Nos quedan 14 semanas." |
| Las 8 mejoras de edición | "toda la propuesta que me enseñaste del 1 al 8 me parece fantástica. Hazme el demo y tomo la decisión entonces para cambiar la regla que tengo. Pero no lo voy a hacer hasta que no vea el demo de ambos canales. ¿Entendido?" |
| Demos | "Hard Times Heritage y Sumerian Vault, hazme el demo … el último video de cada canal … Te voy a dejar que seas tú el que escoja el video" |
| Prioridad | "Si no te ves ahora hacer los demos, pues arranca a montar las fases, porque ya el lunes tiene que salir el primer video." |
| La GPU | "yo quiero que esto viva dentro de Job System" |
| Separar el chat | Pidió mover la producción a otro chat, con un traspaso exacto. |

**Las reglas de los canales siguen como están** (solo zoom y paneo, transiciones suaves) **hasta que ella vea los dos demos y decida.**

## 3. Las 8 mejoras de edición (PROPUESTA: le gustó, falta el demo)

1. Efecto 3D en fotos (parallax).
2. Texto animado al ritmo de la voz.
3. Recortes de época: periódicos y recibos con subrayado (HTH).
4. Mapas animados (Sumerian Vault).
5. Líneas de tiempo animadas (Sumerian Vault).
6. Textura de época: grano, viñeta y polvo.
7. Diseño de sonido.
8. Ritmo de retención: los primeros 30 s rápidos y un cambio de formato visual cada 30–45 s.

(La 9, clips con Wan 2.2, es opcional y no forma parte de su "1 al 8").

**No se prometió ningún número de retención.** El efecto se mide comparando la curva real de retención antes y después.

## 4. Los demos (PENDIENTE)

| Canal | Video elegido (el último publicado) | Tramo del demo |
|---|---|---|
| Hard Times Heritage | "17 Monthly Fees My Grandmother Never Paid — How Many Are You Paying" (`H-ezG630mRM`, 22 oct, 24:24) | 0:00–1:16: el gancho, hasta "And tonight, I'm giving you every one of them." |
| Sumerian Vault | "Before the Flood, the Gods Tried Plague and Famine — What the Atrahasis Tablet Says" (`xEXJe5HuEi0`, 21 oct, 17:39) | 0:00–1:00: el gancho, hasta "So, let's start with the text itself." |

**Por qué no se hicieron en el chat anterior:** la red de esa sesión bloqueaba YouTube, loc.gov y wikimedia.org, así que no había fotos ni audio originales. Donde la red esté abierta (la PC de la dueña o su servidor):
- usar el audio y las imágenes del video original, o la voz fija del canal;
- hacer un antes/después del mismo tramo.

## 5. Lo que hay en este repositorio y puede servir a AYOP

| Pieza | Dónde | Estado |
|---|---|---|
| Estudio GPU propio: Qwen-Image (Apache-2.0) en un pod de RunPod que se apaga solo | `estudio-gpu/` | Escrito; probado contra un ComfyUI simulado; **sin probar con un pod real** |
| Editor Supremo (biblias de los 3 canales, auditor visual, modo de 3 pausas) | `editor-supremo/` | Escrito; **nunca ha producido un video real**. Las biblias (`editor-supremo/overlay/channels/*/CHANNEL_BIBLE.md`) sirven de referencia de estilo |
| Planes y calendarios de los canales | `plan-hard-times-heritage/`, `plan-sumerian-vault/`, `plan-beneath-america/` | Escritos |

**Estado de RunPod:** US$20 de saldo y el volumen `modelos-comfyui` de 60 GB en EU-RO-1. El pod está configurado pero **no desplegado**.

## 6. PENDIENTE, en orden

| # | Tarea | Terminado cuando |
|---|---|---|
| 1 | El video #1 de HTH del lunes 26 de octubre, en AYOP, como de costumbre | Publicado a su hora |
| 2 | El video de Sumerian Vault del martes, en AYOP | Publicado |
| 3 | Los 2 demos de la sección 4 | Ella los vio y decidió sobre la regla de edición |
| 4 | Si ella aprueba: las 8 mejoras dentro de AYOP (etapa Ensamblar) y el cambio de regla escrito con sus palabras | Un video real sale con las mejoras |
| 5 | Si ella lo pide: el estudio GPU dentro de AYOP ("Job System") para no pagar créditos de imágenes | AYOP genera imágenes en su pod |
