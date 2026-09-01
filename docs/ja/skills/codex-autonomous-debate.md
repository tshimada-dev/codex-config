---
source: skills/codex-autonomous-debate/SKILL.md
source_commit: 4547b0f9218b08489064f459dbf1706a8c38a805
canonical: false
---

# codex-autonomous-debate 日本語参考訳

この文書は `skills/codex-autonomous-debate/SKILL.md` の日本語参考訳です。Codexが実行時に読むcanonicalな定義は英語版です。

## 目的

固定ラウンドで同じ主張を繰り返すのではなく、論点の状態を更新する対立的討論を行う。親エージェントは討論者でも自動的な一票でもなく、共通証拠、Claim Ledger、期限、手続きだけを管理する。

参加者を起動する前に [`debate-state-protocol.md`](../../../skills/codex-autonomous-debate/references/debate-state-protocol.md) を読む。終了後にHTMLを生成する場合は [`group-chat-ui.md`](codex-autonomous-debate/references/group-chat-ui.md) も読む。

## 討論契約

- 肯定、否定、または具体的政策で答えられる命題を1つ定める。
- 参加者を起動する前に、命題を `FORECAST`、`CAUSAL`、`FACTUAL`、`POLICY` のいずれかに分類し、判定対象、期限、YES/NO条件、確定情報源、予測の場合は数値閾値を固定する。
- 実在する論争から、実質的に異なる2〜4陣営を選ぶ。各陣営は、他陣営の否定だけでなく、自説の結論と立証責任を持つ。
- 軽量モードは `CRUCIAL_DISPUTE` のhard ceilingを3巡、詳細モードは6巡とする。必須phaseは `OPENING`、`CROSS_EXAM`、`RESPONSE`、`UPDATE`、`CRUCIAL_DISPUTE` だが、情報利得が止まれば早期終了する。
- 実質発言上限を `投票陣営数 * (4 + 最大crucial-dispute巡数)` とする。監査役を使う場合は、`OPENING`と`RESPONSE`の基本2turnに、Evidence Link変更時の監査を各crucial-dispute巡で1回行う最悪ケースとして `2 + 最大crucial-dispute巡数` を加える。Steelman確認と一度の訂正は有界な手続きturnであり、実質発言には数えない。
- 討論時間は `max(8分, 実質発言上限 * 1分)`、resolution時間は `max(4分, 陣営数 * 1分)` とする。
- `DEBATE_DEADLINE` と `RESOLUTION_DEADLINE` は、それぞれ親が観測した `DEBATE_START` と `RESOLUTION_START` から独立に測る。
- 終了状態は `FINAL_CONSENSUS`、`CONSENSUS_WITH_RESERVATIONS`、`FINAL_WINNER`、`TRUE_DEADLOCK`、`INCOMPLETE`。
- 多数決は使わない。同じモデルの複数エージェントは独立した証拠ではなく、少数側に決定的な異議が残る可能性がある。
- 親が勝者を判定するのは、ユーザーが明示した場合、または期限切れでも勝者が必要と指定された場合だけ。
- 開始前に、命題、選択・除外した陣営、任意の監査役、上限、証拠モード、決定規則をユーザーへ示す。

## 陣営と証拠を選ぶ

現実の論争では、異なる行動や判断基準を持つ立場を調べ、同じ理由で同じ判断をするラベルは統合する。重要な対立軸を残す最小集合を2〜4陣営で作り、4陣営を超える場合は除外を明示する。各陣営は擁護可能な分析上の立場であり、人物の模倣や集団全体の代表ではない。

「条件依存」という中道を、もっともらしいという理由だけで追加しない。条件依存自体が異なる行動を導くなら投票陣営にする。因果推論、測定、一般化を監査するだけなら、結論を主張せず投票もしない任意の方法論監査役を使う。

フィクション、提示資料だけを使う歴史問題、純粋な概念問題ではclosed-book modeを使える。現在の現実問題や高リスク問題ではshared-evidence modeを使い、親が権威ある一次資料から陣営マップと構造化Evidence Cardsを作る。全参加者に同一カードを渡し、観測結果と陣営の推論を分け、非対称な追加調査は禁止する。

## 状態駆動プロトコル

詳細な発言形式、Claim Ledgerの状態遷移、Cross-examination、Steelman、早期終了条件は [`debate-state-protocol.md`](../../../skills/codex-autonomous-debate/references/debate-state-protocol.md) を正典とする。

Evidence Cardには安定したID、出典、研究タイプ、対象、比較条件、直接測定した主要結果、限界、因果推論強度、一般化可能性を記録する。引用があるだけではEvidence Cardとして扱わず、討論中に因果強度や外的妥当性を黙って引き上げない。各EvidenceとClaimの関係には `directness`、`independence`、`causal_strength`、`generalizability`、`temporal_relevance`、支持できる範囲、支持できない強い結論を持つEvidence Linkを作り、単純な証拠数や総合点にしない。

親はClaim Ledgerへ原子的な主張を `C1` のようなIDで記録し、`fact`、`inference`、`definition`、`value`、`prediction`を区別する。状態は `proposed`、`agreed`、`disputed`、`unsupported`、`definitional_dispute`、`superseded`。親は複合文を分割してIDを付けられるが、参加者の明示的なsignalなしに合意、裏付けなし、置換済みと判断したり、言い換えを統合したりしない。

各実質発言は `ADD`、`ACCEPT`、`CHALLENGE`、`REFINE`、`CONCEDE`、`QUESTION`、`ANSWER` のいずれかのledger actionを持つ。主要な経験的Claimには、その主張を弱める観測を記した `FALSIFIER` を必須とする。定義・価値Claimにはrevision conditionを持たせる。既存主張の言い換えは新規actionではない。

`FORECAST`では、各投票陣営が `PRIOR`、`AFTER_CROSS_EXAM`、各巡の `AFTER_CRUCIAL_DISPUTE`、`FINAL` で、確率、区間、更新理由を親へ非公開提出する。`ASSIGNED_POSITION`と予測値を分離し、割当立場を維持したまま閾値を下回る予測も許す。同一checkpointの全提出が揃うまでpeerへ数値を見せず、最終artifactでのみ公開する。これらは同じモデルによるrole-conditionedな参加者予測であり、校正済みでも独立推定でも投票でもない。実績確定後に複数予測をBrier score等で評価して初めて校正を論じられる。

phaseは次の順序で行う。

1. `OPENING`: `POSITIVE_CASE`、`BURDEN_OF_PROOF`、主要Evidence ID、自説が崩れる条件を提示する。
2. `CROSS_EXAM`: 相手の立証責任または係争中Claimに対し、答えにくい質問を1つだけ行う。
3. `RESPONSE`: 質問へ直接答えてから、自説の積極的根拠、反論、不確実性を更新する。論点変更は回答と数えない。
4. `UPDATE`: 相手の最強主張を `STEELMAN` し、譲歩、任意のbelief update、最大争点候補、`REQUEST_RESOLUTION: YES | NO`を示す。相手が `STEELMAN_ACCEPTED` を返すか、一度の修正を終えるまで、その解釈を後続反論の土台にしない。
5. `CRUCIAL_DISPUTE`: 指名数が最大の未解決Claimを1件だけ扱い、同数ならClaim IDで決める。これは真偽の多数決ではなく、注意を向ける順序の決定である。

起動前に `PHASE_SPEAKERS` を固定する。`OPENING`は投票陣営の後に監査役、`CROSS_EXAM`は投票陣営のみ、`RESPONSE`は投票陣営の後に監査役、`UPDATE`と `CRUCIAL_DISPUTE` は投票陣営のみとする。crucial cycleでEvidence Linkが追加・変更された場合だけ、親が別の `METHODOLOGY_AUDIT` turnを1回起動する。各phaseは固有の発言順とsuccessor mappingを持ち、そのphaseの最終発言者だけが `<PHASE>_READY` を親へ送る。

全 `UPDATE` 発言後、親は有界な `STEELMAN_CONFIRMATION` subphaseを開始する。親が各Steelmanを変更せず対象へ `followup_task` で転送し、対象は親だけへ `STEELMAN_ACCEPTED` または具体的欠陥付き `STEELMAN_REJECTED` を返す。拒否時は元の作成者へ欠陥を送り、一度だけ訂正して再確認する。全確認が揃うまでresolutionまたは最初の `CRUCIAL_DISPUTE` へ進まず、未解決の拒否が残ればその `UPDATE` checkpointからの直接resolutionを認めない。

`RESPONSE`直後の `UPDATE` checkpoint、または同じ `CRUCIAL_DISPUTE` checkpointで全投票陣営が `REQUEST_RESOLUTION: YES` を送った場合は直接resolutionへ進む。ほかに、2巡連続のlow-information cycle、hard ceiling、または期限で進む。low-informationとは、新規未解決Claim、falsifier、Evidence Link、ledger変化がなく、全員の確率変化が3 percentage points未満の場合である。5 points以上の変化、新しいfalsifier、未解決Claim、追加・訂正されたEvidence Linkがあればceiling内で継続する。固定巡数を埋めるためだけに継続しない。

## 参加者の起動と進行

各陣営につき `fork_turns="none"` の `spawn_agent` を1つ使い、因果・測定・一般化が主要争点の場合だけ投票権のない方法論監査役を追加する。監査役は結論を勧告せず、Evidence→Claimの推論linkだけを監査する。全員へ固定した命題契約、同一Evidence CardsとLinks、陣営と役割、立証責任、Claim Ledger規則、phase形式、`PHASE_SPEAKERS` とphase別successor、期限を渡す。各phaseの開始メッセージには、そのphase用の正確なfenced response templateを転載する。

参加者はreadiness送信後に初回turnを終了し、現在のphase speaker listに含まれる場合だけ実質発言を `<CAMP> <PHASE>` で始める。同一発言を親と全peerへ送り、phase別successorだけを `followup_task` で起動する。発言順の逆順でspawnし、全readiness受信後にopening campへだけ `START OPENING` を送る。

`DEBATE_START` は親がopening campへの送信成功を観測した時刻。親は各phase境界で受信済み発言からClaim Ledgerを更新し、同一 `LEDGER_SNAPSHOT` を全員へ送り、訂正可能性を残した上で次phaseの先頭だけを起動する。

## 共通核によるresolution

討論終了後、`FORECAST`では全員の非公開 `FINAL` を収集してから、親が全投票陣営へ同一 `RESOLUTION_REQUEST` を送る。監査役は予測、候補提出、投票を行わない。各陣営は他候補を見る前に、固定したDecision Ruleへ結び付けた匿名候補を非公開で提出する。

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

親は提出元を非公開で記録し、候補には内容から導く中立IDを付ける。HTMLの新規resolution messageでは `resolution_stage` を必須運用し、匿名の `candidate` と `confirmation` では `camp` を省略して中立 `speaker` を使い、陣営名を表示できないようrendererでも検証する。陣営名を出す最終コメントは `public-statement` として区別する。その後、非投票のsynthesisとして各fieldを原子的命題へ分割し、全候補にある共通核、両立可能な留保、非互換な決定を抽出する。新しい結論を発明、平均、選択、黙って書き換えてはならない。

`COMMON_CORE_CHECK`には候補・Claim IDへのsource mapを付け、全陣営へ確認する。転記、scope、対応付けの誤りは一度だけ訂正できるが、新しい実質議論は追加しない。

いずれかの候補が `OUTCOME: WINNER` を提案した場合、`COMMON_CORE_CHECK`に `WINNER` fieldとcandidate source mapを含める。各陣営は通常の共通核応答ではなく `ACCEPT_WINNER <CAMP>` または `REJECT_WINNER` を返し、全員が同じ勝者を明示的に受諾した場合だけ勝者を確定する。

- 完全な決議へ全員が同意: `FINAL_CONSENSUS`
- 同じ実際的結論と共通核へ同意し、両立可能な留保が残る: `CONSENSUS_WITH_RESERVATIONS`
- 全陣営が同じ `ACCEPT_WINNER <CAMP>` を返す: `FINAL_WINNER`
- 実際的結論が非互換、または訂正後の共通核を実質的理由で拒否: `TRUE_DEADLOCK`
- 必須応答が期限までに不足: `INCOMPLETE`

2対1などの多数派は結果の根拠にしない。ユーザーが明示した場合だけ参考情報として票数を示せるが、終了分類を置き換えない。

## 監視・障害

親は60秒以下の `wait_agent` で期限を監視し、手続き状態だけを更新する。証拠モード違反、逸脱、未訂正の誤読、立証責任放棄、反復、危険、手続き違反の場合だけ全員を `PAUSE` し、一度の `CORRECT` を要求して再開する。参加者の主張を親が書き換えない。

ユーザー中止時は全員へ `STOP`。最初の実質発言前のagent failureだけ一度置換でき、その後は `INCOMPLETE`。message delivery failureは同一内容を一度だけ再試行し、再失敗時は停止する。討論期限ではresolutionを省略せず新しい `RESOLUTION_START` を開始し、resolution期限では必須応答の有無に応じ `INCOMPLETE` または有効な共通核状態を返す。

## 報告とHTML

終了statusを先に示し、命題、陣営と監査役、証拠モード、phase上限、時刻とtimeout、最終Claim Ledger変更、resolution候補、共通核確認、決定的議論、最大の留保・対立、介入、除外主張、議論結果の限界を報告する。

親は原文を変えない時系列イベントログを維持し、有効な公開発言、Steelman確認、匿名resolution候補、共通核check、確認応答を受信時点でそのまま追記する。`messages[].text` には受信した正確な内容を保存し、討論終了時にClaim Ledgerや最終報告から要約・再構成してはならない。あわせて命題契約、完了済みphaseとcrucial cycle数、最終Claim Ledgerとfalsifier、Evidence CardsとLinks、予測trajectoryを保持する。

JSONを欠落のないsource of truthとする。読みやすいchat表示はrendererが実行時に導出する自然言語viewに限る。rendererはartifactの言語に合わせて構造化fieldの見出しを訳し、ledger更新を折りたたみ、吹き出しheaderからphase・round statusを省略できる。ただし同じmessage内の開閉可能な領域にプロトコル原文を必ず保持し、表示用の言い換えで `messages[].text` を置換したり、要約fieldを追加したりしない。

終了済みの `FORECAST` artifactは、`INCOMPLETE` を除き、全投票陣営の `PRIOR` と `FINAL`、`RESPONSE` 完了時の `AFTER_CROSS_EXAM`、完了した全crucial cycleの `AFTER_CRUCIAL_DISPUTE` を欠落なく含める。討論期限で未完了だったphaseのcheckpointは要求しない。終了後は未解決ClaimのfalsifierまたはEvidence Linkのgapから `WHAT_WOULD_RESOLVE_THIS` を作り、必要な観測、対象Claim、期待される更新、収集方法を示す。定義・価値対立しか残らない場合は、genericな調査項目を作らずそう明記する。所定JSONをrepository外に作り、`scripts/render_debate_chat.py`でDecision Rule、予測推移、Evidence Links、「決着に必要な証拠」を含むself-contained HTMLへ変換する。
