---
source: skills/codex-claude-code-reviewer/SKILL.md
source_commit: 615a918590b6d75cf8e6f85508741040baaba56d
canonical: false
---

# codex-claude-code-reviewer 日本語参考訳

この文書は `skills/codex-claude-code-reviewer/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

Codex の作業を Claude Code に read-only の外部レビューとして見てもらい、その findings を Codex が検証してから採用・修正する。

## 前提条件

- user が Claude / Claude Code review を明示的に依頼した、または外部 model review を承認した場合だけ使う。
- review を試みる前に `claude` が利用可能か確認する。
- `claude -p` は repository context を Codex の外へ送る可能性があり、Claude Code の usage cost が発生し得る external call として扱う。
- secrets、`.env` files、private keys、cookies、tokens、credential-like diffs、sensitive customer data は渡さない。
- production deployment、remote mutation、secret handling、destructive operations には使わない。

## Workflow

1. まず Codex 自身で worktree を確認する。
   - `git status --short --branch` を実行する。
   - changed files と unrelated user-owned changes を特定する。
   - 送信対象を理解できる程度に relevant diff を確認する。

2. review scope を選ぶ。
   - implementation review では staged / unstaged diffs を送る。
   - planning review では code diff ではなく plan や task description を送る。
   - large diffs は subsystem ごとに分割して focused reviews を実行する。
   - untracked file contents は helper には含まれない。安全な files を意図的に stage するか、手元で review する。

3. helper script を優先する。
   - external review が意図された状態でだけ、`scripts/invoke-claude-review.ps1` に `-Run` を付ける。
   - `-Scope` で behavior、regressions、tests、security/privacy、subsystem などに focus する。
   - `-Run` を省略すると、Claude を呼ばずに prompt preview を作る。

4. Claude の output を triage する。
   - 各 claimed issue を repository に照らして検証する。
   - speculative、style-only、preference-only comments は、user request に関係しない限り無視する。
   - confirmed issues は Codex が修正し、unrelated user changes は保持する。
   - fix 後は repository の real verification commands を実行する。
   - accepted findings、rejected findings、checks run、residual risk を報告する。

## Helper Script

review 対象 repository から:

```powershell
powershell -ExecutionPolicy Bypass -File "$HOME\.codex\skills\codex-claude-code-reviewer\scripts\invoke-claude-review.ps1" -RepoPath "C:\path\to\repo" -Scope "focus on regression risk" -Run
```

Useful options:

- `-Scope "focus on API behavior and missing tests"` で review focus を追加する。
- `-ExtraPrompt "The target branch is main"` で安全な context を追加する。
- `-OutFile review.txt` で Claude の response を local file に書く。
- `-MaxBudgetUsd 1.00` で Claude Code budget cap を変更する。
- `-MaxPromptChars 200000` で prompt-size refusal threshold を変更する。
- `-Run` を省略すると、Claude を呼ばずに generated prompt path と command preview を表示する。

## レビュープロンプトの形

Claude には findings-first の review output を依頼する。

```text
同梱した Codex の作業内容を、senior code reviewer としてレビューしてください。
ファイルは変更しないでください。提供された context だけに基づいて回答してください。
correctness bugs、regressions、security/privacy issues、data loss、missing tests を優先してください。
findings を最初に返し、severity の高い順に並べ、可能な場合は file/path references を付けてください。
material issues が無い場合はその旨を明確に述べ、残る risk を簡潔に補足してください。
```

## Guardrails

- Claude に tools 実行や file edit をさせない。context は prompt で渡し、review-only output を求める。
- final judgment を outsource しない。verification と implementation の責任は Codex が持つ。
- Claude の advice を理由に unrelated user changes を overwrite / stage しない。
- helper が sensitive-looking path や diff を理由に refuse した場合は、diff を narrow するか、外部共有前に user に確認する。
- Claude Code が利用できない場合は、その旨を伝えて通常の Codex review に fallback する。
