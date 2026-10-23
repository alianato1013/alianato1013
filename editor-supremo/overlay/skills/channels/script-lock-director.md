# Script Lock Director — channel-documentary pipeline

## When to Use

The `script` stage of `channel-documentary`. It converts the user's finished script into
a schema-valid `script` artifact **without changing a single narrated word**, and locks it
with a hash that later stages and the auditor verify.

## Prerequisites

| Requirement | Where |
|---|---|
| Approved `proposal_packet` | previous stage |
| Source script, unchanged | `projects/<project-id>/inputs/script_source.md` |
| Bible sections "Script markers" and "Narration" | `channels/<channel>/CHANNEL_BIBLE.md` |
| Schema | `schemas/artifacts/script.schema.json` |

## Process

### Step 1 — Separate narration from production markers
- **Production markers** are whole lines (or inline tags) in square brackets:
  `[ITEM #18: The Coffee Can Behind the Flour]`, `[ACT 2: The Object]`,
  `[LAYER: 300 FT · The Aquifer]`, `[VISUAL: ...]`, `[BRAND CARD]`.
  They are never spoken.
- **Narration** = everything else, exactly as written (keep punctuation, the "…" pauses, capitalization).
- If any `[VERIFY ...]` or `[SRC ...]` tag is still in the text: STOP, list them, and ask the user.
  Never resolve facts yourself by rewriting.

### Step 2 — Build sections from the bible's markers
- One section per structural marker (item / act / layer), plus `hook` (everything before the
  first marker) and `ending` if the bible defines one.
- `section.text` = that section's narration, verbatim.
- `section.label` = the marker's title (used for chapter cards and YouTube chapters).
- `[VISUAL: ...]` cues become `enhancement_cues` of type `visual` at their position. They are hints
  for the scene director, not narration.
- Timing: `start_seconds`/`end_seconds` from cumulative word counts at the bible's WPM.
  Add `pause_before_seconds` / `pause_after_seconds` only where the bible says so (for example, after a title card).

### Step 3 — Pronunciation only, never wording
- Use `pronunciation_guides` for names (Ereshkigal, Enheduanna, Atrahasis, Kubaba,
  Coeur d'Alene...).
- `delivery_cues.provider_text` may add SSML pauses or phonetic spellings **only**. It must
  contain the same words in the same order. If a TTS provider cannot pronounce a word,
  use a pronunciation guide, never a synonym.

### Step 4 — Lock
- Normalize the narration (all section texts joined with single spaces, whitespace
  collapsed) and compute SHA-256.
- Do the same for the source file with markers removed. **Both hashes must be equal.**
  If they differ, fix the parsing, never the words.
- Store it in `script.metadata.script_lock`:
  ```json
  {"source_path": "inputs/script_source.md", "narration_sha256": "...", "word_count": 0, "wpm": 0}
  ```

### Step 5 — Gate
Present the section list (labels + durations) and the total duration in Spanish.
Write the checkpoint `awaiting_human` and END YOUR TURN.

## Downstream obligations (repeat them in every later stage)
- TTS must read `section.text` (or a `provider_text` with identical words).
- `render_audit` transcribes the final audio. If the transcript differs from the locked
  narration by more than 3 % of words, that is a CRITICAL failure: regenerate the narration.

## Never
- Never add an intro, an outro, a call to action, a sponsor line or a "subscribe" line that is not in the script.
- Never shorten for pacing. Pacing is solved in the edit, not in the words.
- Never translate.
