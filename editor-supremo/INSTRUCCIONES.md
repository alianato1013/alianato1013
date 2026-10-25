# Editor Supremo: instrucciones

**Qué es:** una capa encima de [OpenMontage](https://github.com/calesthio/OpenMontage) (~71k estrellas) que lo convierte en **un editor individual para cada uno de tus 3 canales**. Le entregas un guion terminado y:

1. **Usa tu guion palabra por palabra.** Queda bloqueado con una huella digital (hash): si una sola palabra cambia, el sistema lo detecta y se detiene.
2. **Aplica las reglas fijas del canal** (su "biblia"): estilo, paleta, tipografía, voz, ritmo, música, subtítulos, tipo de imágenes y lo que está prohibido.
3. **Busca o crea cada imagen** según el orden de fuentes del canal: primero archivo real o de dominio público, después IA.
4. **Arma la línea de tiempo**, añade música, subtítulos, transiciones, tarjetas, mezcla de audio y movimiento.
5. **Audita dos veces cada frase contra la imagen que se ve en ese momento:** en la línea de tiempo antes de renderizar y en el video final. Cualquier imagen que no represente lo que se escucha **se rechaza y se reemplaza**. El video no se entrega hasta que todo pasa.

---

## 1. Lo que hay en esta carpeta

| Archivo | Para qué sirve |
|---|---|
| `overlay/CHANNELS.md` | La regla de entrada: si mencionas un canal, el agente lee esto **antes que nada** |
| `overlay/channels/<canal>/CHANNEL_BIBLE.md` | **La biblia inmutable de cada canal** (en inglés, que es el idioma del agente y de OpenMontage) |
| `overlay/styles/custom/<canal>.yaml` | El estilo visual del canal en el formato oficial de OpenMontage (validado) |
| `overlay/pipeline_defs/channel-documentary.yaml` | El flujo de producción propio, con las 2 auditorías obligatorias |
| `overlay/skills/channels/` | Las instrucciones del enrutador, la propuesta, el bloqueo del guion y el auditor |
| `overlay/scripts/channel_audit/audit.py` | La herramienta que empareja cada frase con su imagen y verifica las notas |
| `install.ps1` / `install.sh` | Instaladores para Windows / Mac y Linux |
| `cloud/PASO-A-PASO-NUBE.md` | **Producir en un servidor en la nube** sin llenar tu PC (guía + `cloud/setup-server.sh`) |
| `cloud/YOUTUBE-API-PASO-A-PASO.md` + `overlay/scripts/channel_cloud/youtube_upload.py` | Subir a YouTube directo desde el servidor (privado, programado, con miniatura) |
| `overlay/scripts/channel_cloud/deliver.sh` | Sube el video terminado a Google Drive, verifica la copia y limpia el servidor |

---

## 2. Instalación (una sola vez, en Windows)

1. Instala lo que pide OpenMontage: **Python 3.10+**, **FFmpeg**, **Node.js 18+** y **Claude Code**.
2. Descarga OpenMontage y prepáralo:
   ```powershell
   git clone https://github.com/calesthio/OpenMontage.git
   cd OpenMontage
   py -3 -m venv .venv; .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   cd remotion-composer; npm install; cd ..
   python -m pip install piper-tts
   Copy-Item .env.example .env
   ```
3. Descarga tu repo (`alianato1013`, rama `claude/rea-repository-analysis-9eytp3`) y, desde la carpeta `editor-supremo`, ejecuta:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\install.ps1 -Target C:\ruta\a\OpenMontage
   ```
   Tiene que terminar con `OK playbooks + pipeline`.
4. Abre `OpenMontage\.env` y añade las claves que vayas a usar:
   - `ELEVENLABS_API_KEY` para la voz.
   - `FAL_KEY` para las imágenes y los clips de IA.
   - `PEXELS_API_KEY` y `PIXABAY_API_KEY` para stock gratis.
   - Sin claves también funciona (con voz Piper y material de archivo), pero con menos calidad.
5. Abre la carpeta `OpenMontage` con **Claude Code**.

> Si actualizas OpenMontage (`git pull`), vuelve a ejecutar `install.ps1`. Es seguro repetirlo: no duplica nada.

---

## 3. Cómo pedir un video (lo que escribes en Claude Code)

Siempre di **el canal** y **dónde está el guion**. Ejemplos:

```text
Canal: Hard Times Heritage. Produce este guion con el Editor Supremo: C:\guiones\hth-25-poor-man-habits.md
```
```text
Canal: Sumerian Vault. Guion adjunto en C:\guiones\sv-7-gates.md. Usa la biblia del canal.
```
```text
Canal: Beneath America. Guion: C:\guiones\ba-new-york.md
```

Si no dices el canal, **el agente tiene que preguntarte** (está prohibido que lo adivine por el tema).

### Lo que va a pasar y dónde te pide aprobación

| Etapa | Qué hace | ¿Te pide aprobación? |
|---|---|---|
| 1. Propuesta | Confirma el canal, el estilo y la voz. Te da 3 variantes de **mezcla de imágenes y costo** (A: más archivo y más barato · B: equilibrada · C: más IA). **Nunca cambia el ángulo** | ✅ Sí |
| 2. Guion | Lo divide en secciones usando tus marcadores, calcula los tiempos y **lo bloquea** | ✅ Sí |
| 3. Plan de escenas | Decide qué imagen corresponde a cada frase | ✅ Sí |
| 4. Recursos | Genera la voz con la voz bloqueada del canal y busca o crea las imágenes y la música | ✅ Sí |
| 5. Edición + **auditoría 1** | Arma la línea de tiempo y audita cada frase contra su imagen. Te muestra la hoja de contactos | ✅ Sí |
| 6. Render + **auditoría 2** | Renderiza, transcribe el audio final y vuelve a auditar los fotogramas reales del video | ✅ Sí |
| 7. Publicación | Título, descripción, capítulos, créditos y avisos | ✅ Sí |

**La primera vez en cada canal** te pedirá elegir la voz entre 2–3 muestras. Queda guardada en `channels/<canal>/voice.lock.json` y **nunca cambia**.

### Modo de 3 pausas (cuando ya confíes en el estilo)

La tabla de arriba es el **modo completo**, que viene por defecto. Cuando quieras menos interrupciones, escribe **"activa modo 3 pausas"**. Desde entonces el agente solo se detiene en 3 momentos:
1. la **propuesta**;
2. el **video final**, ya auditado;
3. **"sube a YouTube"**.

Las demás etapas siguen solas, pero solo si pasan sus revisiones. Las dos auditorías siguen siendo obligatorias.

**Aun en este modo, el agente te pregunta cuando:**
- una auditoría no llega a PASA después de 3 intentos de arreglo;
- algo costaría más de lo aprobado en la propuesta;
- la biblia no define algo importante;
- hay que encender la GPU y no tiene el plugin de Runpod.

Para volver al modo completo, escribe **"activa modo completo"**. Recomendación: usa el modo completo en los 2 o 3 primeros videos de cada canal.

---

## 4. Cómo escribir el guion para cada canal (los marcadores)

Los marcadores van **solos en su línea, entre corchetes**. No se narran; le dicen al editor cómo armar el video.

**Hard Times Heritage** (cuenta regresiva, 140 ppm):
```text
Picture a kitchen in Dayton, 1954…            ← gancho (todo lo anterior al primer ítem)
[ITEM #25: The Coffee Can Behind the Flour]
She dropped every spare coin inside…
[VISUAL: close-up of a coffee can full of coins]   ← pista opcional
[ITEM #24: …]
```

**Sumerian Vault** (actos, 140 ppm):
```text
This tablet sits in the Penn Museum…           ← gancho
[ACT 1: The Object]
…
[ACT 2: What the Text Says]
```

**Beneath America** (capas, 150 ppm):
```text
The Angel has fourteen steps that weren't there…   ← gancho
[BRAND CARD]
[LAYER: 0–10 FT · The Streets]
…
[LAYER: 300 FT · The Aquifer]
```

⚠️ **Si tu guion trae etiquetas `[VERIFY]` o `[SRC]` sin resolver, el editor se detiene** y te pide resolverlas. No inventa datos.

---

## 5. El auditor: cómo decide qué imagen se rechaza

Cada fila es **una frase × una imagen que se ve mientras se dice**. El agente **abre cada imagen y la mira** (está prohibido calificar leyendo el prompt) y le pone nota:

| Nota | Significado | Resultado |
|---|---|---|
| 5 | Muestra exactamente lo que dice la frase | ✅ |
| 4 | Representa claramente el tema de la frase | ✅ (mínimo del canal: **4**) |
| 3 | Mismo tema general, pero no lo que dice la frase | ❌ |
| 2–1 | Poco relacionada, sin relación o contradictoria | ❌ |

**Rechazo automático** aunque la nota sea alta: anacronismo (un objeto de otra época), lugar equivocado, número o sujeto equivocado (una "viuda sola" mostrada con una familia), errores de IA (manos, texto deformado), marcas de agua, una persona real hecha con IA, algo prohibido por la biblia, un tono que choca con la frase, subtítulos tapando lo importante o un estilo fuera del canal.

Si hay fallos, el editor **vuelve a elegir, buscar o generar** esa imagen y repite la auditoría. Después de 3 rondas con fallos, se detiene y te muestra cada frase problemática para que decidas.

Puedes ver el resultado tú misma:
- `projects/<proyecto>/audit/storyboard/contact_sheet.html` (antes del render)
- `projects/<proyecto>/audit/render/contact_sheet.html` (video final)
- `audit_report.json` → `"status": "PASS"` o `"FAIL"`

---

## 6. Las reglas que jamás cambian (resumen de cada biblia)

| | Hard Times Heritage | Sumerian Vault | Beneath America |
|---|---|---|---|
| Estilo | Kodachrome de los 50; crema, rojo ladrillo, menta, mostaza | Lapislázuli + oro, luz de vela | Cortes transversales; tierra, cian y amarillo |
| Fuentes de imagen | Library of Congress / archivo → IA de los 50 → stock moderno solo para "hoy" | Fotos reales de tablillas (The Met CC0, Wikimedia) → IA para diosas y rituales | USGS / NASA / NOAA / NPS → stock → Google Earth con atribución → IA solo para cortes |
| Tarjeta de sección | Ítem "#N" en papel crema | Acto en azul y oro | Profundidad "300 FT" en amarillo |
| Ritmo | 3–6 s por imagen, solo fundidos | 3–6 s, solo fundidos | 2–4 s, cortes y fundidos |
| Voz y ppm | Cálida, madura · 140 | Grave, reverente · 140 | Segura, curiosa · 150 |
| Prohibido | Objetos modernos en frases de época, lujo, consejos médicos o de inversión, personas reales con IA | Alienígenas, Egipto o Grecia como si fueran Sumer, cuneiforme falso, tablillas IA presentadas como reales, imágenes del British Museum | Conspiraciones, lugares parecidos que no son el lugar nombrado, desastres de otro sitio |
| Nota mínima | 4 | 4 | 4 |

**¿Quieres cambiar una regla?** Escríbelo explícitamente: *"cambia la biblia de Sumerian Vault: …"*. El agente cita la regla actual, la cambia y lo registra. Sin esa frase, **no puede** cambiar nada.

---

## 7. Limitaciones

- **El auditor es el propio agente mirando cada imagen**, guiado por reglas y una herramienta que empareja frase con fotograma de forma exacta. Es muy estricto, pero no es infalible: **revisa tú la hoja de contactos** en la etapa 5, sobre todo en los primeros videos.
- **Lo probé con un proyecto de prueba:**
  - **Funcionan:** el bloqueo del guion, el emparejamiento frase↔imagen por tiempo, la extracción de fotogramas, la detección de huecos sin imagen, el veredicto PASS/FAIL, los estilos y el pipeline (con los validadores oficiales de OpenMontage) y el bloqueo de etapas sin aprobación.
  - **No lo he probado todavía:** un video real completo de punta a punta (requiere tus claves de API). Hazlo primero con un guion corto de 2–3 minutos.
  - **El instalador de Windows (`install.ps1`) no lo pude ejecutar aquí** porque este servidor no tiene PowerShell; el de Mac/Linux sí lo probé. Si `install.ps1` falla, copia a mano el contenido de `overlay` dentro de la carpeta de OpenMontage y añade al principio de su `CLAUDE.md` la línea: "Si la petición menciona Hard Times Heritage, Sumerian Vault o Beneath America, lee CHANNELS.md primero."
- **Videos de 25 minutos en tu laptop:** el render es lento (no hay GPU dedicada). Funciona, pero para 3 o más videos por semana conviene un servidor en la nube (sin GPU; la IA va por API).
- **Licencia de OpenMontage (AGPL-3.0):** puedes usarlo libremente para tus videos. Solo te obliga a publicar tu código si distribuyes una versión modificada o la ofreces como servicio a otros.
- **Costo:** depende de la mezcla que elijas en la propuesta. Por defecto cada video tiene un tope de **USD 15** (se puede cambiar en la aprobación).
