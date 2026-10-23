# Channel Router — Editor Supremo (binding)

## When to Use

Before ANY action on a request that involves one of the owner's channels:
**Hard Times Heritage**, **Sumerian Vault**, **Beneath America** — or any request that
delivers a script "for my channel", mentions a channel code (`HTH`, `SV`, `BA`), or a
project id starting with `hth-`, `sv-` or `ba-`.

This skill overrides the generic OpenMontage onboarding, reference-video and pipeline
selection routing for these requests. All other OpenMontage rules (Rule Zero,
checkpoints, gates, Layer 3 skills, provider governance) still apply.

## The Three Channels (never mix them)

| Code | Channel | Bible (read in full) | Playbook | Project id prefix |
|---|---|---|---|---|
| `HTH` | Hard Times Heritage | `channels/hard-times-heritage/CHANNEL_BIBLE.md` | `hard-times-heritage` | `hth-` |
| `SV` | Sumerian Vault | `channels/sumerian-vault/CHANNEL_BIBLE.md` | `sumerian-vault` | `sv-` |
| `BA` | Beneath America | `channels/beneath-america/CHANNEL_BIBLE.md` | `beneath-america` | `ba-` |

Pipeline for all three: `channel-documentary` (`pipeline_defs/channel-documentary.yaml`).

## Protocol

### Step 1 — Identify the channel
- If the user names the channel (or code / project prefix), use it.
- If it is not explicit, **ask** ("¿Para qué canal es este guion: Hard Times Heritage, Sumerian Vault o Beneath America?") and END YOUR TURN.
- **Never infer the channel from the topic alone.** Never pick one "because it fits".

### Step 2 — Load the bible
Read the channel's `CHANNEL_BIBLE.md` from top to bottom. Then read
`channels/<channel>/voice.lock.json` if it exists.

### Step 3 — Confirm the locks to the user (one short message)
State, in Spanish: channel, pipeline `channel-documentary`, playbook, render runtime,
locked voice (or "voice not locked yet — will ask once"), visual sourcing order, and the
audit minimum score. Then continue with the pipeline's first stage.

### Step 4 — Run the pipeline
`proposal → script → scene_plan → assets → edit (+storyboard_audit) → compose (+render_audit) → publish`.
Before every stage, re-read the bible sections that the stage depends on
(listed in each bible under "Stage checklist").

## Precedence (when two instructions disagree)

1. The user's explicit instruction **in the current message**, but only if it does not violate an
   IMMUTABLE rule. If it would, say so, quote the rule, and ask the user to confirm the
   bible change explicitly ("cambia la biblia de <canal>: ..."). Only then edit the bible
   and log a `decision_log` entry with `category: "bible_change"`.
2. The channel's `CHANNEL_BIBLE.md`.
3. The channel's style playbook (`styles/custom/<channel>.yaml`).
4. Skills in `skills/channels/`.
5. Generic OpenMontage skills and playbooks.

## Never

- Never load two bibles in the same project, or carry style, voice, palette, fonts,
  music or prompts from one channel into another.
- Never write, rewrite, shorten, "improve" or translate the user's narration. The script
  is locked (see `skills/channels/script-lock-director.md`).
- Never use a playbook other than the channel's playbook.
- Never change voice, render runtime, aspect ratio, fonts or palette mid-project.
- Never skip `storyboard_audit` or `render_audit`, and never deliver a video whose audit
  report is not `PASS`.
- Never "assume" a missing detail: if the bible does not define it and it matters, ask.
