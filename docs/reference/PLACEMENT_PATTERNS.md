# X4 Ship Placement Patterns v0.1

このファイルは、バニラ艦component XMLと動作済みMOD艦から抽出した **配置パターン** をまとめる。

目的は座標コピーではなく、X4艦設計時の機能関係を参照すること。

## Evidence posture

- バニラ実装: 強い参考
- 動作済みMOD: 実用例。ただし公式仕様そのものとは限らない
- 絶対座標: 再利用しない
- 相対配置 / orientation / tags / groups / 機能構成: 再利用候補

Research snapshot: 2026-09-12

---

## Pattern A — Standard L Destroyer with S dock

Observed from Terran L Destroyer.

Typical ship-side structure:

```text
cockpit
playercontrol
aimtarget
countermeasures
engine large standard
large shield standard
medium shield hittable standard
large / medium turrets
fixed large weapons

dockarea
shipstorage / dockingbay
storage
dock_xs
dockdoor animation
```

Important observation:

**Ship Storage exists on a normal destroyer. It is not a carrier-only feature.**

Design use:

- standard S-dock-capable L combat ship baseline
- standard equipment clearance reference
- conventional landing-pad layout reference

---

## Pattern B — Boron / Advanced L Destroyer

Observed from Boron L Destroyer.

Typical differences:

```text
advanced engine large
advanced large shield
advanced medium shield
advanced large / medium turret
S / XS shipstorage
dockarea
dock hatch
```

Design use:

- Advanced/Boron equipment placement reference
- compact surface-element clearance reference
- non-standard dock arrangement reference

Do not assume Boron dock geometry is the default conventional landing-pad pattern.

---

## Pattern C — Service-capable L ship

Observed from repair/rearm-capable Paranid L expeditionary ship.

Baseline dock/storage structure is still present:

```text
dockarea
S / XS shipstorage
storage
```

Additional service-related ship-side connections:

```text
buildmodule
shiptrader
```

Interpretation:

```text
Dock / Storage
!=
Repair / Rearm capability
```

Service capability is an additional layer.

Do not reduce repair/rearm support to a special dock shape only. Confirm the macro-side service/buildmodule requirements.

---

## Pattern D — XL Carrier

Observed from Boron XL Carrier.

Typical structure:

```text
advanced engine extralarge
advanced extralarge shield
multiple combat surface elements
M / S / XS shipstorage
storage
multiple S / M dockareas
buildmodule
shiptrader
optional launch tubes
```

Important observation:

Carrier differentiation is not simply “has storage”.

More useful dimensions are:

- supported dock sizes
- dock count / throughput
- service capability
- launch-tube capability
- overall carrier layout

---

## Pattern E — Standard dock reuse in a MOD ship

Observed from a completed destroyer MOD.

The MOD ship referenced vanilla dock/storage macros rather than bundling a custom dock implementation.

Observed pattern included references equivalent to:

```text
standard S dockarea
XS dock
S shipstorage
XS shipstorage
```

Design lesson:

A custom ship does not require every docking component to be custom-made. Reusing known-good vanilla dock components is a strong default when the design allows it.

---

## Pattern F — Dedicated Launch Tube

Observed from a completed carrier MOD.

The MOD bundled a dedicated launch-tube component with dockingbay semantics.

Observed internal structure:

```text
component class = dockingbay
con_todock
con_dockpos
con_launchpos
launch-tube connection
```

Observed macro policy included the equivalent of:

```text
external dock
landing not allowed
unit use allowed
landing gear not required
not walkable
S / XS sized
```

Interpretation:

Launch Tube is a **specialized dockingbay used for rapid launch**, not a mandatory component for ordinary departure.

Treat this as an observed MOD implementation pattern, not an official universal contract.

---

# Placement rules derived from the patterns

## Rule 1 — Separate capability axes

Treat these independently:

```text
Docking
Storage
Repair / Rearm
Launch Tube
```

Do not infer one from another.

## Rule 2 — Copy relationships, not coordinates

Reference ships teach:

- where functions sit relative to hull regions
- which direction they face
- which clearance they reserve
- which groups they belong to
- which other functions they are near

They do not provide coordinates to paste into a new hull.

## Rule 3 — Connection layout is upstream of detailed geometry

Recommended order:

```text
Blockout
→ Connection placement
→ Clearance validation
→ Layout Freeze
→ detail geometry
```

## Rule 4 — Prefer known-good reusable dock components

If a vanilla dock satisfies the intended design, reuse can reduce implementation risk.

Custom dock / launch-tube geometry is justified when the ship design or throughput requirement materially needs it.
