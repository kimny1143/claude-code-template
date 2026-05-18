---
peer: <peer-id>                        # e.g. dsp / occur / mued / native / SNS / write / LP / data / reserch / blender / freee / cowork / conductor / template
department: <department>               # product | marketing | corporate | research | management
activity: active                       # active | dormant
status: working                        # working | blocked | waiting | done | dormant
current_task: <one-line task summary>
next_action: <one-line next action>
blocked_by: none                       # none | kimny | conductor | peer:<name> | external:<service>
urgency: low                           # low | mid | high (block 15 URGENCY marker と同一 vocabulary)
action_owner: peer                     # peer | conductor | kimny
deadline: null                         # ISO8601 or null
expected_next_check_at: <ISO8601>      # 次の自走 update 予定時刻 (stale 判定 source)
last_update: <ISO8601>                 # 本 file の最終更新時刻
evidence: <PR# | file | commit>        # status の根拠 reference (block 15 EVIDENCE と同一概念)
confidence: high                       # high | mid | low (status 把握の確度)
lane: notification                     # notification | discussion (proposal v3 §4.5 Communication Lanes)
---

## Recent events

<!-- 直近の status change event を時系列で記載 (最新が上)。 1 entry 1 行、 ISO8601 timestamp + 1 行 summary -->

- <ISO8601>: <event 1>
- <ISO8601>: <event 2>

## Notes

<!-- 任意の自由記述。 peer 内部 memo、 next session resume hint、 cross-peer dependency note 等。 削除 OK。 -->

(peer 自由記述スペース)
