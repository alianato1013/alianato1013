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
- **YouTube upload (cloud server):** after the publish gate is approved, write
  `projects/<id>/youtube_upload.json` from the bible's Publishing section, show it to the user, and
  run `python scripts/channel_cloud/youtube_upload.py upload --project projects/<id>` ONLY after the user
  says to upload ("sube a YouTube"). Default privacy: private, with `publish_at` if the user gave a date.
  It refuses to upload unless the render audit is PASS and the authorized channel matches the project.
- **Images at the assets stage (cost rule):** follow the bible's sourcing order. Archive and free
  stock come first, through OpenMontage's stock sources (LOC, NARA, Internet Archive, Wikimedia,
  Pexels, Pixabay). For every line the archive cannot cover, generate on the **own GPU**:
  1. write `projects/<id>/assets/ai_batch.jsonl`, one line per image:
     `{"prompt": "<subject of the line>", "out": "projects/<id>/assets/images/<scene>.png"}`;
  2. if the Runpod MCP tools are available (official plugin `runpod@runpod`), start the user's
     **existing** GPU pod yourself and read its public IP and SSH port. Never create a new pod,
     change its GPU, or start any other pod without the user's explicit OK. Without the tools,
     tell the user: "Necesito la GPU: enciende el pod en Runpod y dame IP y puerto";
  3. run `bash ~/alianato1013/estudio-gpu/tunel.sh <IP> <PUERTO>`;
  4. run `python scripts/channel_assets/gen_image.py --channel <playbook> --batch projects/<id>/assets/ai_batch.jsonl --takes 2`;
  5. run `bash ~/alianato1013/estudio-gpu/tunel.sh --cerrar`, then stop the pod with the Runpod
     tools if you have them. As a safety net, the pod also stops itself after 20 idle minutes.

  Each image's sidecar `.json` goes into `asset_manifest` (license and model). Paid image or video
  APIs (KIE, fal, Higgsfield, etc.) are used **only** if the user approves them at the proposal gate,
  with their cost shown. Assembly and render stay on this server (Remotion, CPU) and never need the GPU.
- **Delivery (cloud server):** after the upload (or when the user says not to upload), run
  `bash scripts/channel_cloud/deliver.sh <project-id>`. It uploads the video and its package to
  cloud storage, verifies the copy and frees the server disk. It refuses to run unless the render
  audit is PASS. Never leave a finished video only on the server, and never delete a project
  that has no `DELIVERED.txt`.

For requests that do not involve these channels, ignore this file and follow
`AGENT_GUIDE.md` as usual.
