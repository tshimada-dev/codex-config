---
source: skills/codex-autonomous-debate/references/group-chat-ui.md
source_commit: 4547b0f9218b08489064f459dbf1706a8c38a805
canonical: false
---

# Group chat artifact 日本語参考訳

この文書は `skills/codex-autonomous-debate/references/group-chat-ui.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

この形式は、討論が終了状態へ到達した後だけ使う。rendererは決定論的に動作し、Python標準libraryだけを使い、参加者が制御する全textをescapeする。生成物は外部network requestを自動実行しない、単一のself-contained HTML fileである。

## Input document

UTF-8 JSONを次の形で書く。v3 field（`proposition_type`、`decision_rule`、`forecast_records`、Claimの`falsifier`、`evidence_links`、`needed_evidence`）と、それ以前からある構造化fieldは後方互換性のため任意である。`proposition_type` がある場合は `decision_rule` が必須で、`FORECAST` では確率 `threshold` も必要になる。新しいresolution messageでは、匿名手続きと帰属を明示する公開発言を区別するため `resolution_stage` を使う。

```json
{
  "lang": "ja | en",
  "title": "短い討論タイトル",
  "proposition": "正確な命題",
  "proposition_type": "FORECAST | CAUSAL | FACTUAL | POLICY",
  "decision_rule": {
    "target": "観測可能な対象eventまたは判断対象",
    "horizon": "判定日、または理由付きNOT_APPLICABLE",
    "yes_condition": "正確なYES・実行条件",
    "no_condition": "正確なNO・代替条件",
    "resolution_source": "対象を確定できる情報源",
    "threshold": 0.5
  },
  "debate_progress": {
    "completed_phases": ["OPENING", "CROSS_EXAM", "RESPONSE", "UPDATE"],
    "completed_crucial_cycles": 1
  },
  "status": "FINAL_CONSENSUS | CONSENSUS_WITH_RESERVATIONS | FINAL_WINNER | TRUE_DEADLOCK | INCOMPLETE",
  "evidence_mode": "closed-book | shared-evidence",
  "camps": [
    {"id": "affirmative", "name": "肯定派", "role": "advocate"},
    {"id": "negative", "name": "否定派", "role": "advocate"},
    {"id": "methods", "name": "方法論監査", "role": "auditor"}
  ],
  "evidence_cards": [
    {
      "id": "F2",
      "title": "短い証拠タイトル",
      "source": "情報源名",
      "source_url": "https://example.com/primary-source",
      "study_type": "RCT",
      "population": "観測対象",
      "conditions": "比較条件",
      "main_finding": "情報源が直接測定したこと",
      "limitations": ["重要な限界"],
      "causal_strength": "high | medium | low | not-assessed",
      "generalizability": "high | medium | low | not-assessed"
    }
  ],
  "claim_ledger": [
    {
      "id": "C1",
      "text": "原子的な主張1件",
      "type": "fact | inference | definition | value | prediction",
      "status": "proposed | agreed | disputed | unsupported | definitional_dispute | superseded",
      "evidence": ["F2"],
      "introduced_by": "affirmative",
      "falsifier": "このClaimを実質的に弱める観測結果"
    }
  ],
  "belief_updates": [
    {
      "camp": "affirmative",
      "phase": "UPDATE",
      "before": 0.78,
      "after": 0.66,
      "reason": "参加者が自己申告した変化の最大理由"
    }
  ],
  "forecast_records": [
    {
      "camp": "affirmative",
      "checkpoint": "PRIOR | AFTER_CROSS_EXAM | AFTER_CRUCIAL_DISPUTE | FINAL",
      "cycle": 1,
      "probability": 0.62,
      "lower": 0.45,
      "upper": 0.76,
      "rationale": "Claim IDを含む非公開の予測理由"
    }
  ],
  "evidence_links": [
    {
      "claim_id": "C1",
      "evidence_id": "F2",
      "supports": "cardから正当に導ける推論",
      "does_not_establish": "cardだけでは導けない強い推論",
      "directness": "high | medium | low | not-assessed",
      "independence": "high | medium | low | not-assessed",
      "causal_strength": "high | medium | low | not-assessed",
      "generalizability": "high | medium | low | not-assessed",
      "temporal_relevance": "high | medium | low | not-assessed"
    }
  ],
  "needed_evidence": [
    {
      "id": "N1",
      "observation": "生きているClaimを識別できる観測または研究",
      "resolves_claims": ["C1"],
      "expected_update": "どの結果がClaimを強化・弱化・反証するか",
      "collection": "実行可能な情報源または測定design"
    }
  ],
  "messages": [
    {
      "kind": "argument | resolution",
      "camp": "安定した小文字ID",
      "phase": "OPENING | CROSS_EXAM | RESPONSE | UPDATE | CRUCIAL_DISPUTE",
      "round": 1,
      "text": "親が受信した時点で記録した有効発言の原文",
      "timestamp": "任意の表示時刻"
    },
    {
      "kind": "system | intervention | resolution",
      "resolution_stage": "candidate | confirmation | public-statement",
      "speaker": "Supervisorまたは匿名candidate ID",
      "text": "観測した手続きeventまたは匿名resolution原文",
      "timestamp": "任意の表示時刻"
    }
  ],
  "summary": {
    "decision": "脚色していない有効な終了判断",
    "agreed_points": ["resolution手続きで受諾された点だけ"],
    "unresolved_objections": ["最も強い留保または対立"]
  }
}
```

`lang` は `ja` または `en` で、省略時は `en`。Camp IDは `^[a-z0-9][a-z0-9_-]{0,31}$`、Evidence IDとClaim IDは英字・数字・dot・hyphen・underscoreを使う。advocateは2〜4陣営とし、任意のauditorは最大1名。`role` 省略時は `advocate`。

rendererは過去artifactを読めるよう、現行の終了statusに加えて旧 `DEADLOCK` も受け付ける。新しい討論では、実際的な判断が真に両立しない場合に `TRUE_DEADLOCK` を使う。

`argument` messageには既知のcampが必要。`proposition_type` を持つ状態駆動artifactの `resolution` messageには必ず `resolution_stage` を設定する。`candidate` と `confirmation` は `camp` を省略し、`Candidate A`、`Common-core check` のような中立 `speaker` を指定する。rendererは匿名stageへのcamp identityを拒否する。`public-statement` は `camp` を指定する。`proposition_type` のない旧artifactでは後方互換性のため `resolution_stage` を省略できる。`system` と `intervention` にはcamp不要。状態駆動討論では `phase` を推奨し、旧 `round` も引き続き受け付ける。

Evidence Cardは構造化された証拠説明であって、情報源が正しいことの証明ではない。直接測定した `main_finding`、`limitations`、因果推論強度、一般化可能性を区別する。source linkは `http` と `https` だけを許可する。Claim Ledgerは同じdocument内にあるEvidence Card IDだけを参照できる。旧belief値は0〜1の参加者自己評価であり、独立した証拠や校正済み予測ではない。

Forecast recordは `FORECAST` artifactだけで許可する。`cycle` は `AFTER_CRUCIAL_DISPUTE` だけで必須となり、繰り返したadaptive cycleを区別する。各 `(camp, checkpoint, cycle)` は一意で、`lower <= probability <= upper` を満たす。`debate_progress` には完了済み作業だけを記録する。`completed_phases` は `OPENING`、`CROSS_EXAM`、`RESPONSE`、`UPDATE` の順序付きprefix、`completed_crucial_cycles` は完全に終えたadaptive cycle数である。

`INCOMPLETE` 以外の終了済み `FORECAST` artifactは、全advocateの `PRIOR` と `FINAL`、`RESPONSE` 完了時の `AFTER_CROSS_EXAM`、完了した全crucial cycleの記録を含む。これにより、早い `DEBATE_DEADLINE` 後の有効resolutionでは未実施phaseのcheckpointを省略できる。`debate_progress` がない場合は旧v3の厳格な要件を維持する。`INCOMPLETE` は失敗証跡を表示できるよう部分recordを保持してよい。予測値はrole-conditionedな参加者予測であり、独立sample、投票、校正済み確率ではない。trajectoryとして表示し、平均しない。校正には、通常は複数予測について後日 `decision_rule.resolution_source` で結果を確定する必要がある。

Evidence Linkは既存のEvidence Card 1件とClaim 1件を参照し、各dimensionは情報源全体ではなくその関係を評価する。dimensionを未定義の総合scoreへまとめない。`needed_evidence` は既存Claim IDを参照し、falsifierまたは `does_not_establish` のgapへ追跡できるようにする。

親が観測したmessageの時系列順を保つ。有効な公開発言、Steelman確認、匿名resolution候補、共通核check、確認応答は、親が受信した時点の原文を `messages` へ追記する。`messages[].text` は要約ではなく欠落のないtranscriptである。後からClaim Ledger、phase state、resolution、最終報告を使って要約・再構成してはならない。妥当性の説明に必要なphase・ledger遷移、介入、timeout、failureも含める。readiness handshakeと通常の配送処理は、妥当性へ影響した場合を除き省略する。画面を会話らしく見せるためだけのdialogueを追加しない。

`phase` と `round` はprotocol上の意味がある場合にJSONへ保持する。状態駆動artifactでは、参加者の吹き出しheaderにstatus textとして表示しない。時系列transcript自体が読順を示すためである。記録済みtimestampは表示してよい。旧artifactではphase・round表示を維持できる。

構造化protocol messageのHTML本文は、rendererが導出する自然言語viewをdefaultとする。たとえば日本語では `POSITIVE_CASE`、`BURDEN_OF_PROOF`、`DIRECT_ANSWER`、`STEELMAN`、`DECISION` をそれぞれ「主張」「この立場が示すべきこと」「回答」「相手の主張を最も強く捉えると」「結論」と表示する。resolution候補と共通核checkも同じ方法で表示する。`LEDGER_ACTIONS` は二次的な開閉領域へ収め、同じmessage内の明示された開閉領域に正確なprotocol原文を保持する。このviewはrender時に導出し、JSONへ言い換えtranscript fieldを追加せず、`messages[].text` を変更しない。

読みやすいviewと原文viewの両方で、参加者が制御するlabelと値をすべてescapeする。開閉領域はJavaScriptなしで機能し、生成HTMLは外部network requestを持たないself-contained fileのままにする。

## Render

```text
python <skill-dir>/scripts/render_debate_chat.py <transcript.json> --output <debate-chat.html>
```

中間JSONと生成HTMLは、ユーザーがrepository artifactを求めた場合を除いてsource repository外に置く。最終回答ではHTMLへlinkする。local renderingを利用できない、または失敗した場合は、失敗を短く報告し、同じ時系列内容をMarkdown transcriptとして示す。
