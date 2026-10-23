# CHANNEL BIBLE — Sumerian Vault (`SV`)

> IMMUTABLE. Everything here is binding for every Sumerian Vault project. Change it only when the
> user explicitly says "cambia la biblia de Sumerian Vault: …", and log a `decision_log` entry with
> `category: "bible_change"`. Never apply these rules to another channel.

## 1. Identity lock

| Field | Value |
|---|---|
| Channel | Sumerian Vault (`@sumerianvault`) |
| Promise | "Real tablets. Real translations. The women history buried." |
| Language | English narration and on-screen text |
| Pipeline | `channel-documentary` |
| Style playbook | `sumerian-vault` (`styles/custom/sumerian-vault.yaml`) |
| Render runtime | `remotion` |
| Format | 16:9, 1920×1080, 30 fps, H.264 + AAC |
| Target length | 22–27 min (from the script; never pad or cut words) |
| Project id prefix | `sv-` |
| Voice | Locked in `channels/sumerian-vault/voice.lock.json` (first run: choose once with the user) |
| Audit minimum score | **4** |
| Budget cap per video | USD 15 unless approved at the proposal gate |

## 2. Angle and audience
- **Angle:** what REAL Sumerian texts say about women, goddesses and the fate of the soul, and where
  those stories reappear in Genesis, myth and modern science. Real objects, real translations;
  scholarship and speculation always kept apart.
- **Audience:** "Diane", 38–65, interested in the Bible, spirituality and hidden history; watches at night.
- **Feeling:** reverence, mystery, intelligence. Never alien sensationalism.

## 3. Script markers
- Everything before the first marker = `hook`.
- `[ACT N: Title]` starts an act (5–6 acts).
- `[VISUAL: …]` = visual hint (not narrated).
- Narration WPM: **140**. Pauses written as "…" are kept and honored by the voice.
- The script already contains the subscribe line, comment prompt and ending. Do not add any.

## 4. Edit grammar
| Moment | What appears |
|---|---|
| Hook | **The real object first**: photograph of the tablet/artifact named in the line, slow push-in; then a quote card with the translated line |
| Start of each act | **Act card** 3 s: `hero_title`, deep blue background, gold Cormorant Garamond title; dissolve |
| A line quotes a translation | **Quote card**: `callout` (quote) in Cormorant Garamond italic, gold rule, text name under it ("— The Descent of Inanna") |
| A line names a tablet, seal, statue or site | A real photograph of that exact object or site |
| Goddess, ritual, underworld, landscape lines | AI images in the playbook style |
| Bible / Genesis echo lines | Public-domain biblical art or manuscript pages (period art, credited) |
| Science echo lines | Clean diagram or `stat_card`; DNA or lab imagery only when the line is about it |
| Maps | Gold-line Mesopotamia map on deep blue, with the named city highlighted |
| Ending | Return to the opening object; end screen 20 s |
- One visual every **3–6 s**, always moving. Motion presets only (`transform.animation`): `zoom-in` on objects and tablets, `pan-left` / `pan-right` on landscapes and maps, `parallax` on figures. Transitions: `dissolve` (fade) only.
- Lower-third (`section_title`) when an object first appears: "Text name · Museum · Number" (only real, verified data).

## 5. Visual sourcing order
1. **Real artifacts and sites:** The Met Open Access (CC0); Wikimedia Commons (PD, CC BY, CC BY-SA with credit);
   Penn Museum, CDLI and Louvre images only when their terms allow commercial use.
   **Never** use British Museum official images (CC BY-NC-SA, non-commercial); find the same object elsewhere.
2. **AI images** for goddesses, rituals, the underworld, landscapes and reconstructions.
3. Public-domain religious art for Genesis or Bible echoes.
4. AI video clips only if approved at the proposal gate.

## 6. AI prompt recipe
`<playbook image_prompt_prefix>` + the concrete subject of the line (which goddess, what action, what
place: Kur, Dilmun, Uruk, the seven gates…) + Sumerian details (horned crown, flounced wool robe,
lapis jewelry, ziggurat, reed boats) + mood from the line. Always attach the playbook negative prompt.
2 takes per image; keep the one that best represents the line.

## 7. Visual rules per line
- A line naming a **specific real object** must show a real photograph of that object (never an AI tablet presented as the real one).
- A line naming a **goddess or person** shows that figure in Sumerian setting (AI), never a generic "ancient woman" if a name is given.
- **Underworld/afterlife lines:** dark, descending imagery: gates, stairs, the queen of the dead, judges.
- **Speculation lines** ("some claim…") get neutral visuals (the object, a map, a candle-lit scribe), never images that present the speculation as fact.
- Quoted lines always get the quote card on screen.

## 8. Forbidden imagery
- Aliens, spaceships, UFOs, sci-fi, "ancient astronaut" tropes.
- Egyptian, Greek, Roman or medieval imagery passed off as Sumerian.
- Fake cuneiform or invented inscriptions presented as real; AI tablets presented as real artifacts.
- AI images of real modern scholars or real people.
- Gore; nudity beyond museum-art standards.

## 9. Audio
- Voice: the locked voice only, verbatim, with pronunciation guides for Sumerian names.
- Music: atmospheric drones, low strings, soft ancient percussion; `music_volume` 0.06, ducked.
- SFX only when the line describes them (water, wind, stone doors).
- Final mix around −14 LUFS integrated.

## 10. Subtitles
Enabled. Cormorant Garamond 700, warm white on a dark translucent box, bottom center, max 7 words per line.
Never cover quote cards or the object.

## 11. Publishing
- Chapters = hook + one per act title.
- Description: hook line; **sources** (text, translation edition or ETCSL, museum, number); image
  credits and licenses; disclosure: "Some illustrations are AI-generated. Translations quoted from
  published scholarly editions; interpretations are labeled as such."
- Mark "Altered or synthetic content" when realistic AI scenes are used.

- **youtube_upload.json** (cloud upload): `category_id` "27" (Education); `privacy` "private"; `publish_at` = the date/time the
  user gives, converted to UTC (if none, upload private without a date and tell the user); `made_for_kids` false;
  `contains_synthetic_media` true when photorealistic AI images are used, otherwise false; `thumbnail` = the approved
  thumbnail file; `default_language` "en". The channel code for this bible is **SV**.

## 12. Stage checklist
| Stage | Re-read sections |
|---|---|
| proposal | 1, 2, 5, 9 |
| script | 3, 1 |
| scene_plan | 4, 5, 7, 8 |
| assets | 5, 6, 8, 9 |
| edit + storyboard_audit | 4, 7, 8, 10, 1 |
| compose + render_audit | 9, 10, 7, 8 |
| publish | 11 |
