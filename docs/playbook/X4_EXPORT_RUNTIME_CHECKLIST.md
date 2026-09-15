# X4 Export / Converter / Runtime Checklist v0.1

このチェックリストは、**Blenderで見た目が成立した艦を、古い中間物や見せかけの成功に引っ張られず、Current X4で動くCandidateまで持っていく**ために使う。

`X4_PLACEMENT_CHECKLIST.md` がLayout Freeze前のGateなら、こちらはその後の **Asset → Export → Convert → Package → X4 Runtime** のGate。

---

## A. Export preflight

- [ ] Blender versionを記録
- [ ] Egosoft Blender Mod Tools versionを記録
- [ ] 対象ship class (`ship_s` / `ship_m` / `ship_l` / `ship_xl`) がscene / export設定と一致
- [ ] 必要なEgosoft addonが有効な状態
- [ ] export前にfactory reset等でaddonを無効化していない
- [ ] `.blend` / export先がactive exporterの要求するpath conventionを満たす
- [ ] Connection名、tag、groupに重複・欠落なし
- [ ] component XMLとgeometry exportを同じCurrent buildから生成

### `[assets]` path trap

2026-09-11時点の現行寄り実例では、Egosoft exporterが `.blend` pathに literal `[assets]` を要求し、条件を満たさない場合でも成功メッセージと紛らわしいinfoだけ出る事例がある。

したがって:

- [ ] active toolでpath条件をprobe
- [ ] export operatorのreturnだけで成功判定しない
- [ ] DAE / component XMLの新規生成時刻・内容まで確認

これはthird-party実装で観測されたtrapなので、将来のtool versionへ固定仕様として埋め込まない。

---

## B. Export output validation

- [ ] component XML parse PASS
- [ ] component class / nameが意図通り
- [ ] geometry source pathが意図通り
- [ ] expected LOD定義が存在
- [ ] material参照が解決可能
- [ ] UV / normal / tangent / binormalに重大警告なし
- [ ] Collision対象が存在
- [ ] animation対象がある場合、必要なparent / restriction / connectionを確認

Custom articulated turret等では追加:

- [ ] socket / yaw / pitchのparent chain
- [ ] yaw / pitch restriction
- [ ] muzzle / laser connectionが動くpartへ追従
- [ ] geometry一致とruntime articulationを別Acceptanceとして扱う

---

## C. XUConverter freshness

Converterは「エラー0」だけではCurrent成果物を変換した証拠にならない。

推奨:

```text
Fresh source dir
+ Fresh destination dir
+ Fresh XUConverter process
```

- [ ] Current export専用のsource directoryを使う
- [ ] destinationに旧buildの残骸がない、またはbuild identityで分離
- [ ] fresh processでinitial scanから処理
- [ ] converter logの対象file数とerror数を記録
- [ ] `.xmf` / `.jcs` / `.ani` 等の期待出力が存在し、空でない
- [ ] output timestampがCurrent exportより後
- [ ] 必要ならSHA-256でCurrent build artifactを固定

### Stale component XML trap

現行寄り実例では、DAEだけ更新した場合にconverter側のcomponent XMLが古いまま残るケースを避けるため、**fresh Blender exporterのcomponent XMLをpackage工程へ明示的に渡す**方式が使われている。

- [ ] packageがconverter directory内の古いcomponent XMLを無条件採用しない
- [ ] latest component XMLのsourceを明示

---

## D. Package integrity

- [ ] 必須LOD meshが全て存在
- [ ] collision / hull / mesh physics outputが全て存在
- [ ] wreckを要求する艦ではwreck outputが存在
- [ ] animation fileが必要なら存在
- [ ] component geometry pathを最終extension pathへ解決
- [ ] indexのmacro / component entryが実体と一致
- [ ] ware → macro → component参照が解決
- [ ] ship macroの`connection ref`がcomponent側の実在Connectionを指す
- [ ] Connection名に重複なし
- [ ] 既存Connection contractを意図せず削除・renameしていない
- [ ] intermediate DAE等、ゲーム配布に不要なものをpackageしない
- [ ] local absolute pathを成果物へ漏らさない

### Case-sensitive path

Linuxや一部の配布経路を考慮し、ファイル名のcaseを曖昧にしない。

特にlocalisation等は、Current X4側の実ファイル名と同じcaseを使う。

- [ ] `t/` 以下を含む参照pathのcase一致
- [ ] Windowsで通ったcase mismatchをPASS扱いしない

---

## E. External asset / texture references

- [ ] Base game / DLCの外部resourceを参照する場合、対象X4 buildのcatalog内に実在
- [ ] DLC resourceなら必要dependencyを明示
- [ ] Egosoft assetをrepoへコピーせず参照で済む場合は参照を優先
- [ ] 自作textureは実fileがpackageに存在
- [ ] texture format / mip chainがCurrent X4で読めることを確認

---

## F. Static validation boundary

Offline validationで確認できるもの:

```text
XML well-formedness
XSD / structural checks
macro / component / ware reference
Connection existence / uniqueness
group / tag constraints
LOD / collision asset presence
localisation IDs
texture references
package completeness
```

Offline validationで**証明できない**もの:

```text
actual turret articulation
actual firing / muzzle behavior
actual docking behavior
actual animation behavior
gameplay integration
save/load behavior
runtime engine interpretation
```

`Blender PASS + tests PASS + XUConverter Errors=0` を `X4 runtime PASS` に読み替えない。

---

## G. X4 runtime acceptance

Game-ready Candidateを実X4へ入れたら、可能な範囲で次を確認する。

### Extension

- [ ] Extensions一覧で認識
- [ ] debug logを確認
- [ ] missing macro / component / material / asset等のblocking errorなし

### Ship appearance

- [ ] Equipment previewでHullが正常
- [ ] 宇宙空間でHullが正常
- [ ] material / texture / LOD切替に明白な異常なし
- [ ] engine / shield / weapon / turretが意図した位置・向き

### Functional equipment

- [ ] Engine装備・動作
- [ ] Fixed Weapon装備・射撃
- [ ] Turret装備
- [ ] Turret yaw / pitch追従
- [ ] Turret muzzle位置
- [ ] Turret firing
- [ ] Shield slot装備
- [ ] Dock / undock（対応艦）
- [ ] Launch Tube（採用時）
- [ ] Dock Door / other animation（採用時）

### Save compatibility / persistence

既存saveや既存艦への互換を意図する場合:

- [ ] 既存艦をload
- [ ] Connection identity変更による欠落がない
- [ ] 必要な新slotの扱いを確認
- [ ] save → reload後も状態維持

新規gameにも対応する場合:

- [ ] 新規gameでship / blueprint / ware等が期待通り利用可能

---

## H. Evidence packet

Runtime PASSを主張する場合、最低限残す:

```text
X4 version / build
Blender version
Egosoft Tools version
source commit
Blender_Properties.xml hash（使用時）
export timestamp
converter timestamp / result
packaged artifact hash
debug log locator
runtime checks performed
known WARN / residual checks
```

スクリーンショットは有用だが、**見た目だけで機能PASSの証拠にしない**。

---

# Completion states

## Offline Technical PASS

Static / Blender / Export / Converter / Package検証がCurrent artifactでPASS。

ゲーム内動作はまだ未確立。

## Game-ready Candidate

Visual Complete + Offline Technical PASS。

X4 runtime acceptanceへ投入可能。

## Runtime Corroborated

対象機能について実X4で確認し、debug logと実挙動が許容範囲。

Custom turret等、個別機能でruntime FAILが出た場合は、他のoffline PASSが残っていてもその機能をPASS扱いしない。

---

## Why this gate exists

2026-09-11更新の公開X4 custom-ship repoでは、regression tests、Blender checks、XUConverterのzero-error conversionまで通過した状態でも、custom turretが実ゲーム内testで失敗した記録がある。

このため本repoでは、**offline successとruntime behaviorを別の証拠層として管理する。**
