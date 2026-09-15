# Egosoft Connection Visualization Reference v0.3

## Purpose

X4艦の設計で必要なのは、装備モデルの精密Bounding Boxを毎回調べることではなく、**船体側が予約すべき配置空間を把握すること**。

Egosoft Blender Mod ToolsはConnection tagに応じてViewportへbox / cylinder等のVisualizationを描画する。

このVisualizationをX4艦設計の**Clearance Authority**として優先する。

## Authority rule

**現行 `Blender_Properties.xml` をAuthorityにする。**

このファイルに記載する数値は調査時点のsnapshotであり、validatorへ固定値として埋め込むための仕様ではない。

Workbench / Toolを実装する場合は、可能な限り現行`Blender_Properties.xml`を読み取る。

---

## Implemented reader

`tools/connection_visualization.py`は、指定された`Blender_Properties.xml`から`connection_visualizations`を探し、Connection tagsに対応するvisualization ruleを解決する。

```bash
python tools/connection_visualization.py \
  ~/Documents/Blender/Blender_Properties.xml \
  --tags "engine large standard" \
  --pretty
```

### Resolution policy

1. query側のtag集合に、ruleのrequired tagsがすべて含まれるruleだけ候補にする。
2. 候補のうちrequired tag数が最大のruleを最も具体的なruleとする。
3. 同じspecificityのruleが複数残る場合は順序を推測せず`AMBIGUOUS`にする。
4. primitive / dimensionを正規化できない場合はraw attributesを保持し、黙ってsnapshot値へfallbackしない。

### Source identity

Catalog出力には入力XMLのSHA-256を記録する。

Validation report側では将来的に少なくとも次を一緒に保存する。

```text
Blender version
Egosoft Blender Mod Tools version
Blender_Properties.xml SHA-256
validation timestamp
```

### Runtime acceptance boundary

Repo内testsはEgosoft配布XMLを再配布せず、synthetic fixtureだけを使用する。

したがって、CI PASSは以下を証明する。

- parserの構文・基本契約
- tag specificity解決
- ambiguity fail-closed
- 複数の一般的なXML表現の正規化

一方で、**現行Egosoft Blender Mod Tools v0.7.0の実`Blender_Properties.xml`へ適用したruntime probeは別Acceptance**とする。

---

## Snapshot observed during research

Research date: 2026-09-12

### L Engine

```text
standard: cylinder 50 x 50 x 50 m
advanced/Boron: cylinder 25 x 25 x 25 m
```

### XL Engine

```text
standard: cylinder 150 x 150 x 150 m
advanced/Boron: cylinder 75 x 75 x 75 m
```

### L Shield

```text
standard: box 32 x 64 x 16 m
advanced/Boron: box 16 x 32 x 8 m
```

### XL Shield

```text
standard: box 96 x 192 x 48 m
advanced/Boron: box 48 x 96 x 24 m
```

### L Turret

```text
standard: box 64 x 64 x 64 m
advanced/Boron: box 32 x 32 x 32 m
```

### Dock approach / exclusion snapshots

```text
ship_s exclusion zone: 70 x 400 x 70 m
ship_m exclusion zone: 180 x 500 x 180 m
```

These values must be re-read from the active tool data when version-sensitive correctness matters.

---

## Design interpretation

Visualization should answer:

```text
Can the selected equipment fit here?
Can it rotate / occupy its expected zone without obvious hull conflict?
Can a ship approach / depart the dock without the hull blocking the reserved corridor?
```

It is not intended to reproduce every visual protrusion of the final equipment model.

### What Visualization does NOT prove

Visualization PASSだけでは、次は証明できない。

```text
component Connection ↔ ship macro binding
binding先macroのattachment connection
Connection name / ID persistence
custom turret IK / articulation
muzzle / firing axis
Dockの実runtime behavior
animation behavior
save compatibility
X4 runtime interpretation
```

したがって:

```text
Visualization PASS
    ↓
Binding / Identity validation
    ↓
Export / Package validation
    ↓
X4 Runtime Corroboration
```

まで別Gateとして扱う。

---

## Workbench integration target

A future `x4_layout` capability should:

1. locate active `Blender_Properties.xml`
2. call/consume the domain reader from this repo
3. resolve a Connection's tags to the active visualization rule
4. expose the shape / dimensions as Reserved Clearance
5. compare Reserved Clearance against Hull / neighboring reserved zones
6. produce PASS / WARN / FAIL evidence

Do not make the generic 3D Core aware of X4 tag names.

---

## Version boundary

X4 equipment standards can change between game/tool versions.

A stale snapshot must not silently override current tool data.
