---
source: skills/codex-autonomous-debate/SKILL.md
source_blob: fba35aca5d87928a94689a98a1814d72538ebb73
canonical: false
---

# codex-autonomous-debate 日本語参考訳

この文書は `skills/codex-autonomous-debate/SKILL.md` の日本語参考訳です。Codexが実行時に読むcanonicalな定義は英語版です。

## 目的

固定ラウンドで同じ主張を繰り返すのではなく、論点の状態を更新する対立的討論を行う。決定論的なcontrollerが手続きを所有し、親エージェントは討論者でも自動的な一票でもなく、共通証拠、Claim Ledger、手続きだけを監督する。

参加者を起動する前に [`debate-state-protocol.md`](../../../skills/codex-autonomous-debate/references/debate-state-protocol.md) と [`controller-protocol.md`](../../../skills/codex-autonomous-debate/references/controller-protocol.md) を読む。終了後にHTMLを生成する場合は [`group-chat-ui.md`](codex-autonomous-debate/references/group-chat-ui.md) も読む。

## 討論契約

- 肯定、否定、または具体的政策で答えられる命題を1つ定める。
- 参加者を起動する前に、命題を `FORECAST`、`CAUSAL`、`FACTUAL`、`POLICY` のいずれかに分類し、判定対象、期限、YES/NO条件、確定情報源、予測の場合は数値閾値を固定する。
- 実在する論争から、実質的に異なる2〜4陣営を選ぶ。各陣営は、他陣営の否定だけでなく、自説の結論と立証責任を持つ。
- 通常は3巡・6巡や固定の時間上限を置かない。結論に必要な論点が解消した時点でresolutionへ進む。緊急時だけ明示したemergency limitを適用する。
- controllerの既定emergency safeguardは十分大きな `event_limit: 10000` と無効な `time_limit_seconds`。通常終了条件として使わず、暴走・停止時だけ最後の有効stateを凍結する。確定済みの形式的deadlockがなければ `INCOMPLETE` とし、合意や勝者を作らない。
- 終了状態は `FINAL_CONSENSUS`、`CONSENSUS_WITH_RESERVATIONS`、`FINAL_WINNER`、`TRUE_DEADLOCK`、`INCOMPLETE`。
- 多数決は使わない。同じモデルの複数エージェントは独立した証拠ではなく、少数側に決定的な異議が残る可能性がある。
- 開始前に、命題、選択・除外した陣営、任意の監査役、証拠モード、決定規則、emergency safeguardをユーザーへ示す。

## 陣営と証拠を選ぶ

現実の論争では、異なる行動や判断基準を持つ立場を調べ、同じ理由で同じ判断をするラベルは統合する。重要な対立軸を残す最小集合を2〜4陣営で作り、4陣営を超える場合は除外を明示する。各陣営は擁護可能な分析上の立場であり、人物の模倣や集団全体の代表ではない。

「条件依存」という中道を、もっともらしいという理由だけで追加しない。条件依存自体が異なる行動を導くなら投票陣営にする。因果推論、測定、一般化を監査するだけなら、結論を主張せず投票もしない任意の方法論監査役を使う。

フィクション、提示資料だけを使う歴史問題、純粋な概念問題ではclosed-book modeを使える。現在の現実問題や高リスク問題ではshared-evidence modeを使い、親が権威ある一次資料から陣営マップと構造化Evidence Cardsを作る。全参加者に同一カードを渡し、観測結果と陣営の推論を分け、非対称な追加調査は禁止する。

## 状態駆動プロトコル

詳細な発言形式、Claim Ledgerの状態遷移、Cross-examination、Steelman、早期終了条件は [`debate-state-protocol.md`](../../../skills/codex-autonomous-debate/references/debate-state-protocol.md) を正典とする。

Evidence Cardには安定したID、出典、研究タイプ、対象、比較条件、直接測定した主要結果、限界、因果推論強度、一般化可能性を記録する。引用があるだけではEvidence Cardとして扱わず、討論中に因果強度や外的妥当性を黙って引き上げない。各EvidenceとClaimの関係には `directness`、`independence`、`causal_strength`、`generalizability`、`temporal_relevance`、支持できる範囲、支持できない強い結論を持つEvidence Linkを作り、単純な証拠数や総合点にしない。

controllerはstructured ledger actionから原子的な主張へ `C1` のようなIDを決定論的に付け、`fact`、`inference`、`definition`、`value`、`prediction`を区別する。状態は `proposed`、`agreed`、`disputed`、`unsupported`、`definitional_dispute`、`superseded`。参加者はstatusを直接設定できず、controllerが明示的signalから導出する。親は主張内容を判断・統合・書換えしない。

各実質発言は `ADD`、`ACCEPT`、`CHALLENGE`、`REFINE`、`CONCEDE`、`QUESTION`、`ANSWER` のいずれかのledger actionを持つ。主要な経験的Claimには、その主張を弱める観測を記した `FALSIFIER` を必須とする。定義・価値Claimにはrevision conditionを持たせる。既存主張の言い換えは新規actionではない。

`FORECAST`では、各投票陣営が `PRIOR`、`AFTER_CROSS_EXAM`、各巡の `AFTER_CRUCIAL_DISPUTE`、`FINAL` で、確率、区間、更新理由を親へ非公開提出する。`ASSIGNED_POSITION`と予測値を分離し、割当立場を維持したまま閾値を下回る予測も許す。同一checkpointの全提出が揃うまでpeerへ数値を見せず、最終artifactでのみ公開する。これらは同じモデルによるrole-conditionedな参加者予測であり、校正済みでも独立推定でも投票でもない。実績確定後に複数予測をBrier score等で評価して初めて校正を論じられる。

phaseは次の順序で行う。

1. `OPENING`: `POSITIVE_CASE`、`BURDEN_OF_PROOF`、主要Evidence ID、自説が崩れる条件を提示する。
2. `CROSS_EXAM`: 相手の立証責任または係争中Claimに対し、答えにくい質問を1つだけ行う。
3. `RESPONSE`: 質問へ直接答えてから、自説の積極的根拠、反論、不確実性を更新する。論点変更は回答と数えない。
4. `UPDATE`: 相手の最強主張を `STEELMAN` し、譲歩、任意のbelief update、最大争点候補、`REQUEST_RESOLUTION: YES | NO`を示す。相手が `STEELMAN_ACCEPTED` を返すか、一度の修正を終えるまで、その解釈を後続反論の土台にしない。
5. `CRUCIAL_DISPUTE`: 指名数が最大の未解決Claimを1件だけ扱い、同数ならClaim IDで決める。これは真偽の多数決ではなく、注意を向ける順序の決定である。

controllerが `PHASE_SPEAKERS` と次のeligible actionを管理する。`OPENING`は投票陣営の後に監査役、`CROSS_EXAM`は投票陣営のみ、`RESPONSE`は投票陣営の後に監査役、`UPDATE`と `CRUCIAL_DISPUTE` は投票陣営のみとする。crucial cycleでEvidence Linkが追加・変更された場合だけ `METHODOLOGY_AUDIT` を行う。参加者はcontrollerが返した `next_actor` と `next_action` を受け取った時だけ発言し、自分でsuccessorを推測・起動しない。

全 `UPDATE` 発言後、controllerが `STEELMAN_CONFIRMATION` subphaseを開始する。親はcontrollerが指定した対象へ各Steelmanを変更せず転送し、対象は親だけへ `STEELMAN_ACCEPTED` または具体的欠陥付き `STEELMAN_REJECTED` を返す。controllerは順序と一度だけの訂正を強制し、全確認が揃うまでresolutionまたは最初の `CRUCIAL_DISPUTE` へ進めない。

`RESPONSE`直後の `UPDATE` checkpoint、または同じ `CRUCIAL_DISPUTE` checkpointで全投票陣営が `REQUEST_RESOLUTION: YES` を送った場合は直接resolutionへ進む。ほかに、同じoperative conclusionが明示された場合、または新しいClaim、falsifier、Evidence Link、ledger変化、具体的な次の検証がないlow-information cycleが2巡続いた場合にresolutionへ進む。5 points以上の確率変化は0〜1の更新後確率と組にして記録する。各陣営の更新後確率が実際に変化した場合や、新しいfalsifier、未解決Claim、追加・訂正されたEvidence Linkがあれば6巡を超えても継続する。

## 参加者の起動と進行

各陣営につき `fork_turns="none"` の `spawn_agent` を1つ使い、因果・測定・一般化が主要争点の場合だけ投票権のない方法論監査役を追加する。監査役は結論を勧告せず、Evidence→Claimの推論linkだけを監査する。全員へ固定した命題契約、同一Evidence CardsとLinks、陣営と役割、立証責任、Claim Ledger規則、phase形式を渡す。各phaseの開始メッセージには、そのphase用の正確なfenced response templateとcontrollerが返したeligible actionを転載する。

参加者はreadiness送信後に初回turnを終了し、controllerが自分を `next_actor` として返した場合だけ実質発言を `<CAMP> <PHASE>` で始める。発言は親だけへ送り、peerやsuccessorを直接起動しない。親は原文を保存し、明示fieldだけを安定した `event_id` を持つstructured action envelopeへ写してcontrollerへ送る。accepted時だけ原文を全peerへ共有し、返された次actorだけを `followup_task` で起動する。

controller stateはaccepted/rejected receiptごとに保存する。再開時はserialized stateを読み、そこにあるphase、ledger、confirmation、`next_actor`、`next_action`から続行する。transcript proseから手続き状態を再構成しない。

## 共通核によるresolution

controllerが `RESOLUTION_CANDIDATE` をeligibleにした後、`FORECAST`では全員の非公開 `FINAL` を収集し、返された `next_actor` だけへ候補を要求する。監査役は予測、候補提出、投票を行わない。各陣営は他候補を見る前に、固定したDecision Ruleへ結び付けた匿名候補を非公開で提出する。

```text
RESOLUTION_CANDIDATE
OUTCOME: CONSENSUS | CONSENSUS_WITH_RESERVATIONS | WINNER | DEADLOCK
WINNER: <CAMP | NONE>
DECISION: <実際の結論・行動>
AGREED_POINTS:
- <Claim ID付き合意点>
RESERVATIONS:
- <両立可能な留保>
CONFLICTS:
- <非互換な異議>
RATIONALE:
- <理由>
```

controllerは提出元をprivate stateだけへ記録し、候補には内容から導く中立IDを付ける。公開用 `artifact_metadata()` は提出元を `anonymous` に置換する。HTMLの新規resolution messageでは `resolution_stage` を必須運用し、匿名の `candidate` と `confirmation` では `camp` を省略して中立 `speaker` を使う。controllerはstructured fieldから全候補にある共通核、両立可能な留保、非互換な決定、source mapを決定論的に作る。新しい結論を発明、平均、選択、黙って書き換えてはならない。

`COMMON_CORE_CHECK`には候補・Claim IDへのsource mapを付け、全陣営へ確認する。転記、scope、対応付けの誤りは一度だけ訂正できるが、新しい実質議論は追加しない。

いずれかの候補が `OUTCOME: WINNER` を提案した場合、`COMMON_CORE_CHECK`に `WINNER` fieldとcandidate source mapを含める。各陣営は通常の共通核応答ではなく `ACCEPT_WINNER <CAMP>` または `REJECT_WINNER` を返し、全員が同じ勝者を明示的に受諾した場合だけ勝者を確定する。

- 完全な決議へ全員が同意: `FINAL_CONSENSUS`
- 同じ実際的結論と共通核へ同意し、両立可能な留保が残る: `CONSENSUS_WITH_RESERVATIONS`
- 全陣営が同じ `ACCEPT_WINNER <CAMP>` を返す: `FINAL_WINNER`
- 実際的結論が非互換、または訂正後の共通核を実質的理由で拒否: `TRUE_DEADLOCK`
- 必須応答を取得できない、または形式的deadlockのないままemergency safeguardが作動: `INCOMPLETE`

2対1などの多数派は結果の根拠にしない。ユーザーが明示した場合だけ参考情報として票数を示せるが、終了分類を置き換えない。

## 監視・障害

親は60秒以下の `wait_agent` で応答を監視し、controllerへのtransportだけを担当する。証拠モード違反、逸脱、未訂正の誤読、立証責任放棄、反復、危険、手続き違反の場合だけ全員を `PAUSE` し、一度の `CORRECT` を要求して再開する。参加者の主張を親が書き換えない。

ユーザー中止時はcontrollerへ `CANCEL` を送り全員へ `STOP`。最初の実質発言前のagent failureだけ一度置換でき、その後はcontrollerへ `FAILURE` を送り `INCOMPLETE` とする。message deliveryが曖昧なら同じenvelopeと `event_id` を一度だけ再送し、二重commitを防ぐ。再失敗時は停止する。emergency safeguard作動時は最後のaccepted stateを凍結し、既に形式的deadlockが確定している場合だけ `TRUE_DEADLOCK`、それ以外は `INCOMPLETE` とする。

## 報告とHTML

controllerは構造化action envelope（安定したevent ID、action type、payload）を使って進行を記録する。action log、Claim Ledger、参加者状態、resume pointはシリアライズ可能なstate bundleとして保存し、再開時に復元する。同じeventの再送は二重適用しない。通常の3巡・6巡や固定deadlineは設けず、結論が整った時点でresolutionへ移る。暴走・障害・配送停止などの緊急時だけemergency limitを適用し、打ち切りをartifactに記録する。

controllerの終了statusを先に示し、命題、陣営と監査役、証拠モード、完了phase/cycle、emergency safeguard状態、最終Claim Ledger変更、resolution候補、共通核確認、決定的議論、最大の留保・対立、介入、除外主張、議論結果の限界を報告する。

親は原文を変えない時系列イベントログを維持し、有効な公開発言、Steelman確認、匿名resolution候補、共通核check、確認応答を受信時点でそのまま追記する。`messages[].text` には受信した正確な内容を保存し、討論終了時にClaim Ledgerや最終報告から要約・再構成してはならない。あわせて命題契約、完了済みphaseとcrucial cycle数、最終Claim Ledgerとfalsifier、Evidence CardsとLinks、予測trajectoryを保持する。

JSONを欠落のないsource of truthとする。読みやすいchat表示はrendererが実行時に導出する自然言語viewに限る。rendererはartifactの言語に合わせて構造化fieldの見出しを訳し、ledger更新を折りたたみ、吹き出しheaderからphase・round statusを省略できる。ただし同じmessage内の開閉可能な領域にプロトコル原文を必ず保持し、表示用の言い換えで `messages[].text` を置換したり、要約fieldを追加したりしない。

終了済みの `FORECAST` artifactは、`INCOMPLETE` を除き、全投票陣営の `PRIOR` と `FINAL`、`RESPONSE` 完了時の `AFTER_CROSS_EXAM`、完了した全crucial cycleの `AFTER_CRUCIAL_DISPUTE` を欠落なく含める。`INCOMPLETE` では未完了phaseのcheckpointを要求しない。終了後は未解決ClaimのfalsifierまたはEvidence Linkのgapから `WHAT_WOULD_RESOLVE_THIS` を作り、必要な観測、対象Claim、期待される更新、収集方法を示す。定義・価値対立しか残らない場合は、genericな調査項目を作らずそう明記する。所定JSONへ公開用 `controller` metadataを追加し、repository外で `scripts/render_debate_chat.py` を実行してself-contained HTMLへ変換する。
