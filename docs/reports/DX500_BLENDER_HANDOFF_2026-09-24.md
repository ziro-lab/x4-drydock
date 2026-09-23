# DX-500 Blender handoff — 2026-09-24

## Result

**Blender-side handoff completed. Full X4 MOD pipeline is NOT yet established end-to-end.**

The model intentionally uses simple modular boxes, chamfers and shallow panel/rib details. No additional silhouette approval is required for this process-establishment pilot. Do not interpret this as an installable MOD, official Connection/clearance PASS, or X4 runtime acceptance.

- Source commit: `3ce5da953c7439d0e85fc40cdaefa4d9848f83c8`
- Blender: `5.2.1 LTS`, official Linux build, archive checked against official SHA256 list
- Actions run: https://github.com/ziro-lab/x4-drydock/actions/runs/35889167159
- Job: `107276978037`, `blender-handoff`, **success**
- Artifact: `10763748648`, `dx500-blender-handoff-3ce5da953c7439d0e85fc40cdaefa4d9848f83c8`
- Artifact location: https://github.com/ziro-lab/x4-drydock/actions/runs/35889167159/artifacts/10763748648
- Artifact expiry reported by GitHub: `2026-11-22T16:30:58Z`. Rebuild from the source commit when expired.
- ZIP size: 10,214,957 bytes
- ZIP SHA256: `763ae024b54f56b2f4add82bbeca997998a5b6ccf1b558c586baa5edeaa8a170`

Documentation-only commits after this source commit do not change the generated geometry. The artifact's own build_identity/source_commit remains the authority for that packet.

## What was actually tested

| Check | Result |
| --- | --- |
| Python syntax + unit tests on the actual repository input | 14/14 PASS |
| Official Blender download verification | SHA256 PASS |
| Native .blend generation | PASS |
| Fresh-process reopen: dx500_handoff.blend | PASS, errors 0 |
| Fresh-process reopen: dx500_geometry_only.blend | PASS, errors 0 |
| Decreasing LOD triangle counts | 5,040 → 2,000 → 1,808 → 624 |
| Actual LOD0 hull dimensions L/W/H | 500.600006 / 322.400024 / 180.000000 m |
| Convex source pieces | 50 uncooked boxes |
| Source parts / reserved volumes / candidates | 124 / 14 / 18 |
| Preview render | hero, top, side, front, rear, collision: 6 PNGs |
| Required packet files | 29 files |
| SHA256 packet verification after retrieval | All entries matched |
| Original spec hash vs design manifest | Matched |

Blender stage timings from this run (excluding checkout/install/download): build 7.833s, native inspection 0.766s, geometry-only inspection 0.666s, render 12.661s. These are single-run observations, not a performance promise.

After retrieval, all six PNGs were visually reviewed. The orthographic views show the same modular hull, four rear equipment mockups and reserved bay location; the collision view excludes the mock engine/turret/dock floor geometry and retains the central recess.

An additional CPython check of all six OBJ exports confirmed finite vertex data, valid vertex/UV/normal indices and triangular faces. LOD0 OBJ bounds and triangle count agree with the native-file report. This is an OBJ structure check, **not** an older-Blender importer test.

## Native-file identities

```text
dx500_handoff.blend
  bytes: 392175
  sha256: a025a90db7450cb6faaa1dba48f7598d8566ab01e37b97f36038927c851489c8

dx500_geometry_only.blend
  bytes: 292758
  sha256: bd13ed236eb52b3a8fe2a6237f97f8ad9ad1740d8ec6071d2b117bf601b53963
```

The handoff file retains editable source parts, optional equipment mockups and generic candidate Empty objects. The geometry-only file is a whitelist of LOD/collision/convex/wreck collections, with no candidate Empty or display equipment objects. Use a separately named local copy for Mod Tools setup; never regenerate over a manually adjusted file.

## Pipeline failures found and fixed

1. Official Blender reports `Blender 5.2.1 LTS`, not the original strict banner string. The launcher now accepts the two exact 5.2.1 banner variants without accepting other versions.
2. Hidden collections were not evaluated immediately after reopening: their queried world matrices caused false cavity/clearance failures. The read-only inspector now exposes collections and updates the view layer before measuring them; it never saves this temporary visibility state.
3. The inherited visualization document claimed a reader/parser test suite existed, but those files were absent from this repository. The document now records this honestly as a future/local task instead of treating copied documentation as implementation evidence.

## Modeling problems prevented

- Converted the old -X bow layout to +Y bow, +Z up and metre units.
- Replaced the solid M05 cargo block with side boxes, end walls and a floor around a real central cavity.
- Kept candidate equipment, dock mock floor and diagnostic volumes out of the exported hull and collision source.
- Split independent collision boxes so a single giant convex hull does not silently fill the bay.
- Kept game-material identifiers and macro bindings unresolved rather than inventing plausible IDs.
- Retained the simple box-based model instead of spending the pilot budget on bespoke turret rigs, dock animations or decorative detail.

## Remaining local gates — not complete

The detailed sequence is in [PIPELINE.md](../../ships/dx500_pilot/PIPELINE.md). These are the current acceptance gaps:

1. **Tool environment and one official sample:** confirm installed X4/build/DLC, Egosoft Tools version and supported Blender version, then export/convert one official sample. The source Blender version does not prove add-on compatibility.
2. **Geometry/material/physics integration:** assign current game materials, exporter metadata and supported LOD/wreck/collision conventions; prepare/cook the actual Jolt-related output. The 50 boxes are source geometry, not finished physics data.
3. **Functional ship configuration:** formal Connections, orientations, tag/group semantics, cockpit/rooms, engine/shield/turret attachment and dock/storage binding. Reserve sizes here are design AABBs, not current-tool authority.
4. **Ship definitions and gameplay values:** select a current, compatible baseline ship for reference, then define the pilot's hull/crew/cargo/storage/handling parameters and acquisition/pricing policy as applicable. Do not assume geometry dimensions or placeholder counts supply those values. Use explicit project IDs and keep copied game assets out of this public repository.
5. **Package and acquisition:** content.xml, component/macro indexes, ware/reference chain, localisation and dependencies; at least one confirmed way to obtain/spawn the ship in the game.
6. **Runtime:** separate test save, recognition/debug log, visuals, flight/cockpit, equipment changes, firing/shields, docking/storage/departure, collisions/LOD/wreck, save/reload.

### OBJ fallback limitation

The supplied OBJ/MTL files preserve geometry, UV coordinates, face normals, basic material names and native-coordinate dimensions. They do **not** preserve Blender collections, candidate Empty objects, custom properties or vertex-colour attributes. On fallback import, recreate required channels such as `uv1` / `col` according to the current shader/exporter requirements, and reconstruct candidate positions from the JSON/CSV. Do not expect an OBJ import to be equivalent to opening the handoff .blend.

### Validation limits

The closed-edge/manifold tests are not a solid-union or arbitrary self-intersection proof. The UVs intentionally tile, not a unique bake atlas. The wreck is a simple same-outline source. Current equipment clearance, official exporter semantics, dock behavior and game physics still require the local gates above.

## Next useful acceptance

Do not expand this model's ornamentation or build a general-purpose modding framework yet. First confirm that the local toolchain can export and convert an official sample, then integrate the DX500 hull with a simple current material. This isolates environment problems from ship-specific problems and is the shortest route to establishing the remaining half of the workflow.
