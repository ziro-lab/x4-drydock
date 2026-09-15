# X4 Ship Production Workflow v0.2

## Goal

X4向け艦船を、見た目だけ完成した3Dではなく **ゲーム内で機能する構造を先に成立させてから詳細化する**。

中心原則:

> Blockoutの次にX4 ConnectionとClearanceを固める。  
> Layout Freeze後に詳細造形へ進む。

---

## Phase 0 — Ship Intent

最低限決める。

- Size: S / M / L / XL
- Role: destroyer / carrier / auxiliary / transport / mining / etc.
- おおよその全長・全幅・全高
- [`SHIP_DIMENSION_BASELINES.md`](../reference/SHIP_DIMENSION_BASELINES.md) と照合したscale position
- Fixed Weapon
- Turret
- Shield
- Dock有無
- 対応艦載機サイズ
- Ship Storage
- Repair / Rearm有無
- Launch Tube有無
- Standard / Advanced装備規格

Output例:

```text
Size: L
Role: Destroyer
Target L/W/H: 800 / 260 / 180 m
Scale reference: L central band
Scale verdict: NORMAL
Engine: L Advanced x4
Main Weapon: L x2
Turret: L x2 / M x12
Dock: S
Ship Storage: S / XS
Repair/Rearm: No
Launch Tube: No
```

`Scale verdict`:

```text
NORMAL  = current referenceの中央帯付近
EDGE    = observed range内だが端に近い
OUTLIER = observed range外。意図と理由を記録
```

OUTLIERは自動却下しない。意図せずclass scaleを外れることを防ぐためのflagとして使う。

---

## Phase 1 — Reference Load

必要なものだけ読む。

優先順位:

1. 現行Egosoft ToolsのConnection Visualization
2. 同種バニラ艦component XML
3. 動作済みMOD艦の配置例
4. 本repoのreference

他艦からコピーするのは絶対座標ではなく、**相対配置・向き・clearance・機能構成**。

Scaleについては1隻だけを基準にせず、class range / role / 複数の近似艦を参照する。

---

## Phase 2 — Blockout

細部を作らず、以下だけ決める。

- Main Hull
- 艦首 / 艦尾
- Engine Block
- Bridge Volume
- Dock / Hangar Volume
- 主要な張り出し
- おおよその全長 / 全幅 / 全高

この段階では装甲板・パネル・アンテナ等を仕上げない。

### Scale Gate

Blockout確定前に:

- [ ] Target classのabsolute observed rangeを確認
- [ ] central reference bandを確認
- [ ] LengthだけでなくWidth / Heightの見た目も近似艦と比較
- [ ] Dock / Engine / Turretのreserved volumeを置ける余裕がある
- [ ] OUTLIERの場合、意図したdesign reasonを記録
- [ ] 後からCurrent 9.x再計測値が得られた場合に再評価できるようsource versionを記録

暫定的な5.00 length baselineでは、特にM→Lの物理サイズ差が大きい。L艦を200〜300m程度で進める場合は意図的OUTLIERとして扱う。

Checkpoint: `BLOCKOUT_BASELINE`

---

## Phase 3 — X4 Functional Skeleton

### Basic large ship

必要に応じて配置:

```text
cockpit
playercontrol
aimtarget
countermeasures
dynamicroom
engine
shield
weapon
turret
```

### Dock-capable ship

追加:

```text
dockarea
dockingbay / shipstorage
storage
dock_xs
optional dock hatch
```

Ship Storageは空母専用ではない。通常L艦にも存在し得る。

### Service-capable ship

追加候補:

```text
buildmodule
shiptrader
service / resupply macro requirements
```

通常Dock機能とRepair/Rearmを別機能として扱う。

### Carrier

必要に応じて:

```text
multiple S docks
M docks
S / M / XS ship storage
repair / rearm
optional launch tubes
```

Launch Tubeは通常発艦の代用品ではなく、高速発艦用の追加設備。

---

## Phase 4 — Placement Validation

X4艦制作の中心工程。

### 4A Equipment Clearance

確認:

```text
Engine ↔ Hull
Engine ↔ Engine
Turret ↔ Hull
Turret ↔ Turret
Shield ↔ Hull
Weapon firing direction ↔ Hull
```

Egosoft Toolsが持つVisualizationをAuthorityとして使う。

### 4B Dock Clearance

確認:

```text
Dock surface
Approach corridor
Departure corridor
Exclusion zone
Hatch movement
```

艦橋、翼、アンテナ、タレット、装甲などが発着経路を塞がないこと。

### 4C Functional Relationship

Connectionが存在するだけではPASSにしない。

例:

```text
Dock
↓
Ship Storage
↓
Hangar volume
```

の位置関係が自然であること。

### 4D Orientation

特に確認:

```text
Engine direction
Fixed Weapon direction
Turret mounting plane
Dock approach direction
Launch Tube launch direction
```

Referenceから絶対座標ではなく相対方向を学ぶ。

---

## Placement Result

### PASS

機能上の干渉なし。

### WARN

成立するが改善余地あり。

例:

- 射界が狭い
- Dock進入が窮屈
- Engine周辺が詰まっている
- 配置の見栄えが悪い

### FAIL

例:

- 必須Connection欠落
- Clearance侵害
- Dock進入路閉塞
- Launch Tube出口閉塞
- Connection方向の明白な異常
- 必要機能を配置する空間がない

---

## Auto-fix loop

FAIL時はまず局所修正を試す。

```text
原因特定
↓
Connection移動 または Blockout局所修正
↓
再検証
```

シルエットを大きく変える必要がある場合は、Astra/User判断へ上げる。

---

## Diagnostic Views

配置検証では高品質レンダリングより診断を優先。

最低限:

```text
Top
Side
Front
Perspective
```

必要に応じて重ねる:

```text
Hull
Connection
Equipment Clearance
Dock Corridor
Exclusion Zone
```

---

## Gate A — Layout Freeze

以下を満たしたら配置を固定。

```text
Scale / Volume             PASS or intentional OUTLIER
Required Connections       PASS
Equipment Clearance        PASS
Dock Clearance             PASS
Orientation                PASS
Functional Relationship    PASS
```

WARNは残してよいがFAILは0件。

Checkpoint: `X4_FUNCTIONAL_LAYOUT_FIXED`

Layout Freeze後はConnectionとReserved Clearanceを原則変更しない。

変更が必要になった場合:

```text
Detail Modeling停止
↓
Layout Freeze解除
↓
Phase 4再検証
↓
PASS
↓
再Freeze
```

---

## Phase 5 — Detail Modeling

ここで初めて本格造形する。

例:

- Armor
- Panels
- Engine housing
- Turret bases
- Dock exterior
- Hangar exterior
- Bridge
- Antenna
- Lights
- Decals
- Mechanical details

Connection Visualization領域はReserved Zoneとして扱う。

大きな造形変更後は全検証ではなく、変更領域周辺のLocal Clearance Checkを行う。

---

## Phase 6 — X4 Asset Finishing

形状完成後にゲーム用技術要素を仕上げる。

```text
Materials
UV
Normals / Tangents
Collision
LOD0 / LOD1 / LOD2 / LOD3
Wreck
Dock Door Animation
other Animation
```

大型艦ではLOD0〜3とWreckを基本品質目標にする。ただし実艦・対象サイズに合わせる。

---

## Phase 7 — Export / Converter

重い処理は分離する。

```text
Job 1: Blender Asset Save
→ checkpoint

Job 2: Egosoft Export
→ checkpoint

Job 3: XUConverter
→ validation

Job 4: Fresh reopen / output inspection
```

Converterが成功しても、material / UV / normal / tangent / collision等の警告があれば完成扱いにしない。

詳細は [`X4_EXPORT_RUNTIME_CHECKLIST.md`](X4_EXPORT_RUNTIME_CHECKLIST.md) を使う。

---

## User review points

### Review 1 — Blockout

主に見るもの:

- silhouette
- scale
- design direction

### Review 2 — Functional Layout

主に見るもの:

- weapon placement
- engine placement
- dock placement
- carrier layout
- 見た目として納得できるか

Technical gateはTool側で行う。

### Review 3 — Final Model

完成形確認。

---

## Completion levels

### Visual Complete

見た目が完成。

### Technical Complete

最低限:

```text
Connection PASS
Clearance PASS
Collision PASS
LOD PASS
Wreck PASS
Export PASS
Converter PASS
```

### Game-ready Candidate

Visual Complete + Technical Complete。

ゲーム内検証を行う場合は、このCandidateから開始する。
