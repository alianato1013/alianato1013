# Channel Proposal Director — channel-documentary pipeline

## When to Use

First stage of `channel-documentary`. The script already exists (the user wrote it), and
the channel's angle, format and style are already decided in its bible. This stage does
NOT invent concepts. It locks the production plan and the budget, and asks the user to
approve them.

## Prerequisites

| Requirement | Where |
|---|---|
| Channel identified | `skills/channels/channel-router.md` |
| Bible read in full | `channels/<channel>/CHANNEL_BIBLE.md` |
| Voice lock (if it exists) | `channels/<channel>/voice.lock.json` |
| The user's script file | Ask for it if not provided. Save it unchanged to `projects/<project-id>/inputs/script_source.md` |
| Preflight / provider menu | AGENT_GUIDE "Mandatory Preflight" |

## Process

### Step 1 — Initialize the project
- Project id: `<prefix>-<kebab-title>`, where prefix is `hth`, `sv` or `ba`.
- `init_project('<project-id>', title='<Title>', pipeline_type='channel-documentary')`,
  and set the style playbook to the channel's playbook (`hard-times-heritage`,
  `sumerian-vault` or `beneath-america`).
- Open the Backlot board (non-blocking).

### Step 2 — Measure the script
Count the narrated words (exclude bracketed production markers like `[ITEM #3: ...]`,
`[VISUAL: ...]`, `[ACT 2: ...]`, `[LAYER: ...]`). Target duration = words / bible WPM × 60.
If the script still contains `[VERIFY]` tags, STOP and ask the user to resolve them first.

### Step 3 — Voice lock
- If `voice.lock.json` exists: use exactly that provider + voice id + settings.
- If not: present 2–3 voices that match the bible's "Voice" spec, generate a 15-second
  sample of the script's first lines with each, and ask the user to choose. Write the
  choice to `channels/<channel>/voice.lock.json`:
  ```json
  {"provider": "...", "voice_id": "...", "settings": {...}, "locked_on": "YYYY-MM-DD", "sample_path": "..."}
  ```
  From then on the voice never changes for this channel.

### Step 4 — Three treatment variants (all inside the bible)
`proposal_packet.concept_options` requires three options. They are NOT different angles.
They differ only in the sourcing mix and cost, always inside the bible's limits:

| Option | Sourcing mix | Use when |
|---|---|---|
| `A-archive-led` | Max real/licensed/public-domain imagery, AI only where the bible says it is needed | Lowest cost, most authentic |
| `B-balanced` | The bible's default mix | Default |
| `C-cinematic` | Max AI imagery the bible allows (still respecting the bible's AI rules) | Hero episodes |

For each: `hook` = the script's own first line (quoted, unchanged); `narrative_structure` =
the bible's structure; `visual_approach` = the mix; `target_duration_seconds` from Step 2.

### Step 5 — Production plan
- `pipeline`: `channel-documentary`
- `playbook`: the channel's playbook
- `render_runtime`: the bible's runtime (Remotion)
- `voice_selection`: the locked voice
- `music_source`: per the bible
- `delivery_promise`: "Long-form 16:9 documentary, narration verbatim, every sentence visually matched, audit PASS"
- `cost_estimate`: itemized (TTS, images, video clips, music) with `budget_cap_usd` from the bible

### Step 6 — Gate
Write the checkpoint `awaiting_human`, present the 3 options in Spanish with their costs,
recommend B unless the bible says otherwise, and END YOUR TURN.

## Never
- Never propose a different topic, angle, structure, title format or visual style.
- Never edit the script here.
