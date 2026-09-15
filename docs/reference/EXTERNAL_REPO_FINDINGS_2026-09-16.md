# External X4 Modding Repo Findings — 2026-09-16

このファイルは、公開X4 modding repoから得た**実装上の観察点**を、どこまで本repoへ取り込んだか記録するためのメモ。

Third-party repoはAuthorityではない。特に古いrepoの仕様記述はCurrent X4 9.xへ直接適用せず、現行X4 data / Egosoft Tools / runtime evidenceで再確認する。

---

## 1. drjele/x4-andromeda-ascendant

Repository:
https://github.com/drjele/x4-andromeda-ascendant

Observed current handoff date: 2026-09-11.

### High-value observations

- Blender/Pythonからcustom XL shipを生成・importし、LOD / collision / connection / X4 packageまで実運用している。
- Offline regression、Blender check、XUConverter zero-error conversionが通っていても、custom turretはin-game acceptanceで失敗した。
- exporter / converterには「成功ログだけではCurrent artifactの成功を証明できない」trapがある。
- current pipelineではfresh converter processとfresh input/output directoriesを重視している。
- Blender exporterへ渡すpath conventionに`[assets]`が関与する実例がある。
- package工程ではfresh Blender component XMLを明示的に受け取り、converter側のstale component XMLを避けている。
- package時にLOD / collision / Jolt / animationの必須成果物を個別に存在・size検証している。
- 既存Connection name / tag / group contractを意図せず壊していないか検証している。
- macro側`connection ref`がcomponent側の実Connectionへ解決するか検証している。
- custom articulated turretではyaw/pitch IK chainとmuzzle parentをstatic validatorで確認している。
- texture mip chain、localisation、external base-game texture referenceまでproject validatorで確認している。
- Connection identifierはmacro bindingやsaveとの関係があるため、stable identityとして扱っている。

### Adopted here

- `X4_PLACEMENT_CHECKLIST.md`: Connection identity / macro binding / custom turret hierarchyを追加。
- `X4_EXPORT_RUNTIME_CHECKLIST.md`: fresh export / converter freshness / stale output / package integrity / runtime evidenceを追加。
- Offline PASSとRuntime Corroboratedを明示的に分離。

### Do not copy blindly

- Andromeda固有のtag、macro ID、equipment contract。
- project固有のmaterial / texture choices。
- failed custom turret implementationそのもの。

---

## 2. rjtwins/X4-Blender-Module-Drag-and-Drop

Repository:
https://github.com/rjtwins/X4-Blender-Module-Drag-and-Drop

Last pushed: 2020-01-29. Historical reference only.

### Useful leads

- hardpointを3D上で配置し、position / orientationをX4 Connection XMLへ変換する設計。
- mirrored hardpoint placement。
- component-side Connectionとship macro-side bindingを別工程として扱っている。
- Engine / Shield / Turret / Fixed Weapon / Dock / Storage / Waypoint等を別module typeとして扱う。
- group assignmentが単なる整理用metadataではなく、装備挙動へ関与するという実装知見。
- Dock / Storage / cockpit等でConnectionだけでなくmacro bindingが必要という制作フロー。
- waypoint / mass-traffic / docking pathという追加の空間関係が存在する。

### Adopted here

- `X4_PLACEMENT_CHECKLIST.md`でConnection placementとmacro bindingを別チェックにした。
- group semanticsを確認項目へ追加。
- custom dock / traffic pathではwaypointの必要性をCurrent vanilla exampleで再確認する項目を追加。

### Historical warning

このrepoはpre-9.xのため、次のような具体的断定はCurrent ruleとして固定しない。

- engine size mixing rules
- fixed weapon group / naming rules
- shield group semanticsの細部
- waypoint naming contract

これらはCurrent X4 data / XSD / current working examplesで再確認する。

---

## 3. ratilicus/x4

Repository:
https://github.com/ratilicus/x4

Last pushed: 2022-03-14. Historical pipeline reference.

### Useful leads

- Game catalog extraction → source corpus → mod compile → index generation → package → extensionsへの配置という再現可能な工程。
- macros / components indexを明示的に扱う。
- Base gameとDLC sourceを分離して見る。
- package後は実ゲームのExtensions認識とDebug Logで確認する。

### Adopted here

本repoではCAT/DAT packingを必須にしないが、次は維持する。

- index / macro / component reference completeness
- source provenance
- package後のruntime recognition
- Debug Log確認

---

## 4. KennyG1990/X4_Forge

Repository:
https://github.com/KennyG1990/X4_Forge

Observed repository activity through 2026-09-09.

3D modelling toolではないが、X4 project validation / package / deploy / runtime evidenceの設計参考として有用。

### High-value patterns

- file単体ではなくproject全体をvalidateする。
- XML well-formednessだけでなくXSD / reference / identifier / package completenessを分離して見る。
- effective base+DLC+extension realityを前提にする。
- packageを再open / verifyする。
- deploy前にadd / overwrite / delete / preserve planを見る。
- rollback / recoveryを持つ。
- runtime debug evidenceをsourceへ結び付ける。
- static validationがruntime behaviorを保証しないことを明示する。
- current green baselineとの差分としてnew warningを扱う。

### Adopted here

- package completenessとreference integrityを`X4_EXPORT_RUNTIME_CHECKLIST.md`へ追加。
- Runtime Corroboratedを別証拠層にした。
- 将来自動deployする場合はstaged / recoverable deploymentを優先する。

---

# Combined lessons

既存repoから見た、本repoで特に落とさない方がよい境界は次。

```text
Geometry placement
    !=
Connection semantics
    !=
Macro binding
    !=
Converted asset freshness
    !=
Package completeness
    !=
X4 runtime behavior
```

それぞれ別のfailure modeを持つ。

したがって最終工程は:

```text
Blockout
→ Functional Connection layout
→ Macro / identity binding
→ Layout Freeze
→ Detail / UV / Material / Collision / LOD
→ Fresh Export
→ Fresh Convert
→ Package reference validation
→ Game-ready Candidate
→ Runtime Corroboration
```

とする。
