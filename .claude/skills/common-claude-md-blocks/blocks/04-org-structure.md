<!-- Evidence: 2026-06-11 組織再編 v2 改定 (kimny Q1-Q7 確定 / 即時移行)。
     確定版 = _conductor/docs/inbox/proposal-org-restructure-20260611.md (v2)。
     旧構成: プロダクト部=mued/native/dsp/occur、マーケ部=SNS/write/LP、分析研究部=reserch/data。
     変更: occur=closed / native→product課 畳込 / write+LP+blender→content課 / reserch+data→insight課 / product課・Chief 新設。
     ★ native の workspace 物理畳込は Tier2 matrix main 反映後 (保護条件)。 -->
## 組織体制（2026-06-11 組織再編v2改定）

### 経営体制
| 役職 | 課 | 機能 |
|------|-----|------|
| CEO | kimny | 最終判断・方針決定 |
| COO | conductor | 執行・調整・記録 |
| CCO | template課 | プロダクト基盤・品質・技術戦略 |
| CFO | freee課 | 財務・コスト・収益性チェック |
| 参謀(Chief) | Chief課 | 戦略助言（on-demand・指揮権なし・`_chief`のみ書込） |

### 部署構成（11課常時 + Chief on-demand）
| 部 | 課 |
|----|----|
| 経営部 | conductor(COO)、template課(CCO)、freee課(CFO)、cowork課 |
| プロダクト部 | mued課、product課、dsp課 |
| マーケティング部 | SNS課、content課、growth課 |
| 分析部 | insight課 |

- **product課** = 旧 native課 / occur課 の畳み先・製品横断統括（occur は 2026-06-11 closed、記憶は product課が保持）
- **content課**（母体 `_contents-writing`）= 旧 write課 + LP課 + blender課 の統合（制作・配信）
- **insight課**（母体 `_data-analysis`）= 旧 reserch課 + data課 の統合（reserch は dormant化、free15計測は母体継続=無断絶）
- **Chief（参謀）** = on-demand 起動・指揮権なし・戦略助言のみ（`_chief` に書込、コードPRは出さない）

戦略的提案はconductor経由でpolicy-gate（経営部会議）を通してからCEO(kimny)に提示する。
