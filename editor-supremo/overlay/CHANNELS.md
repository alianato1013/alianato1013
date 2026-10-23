# CHANNEL MODE — read this before AGENT_GUIDE routing

This OpenMontage install has a local overlay called **Editor Supremo** for three
YouTube channels. When a request involves any of them, these rules come FIRST.

**Triggers:** the user mentions *Hard Times Heritage*, *Sumerian Vault*, *Beneath America*,
the codes `HTH` / `SV` / `BA`, a project id starting with `hth-` / `sv-` / `ba-`, or hands
over a script "for my channel".

**On a trigger, do exactly this:**
1. Read `skills/channels/channel-router.md` and follow it.
2. Read the channel's bible: `channels/<channel>/CHANNEL_BIBLE.md` (in full).
3. Use ONLY the pipeline `channel-documentary`.

**Non-negotiable:**
- One channel per project. Never mix bibles, playbooks, voices or prompts.
- The user's script is used word for word. Never rewrite narration.
- Every narrated sentence must match the visual on screen. The visual audit
  (`skills/channels/visual-auditor.md`) must PASS on the timeline AND on the final render
  before anything is delivered.
- If something is not defined in the bible and it matters: ask. Do not assume.
- **Delivery (cloud server):** after the publish gate is approved, run
  `bash scripts/channel_cloud/deliver.sh <project-id>`. It uploads the video and its package to
  cloud storage, verifies the copy and frees the server disk. It refuses to run unless the render
  audit is PASS. Never leave a finished video only on the server, and never delete a project
  that has no `DELIVERED.txt`.

For requests that do not involve these channels, ignore this file and follow
`AGENT_GUIDE.md` as usual.
