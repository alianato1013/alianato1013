# Brain Storming: paso a paso

**Qué es:** un empleado que se hace experto en **un solo nicho**. Lo estudia todos los días, aprende de tus ventas y te propone:
- **productos nuevos para el mismo avatar** (la escalera de valor);
- **mercados nuevos**, cuando el actual esté probado.

Tú supervisas y decides. **Nada se publica ni gasta dinero sin que escribas "publica <ID>".**

```
                    ┌──────────── CEREBRO DEL NICHO (crece cada día, nunca olvida) ────────────┐
                    │ BIBLIA · NICHO · AVATAR · ÁNGULOS · PRODUCTOS · MERCADOS · APRENDIZAJES  │
                    │ COMPETIDORES (historial) · MERCADOS (historial) · ESTADÍSTICAS propias   │
                    └───────────────▲───────────────────────────┬──────────────────────────────┘
                                    │ aprende                   │ decide con
 06:20 cada día                     │                           ▼
 ESPÍA ──► datos del día ──► BIBLIOTECARIO ──────────────► ESTRATEGA ──► REPORTE + PROPUESTAS
 (Meta Ads Library, landings,       (actualiza el cerebro      (máx. 3 por día:     │
  TikTok, Instagram, Banco Mundial,  con fuente y confianza)    productos, creativos,│
  competidores, tus métricas de Meta)                           mercados)            │
 REGLAS FIJAS ──► APAGAR / ESCALAR automáticos ──────────────────────────────────────┤
                                                                                     ▼
                            TÚ (app de Claude):  "cola"  ·  "prepara P-…"  ·  "publica P-…"  ·  "rechaza P-…: motivo"
                                                                                     │
                            PUBLICADOR ──► ImpulTienda (producto, ebook, embudo, precios por país)
                                       ──► Meta Ads (campaña + conjunto + anuncios, con topes duros)
                                       ──► tus resultados vuelven al cerebro mañana
```

## El equipo (los "empleados")

| Empleado | Qué hace | Cuándo |
|---|---|---|
| **Cazador** | Puntúa nichos candidatos con datos reales:<br>• demanda;<br>• longevidad de los anuncios;<br>• océano azul (muchos anuncios en el origen, pocos en el destino);<br>• TikTok.<br>Funda el cerebro del nicho elegido | Una vez (o cuando lo pidas) |
| **Espía** | Ofertas high ticket escalando, sus 3 creativos ganadores, landings, ideas de TikTok e Instagram, mercados | Cada día |
| **Bibliotecario** | Mete lo nuevo en el cerebro: cada dato con fuente y confianza; lo contradicho se tacha, nunca se borra; tus rechazos se guardan como preferencias. El domingo consolida todo | Cada día |
| **Estratega** | Lee todo el cerebro y propone lo siguiente en la escalera o en los mercados, con evidencia | Cada día |
| **Reglas fijas** (código, no IA) | Apagar un anuncio que gastó 2× tu CPA objetivo sin ventas. Subir 20 % el presupuesto si hubo 3+ ventas en 3 días con CPA bajo el objetivo | Cada día |
| **Publicador** | Ejecuta exactamente la propuesta que aprobaste | Solo cuando lo dices |

**Cómo aprende el cerebro:** cada anuncio se nombra `BS|propuesta|ángulo|mercado|producto|creativo`. Así el sistema sabe qué ángulo, qué producto y qué mercado vende, y lo resume en `ESTADISTICAS.md`. Ese archivo es la base de los aprendizajes.

**Tus datos viven en el servidor**, en `~/brain-data`, fuera de GitHub:
- tienen historial de cambios con git (puedes ver cómo evolucionó el cerebro día a día);
- tienen una copia diaria en Google Drive (`BrainStorming/`).

---

## Paso 1: Lo que ya debes tener

- El **servidor** del Editor Supremo (`editor-supremo/cloud/PASO-A-PASO-NUBE.md`), con Claude Code con la sesión iniciada y rclone conectado a Drive.
- **ScrapeCreators** con la llave guardada (`espia-ofertas/PASO-A-PASO-ESPIA.md`, pasos 1 y 3).

## Paso 2: Instalar Brain Storming (2 min)

```bash
ssh editor@IP
cd ~/alianato1013 && git pull
python3 ~/alianato1013/brain-storming/brain.py init
```
Esto crea `~/brain-data/` con:
- `config.json` (límites y reglas);
- `candidatos.json` (nichos de ejemplo);
- el manual del agente (`CLAUDE.md`).

**Revisa los límites de dinero** en `config.json`:
```bash
nano ~/brain-data/config.json
```

| Límite | Valor por defecto | Qué hace |
|---|---|---|
| `max_presupuesto_diario_por_conjunto_usd` | 20 | Ningún conjunto de anuncios puede pasar de esto por día |
| `max_presupuesto_nuevo_por_dia_usd` | 40 | El total de campañas nuevas que se pueden publicar en un mismo día |
| `cpa_objetivo_usd_por_defecto` | 12 | Lo que estás dispuesto a pagar por venta (luego se ajusta por nicho en `nicho.json`) |

`brain.py` **se niega** a publicar por encima de estos topes. Solo tú los cambias.

## Paso 3: Conectar tu cuenta de Meta (20 min, una sola vez)

Se usa un **token de usuario del sistema**: no caduca y solo tiene acceso a lo que tú le asignas.

1. Ve a **developers.facebook.com** → **Mis apps** → **Crear app** → tipo **Otro** → **Empresa** → nombre `brain-storming`. Vincúlala a tu portafolio comercial.
2. Dentro de la app: **Agregar producto** → **API de marketing**.
3. Ve a **business.facebook.com** → **Configuración** → **Usuarios** → **Usuarios del sistema** → **Agregar**: nombre `brain`, rol **Administrador**.
4. Con `brain` seleccionado → **Asignar activos**:
   - tu **cuenta publicitaria**: control total;
   - tu **página de Facebook**: control total;
   - tu **píxel / conjunto de datos**.
5. **Generar token** → elige la app `brain-storming` → caducidad **Nunca** → permisos: `ads_management`, `ads_read`, `business_management`, `pages_show_list`, `pages_read_engagement`, `pages_manage_ads` → **Generar**. **Copia el token** (solo se muestra una vez).
6. En el servidor:
   ```bash
   mkdir -p ~/.config/brain && nano ~/.config/brain/meta_token      # pega el token, guarda
   chmod 600 ~/.config/brain/meta_token
   ```
7. **Busca los ids** que te pedirá el agente: la cuenta publicitaria (`act_…`, en el Administrador de anuncios), el id de la página y el id del píxel (en el Administrador de eventos).

> Las pantallas de Meta cambian a menudo. Si un botón no tiene este nombre exacto, busca el más parecido.
>
> La versión de la API (`meta.graph_version`, por defecto `v24.0`) se puede cambiar en `config.json` si Meta la retira.

## Paso 4: Abrir a Brain desde la app de Claude (2 min)

En el servidor:
```bash
tmux new -s brain
cd ~/brain-data && claude remote-control
```
- Sal de tmux con **Ctrl+B y luego D**.
- La sesión aparece en tu **app de Claude Code**, en el PC o el celular. Desde ahí hablas con Brain.
- **ImpulTienda:** escribe `/mcp` en esa sesión.
  - Si aparece **Impultienda**, Brain crea productos y embudos solo.
  - Si no aparece, esa parte la haces desde la app de Claude donde ya tienes ImpulTienda conectado. El Publicador te dice exactamente qué copiar.

## Paso 5: Elegir el nicho (una vez, ~30 min)

Escríbele a Brain:
1. **"busca nichos"**
   - Brain propone de 6 a 10 candidatos (o usa los tuyos) y **te pide OK** antes de gastar créditos (~10 créditos por candidato).
   - Después te entrega `RECOMENDACION.md`:
     - puntaje con datos reales;
     - durabilidad;
     - profundidad de la escalera (5+ productos para el mismo avatar);
     - océano azul por país;
     - riesgos.
2. **"fija el nicho <nombre>"**
   - Brain crea el cerebro y te pide: el `store_id` de ImpulTienda, los ids de Meta del paso 3 y tu CPA objetivo.
   - Corre el primer día.
   - Te muestra el borrador de la **BIBLIA** (marca, promesa, reglas). **Apruébala o corrígela:** es lo único que no cambia sin tu orden.

## Paso 6: Programarlo cada día (2 min)

```bash
crontab -e
```
Añade esta línea:
```
20 10 * * * /home/editor/alianato1013/brain-storming/run-diario.sh >/dev/null 2>&1
```
- Corre a las **10:20 UTC = 6:20 a. m. en Puerto Rico**.
- Si también tienes el Espía solo programado, **quítalo**: Brain ya lo incluye.

## Paso 7: Tu rutina (5–10 min al día)

| Escribes | Pasa |
|---|---|
| **"estado"** | El nicho, los resultados de 7 días y las propuestas esperando |
| **"reporte de hoy"** | El resumen del reporte: qué aprendió el cerebro, la competencia, tus resultados, las propuestas y el plan |
| **"cola"** | La lista de propuestas pendientes |
| **"explícame P-20261024-E1"** | El porqué, con enlaces a la evidencia |
| **"prepara P-…"** | Crea el producto y el embudo en ImpulTienda (pausado), genera las imágenes o videos, simula la publicación y te muestra todo **sin gastar** |
| **"publica P-…"** | Activa el embudo, crea los anuncios en Meta y los enciende, dentro de los topes |
| **"rechaza P-…: motivo"** | La descarta, y **el cerebro aprende tu preferencia** |
| **"sincroniza ventas"** | Trae tus ventas de ImpulTienda al cerebro (recomendado 1 vez por semana) |
| **"qué sabe el cerebro de <tema>"** | Responde citando las fuentes |
| **"cambia la biblia del nicho: …"** | Cambia una regla fija de la marca |

**Puedes decir "publica" sin "prepara":** Brain prepara y publica en el mismo paso. Usa "prepara" cuando quieras ver los creativos antes.

---

## Costos aproximados

| Concepto | Por día |
|---|---|
| ScrapeCreators | ~50–110 créditos (Espía ≤ 80 + seguimiento ≤ 30). El paquete de USD 47 dura unos **7–15 meses** |
| Claude | 2 sesiones cortas al día en el servidor (Bibliotecario + Estratega), con tu suscripción |
| Meta Ads | Solo lo que publiques, dentro de tus topes |
| Servidor y Drive | Los mismos que ya tienes |

Son estimaciones. El gasto real de créditos aparece en cada `EVIDENCIA.md` y en "estado".

## Seguridad

- **No instala nada:** solo Python estándar y Claude Code, que ya tienes.
- **Las llaves viven solo en el servidor**, con permisos privados:
  - ScrapeCreators en `~/.config/espia/`;
  - Meta en `~/.config/brain/`.
- **Los datos del negocio no se suben a GitHub:** viven en `~/brain-data` y en tu Drive.
- **En las corridas automáticas Claude solo puede leer y escribir archivos.** No tiene terminal, ni internet, ni puede publicar.
- **Para publicar hacen falta tres cosas:**
  1. tu "publica <ID>";
  2. una propuesta válida (el verificador revisa los países, el presupuesto, el CTA y que cada anuncio o video citado exista en los datos);
  3. los topes de dinero.
- **Todo lo creado en Meta queda registrado** en la propuesta y en `DECISIONES.md`.

## Lo que tienes que saber (honesto)

- **Probado aquí, con servidores simulados de ScrapeCreators, el Banco Mundial y Meta:**
  - la puntuación de nichos y la creación del cerebro;
  - la corrida diaria completa y el historial de competidores y mercados;
  - las métricas y las estadísticas por ángulo, mercado y producto;
  - apagar y escalar automáticos, sin duplicarse;
  - el verificador, rechazando países, presupuestos, CTAs y anuncios inventados;
  - la publicación en Meta: imagen, video, topes, simulación sin efectos y reanudación;
  - rechazar con motivo y el ciclo diario con reintento.
- **Sin probar con cuentas reales,** porque desde aquí no hay acceso a ScrapeCreators ni a Meta: la primera publicación real.
  - **Recomendación:** la primera vez usa "prepara" y después "publica" con un presupuesto chico (5–10 USD por día). Revisa en el Administrador de anuncios que todo quedó como esperabas.
  - Si Meta responde con un error, queda guardado en la propuesta y en `*.meta-log.jsonl`. Mándamelo.
- **La API de Meta cambia:** desde la v24.0 exige el parámetro de presupuesto compartido (ya incluido) y en octubre de 2026 anunció cambios de audiencias. Si un campo cambia, el error lo dirá y se ajusta en una línea.
- **Las ventas de ImpulTienda** entran por su conector, en una sesión donde esté disponible ("sincroniza ventas"). Las compras que mide Meta (píxel) entran solas cada día.
- **"Más de 100 anuncios" y "competencia baja" son señales,** no garantías. Por eso el sistema aprende sobre todo de **tus propias ventas**, y la evidencia propia pesa más que la de otros.
- **El cerebro necesita semanas de datos** para ser bueno. Los primeros días sus aprendizajes serán de confianza B (baja), y eso es lo correcto.
