# Producir en la nube sin llenar tu PC: paso a paso

**Sí se puede.** Tu PC solo sirve de "control remoto". Todo el trabajo pesado y los archivos viven fuera de ella:

```
TU PC / CELULAR                 SERVIDOR EN LA NUBE                    GOOGLE DRIVE
(app de Claude o navegador) ──▶  OpenMontage + Editor Supremo   ──▶  YouTube/<Canal>/<video>/
 solo das órdenes y apruebas     busca, genera, edita, audita,         final.mp4 + paquete
 no se guarda ningún video       renderiza y luego se limpia solo      (lo ves sin descargarlo)
```

- **Tu PC no instala OpenMontage, no renderiza y no guarda videos.**
- **El servidor no se llena:** al terminar cada video, el script `deliver.sh` lo sube a Google Drive, **verifica que la copia está completa** y borra del servidor las imágenes, el audio y el render (conserva solo los archivos pequeños de registro).
- Si la auditoría del video no pasó, **no se sube nada y no se borra nada**.

---

## Paso 1: Contratar el servidor (15 min)

**Lo que necesitas:** Ubuntu 24.04, **8 vCPU**, **16 GB de RAM o más**, **150 GB de disco o más**. No necesitas GPU: la IA se hace por API.

| Proveedor | Plan de referencia | Precio aprox. (verifícalo) | Nota |
|---|---|---|---|
| **Contabo** (recomendado por precio) | Cloud VPS 8: 8 vCPU, 24 GB RAM | ~USD 16/mes | CPU compartida: la velocidad de render puede variar |
| Hetzner | CPX/CCX de 8 vCPU | Subió mucho en 2026 (las fuentes no coinciden) | Muy fiable; revisa el precio actual |
| DigitalOcean / Vultr | 8 vCPU, 16 GB | ~USD 80–100/mes | Más caros |

> Los precios vienen de comparadores de 2026 y cambian a menudo. Confírmalos en la web del proveedor antes de pagar. La mayoría **cobra aunque el servidor esté apagado**; solo dejas de pagar si lo eliminas.

Al crearlo elige **Ubuntu 24.04** y la región más cercana (EE. UU. Este, si estás en Puerto Rico).

## Paso 2: Crear tu llave de acceso en Windows (5 min, una sola vez)

En **PowerShell**:
```powershell
ssh-keygen -t ed25519
type $env:USERPROFILE\.ssh\id_ed25519.pub
```
Pulsa Enter en todas las preguntas. Copia la línea que empieza con `ssh-ed25519` y **pégala en el proveedor** al crear el servidor (campo "SSH key").
Si el proveedor solo te dio una contraseña, añade la llave así (cambia `IP` por la IP de tu servidor):
```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh root@IP "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

## Paso 3: Preparar el servidor con un solo comando (20–40 min, automático)

```powershell
ssh root@IP
```
Ya dentro del servidor:
```bash
curl -fsSL https://raw.githubusercontent.com/alianato1013/alianato1013/claude/rea-repository-analysis-9eytp3/editor-supremo/cloud/setup-server.sh -o setup.sh
bash setup.sh
```
**Instala todo:**
- FFmpeg, Python, Node y las dependencias de render.
- Las **fuentes de tus canales** (Playfair, Lora, Cormorant, Montserrat, Inter).
- 8 GB de memoria de intercambio.
- El firewall (solo SSH).
- Un usuario `editor`.
- **OpenMontage + Editor Supremo** (y lo valida).
- **Claude Code** y **rclone**.

Al final verás `DONE.`

## Paso 4: Poner tus claves de API (5 min)

```powershell
ssh editor@IP
```
```bash
nano ~/OpenMontage/.env
```
Pega tus claves (`ELEVENLABS_API_KEY`, `FAL_KEY`, `PEXELS_API_KEY`, `PIXABAY_API_KEY`, etc.). Guarda con **Ctrl+O → Enter → Ctrl+X**.
Las claves quedan **solo en el servidor**; no las pegues en el chat.

## Paso 5: Conectar Google Drive (10 min, una sola vez)

En el servidor:
```bash
rclone config
```
Responde así:
1. `n` (nuevo remoto) → nombre: **`gdrive`**
2. Tipo de almacenamiento: **`drive`** (Google Drive)
3. `client_id` y `client_secret`: deja vacío (Enter)
4. Scope: **`1`** (acceso completo)
5. Lo siguiente en blanco hasta: *"Use web browser to automatically authenticate?"* → **`n`**
6. Te mostrará un comando que empieza con `rclone authorize "drive" ...`. **Cópialo.**

En tu PC (solo para este paso):
1. Descarga rclone para Windows desde rclone.org/downloads, descomprímelo y abre PowerShell en esa carpeta.
2. Pega el comando: `.\rclone.exe authorize "drive" "..."`. Se abre el navegador; entra con tu cuenta de Google y acepta.
3. PowerShell muestra un **código (token)**. Cópialo y pégalo en el servidor. Termina con Enter y `q`.
4. Después puedes **borrar la carpeta de rclone de tu PC**; no se vuelve a necesitar.

Comprueba en el servidor:
```bash
rclone mkdir gdrive:YouTube
rclone mkdir gdrive:Guiones
rclone lsd gdrive:
```

**Espacio en Drive:**
- Google da 15 GB gratis, que alcanzan para unos 5–8 videos de 25 min.
- Para guardar un archivo histórico, Google One de 2 TB cuesta unos USD 10/mes (verifica el precio).
- Si prefieres no pagar: borra de Drive cada video después de subirlo a YouTube (YouTube es tu archivo final).

## Paso 6: Abrir el editor y controlarlo desde la app de Claude (5 min)

En el servidor:
```bash
tmux new -s editor
cd ~/OpenMontage
claude
```
- La primera vez, Claude Code te muestra un enlace para iniciar sesión: ábrelo en tu PC o celular y aprueba. Necesitas una suscripción de Claude; para sesiones largas de producción conviene **Max**.
- Sal de esa sesión y deja el editor escuchando:
  ```bash
  claude remote-control
  ```
- La sesión aparece en tu **app de Claude Code** (PC o celular). **Desde ahí le das las órdenes**, igual que en este chat.
- Para dejarlo corriendo aunque cierres PowerShell: **Ctrl+B y luego D**. Para volver: `ssh editor@IP` y `tmux attach -t editor`.

## Paso 7: Producir un video

1. **Sube el guion** a tu Google Drive, carpeta **`Guiones`** (desde el navegador; no ocupa espacio en tu PC).
2. En la sesión del editor, escribe:
   ```text
   Trae los guiones nuevos: rclone copy gdrive:Guiones ~/guiones
   Canal: Hard Times Heritage. Guion: ~/guiones/hth-25-poor-man-habits.md
   ```
3. Aprueba cada etapa cuando te lo pida (propuesta, guion, escenas, recursos, auditoría y render).
4. **Para ver el tablero en vivo** (opcional; se ve en el navegador sin descargar nada):
   ```powershell
   ssh -L 4750:localhost:4750 editor@IP
   ```
   Abre `http://localhost:4750` en tu PC.
5. Al aprobar la publicación, el editor ejecuta `deliver.sh` **solo**:
   - sube a `Drive / YouTube / <Canal> / <proyecto>/` el `final.mp4`, las miniaturas, el paquete de publicación, los reportes de auditoría y el guion;
   - verifica la copia;
   - **limpia el servidor**;
   - te da el enlace.

## Paso 8: Subir a YouTube directo desde la nube

Sigue **`YOUTUBE-API-PASO-A-PASO.md`** (una sola vez, gratis, ~30 min). A partir de ahí le dices al editor:
*"Sube a YouTube, programado para el lunes a las 10 a. m. hora del Este"*. El servidor sube el video (privado + programado), pone la miniatura, lo guarda en Drive y se limpia. **Tu PC nunca toca el archivo.**

---

## Mantenimiento

| Tarea | Comando (en el servidor) |
|---|---|
| Ver el espacio libre | `df -h ~` |
| Actualizar el Editor Supremo | `cd ~/alianato1013 && git pull && bash editor-supremo/install.sh ~/OpenMontage` |
| Actualizar OpenMontage | `cd ~/OpenMontage && git pull && . .venv/bin/activate && pip install -r requirements.txt && bash ~/alianato1013/editor-supremo/install.sh ~/OpenMontage` |
| Entregar a mano un proyecto | `cd ~/OpenMontage && bash scripts/channel_cloud/deliver.sh <proyecto>` |
| Volver a la sesión del editor | `tmux attach -t editor` |

## Costos mensuales aproximados

| Concepto | Costo |
|---|---|
| Servidor (Contabo, 8 vCPU) | ~USD 16–20 |
| Google Drive | Gratis (15 GB) o ~USD 10 (2 TB) |
| API por video (voz, imágenes) | Según la mezcla A/B/C que apruebes; tope de USD 15 por video |
| Suscripción de Claude | Tu plan actual (Max recomendado) |

## Lo que tienes que saber

- **El tiempo de render en el servidor no lo he medido.** Un video de 25 min a 1080p son unos 45.000 fotogramas, y en una CPU compartida puede tardar bastante. **Haz primero una prueba de 2–3 min.** Si es lento, sube a un plan con más vCPU.
- **Lo que probé aquí:**
  - **Funciona:** el script de entrega con rclone real (bloquea si la auditoría no pasó; si pasó, sube, verifica con 0 diferencias y limpia).
  - **Solo revisé la sintaxis:** el instalador del servidor. Ejecútalo en un Ubuntu 24.04 limpio; si un paso falla, la guía te dice dónde está cada pieza.
- **Seguridad:** entra solo con tu llave SSH, no compartas el archivo `.env` y no abras otros puertos. El tablero se ve por el túnel SSH, no por internet.
