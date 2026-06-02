---
source: skills/codex-context-handoff/SKILL.md
source_commit: 48eb930dceb63657f8f66ca4238e48954f48ef80
canonical: false
---

# codex-context-handoff 日本語参考訳

この文書は `skills/codex-context-handoff/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

長時間作業、中断、再開、handoff、context compaction に備えて、次の session や agent が自然に続けられる durable context を残す。

## 何を残すか

- objective と current state
- changed files と重要な decisions
- verified commands と results
- skipped checks と理由
- unresolved risks
- next step
- tool gaps や verification fallbacks

## どこに残すか

- 既存の repo convention、run note、planning location がある場合はそれを優先する。
- active run note がある場合は、そこに `## Handoff` として簡潔に追記する。
- convention がなく長時間作業として run note が必要な場合は `$HOME\.codex\runs\<repo-name>\` を使う。
- 単体 handoff file が必要な場合だけ `$HOME\.codex\handoffs\<repo-name>\` を使う。

## 良い handoff

- 次の agent が repo を最初から読み直さなくても動ける。
- user-owned changes と自分の変更が分かる。
- 実行した commands と結果が分かる。
- 「次に何をすべきか」が一文で分かる。

## 避けること

- 大量の file contents を貼る。
- 曖昧な「ほぼ完了」だけを書く。
- 未検証なのに検証済みのように書く。
- secrets、tokens、credentials、cookies、private keys、environment variable dump を含める。
