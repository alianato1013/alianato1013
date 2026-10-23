# Subir a YouTube desde la nube: configuración paso a paso (una sola vez)

Con esto, el servidor sube cada video **directo a tu canal**: privado y programado, con título, descripción, capítulos, miniatura y la marca de contenido sintético. **Tu PC nunca toca el archivo.**

**Costo:** gratis. **Tiempo:** ~30 minutos la primera vez.
**Antes de empezar:** el servidor ya preparado (`PASO-A-PASO-NUBE.md`, pasos 1–4) y la cuenta de Google **dueña de tus canales**.

> La consola de Google cambia de diseño a menudo. Si un botón no aparece con este nombre exacto, busca el más parecido. Los nombres en español pueden variar un poco según tu idioma.

---

## Parte A: Google Cloud (en el navegador de tu PC)

### A1. Entrar
Ve a **console.cloud.google.com** con la cuenta de Google de tus canales. Si es la primera vez, acepta los términos. No necesitas tarjeta de crédito: esta API es gratis.

### A2. Crear el proyecto
1. Arriba a la izquierda, haz clic en el **selector de proyectos** → **Proyecto nuevo**.
2. Nombre: `editor-supremo` → **Crear**.
3. Cuando termine, asegúrate de que `editor-supremo` está **seleccionado** arriba.

### A3. Activar la API de YouTube
1. Menú ☰ → **APIs y servicios** → **Biblioteca**.
2. Busca **YouTube Data API v3** → ábrela → **Habilitar**.

### A4. Pantalla de consentimiento
1. Menú ☰ → **Google Auth Platform** (o **APIs y servicios → Pantalla de consentimiento de OAuth**) → **Comenzar**.
2. **Información de la app:** nombre `Editor Supremo` y tu correo como correo de asistencia → **Siguiente**.
3. **Público:** **Externo** → **Siguiente**.
4. **Información de contacto:** tu correo → **Siguiente**.
5. Acepta la política de datos de usuario → **Crear**.

### A5. Publicar la app (importante)
1. En Google Auth Platform → **Público** → **Publicar aplicación** → **Confirmar**. El estado pasa a **En producción**.
2. **Por qué:** si la dejas en "Prueba", el permiso **caduca cada 7 días** y tendrías que volver a autorizar cada semana.
3. No necesitas enviarla a verificación: es una app privada para tus propios canales. Al autorizar verás el aviso "Google no ha verificado esta app", y es normal.

### A6. Crear la llave de la app (cliente OAuth)
1. Google Auth Platform → **Clientes** → **Crear cliente**.
2. Tipo de aplicación: **App de escritorio**. Nombre: `editor-supremo-servidor` → **Crear**.
3. **Descargar JSON**. Se guarda en tu carpeta Descargas como `client_secret_….json`.

---

## Parte B: Pasar la llave al servidor (PowerShell en tu PC)

Cambia `IP` por la IP de tu servidor y `client_secret_XXXX.json` por el nombre real del archivo:
```powershell
scp "$env:USERPROFILE\Downloads\client_secret_XXXX.json" editor@IP:~/.config/editor-supremo/youtube/client_secret.json
```
Después **borra el archivo de tu PC** (y vacía la papelera). La llave queda solo en el servidor.

---

## Parte C: Verificar cada canal en YouTube (una vez por canal)

En **youtube.com/verify**, con cada canal seleccionado, verifica por teléfono. Es necesario para:
- **subir videos de más de 15 minutos** (los tuyos duran 20–30);
- **poner miniaturas personalizadas**.

---

## Parte D: Autorizar cada canal (una vez por canal)

1. En PowerShell, abre la conexión **con túnel** y **déjala abierta**:
   ```powershell
   ssh -L 8765:localhost:8765 editor@IP
   ```
2. En esa misma ventana (ya estás dentro del servidor):
   ```bash
   cd ~/OpenMontage && . .venv/bin/activate
   python scripts/channel_cloud/youtube_upload.py auth --channel HTH
   ```
3. Copia el enlace que aparece y ábrelo en el navegador de tu PC.
4. Elige tu cuenta de Google y luego **el canal** ("Elige una cuenta o una cuenta de marca") → **Hard Times Heritage**.
5. En "Google no ha verificado esta app": **Configuración avanzada** → **Ir a Editor Supremo (no seguro)**.
6. Marca los permisos → **Continuar**. Verás "Listo. Ya puedes cerrar esta pestaña".
7. En la terminal tiene que salir:
   `Authorized HTH -> YouTube channel 'Hard Times Heritage.'`
   Si sale otro canal, repite el paso 2 y elige el correcto.
8. Repite para los otros canales:
   ```bash
   python scripts/channel_cloud/youtube_upload.py auth --channel SV
   python scripts/channel_cloud/youtube_upload.py auth --channel BA   # cuando exista Beneath America
   ```
9. Comprueba:
   ```bash
   python scripts/channel_cloud/youtube_upload.py whoami
   ```

---

## Parte E: Uso diario

Cuando apruebes la publicación de un video, escríbele al editor (en la app de Claude):
```text
Sube a YouTube, programado para el lunes 26 de octubre a las 10:00 a. m. hora del Este.
```
El editor:
1. Escribe `youtube_upload.json` con lo que dice la biblia del canal (título, descripción con capítulos y créditos, etiquetas, categoría, privado + fecha, contenido sintético, miniatura) y **te lo muestra**.
2. Hace una prueba sin subir (`--dry-run`).
3. Sube el video, pone la miniatura y guarda el enlace en `YOUTUBE.txt`.
4. Ejecuta la entrega a Google Drive y limpia el servidor.

**Protecciones incluidas:**
- **No sube** si la auditoría del video no pasó.
- **No sube** a un canal distinto del del proyecto: un video `hth-` solo puede ir al canal autorizado como HTH, y lo comprueba con el ID del canal.
- **No sube dos veces** el mismo proyecto.
- Si la red falla, **reintenta** solo.

---

## Parte F: La primera subida, y algo que hay que comprobar

Google tiene **dos versiones de su documentación que se contradicen**:
- una dice que los videos subidos desde un proyecto de API **sin auditar** quedan **bloqueados como privados**;
- otra dice que **ya no** se bloquean.

No hay forma de saber cuál aplica a tu proyecto sin probar. Por eso:

1. Sube el **primer video como privado** (es lo que hace el editor por defecto).
2. En **YouTube Studio → Contenido**, mira la columna de visibilidad:
   - **"Privado" normal, y puedes cambiarlo o programarlo:** todo listo, no tienes que hacer nada más.
   - **"Bloqueado (privado)":** tu proyecto necesita la **auditoría de YouTube API** (gratis). Busca "YouTube API Services Audit and Quota Extension Form" y llénalo:
     - explica que es una herramienta interna para subir los videos de **tus propios canales**;
     - nombra los canales;
     - di que no accede a datos de otros usuarios.

     Suele tardar días o semanas. Mientras tanto, sube a mano desde Drive (descargar, subir y borrar).

**Límite diario:** la API trae una cuota gratuita diaria. Cada subida gasta una parte, y alcanza para varias subidas por día (más que tus ~6 por semana). Puedes ver tu cuota en la consola → APIs y servicios → YouTube Data API v3 → **Cuotas**.

---

## Seguridad

- La llave (`client_secret.json`) y los permisos (`token_HTH.json`, etc.) viven **solo en el servidor**, en `~/.config/editor-supremo/youtube/`, con permisos privados. No están en el repositorio.
- El permiso pedido es solo **subir videos y leer el nombre del canal**. No puede borrar videos ni ver tus datos privados.
- Para revocarlo cuando quieras: **myaccount.google.com/permissions** → Editor Supremo → Quitar acceso.
