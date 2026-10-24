# Estudio GPU propio: imágenes de IA sin pagar créditos

## Primero: qué es una GPU y por qué no necesitas comprar una

Una **GPU** es el chip que hace los cálculos de la IA que genera imágenes. Tu laptop no tiene una dedicada, y comprar una buena (RTX 4090 o 5090) cuesta miles de dólares.

**No hace falta comprarla: se alquila por hora.** En RunPod alquilas una computadora con GPU en la nube:
- la **enciendes** solo mientras se generan las imágenes de un video;
- se **apaga sola** cuando termina;
- **pagas solo esos minutos.**

Es como un taxi: no compras el carro, pagas el viaje.

**Precios de referencia (2026; confírmalos en la web):**
- RTX 4090: ~US$0,34/h ([Hack'celeration](https://www.hackceleration.com/labs/runpod-pricing), [Beam](https://www.beam.cloud/blog/nvidia-rtx-4090-pricing));
- RTX 5090: ~US$0,69–0,99/h ([ComputePrices](https://computeprices.com/providers/runpod/gpus/rtx5090), [DIY AI](https://diyai.io/ai-tools/hosting/runpod-pricing/)).

## Cómo encaja en tu sistema de producción

```
TU SERVIDOR (Contabo, sin GPU, ~US$16/mes) — aquí vive todo el sistema
 1. Propuesta ─ 2. Guion (bloqueado) ─ 3. Plan de escenas
 4. RECURSOS
    a) Archivo gratis primero: Library of Congress, NARA, Internet Archive, Wikimedia
       (OpenMontage ya trae estos buscadores)
    b) Lo que el archivo no tiene → lista de imágenes (ai_batch.jsonl)
          │   túnel seguro (SSH)
          ▼
      ┌──────────────────────────────────────────────┐
      │ GPU ALQUILADA (RunPod, por hora)             │
      │ ComfyUI + Qwen-Image (licencia comercial OK) │
      │ ~35 s por imagen en una 4090                 │
      │ se apaga sola tras 20 min sin trabajo        │
      └──────────────────────────────────────────────┘
          │   las imágenes vuelven al servidor
          ▼
 5. Edición + auditoría 1 ─ 6. ENSAMBLADO Y RENDER (Remotion, en el servidor, NO usa GPU) + auditoría 2
 7. Publicación ─ entrega a Drive ─ subida a YouTube
```

**Respuesta corta a tu pregunta:**
- **el guion, la estructura visual, el ensamblado y el render** siguen en tu servidor, como hasta ahora;
- **la GPU solo hace una cosa:** las imágenes de IA que el archivo no tiene. Se usa unos minutos por video y se apaga.

## Por qué Qwen-Image y no FLUX

La plantilla que trae OpenMontage usa **FLUX 2 Dev**, y su licencia **no permite uso comercial** ([Hugging Face](https://huggingface.co/black-forest-labs/FLUX.2-klein-base-9B/blob/main/LICENSE.md), [InVideo](https://invideo.io/blog/flux-ai-image-generator/)). Un canal monetizado es uso comercial.

Por eso usamos **Qwen-Image** con su acelerador **Lightning**. Los dos tienen **licencia Apache-2.0**, que permite uso comercial:
- [Comfy-Org/Qwen-Image](https://huggingface.co/Comfy-Org/Qwen-Image), con su [tutorial oficial en ComfyUI](https://docs.comfy.org/tutorials/image/qwen/qwen-image);
- [lightx2v/Qwen-Image-Lightning](https://huggingface.co/lightx2v/Qwen-Image-Lightning).

Para video, si algún día lo apruebas: **Wan 2.2** (Apache-2.0).

## Lo que cuesta un video de Hard Times Heritage (estimado)

| Concepto | KIE (lo que pagas hoy) | Estudio propio |
|---|---|---|
| Imágenes de archivo (LOC, NARA, Internet Archive) | — | **US$0** |
| ~150–300 imágenes de IA (incluye las 2 versiones por imagen) | Créditos (US$50 cada 10.000) | ~1,5–3 h de GPU ≈ **US$0,50–3** |
| Almacenar los modelos (disco persistente de ~40 GB) | — | Unos pocos dólares al mes (confírmalo en RunPod) |
| Ensamblado y render | — | US$0 (tu servidor) |

**Base del cálculo:**
- tiempo por imagen: ~34 s en una RTX 4090D con Lightning, según la [guía de ComfyUI](https://docs.comfy.org/tutorials/image/qwen/qwen-image);
- número de imágenes: el canal cambia de imagen cada 3–6 s, así que un video de 25 minutos lleva unas 250–500 imágenes, y una parte sale del archivo.

**Son estimaciones.** El gasto real lo ves al final de cada tanda: el script imprime los minutos de GPU usados.

---

## Configuración (una sola vez, ~40 min)

### 1. Crea tu cuenta en RunPod (en tu PC)

1. Entra a **runpod.io** → **Sign up** → **Billing**, y carga crédito: con US$10 tienes para varios videos.
2. **Settings → SSH Public Keys:** pega la llave pública de tu **servidor**. Para verla, en el servidor:
   ```bash
   ssh editor@IP
   cat ~/.ssh/id_ed25519.pub 2>/dev/null || (ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519 && cat ~/.ssh/id_ed25519.pub)
   ```
3. **Storage → Network Volume → New:** 60 GB, en la misma región donde vayas a crear el pod. Es el disco donde quedan los modelos para no descargarlos cada vez.

### 2. Crea el pod (la computadora con GPU)

1. **Pods → Deploy.**
2. **GPU:** RTX 4090 (la más barata que sirve) o RTX 5090 (más rápida).
3. **Template:** "RunPod PyTorch" (la oficial).
4. **Network Volume:** el de 60 GB, montado en `/workspace`.
5. **Expose TCP Ports:** que incluya el 22 (SSH).
6. **Deploy.** Cuando esté en verde: **Connect → SSH over exposed TCP**. Ahí verás la **IP** y el **puerto** (por ejemplo, `ssh root@69.30.85.12 -p 22104`).

### 3. Primera conexión desde tu servidor (descarga los modelos, ~10–20 min)

```bash
ssh editor@IP_DE_TU_SERVIDOR
cd ~/alianato1013 && git pull && bash editor-supremo/install.sh ~/OpenMontage
bash ~/alianato1013/estudio-gpu/tunel.sh 69.30.85.12 22104
```
Usa la IP y el puerto de tu pod. Tiene que terminar con:
```
OK: http://127.0.0.1:8188 ready with Qwen-Image + Lightning
```

### 4. Opcional pero recomendado: que el agente encienda y apague el pod solo (5 min)

Runpod tiene un plugin oficial para Claude Code ([agents.runpod.io](https://agents.runpod.io/), código en [runpod/runpod-plugins-official](https://github.com/runpod/runpod-plugins-official)).

**Instálalo en el Claude Code de tu servidor,** no en tu PC ni en esta sesión:
```bash
ssh editor@IP_DE_TU_SERVIDOR
claude plugin marketplace add runpod/runpod-plugins-official
claude plugin install runpod@runpod
claude plugin list | grep -A2 'runpod@runpod'      # debe decir: Status: ✔ enabled
```

Después, en la sesión del editor (la que controlas desde la app):
1. Escribe `/reload-plugins`.
2. Escribe `/mcp` → **runpod** → **Sign in with Runpod**, y aprueba en el navegador. El acceso usa OAuth: **no se crea ni se guarda ninguna llave**.

**Cómo queda:** el agente enciende **tu** pod, toma la IP y el puerto, genera las imágenes y lo apaga. Tú no haces nada.

Por regla del sistema (`CHANNELS.md`), el agente **solo** puede encender y apagar el pod que ya creaste. **No puede crear pods nuevos ni cambiar la GPU sin tu OK.**

---

## Uso en cada video (lo que harás tú: 1 minuto)

1. Le pides el video al Editor, como siempre: "Canal: Hard Times Heritage. Guion: …".
2. En la etapa de **recursos**, el agente:
   - busca primero en el archivo gratis;
   - después arma la lista de imágenes de IA que faltan;
   - y te dice: **"Necesito la GPU: enciende el pod y dame IP y puerto".**
3. Entras a runpod.io → tu pod → **Start**. Copias la IP y el puerto de **Connect** y se los pegas al agente.
4. El agente:
   - conecta el túnel;
   - genera todas las imágenes, con 2 versiones cada una;
   - cierra el túnel.

   **El pod se apaga solo a los 20 minutos sin trabajo.**
5. Sigue la edición, la auditoría y el render en tu servidor, como siempre.

**Si alguna vez dudas, entra a runpod.io y mira que el pod diga "Stopped".** Un pod encendido cobra por hora. Un pod detenido solo cobra el disco.

## Seguridad y licencias

- **ComfyUI solo escucha dentro del pod** (`127.0.0.1`). Nadie en internet puede usarlo: solo tu servidor, a través del túnel SSH con tu llave.
- **Cada imagen guarda una ficha `.json`** con el modelo, la licencia (Apache-2.0), el prompt y la semilla. El auditor y el `asset_manifest` la usan.
- **Las APIs de pago (KIE y otras) quedan solo para excepciones** que tú apruebes en la propuesta, con su costo visible.

## Lo que tienes que saber

- **Probado aquí:**
  - el generador `gen_image.py`, contra un ComfyUI simulado: aplica el estilo del canal (Kodachrome de los 50 + lista negativa), hace 2 versiones, procesa la lista completa y guarda las fichas;
  - los scripts, revisados en su sintaxis.
- **Sin probar aquí:** un pod real de RunPod, porque desde aquí no hay GPU ni cuenta. La primera conexión es la prueba real.
  - Si algo falla, el mensaje dice en qué paso.
  - El apagado automático usa la herramienta `runpodctl` de RunPod. Si no está disponible, el registro lo avisa y **tendrás que detener el pod a mano**.
- **Calidad:** Qwen-Image con Lightning es muy bueno para fotos realistas. Igual revisa la hoja de contactos de la etapa 5 en los primeros videos: el auditor rechaza lo que no cumpla la biblia y lo vuelve a generar.
- **La biblia del canal no cambió:** archivo primero, después IA y después stock moderno solo para "hoy". Lo único que cambia es **dónde** se genera la IA: en tu GPU alquilada y no con créditos.
