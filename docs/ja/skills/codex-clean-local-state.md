---
source: skills/codex-clean-local-state/SKILL.md
source_blob: 811336b35b552b6bb5c7673f5b596f3f50e633d1
canonical: false
---

# codex-clean-local-state 日本語参考訳

この文書は `skills/codex-clean-local-state/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

最近の作業を保護しながら、肥大化した Codex Desktop の local state を診断・整理する。transcript本文、`auth.json`、secret、config値、log本文は読まず、aggregate metadata だけを扱う。

## Safety contract

- 最初はread-onlyで調査し、userが永久削除を明示承認するまでlocal stateを変更しない。
- `CODEX_HOME` 全体を削除しない。config、auth、skills、plugins、attachments、worktrees、memories、goals、その他無関係なapplication dataは対象外とする。
- shutdown前にtimezone付きcutoffを1つ固定し、app終了待ちの間にretention windowを動かさない。
- transcript mtimeと`threads.updated_at_ms`の両方がcutoffより古いthreadだけを候補にする。
- recent、missing、root外、timestamp不明、job参照中のthreadが含まれるparent/child spawn component全体を保護する。
- DB evidenceと対応しないtranscript fileは保持する。
- 実行候補のID、path、size、file mtime、DB timestamp、archive stateを承認済みbaselineと一致させる。新規候補や実質的に変化した候補があれば停止する。
- mutation前にCodex Desktop processを停止し、live SQLiteを編集しない。
- output directoryは`CODEX_HOME/backups`直下の一意なchildに限定する。
- output作成やtranscript移動より前に、state/log DBの必須table・column・integrity・foreign keyを検証する。
- mutation前に`state_5.sqlite`、`logs_2.sqlite`、`session_index.jsonl`をbackupする。recent workを正常に開けるまでbackupを保持する。
- post-restart verificationが通るまでtranscriptをexact quarantineに残す。quarantine purgeは別の明示承認後に行う。
- 小さなnamed setでは、installed CLIが対応していればofficial `codex delete`を優先する。bundled bulk cleanerはretention-based cleanupでofficial CLIが使えない、または非実用的な場合だけ使う。

## 1. 変更せずに診断する

`CODEX_HOME`を解決する。defaultは`~/.codex`。

```powershell
python scripts/inspect_codex_state.py --root "$CodexHome" --days 14 --output "$AuditDir\inventory.json"
```

以下を報告する。

- `sessions`と`archived_sessions`のtotal/old transcript数とsize
- `logs_2.sqlite`のsizeと回収可能free-page見積もり
- `state_5.sqlite`のsize
- process toolが利用可能ならCodex/ChatGPT process数とmemory

古いtranscript fileが存在するだけで安全に削除できるとは判断しない。

## 2. Guarded baseline planを作る

`inventory.json`のexact `cutoff`を再利用する。

```powershell
python scripts/cleanup_stale_codex_sessions.py --root "$CodexHome" --cutoff "$Cutoff" --plan-output "$BaselinePlan"
```

次を確認する。

- `cross_boundary_edges`が0
- candidateのfile timestampとDB timestampが両方old
- recentまたはconnected workがprotectedとして数えられている
- unmapped fileが保持される
- candidate数とbytesがuserに提示する内容と一致する

cutoff、永久削除数、transcript回収見積もり、log compaction見積もり、一時backup/quarantine容量、二段階purgeを説明する。削除承認をまだ得ていなければ停止し、明示承認を求める。

## 3. App終了後だけ実行する

`CODEX_HOME/backups`の下に一意で未作成のoutput directoryを使う。Windowsでは、Codex終了後も処理を継続できるようbundled waiterをhidden PowerShell processで起動する。

```powershell
Start-Process -FilePath powershell.exe -WindowStyle Hidden -ArgumentList @(
  '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$SkillRoot\scripts\wait_and_execute.ps1`"",
  '-Execute', '-CodexHome', "`"$CodexHome`"", '-BaselinePlan', "`"$BaselinePlan`"",
  '-OutputDir', "`"$OutputDir`"", '-Cutoff', "`"$Cutoff`""
)
```

userにtrayからCodexを完全終了し、cleanup完了後にappを再起動して同じtaskへ戻るよう伝える。waiterは`ChatGPT Classic`を無視し、`ChatGPT`、`codex`、`codex-code-mode-host`の終了を待つ。

Windows以外ではPowerShell waiterを使わず、すべてのCodex Desktop process終了を待つ外部processを用意するか、別terminalからexecutorを実行してもらう。

```text
python cleanup_stale_codex_sessions.py --root <CODEX_HOME> --cutoff <CUTOFF> --execute --ack-app-stopped --baseline <PLAN> --output-dir <NEW_OUTPUT_DIR>
```

app実行中に`--ack-app-stopped`を渡さない。

## 4. 再起動後に検証する

```powershell
python scripts/verify_cleanup.py --root "$CodexHome" --output-dir "$OutputDir"
```

以下をすべて通す。

- removed IDがexecution candidateと完全一致する
- protected/recent rowやfileが欠落していない
- live locationにcandidate fileやindex entryが残っていない
- quarantine pathとsizeがexecution planに完全一致する
- state、logs、backup hash検査が通る
- SQLite foreign-key errorが0
- VACUUM前後でlog row signatureが不変で、restart後のlog数は減少していない

removed thread row、quarantine中のtranscript bytes、DB前後size、backup path、主観的なprocess/memory改善を報告する。quarantine purge前にrecent workを1、2件開いてもらう。

## 5. 検証成功後だけquarantineをpurgeする

`verification.json`が`passed: true`で、recent sessionを正常に開け、userがfinal purgeを明示承認した後に実行する。

```powershell
python scripts/cleanup_stale_codex_sessions.py --root "$CodexHome" --purge-quarantine --ack-verified --output-dir "$OutputDir"
```

purgerはpathとsizeが一致するexact planned quarantine fileだけを削除する。unexpected file、changed file、verification artifact不一致、二重purgeは拒否する。purge後にverificationを再実行し、database/index backupはuserが別途削除を承認するまで保持する。

## Failure handling

- planning/preflightがtable、column、integrity、foreign keyの不足で失敗したら停止する。DBをその場しのぎでpatchしない。
- waiter失敗時はstatus、runner log、`FAILED.json`、backup、quarantineを確認する。同じoutput directoryで2回目を開始しない。
- metadata commit前の失敗では、moved transcriptとindexを自動復元する。
- metadata commit後の失敗では、backupとquarantineを保持してretry/restore前に診断する。
- purgeがquarantineを拒否したら保持して差異を調査し、delete scopeを広げない。
- cleanup成功後もappが遅い場合は、renderer/process数、app cache、extension/plugin、current-version supportを別途調査し、削除範囲を自動拡張しない。

## Bundled scripts

- `scripts/inspect_codex_state.py`: read-only aggregate inventoryと回収見積もり
- `scripts/cleanup_stale_codex_sessions.py`: guarded plan、destructive executor、exact verified purge
- `scripts/wait_and_execute.ps1`: Windows app-exit waiterとexecutor launcher
- `scripts/verify_cleanup.py`: backup-to-current post-restart auditとverification artifact
- `scripts/test_cleanup_stale_codex_sessions.py`: preflight、protection、rollback、quarantine、verification、purgeのdisposable integration tests
