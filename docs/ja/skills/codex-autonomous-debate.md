---
source: skills/codex-autonomous-debate/SKILL.md
source_blob: 72890e682a74b5adecfde82013f178257f1b4a02
canonical: false
---

# codex-autonomous-debate 日本語参考訳

この文書は `skills/codex-autonomous-debate/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

論争を実際に構成している、証拠で確認可能な立場同士を直接討論させる。親エージェントは共通事実と手続きを管理するが、通常の討論には参加せず、自動的な一票にもならない。

## 討論契約

- 肯定、否定、または具体的な政策選択で答えられる命題を1つ定める。
- 固定された二人格ではなく、実在する論争の重要な相違を保つ2〜4陣営を選ぶ。
- 軽量討論は各陣営3ラウンド、1発言約300文字を基準とする。
- 深い討論は各陣営5ラウンド、1発言約500文字を基準とする。
- 討論時間は `max(4分, 陣営数 * ラウンド数 * 1分)` で計算する。
- resolution時間は `max(3分, 陣営数 * 1分)` で計算する。
- 例えば、3陣営 * 3ラウンドでは討論9分 + resolution 3分、3陣営 * 5ラウンドでは討論15分 + resolution 3分とする。
- 2つの期限を独立させる。`DEBATE_DEADLINE` は `DEBATE_START` から、`RESOLUTION_DEADLINE` は後で始まる `RESOLUTION_START` から測る。討論の超過時間や未使用時間をresolution時間から差し引かない。
- 終了状態は原則として参加者が所有する `FINAL_CONSENSUS`、`FINAL_WINNER`、`DEADLOCK` のいずれかとする。
- 多数決は使わない。同じモデルの複数エージェントは独立した証拠ではなく、少数意見に決定的な反論が残る可能性がある。
- 親による判定は、ユーザーが明示した場合、または期限切れで勝者が必要な場合だけ行う。
- 開始前に、命題、選択・除外した陣営、制限、証拠モード、決定規則をユーザーへ示す。

## 陣営を選ぶ

現実の論争では、討論者を作る前に実際の対立構造を調べる。

1. 異なる行動を提案するか、実質的に異なる判断基準を持つ立場を特定する。
2. 表現が違っても同じ理由で同じ判断をする立場は統合する。
3. 重要な対立軸を残す最小集合を選び、通常は2〜4陣営とする。
4. 重要な陣営が4つを超える場合は影響の大きい4つを選び、除外を明示する。除外によって依頼目的が変わる場合だけユーザーへ確認する。
5. 各陣営は擁護可能な立場として記述し、特定人物の模倣や集団全体の代表とは主張しない。

フィクション、提示資料だけを使う歴史問題、純粋な概念問題に限り closed-book mode を使える。このモードでは外部調査と未確認の統計、法律、研究、固有事例を禁止し、仮定は仮定と明記する。

現在の現実問題や高リスク問題では shared-evidence mode を使う。親が権威ある情報源から中立的な共通事実パケットと、陣営の実在を示す引用付き陣営マップを作り、全参加者へ同一内容を渡す。討論中の非対称な追加調査は禁止する。

選択した陣営は論争を分析するためのモデルであって人口上の代表ではなく、討論結果は客観的真実や専門的助言の証明ではないと明示する。

## 陣営エージェントを起動する

各陣営につき `fork_turns="none"` の `spawn_agent` を1つ使う。ユーザーが別タスクを明示依頼しない限り、ユーザー所有のCodexタスクは作らない。

全参加者へ、命題、証拠モード、同一事実パケット、全陣営マップ、自分の判断基準と立証責任、参加者名、固定発言順、次の発言者、ラウンド上限、両phaseの時間枠、親が所有する期限規則を渡す。

各参加者は次に従う。

1. `send_message` で親へ `READY_<CAMP>` を送り、初回turnを終了する。
2. 実質発言に `<CAMP> <ROUND>/<MAX_ROUNDS>` を付ける。
3. 自分のturnではpeerから届いたmessageを読み、直前の一人だけでなく最も強い未解決反論へ答える。
4. 同一発言を `send_message` で親へcopyする。
5. 次の発言者以外には `send_message`、次の発言者には `followup_task` で同じ発言を送り、次のturnを1つだけ起動する。
6. 親の確認を待たず継続する。
7. 親からの `PAUSE`、`RESUME`、`CORRECT`、`STOP` に従う。
8. readiness、介入、resolution messageではなく、実質的な討論発言だけをラウンド数として数える。

発言順の逆順でspawnし、親が期待する全 `READY_<CAMP>` を受信するまで待つ。親はopening campだけへ `followup_task` で `START` を送る。`DEBATE_START` は、親がopening campへの `START` 送信成功を観測した時刻とする。参加者内部のreasoningは観測不能なので開始時刻に使わない。送信に失敗した場合はdelivery failure規則に従い、再試行が成功するまで時計を開始しない。

`DEBATE_DEADLINE = DEBATE_START + 討論時間` とし、得られたtimestampを `DEBATE_DEADLINE: <timestamp>` として、新しいturnを起動せず全active campへ直ちに送る。その後は親が議論を中継せずring状に進行する。最終ラウンドの最後の発言者は次の陣営を起動せず、親へ `send_message` で `RESOLUTION_READY` を送る。

## 議論規則

- 最低ラウンドまでは割り当てられた提案を維持する。個別論点は譲歩してよいが、陣営を黙って変更しない。
- 他陣営の最も強い合理的解釈へ答える。
- パケット上の事実、推論、価値判断、仮定を分ける。
- 統計、研究、引用、法律、技術能力、固有事例を捏造しない。
- 人格攻撃、動機の決めつけ、論点逸脱、標語の反復、妥協自体を目的にした結論を避ける。
- 原則、実装、失敗、悪用、影響を受ける集団、代替案、可逆性、不確実性下の判断を必要に応じて検討する。
- 立場が収束し始めた場合は、共有された前提と、なお残る価値判断または証拠上の対立を明示する。

## 多数決を使わず終了する

opening campにresolutionの起草・回覧を任せない。`RESOLUTION_READY` の後、親が同一の `RESOLUTION_REQUEST` を全active campへ `followup_task` で送る。`DEBATE_DEADLINE` が先に到来した場合は討論を終了して後続の実質発言を採用せず、resolutionを省略せずvalid transcriptだけを使って同じrequestを送る。

`RESOLUTION_START` は、親が全active campへの同一 `RESOLUTION_REQUEST` の送信成功を観測した時刻とする。いずれかの送信に失敗した場合はdelivery failure規則に従い、完全なrequest一式が送信されるまでresolution時計を開始しない。`RESOLUTION_DEADLINE = RESOLUTION_START + resolution時間` とし、新しいturnを起動せず得られたtimestampを全active campへ送る。resolution時間はcandidate提出、同値性比較またはcandidate回覧、最終承認を含み、討論phaseには使わない。

各陣営は他の候補を見る前に、次の `RESOLUTION_CANDIDATE` を独立かつ非公開で親だけへ提出する。

```text
RESOLUTION_CANDIDATE
OUTCOME: CONSENSUS | WINNER | DEADLOCK
WINNER: <CAMP | NONE>
DECISION: <実際の結論・行動>
AGREED_POINTS:
- <合意点>
UNRESOLVED_OBJECTIONS:
- <未解決反論>
RATIONALE:
- <理由>
```

候補本文には提出陣営を記載せず、親だけがメッセージ送信元から対応関係を非公開で記録する。親は全active campの提出または `RESOLUTION_DEADLINE` まで候補を公開しない。候補の統合、書き換え、新しい文章の合成は禁止する。

`OUTCOME`、`WINNER`、実際の `DECISION`、重要な `AGREED_POINTS`、`UNRESOLVED_OBJECTIONS` が一致する場合だけ同値候補とする。言い回しや順序だけの差は無視できるが、実質的な同値性に疑いがあれば別候補として扱う。

全候補が同値なら、親は候補IDとfield別比較を含む `EQUIVALENCE_CHECK` を全陣営へ送る。全active campが `ACCEPT_EQUIVALENCE` を返した場合だけ共通outcomeを確定する。一つでも `REJECT_EQUIVALENCE` があれば `DEADLOCK` とし、争いのあるfieldを残す。

候補が異なる場合、親は陣営名を隠した中立的なcandidate IDを割り当てる。発言順や提出順ではなく、候補内容から導く決定的なキーで並べ、全候補を変更せず同じ順序で全陣営へ送る。各陣営は追加の実質議論をせず、`ACCEPT <CANDIDATE_ID>` または `REJECT_ALL` を返す。全active campが同じ候補を承認した場合だけ `FINAL_CONSENSUS` または `FINAL_WINNER` とする。それ以外は `DEADLOCK` とし、親が共通点として報告できるのは全候補で同一のfieldだけとする。

`RESOLUTION_DEADLINE` までに候補または必要な確認を提出しないactive campがあれば、その立場を推測せず `INCOMPLETE` とする。必要な応答がすべて届いても、同値または同一の候補を全陣営が承認しなければ `DEADLOCK` とする。

有効な終了状態を確認したら、親は全active agentへ `STOP` を送り、以後の実質発言を採用しない。

## 親の監視と介入

親は60秒以下の間隔で `wait_agent` を使い、記録した親観測の開始時刻を基準に `DEBATE_DEADLINE` と `RESOLUTION_DEADLINE` を独立して管理する。参加者から届くcopyを確認するが、正当な議論を称賛、要約、誘導、中継、代答しない。

証拠モード違反、命題からの逸脱、訂正可能な誤読、最低ラウンド前の立場放棄、敵対・反復・危険・手続き違反の場合だけ介入する。介入時は全員を `PAUSE` し、無効部分を指定し、責任陣営へ同じ番号の `CORRECT` を要求してから次の発言者だけを `RESUME` する。親が議論を書き換えてはならない。

## 中止・障害

- ユーザー中止時は全active agentへ直ちに `STOP` を送り、結果なしと報告する。
- 最初の実質発言前にagentが失敗した場合だけ、同一パケット、陣営、valid transcriptによるfresh replacementを1回許す。討論へ実質的に影響した後は置換せず、`INCOMPLETE` とする。
- message deliveryに失敗したら同一送信を1回だけ再試行する。再失敗時は到達可能な全agentを停止し、欠落陣営を親が代演しない。
- `DEBATE_DEADLINE` では実質的な討論だけを終了し、後続の議論を無視して、新しい `RESOLUTION_START` から完全なresolution phaseを開始する。討論時間切れだけを理由に `STOP` を送らない。
- `RESOLUTION_DEADLINE` では全active agentへ `STOP` を送り、後続messageを無視する。必要な候補または確認が不足していれば `INCOMPLETE`、それ以外は `DEADLOCK` とする。ユーザーが勝者を要求した場合だけvalid transcriptを判定する。

## 報告

`FINAL_CONSENSUS`、`FINAL_WINNER`、`DEADLOCK`、`INCOMPLETE`、または親のtimeout判定を先に示す。その後、次を報告する。

- 命題、選択・除外陣営、ラウンド、証拠モード。
- `DEBATE_START`、`DEBATE_DEADLINE`、`RESOLUTION_START`、`RESOLUTION_DEADLINE` と、各phaseがtimeoutしたか。
- resolution候補、同値性比較、確認。
- 決定的議論と最強の未解決反論。
- 親の介入・障害、または存在しなかったこと。
- 検討から除外した異議対象の主張。
- これは選択した陣営による議論上の結果であり、現実問題の客観的な解決ではないという限界。

ユーザーが全文や詳細分析を求めない限り、報告は簡潔にする。
