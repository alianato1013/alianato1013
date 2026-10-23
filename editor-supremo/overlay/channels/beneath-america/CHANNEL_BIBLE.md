# CHANNEL BIBLE — Beneath America (`BA`)

> IMMUTABLE. Everything here is binding for every Beneath America project. Change it only when the
> user explicitly says "cambia la biblia de Beneath America: …", and log a `decision_log` entry with
> `category: "bible_change"`. Never apply these rules to another channel.

## 1. Identity lock

| Field | Value |
|---|---|
| Channel | Beneath America (final name/handle to be confirmed by the user; record it here) |
| Promise | "Every place has a story underneath." |
| Language | English (US) |
| Pipeline | `channel-documentary` |
| Style playbook | `beneath-america` (`styles/custom/beneath-america.yaml`) |
| Render runtime | `remotion` |
| Format | 16:9, 3840×2160 if every source allows it, otherwise 1920×1080; 30 fps; H.264 + AAC |
| Target length | 18–28 min (from the script; never pad or cut words) |
| Project id prefix | `ba-` |
| Voice | Locked in `channels/beneath-america/voice.lock.json` (first run: choose once with the user) |
| Audit minimum score | **4** |
| Budget cap per video | USD 15 unless approved at the proposal gate |

## 2. Angle and audience
- **Angle:** what is really underneath famous US places (geology, water, tunnels, buried cities,
  engineering), explained from the visible symptom down to the cause, layer by layer. Real science only.
- **Audience:** "Mike", 35–70, US, loves maps, engineering and documentaries; watches on TV; searches his own state or city.
- **Feeling:** curiosity, scale, "I didn't know that". Never conspiracy, never fear-mongering.

## 3. Script markers
- Everything before the first marker = `hook`.
- `[BRAND CARD]` = 2 s logo card "BENEATH <PLACE>" (not narrated).
- `[LAYER: <depth> · <name>]` starts a chapter (for example `[LAYER: 300 FT · The Aquifer]`).
- `[VISUAL: …]` = visual hint (not narrated).
- Narration WPM: **150**.

## 4. Edit grammar
| Moment | What appears |
|---|---|
| Hook | The visible surface symptom of the place (drone/photo of that exact place), then a quick tease of the cross-section |
| `[BRAND CARD]` | 2 s: "BENEATH <PLACE>" in Montserrat 900 white, yellow underline, over a dark cross-section silhouette |
| Start of each layer | **Depth card** 2 s: big yellow depth ("300 FT") + layer name; low rumble SFX; hard `cut` in, then the next visual uses `zoom-in` on the deeper part of the cross-section (this is the "descent") |
| Every layer | The **cross-section diagram** of this place appears at least once, with the current layer highlighted |
| Lines about the place today | Drone, satellite or ground footage of that exact place |
| History / discovery lines | Archival photos (LOC, NARA, agency archives) of that place or that project |
| Numbers | `stat_card` or `stat_reveal` with the number exactly as narrated, with units |
| Maps | USGS/NOAA maps or 3D terrain of the named area; satellite zooms from the US down to the place |
| Ending | Back to the surface shot of the opening; end screen 20 s |
- One visual every **2–4 s**, never static. Stills use motion presets only (`zoom-in`, `zoom-out`, `pan-left`, `pan-right`, `ken-burns`); real footage carries its own motion. Transitions: `cut` or `dissolve` only.
- `section_title` overlay, top-left: "<DEPTH> · <LAYER NAME>" during the whole layer.

## 5. Visual sourcing order
1. **US federal public domain:** USGS, NASA, NOAA, National Park Service, Library of Congress, NARA,
   US Army Corps of Engineers, Bureau of Reclamation (check each item's credit line).
2. **Free stock:** Pexels, Pixabay, Mixkit (drone, city, nature).
3. **Google Earth Studio** flyovers with the on-screen "Google Earth" attribution its terms require.
4. **AI images** only for cutaway illustrations and reconstructions that no photo can show
   (a cross-section, a buried 1880s street, a magma chamber).
5. AI video clips only if approved at the proposal gate.

## 6. AI prompt recipe
`<playbook image_prompt_prefix>` + the exact subject of the line (which city/landmark on the surface,
which layers, what is inside them: tunnels, aquifer, salt dome, shipwreck, magma) + scale cues.
Always attach the playbook negative prompt. Labels are added in the edit, never generated inside the image.
2 takes per image; keep the one that best represents the line.

## 7. Visual rules per line
- **A named place must be that exact place.** Look-alike cities, rivers or landmarks are `WRONG_PLACE`.
- Lines about depth or layers → the cross-section with that layer highlighted.
- Numbers said aloud → on screen exactly as narrated.
- Lines about the past → archival imagery of that place, or a clearly illustrative reconstruction.
- Disaster or damage lines → footage of that event and place only; never stock disasters from elsewhere.

## 8. Forbidden imagery
- Conspiracy imagery (secret bunkers "they hide", reptilians, lizard people, "ancient tunnels connecting cities").
- Disaster footage from other places presented as this place.
- AI-invented landmarks or buildings presented as real.
- Generated text inside images; maps with invented geography.

## 9. Audio
- Voice: the locked voice only, verbatim, with pronunciation guides for place names.
- Music: atmospheric electronic or orchestral pulse, steady build; `music_volume` 0.08, ducked.
- SFX: whoosh on transitions, low rumble on layer descents, ambience only when matching the image.
- Final mix around −14 LUFS integrated.

## 10. Subtitles
Enabled. Inter 600, white with a black outline, bottom center, max 8 words per line.
Never cover depth labels or the highlighted layer.

## 11. Publishing
- Chapters = hook + one per layer ("0:00 The Symptom", "1:10 0–10 FT · The Streets", …).
- Description: first line with the place and the promise; chapters; **sources** (USGS, NOAA, NASA, NPS,
  agencies, studies); image credits; Google Earth attribution if used; disclosure: "Some diagrams are
  illustrations; AI-assisted where noted."
- Mark "Altered or synthetic content" when realistic AI reconstructions are used.

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
