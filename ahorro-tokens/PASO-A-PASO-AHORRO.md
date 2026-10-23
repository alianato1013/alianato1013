# Ahorro de tokens en Claude Code: paso a paso

**Qué consigues:**
1. **Tus tareas automáticas (Brain, Espía) no se detienen por los límites de tu plan.** Corren con una llave de API (pago por uso) y un tope en dólares por corrida.
2. **Tu plan Max queda para ti:** lo que hablas conmigo en la app y la producción de tus canales.
3. **Cada tarea gasta menos tokens:**
   - rtk comprime lo que devuelve la terminal;
   - cada tarea usa el modelo justo: Sonnet para lo rutinario, Opus para decidir.
4. **Las tareas web cuestan menos:** Playwright lee las páginas como texto en vez de con capturas de pantalla.
5. **Ves en qué se gasta todo,** con ccusage.

> **Lo que no hace nadie:** volver "ilimitado" tu plan. Los límites de 5 horas y semanales los pone Anthropic en sus servidores. Este sistema hace que **no dependas de ellos** para lo automático y que **gastes menos** en lo demás.

## Lo que se instala (todo en el servidor, nada en tu PC)

| Pieza | Repositorio | Licencia | Qué hace |
|---|---|---|---|
| **rtk** (edición OSS) | [rtk-ai/rtk](https://github.com/rtk-ai/rtk) · ~84k ⭐ | Apache-2.0 | Comprime la salida de los comandos de terminal antes de que Claude la lea. El proyecto dice que ahorra 60–90 % en comandos comunes (medición propia). La telemetría está **apagada** por defecto. Instalamos la edición OSS **sin el "proxy"**, para que tu tráfico con Anthropic no pase por nada intermedio |
| **ccusage** | [ccusage/ccusage](https://github.com/ccusage/ccusage) · ~19k ⭐ | — | Lee tus registros locales y te dice cuánto gastaste por día, sesión y ventana de 5 horas |
| **Playwright MCP** | [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) · ~38k ⭐ | Apache-2.0 (Microsoft) | Un navegador sin pantalla que Claude usa leyendo la página como texto |
| **claude-auto.sh** | este repositorio | — | Elige el modelo de cada tarea automática y, si hay llave de API, la usa con un tope de dólares por corrida |

---

## Paso 1: Crear la llave de API de Anthropic (10 min, en tu PC)

1. Entra a **console.anthropic.com** (puede ser la misma cuenta de Claude).
2. **Billing** → agrega un método de pago y un crédito inicial pequeño (por ejemplo, US$20).
3. **Limits** (o "Límites de gasto") → pon un **tope mensual**. Por ejemplo, US$40 el primer mes. Así nunca gastas más de eso, pase lo que pase.
4. **API Keys** → **Create Key** → nombre `servidor-cron` → copia la llave (empieza con `sk-ant-`).
5. **No la pegues en el chat.** Solo va en el servidor, en el paso 2.

> La llave de API se cobra **aparte** de tu plan Max: es pago por uso. Esa es justamente la ventaja: no consume tu plan.

## Paso 2: Instalar en el servidor (10 min)

```powershell
ssh editor@IP
```
```bash
cd ~/alianato1013 && git pull
bash ~/alianato1013/ahorro-tokens/instalar.sh
```

El instalador:
1. **Instala rtk** y lo conecta a Claude Code. Si pregunta por el **proxy**, responde **NO**.
2. **Instala ccusage.**
3. **Agrega Playwright** a Claude Code (sin pantalla y sin guardar sesiones).
4. **Te pide la llave de API.** Pégala (no se ve en la pantalla) y pulsa Enter. Si prefieres seguir con tu suscripción, pulsa Enter sin pegar nada.

**Si Playwright avisa que faltan librerías,** ejecuta esto una vez con `ssh root@IP`:
```bash
npx -y playwright@latest install-deps chromium
```

## Paso 3: Comprobar

```bash
bash ~/alianato1013/ahorro-tokens/uso.sh
```
Verás tres cosas:
- lo que ahorró rtk;
- el consumo de los últimos 7 días por modelo;
- la ventana de 5 horas actual.

**Brain y el Espía ya están conectados.** En su próxima corrida los registros dirán:
```
[claude-auto] rutina · model=sonnet · billing=API key · cap=US$1.50
```

---

## Cómo queda repartido el trabajo

| Tarea | Modelo | Se paga con |
|---|---|---|
| Brain: Bibliotecario (actualiza el cerebro) | **Sonnet** | Llave de API |
| Brain: Estratega (propuestas y reporte) | **Opus** (si está saturado, Sonnet) | Llave de API |
| Espía: Analista (si lo sigues usando solo) | **Opus** | Llave de API |
| Tus conversaciones conmigo en la app | El que elijas | Tu plan Max |
| Producción de los canales (Editor Supremo) | El que elijas (ver los consejos abajo) | Tu plan Max |

Para cambiar los modelos o el tope, edita el archivo:
```bash
nano ~/.config/ahorro-tokens/config.sh
```

## Consejos para tus sesiones en la app (plan Max)

- **Canales (Editor Supremo):**
  - escribe `/model opus` para la propuesta y el guion;
  - escribe `/model sonnet` para recursos, edición y auditoría.
- **Escribe `/compact` al terminar cada etapa.** Resume la conversación para que Claude no vuelva a leer todo. Usa `/clear` entre un video y el siguiente. Ojo: `/clear` vacía la conversación, pero **no devuelve cuota**.
- **Para tareas web, en este orden:**
  1. **API**, si existe: YouTube, ImpulTienda, Meta y ScrapeCreators ya están conectadas;
  2. **Playwright** ("usa playwright para…"), para páginas públicas;
  3. **Claude in Chrome** solo cuando haga falta **tu sesión iniciada**: es lo que más tokens gasta, porque trabaja con capturas de pantalla.
- **Trabajo pesado fuera de las horas pico:** las fuentes dicen que entre semana, de 5 a 11 a. m. hora del Pacífico (8 a. m. a 2 p. m. en Puerto Rico), la cuota se gasta más rápido. Tus crons ya corren antes de esa franja.

## Costos (honesto)

- **El tope por corrida es de US$1,50.** Brain hace como máximo 3 corridas de Claude al día: el Bibliotecario y el Estratega, con un reintento. El **peor caso** sería ~US$4,50/día, aunque normalmente se gasta bastante menos.
- **El tope mensual de la consola** (paso 1) es tu red de seguridad final.
- **La primera semana, mira `uso.sh`.** Con el gasto real ajustamos el tope o pasamos el Estratega a Sonnet si el costo no se justifica.

## Seguridad

- **La llave vive solo en el servidor,** en `~/.config/ahorro-tokens/anthropic_api_key`, con permisos privados. Nunca pasa por el repositorio.
- **Las corridas automáticas tienen tope en dólares** y siguen sin poder usar la terminal, internet ni publicar. Solo leen y escriben archivos.
- **rtk** es la edición Apache-2.0, sin el proxy y con la telemetría apagada. Para quitarlo, sigue su [guía de desinstalación](https://www.rtk-ai.app/guide/getting-started/installation).
- **Playwright** corre aislado y no guarda sesiones. Por eso **no puede** entrar a cuentas tuyas: para eso está Claude in Chrome en tu PC.

## Lo que tienes que saber

- **Probado aquí:**
  - el lanzador `claude-auto.sh`: modelo por tarea, uso de la llave solo si existe, tope por corrida y respaldo;
  - Brain usándolo en su ciclo diario.
- **Sin probar aquí:** la instalación real de rtk, ccusage y Playwright. Este entorno no puede instalar en tu servidor. El instalador tiene comprobaciones y se detiene si algo falla.
- **rtk solo comprime los comandos de terminal.** Leer archivos o buscar con las herramientas propias de Claude no pasa por él.
- **El ahorro de rtk lo mide el propio proyecto.** Tu ahorro real lo verás en `rtk gain`.
