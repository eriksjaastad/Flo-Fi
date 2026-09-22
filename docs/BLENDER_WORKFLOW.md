# Blender character work

Read this when creating, editing, or evaluating Flo's Blender assets. It records
the September 22, 2026 research and failed portrait experiment. This is workflow
guidance, not a claim that we have achieved Flo's likeness or a replacement for
the [style guide](STYLE_GUIDE.md).

## Start with identity and references

The canonical likeness reference is **v20_04**, locally available as
`tools/ComfyUI/input/flo_v20_04_ref.png` and
`tools/ComfyUI/training/flo/comfy_v20_04_realcartoon_warm_00001_.png`.
These files live under ignored `tools/`; a fresh checkout may not contain them.
Locate and inspect the actual reference before modeling. Check project memory
and existing assets if it is missing; do not substitute a different generated
face just because its caption says Flo.

Use derived front, three-quarter, and profile references when available, but
check them against the original. Generated alternate views can disagree about
the nose, jaw, expression, and hair. Identify uncertain anatomy rather than
averaging inconsistent references into a different person.

The target is an adult, stylized semi-realistic character with expressive hazel
eyes, warm skin, freckles, auburn hair, and an approachable smile. Matching her
colors and clothes is insufficient: facial proportions and expression must
carry the likeness. Avoid drifting into a flat face, doll, or childlike design.

Confirm the asset's intended scope from the request: likeness study, full-body
character, rigged animation asset, or render reference. A bust is not a complete
body; a saved scene is not a rig. Preserve the requested provenance. For a fresh
Blender-built interpretation, do not quietly import Meshy geometry or switch to
another image-to-3D service. Record any reused base mesh, texture, or library
asset and its source when reuse is in scope.

## Use the available Blender interface

The project's production constraint remains CLI/API/headless operation; Erik
does not need to operate creation tools. Blender's Python API (`bpy`) can create,
edit, inspect, save, and render scenes through the Blender executable. A missing
MCP tool is not a reason to abandon that route or an explanation for bad art.

Distinguish these states: Blender installed, an add-on installed, a server
running, and tools actually callable in the current session. One does not prove
the others. Use connected tools when available within the project constraint;
otherwise use background scripts. Do not launch a GUI or change integrations
merely to satisfy this guide.

Set `BLENDER_BIN` to the installed executable (often `blender` on PATH; the
standard macOS app path is `/Applications/Blender.app/Contents/MacOS/Blender`).
From the project root, this read-only probe verifies startup and the actual API:

```sh
"$BLENDER_BIN" --background --factory-startup --python-exit-code 1 \
  --python-expr 'import bpy; print("Blender:", bpy.app.version_string); print("Engine:", bpy.context.scene.render.engine)'
```

For a new scene, pass the build script with `--python`. To edit a saved scene,
pass its `.blend` path before the script. `--factory-startup` avoids loading user
startup customizations; it does not authorize clearing or overwriting an
existing scene. Save checkpoints to distinct paths. Use `--python-exit-code 1`
so a Python exception fails the command rather than looking like a successful
build. Check the installed API or [current API reference](https://docs.blender.org/api/current/)
when using unfamiliar operators, material sockets, or render settings.

Keep geometry, materials, lights, and cameras editable and named. Organize face,
hair, clothing, and studio elements so each can be isolated. Save the modeling
recipe and settings with the asset. Scripts should support focused revisions;
do not repeatedly replace a refined scene with its initial blockout.

## Establish the head before finishing the character

Choose a representation that supports the anatomy and the requested style.
Begin with a continuous head surface and meaningful skull, jaw, cheek, muzzle,
and orbital volumes. Primitives and procedural curves can help blocking, but
adding detail to an unsuccessful blockout does not make it a convincing face.
Use mesh editing, sculpting, remeshing, or topology refinement as the forms
require; do not lock the task to one mathematical surface recipe.

Work in small, visually reviewable changes. Render neutral clay views of the
head early, with hair and clothing hidden. Match camera angle, perspective,
expression, and framing to the reference as closely as possible before judging
proportions. Use front, three-quarter, and profile views; add other views where
they expose a specific uncertainty. Check:

| Area | What the images must establish |
| --- | --- |
| Head volume | Skull depth, jaw taper, chin projection, and cheek volume hold up in profile as well as front view. |
| Eyes | Orbital volume and lids seat the eyes in the face; eye size, spacing, direction, and expression resemble Flo. |
| Nose | Bridge, tip, wings, and nostrils form a coherent volume with the right projection. |
| Smile | Lips, mouth corners, cheeks, teeth, and oral cavity belong to the same expression; teeth do not read as floating beads. |
| Likeness | Facial structure and expression resemble the reference without relying on auburn hair, freckles, or the jacket to identify her. |

Record what differs from the reference and revise those forms before moving
on. These are agent self-review checks, not new requests for permission at every
step. Continue authorized modeling and correction. If repeated edits leave the
same defect, reconsider the representation or method rather than increasing
polygon counts, render samples, or decoration. Report an unresolved likeness
honestly; do not rename it a finished interpretation to lower the standard.

Once the head holds up, develop the hair's overall silhouette, part, roots, and
large waves before strand detail. Inspect its scalp attachment and volume from
the sides and back. Shape the clothing around the body with actual thickness,
folds, and connections; frontal panels must not become disconnected sheets in
profile. Check the smile again with neutral materials before final lighting.

## Verify the actual artifact

Use both neutral geometry views and shaded renders. Lighting can disguise a
flat face or intersection; render success, object count, resolution, and a
playable MP4 are technical checks, not evidence of character quality.

Before delivery, reopen the saved `.blend` and inspect its final state. Check
several angles, close facial views, and representative turntable frames from
the front, sides, and back. Fix visible gaps, clipping, floating features, and
missing dependencies. Clearly label bust/full-body scope, rigging state, and
remaining likeness problems. Keep AI-enhanced images separate and labeled;
they cannot serve as proof of the mesh's appearance.

Keep large outputs in a distinct run directory under ignored `output/`. Include
the editable scene, necessary packed or accompanying assets, build/render
recipes, reference provenance, settings, and review notes. Promote reusable
production scripts into tracked source only when they are actually ready; the
rejected September study's script is not a recommended starting template.

Append the experiment's expectation, actual result, user feedback when supplied,
lesson, next change, and artifact paths to
[`data/experiment_log.jsonl`](../data/experiment_log.jsonl). Use project-relative
paths and mark local-only dependencies. Preserve previous records. Distinguish
agent assessment from user acceptance; delivery alone never means approval.

## Rejected experiment: September 22, 2026

`blender_flo_original_study_20260922` attempted a fresh portrait using a
parameterized head surface, shallow eye surfaces, curve lips, repeated swept
hair locks, and simplified clothing. Several revisions and a turntable were
delivered. Erik rejected the result as flat, doll-like, and unlike Flo apart
from the hair color and clothes. The local evidence is under
`output/flo-blender-study-2026-09-22/`; it is not part of a fresh checkout.

The failure was the modeling approach and acceptance judgment. The agent saw
weak likeness and continued adding finish. A functioning Blender invocation
and successful file checks did not satisfy the request. Keep the result as a
failed experiment, not an approved baseline or evidence of a model's ceiling.

The next meaningful experiment is a head-only sculpt reviewed in neutral clay
against the canonical and consistent derived references. That experiment has
not yet demonstrated a better likeness.

## Research and what it establishes

Sources reviewed September 22, 2026; recheck capabilities when the toolchain
changes. These examples inform the approach, not a promise of equivalent art.

- [Architectural visualization with Astra](https://developers.openai.com/blog/architectural-visualization-with-astra)
  documents editable Blender work through `bpy`, background rendering, repeated
  visual revisions, and solid-mode inspection. Some later assets and textures
  were imported. It also used computer use; that part is not adopted by this
  project's headless workflow. Architecture examples do not establish human
  facial-likeness performance.
- [Little Ritual](https://developers.openai.com/showcase/little-ritual) documents
  editable Blender assets and iteration for stylized pet characters.
  [Physics museum](https://developers.openai.com/showcase/physics-museum) includes
  Blender-authored environment and exhibit geometry. Neither is a Flo benchmark.
- [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
  recommends concise, relevant guidance and a clear completion standard. Use
  this document to support judgment, not to force an elaborate recipe on every
  small Blender edit.
- [MCP for Blender](https://github.com/ahujasid/mcp-for-blender) exposes Python
  execution, scene inspection, screenshots, and optional asset/generation
  integrations. Its presence alone does not guarantee quality or original
  geometry. Check the installed version before relying on a listed tool.
- [Blender Studio's Stylized Character Workflow](https://studio.blender.org/training/stylized-character-workflow/)
  emphasizes head design, sculpting, expression tests, and clean topology. It
  teaches Blender 2.8; its production principles are useful, but old UI/API
  instructions need checking against the installed version.

The reviewed material does not establish special Blender-specific Astra
training or guaranteed likeness reconstruction. Judge capability through the
actual saved geometry and its reference comparison.
