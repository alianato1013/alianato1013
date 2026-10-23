# CHANNEL BIBLE — Hard Times Heritage (`HTH`)

> IMMUTABLE. Everything here is binding for every Hard Times Heritage project. Change it only
> when the user explicitly says "cambia la biblia de Hard Times Heritage: …", and log a
> `decision_log` entry with `category: "bible_change"`. Never apply these rules to another channel.

## 1. Identity lock

| Field | Value |
|---|---|
| Channel | Hard Times Heritage (`@hardtimesheritage`) |
| Language | English (US) narration and on-screen text |
| Pipeline | `channel-documentary` |
| Style playbook | `hard-times-heritage` (`styles/custom/hard-times-heritage.yaml`) |
| Render runtime | `remotion` (never switch to hyperframes or anything else) |
| Format | 16:9, 1920×1080, 30 fps, H.264 + AAC |
| Target length | 24–28 min (from the script; never pad or cut words) |
| Project id prefix | `hth-` |
| Voice | Locked in `channels/hard-times-heritage/voice.lock.json` (first run: choose once with the user) |
| Audit minimum score | **4** (both storyboard and render) |
| Budget cap per video | USD 15 unless the user approves more at the proposal gate |

## 2. Angle and audience (why every visual choice exists)
- **Angle:** the money wisdom of 1950s working-class women, translated for life on a fixed income today.
- **Audience:** "Margaret", 64–78, US, often living alone on Social Security or a small pension; grew up
  watching her mother stretch every dollar; watches long videos on a living-room TV.
- **Feeling to create:** pride, control, warmth, nostalgia. Never mockery, shame or fear without a solution.

## 3. Script markers (what the script-lock director parses)
- Everything before the first marker = `hook`.
- `[ITEM #N: Short Name]` on its own line starts a countdown item (N counts down to 1).
- `[VISUAL: …]` = a visual hint for that position (not narrated).
- Narration WPM for timing: **140**.
- The script already contains its subscribe line, comment prompts and ending. Do not add any.

## 4. Edit grammar (how a video is built)
| Moment | What appears |
|---|---|
| Hook (0:00–~0:45) | Era images matched line by line; no logo, no intro, no title card |
| Start of each item | **Item card** 2.5 s: `text_card` on cream paper texture, "#N" in brick red Playfair Display 900, item name below in Lora; page-turn SFX; dissolve in |
| "Back then" lines | 1950s domestic scenes (archive or AI Kodachrome) |
| "How it worked" lines | Close-ups of hands doing the task and of the objects named |
| Numbers then vs now | `comparison` card ("1955: $4 / week" vs "Today: $300") or `stat_card` with the number exactly as narrated |
| "How to do it today" lines | Modern stock: a senior (60+) at home, at the grocery store, with a receipt, budgeting at a kitchen table |
| Comment prompt lines | A mother-and-daughter or grandmother image from the era matching the item |
| Subscribe line | The item's own subject image (no subscribe animation, no bell graphics) |
| Ending | Recap images of the strongest items; end screen 20 s over a warm era kitchen image |
- One visual every **3–6 s**, always moving. Use only the composer's motion presets on stills (`transform.animation`): `ken-burns-slow-zoom`, `zoom-in`, `zoom-out`, `pan-left`, `pan-right`, alternating so consecutive images never repeat the same move. Transitions: `dissolve` (fade) only; never `cut` except into the item card.
- A visual may span several sentences **only** if it represents every one of them (the audit checks this).
- Section title overlay (`section_title`, top-left) shows "#N · Item name" for the whole item.

## 5. Visual sourcing order (follow strictly)
1. **Public-domain archive** for era scenes: Library of Congress (FSA/OWI 1935–1945, including color), National
   Archives, Prelinger Archives (check each film's license), Wikimedia Commons (PD/CC BY with credit).
2. **AI images** in the playbook style when the line needs a specific scene the archive does not have.
3. **Modern stock** (Pexels/Pixabay/Unsplash) **only** for "today" lines.
4. AI video clips only if approved at the proposal gate (option C).
Every non-generated asset records `license` and `original_url` in `asset_manifest`.

## 6. AI prompt recipe
`<playbook image_prompt_prefix>` + **the concrete subject of the line** (who, what object, what action,
which room) + era details (1950s clothing, appliances, packaging) + framing (close-up for objects and hands).
Always attach the playbook `image_negative_prompt`. Generate 2 takes per needed image and keep the
one that best represents the line.

## 7. Visual rules per line (used by scene planning and by the audit)
- If the line names an **object** (coffee can, envelope, flour sack, ledger), that object must be visible.
- If the line names a **person type** (widow, mother, daughter, husband, neighbor), show that person type, alone if the line says alone.
- **Era must match the line:** 1930s–1950s lines → period images; "today" lines → modern images.
- Money amounts said aloud appear on screen exactly as said.
- Abstract lines (pride, worry, "and that changed everything") → the emotion on a period face, or the item subject.

## 8. Forbidden imagery
- AI images of real, identifiable people (no presidents, celebrities, famous photographs recreated).
- Modern objects in era lines (phones, plastic packaging, LED lights, flat TVs, modern cars).
- Luxury or wealth imagery (mansions, jewelry, champagne), or brand logos.
- Medical imagery or remedies; anything that looks like financial or investment advice graphics (stock tickers, crypto).
- Mocking, caricature or cartoon styles; anime; 3D renders.

## 9. Audio
- Voice: the locked voice only, reading the script verbatim (pronunciation guides allowed).
- Music: nostalgic soft piano or gentle strings, continuous bed, `music_volume` 0.07, ducked under narration.
- Loudness: final mix around −14 LUFS integrated, narration clearly on top; no clipping.
- SFX: only the playbook's subtle page turn on item cards and coin sounds when coins are on screen.

## 10. Subtitles
Enabled. Lora 600, white on a semi-transparent dark box, bottom center, max 7 words per line, large
(the audience is 60+). Never cover the object that makes the frame relevant (render audit `OCCLUDED`).

## 11. Publishing
- YouTube chapters = hook + one chapter per item label (`0:00 Intro`, `1:02 #25 The Coffee Can`, …).
- Description: first line with the promise; chapters; sources & image credits; the disclosure
  "Narration produced with AI voice; some illustrations are AI-generated. Scripts are researched and
  edited by our team. Historical household practices for general education, not financial advice."
- Mark "Altered or synthetic content" in YouTube Studio when photorealistic AI images of historical scenes are used.

## 12. Stage checklist (re-read before each stage)
| Stage | Re-read sections |
|---|---|
| proposal | 1, 2, 5, 9 |
| script | 3, 1 (WPM) |
| scene_plan | 4, 5, 7, 8 |
| assets | 5, 6, 8, 9 |
| edit + storyboard_audit | 4, 7, 8, 10, 1 (min score) |
| compose + render_audit | 9, 10, 7, 8 |
| publish | 11 |
