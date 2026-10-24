# Montaje completo guiado por Claude Code (instrucciones para el agente)

> **Para ti, la dueña:** abre Claude Code en tu computadora y pega esta única línea:
>
> `Lee https://raw.githubusercontent.com/alianato1013/alianato1013/claude/rea-repository-analysis-9eytp3/MONTAJE-CON-CLAUDE.md y guíame paso a paso para montar mi sistema. Yo hago solo lo que me pidas.`
>
> Claude ejecuta los comandos. Tú solo haces lo que una máquina no puede hacer: pagar, iniciar sesión, aprobar permisos y escribir contraseñas.

---

## Reglas para el agente (Claude Code en la PC de la dueña)

1. **Un paso a la vez.** Antes de cada paso, explica en 1–2 líneas qué vas a hacer y por qué. Después de cada paso, **verifica** que funcionó y dilo. Nunca avances con un paso fallido.
2. **La dueña no es técnica.**
   - Habla en español, con frases cortas.
   - Cuando ella deba hacer algo, dale **una sola acción** con el botón o la pantalla exactos.
   - Pídele captura si hay duda.
3. **Secretos.**
   - Nunca le pidas que pegue en el chat contraseñas, tokens ni llaves de API.
   - Cuando haga falta una, abre el editor o el comando en una terminal donde **ella** la escriba directamente, por ejemplo con `nano` dentro de una sesión `ssh` interactiva.
   - Las llaves **públicas** SSH sí se pueden mostrar y copiar.
4. **Dinero.**
   - No contrates, no despliegues pods y no cargues saldo sin su OK explícito.
   - Ella paga en el navegador.
   - Si dejas un pod de Runpod encendido sin trabajo, avísale que lo detenga.
5. **Esta PC es Windows.**
   - Los comandos locales van en **PowerShell**.
   - Los comandos del servidor se ejecutan con `ssh editor@IP "comando"` o en una sesión `ssh` interactiva.
   - No mezcles sintaxis: `||` y `&&` no funcionan en PowerShell 5.
6. **Fuente de verdad:** las guías del repositorio. Si algo de la pantalla real no coincide, describe lo que ves y adapta; no inventes opciones.
7. **Al final de cada fase,** muestra la tabla de progreso actualizada (ver abajo).

## Lo que ya existe (no repetir)

- **Runpod:** cuenta creada y saldo de **US$20**. Network volume **`modelos-comfyui`** de 60 GB en **EU-RO-1**. El pod **todavía no** está creado. La plantilla elegida es "Runpod PyTorch 2.8.0", GPU **RTX PRO 4500**, puerto TCP 22 y Jupyter apagado.
- **El repositorio** con todo el código: `github.com/alianato1013/alianato1013`, rama `claude/rea-repository-analysis-9eytp3`.

## Tabla de progreso (muéstrala al final de cada fase)

| Fase | Qué | Estado |
|---|---|---|
| 1 | Servidor en la nube contratado | ☐ |
| 2 | Llave SSH de la PC → servidor | ☐ |
| 3 | Servidor preparado (`setup-server.sh`) | ☐ |
| 4 | Llaves de API en el servidor | ☐ |
| 5 | Google Drive conectado (rclone) | ☐ |
| 6 | Claude Code en el servidor + control desde la app | ☐ |
| 7 | GPU: llave en Runpod, pod creado, modelos descargados | ☐ |
| 8 | Brain Storming + ahorro de tokens | ☐ |
| 9 | Prueba: 1 video corto de Hard Times Heritage | ☐ |

---

## Fase 1: Contratar el servidor (lo hace ella en el navegador)

Guía: `editor-supremo/cloud/PASO-A-PASO-NUBE.md`, paso 1.

- **Proveedor:** Contabo (Cloud VPS de 8 vCPU / 24 GB RAM, ~US$16/mes; confirmar el precio en la web).
- **Sistema:** **Ubuntu 24.04.** **Región:** EE. UU. Este.
- **Cuando termine,** ella recibe un correo con la **IP** y la **contraseña de root**. Pídele **solo la IP**. La contraseña la escribirá ella en la terminal cuando se la pida.

## Fase 2: Llave SSH de la PC (lo haces tú, en PowerShell)

1. Comprueba si existe: `Test-Path $env:USERPROFILE\.ssh\id_ed25519.pub`.
2. Si no existe: `ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\id_ed25519 -N '""'`.
3. Copia la llave al servidor. **La contraseña de root la escribe ella** cuando la terminal la pida:
   ```powershell
   type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh root@IP "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
   ```
4. **Verifica** que ya entra sin contraseña: `ssh -o BatchMode=yes root@IP "echo ok"`.

## Fase 3: Preparar el servidor (lo haces tú; tarda 20–40 min)

```powershell
ssh root@IP "curl -fsSL https://raw.githubusercontent.com/alianato1013/alianato1013/claude/rea-repository-analysis-9eytp3/editor-supremo/cloud/setup-server.sh -o setup.sh && bash setup.sh"
```

- **Tiene que terminar en `DONE.`** Si falla, lee el error, explícaselo y corrígelo.
- **Verifica:** `ssh editor@IP "ls ~/OpenMontage ~/alianato1013 && claude --version"`.

## Fase 4: Llaves de API (las escribe ella)

Abre una sesión interactiva para que ella pegue sus llaves en el archivo. Guía: `PASO-A-PASO-NUBE.md`, paso 4.

```powershell
ssh -t editor@IP "nano ~/OpenMontage/.env"
```

Explícale qué línea va con cada llave:
- `ELEVENLABS_API_KEY` (voz);
- `PEXELS_API_KEY` y `PIXABAY_API_KEY` (gratis, para stock moderno).

Las que no tenga, quedan vacías. **Guardar:** Ctrl+O, Enter, Ctrl+X.

## Fase 5: Google Drive (ella aprueba en el navegador)

Sigue `PASO-A-PASO-NUBE.md`, paso 5 (`rclone config` en el servidor + `rclone authorize` en la PC).
- Descarga rclone para Windows tú mismo en una carpeta temporal y bórrala al terminar.
- **Verifica:** `ssh editor@IP "rclone lsd gdrive:"`.

## Fase 6: Claude Code en el servidor (ella inicia sesión)

```powershell
ssh -t editor@IP "tmux new -As editor"
```

1. Dentro de tmux: `claude`. Ella abre el enlace y aprueba el inicio de sesión. Después, `/exit`.
2. `cd ~/OpenMontage && claude remote-control`. La sesión aparece en su app de Claude.
3. Para salir de tmux sin cerrarlo: **Ctrl+B y luego D**.

**Verifica** con ella que ve la sesión en la app.

## Fase 7: GPU en Runpod (estudio de imágenes)

Guía: `estudio-gpu/PASO-A-PASO-ESTUDIO-GPU.md`.

1. **Llave del servidor:**
   ```powershell
   ssh editor@IP "test -f ~/.ssh/id_ed25519 || ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519; cat ~/.ssh/id_ed25519.pub"
   ```
   Muéstrale la línea `ssh-ed25519 …`. Ella la pega en Runpod → **Credentials → SSH public keys → Add SSH key**, con el título `servidor-editor`.
2. **Ella despliega el pod.** Pods → Deploy, con todo lo que ya eligió: RTX PRO 4500, PyTorch 2.8.0, volumen `modelos-comfyui` en `/workspace`, TCP 22. Que lo llame `estudio-imagenes`.
3. **Ella te da la IP y el puerto** de *Connect → SSH over exposed TCP*.
4. **Tú ejecutas** (la primera vez descarga ~31 GB de modelos, 10–20 min):
   ```powershell
   ssh editor@IP "bash ~/alianato1013/estudio-gpu/tunel.sh IP_POD PUERTO_POD"
   ```
   **Tiene que terminar con** `OK: … ready with Qwen-Image + Lightning`. Después:
   ```powershell
   ssh editor@IP "bash ~/alianato1013/estudio-gpu/tunel.sh --cerrar"
   ```
   y dile que **detenga el pod** (Stop).
5. **Opcional:** instala el plugin oficial de Runpod en el Claude del servidor (paso 4 de la guía), para que el Editor encienda y apague el pod solo.

## Fase 8: Brain Storming y ahorro de tokens

- **Ahorro de tokens** (`ahorro-tokens/PASO-A-PASO-AHORRO.md`). La llave de API de Anthropic la pega ella cuando el instalador la pida:
  ```powershell
  ssh -t editor@IP "bash ~/alianato1013/ahorro-tokens/instalar.sh"
  ```
- **Brain Storming** (`brain-storming/PASO-A-PASO-BRAIN-STORMING.md`):
  1. `ssh editor@IP "python3 ~/alianato1013/brain-storming/brain.py init"`;
  2. la llave de ScrapeCreators la pega ella con `ssh -t editor@IP "mkdir -p ~/.config/espia && nano ~/.config/espia/scrapecreators.key"`;
  3. siembra el nicho: `ssh editor@IP "python3 ~/alianato1013/brain-storming/brain.py sembrar mi-vida-en-orden"`.
- **Segunda sesión en la app, solo para Brain:** abre `ssh -t editor@IP "tmux new -As brain"` y dentro ejecuta `cd ~/brain-data && claude remote-control`. Después Ctrl+B y D.
  Al final ella debe ver **dos sesiones** en su app de Claude:
  - **Editor** (YouTube), en `~/OpenMontage`;
  - **Brain** (productos digitales), en `~/brain-data`.

  Verifícalo con ella.
- El token de Meta y la programación diaria (cron) se hacen solo cuando ella lo pida. Siguen sus guías.

## Fase 9: Prueba final

Desde la app de Claude, en la sesión del Editor, ella pide un video **corto** de Hard Times Heritage (2–3 minutos de guion). Acompáñala hasta la etapa de recursos para confirmar que:
- el agente busca primero en el archivo gratis;
- pide la GPU y genera las imágenes faltantes;
- entrega el video a Drive.

**Al terminar:** tabla de progreso completa y lista de cuentas y costos mensuales (servidor, volumen de Runpod, APIs).
