---
source: skills/codex-secure-ssh-doas-ops/SKILL.md
source_blob: df068532dc05a2ae9d19869c419a7bd5f77830b9
canonical: false
---

# codex-secure-ssh-doas-ops 日本語参考訳

この文書は `skills/codex-secure-ssh-doas-ops/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

SSH transport の自動化と privileged authentication を分離する。password は user が目視できる native SSH / doas prompt にだけ入力し、agent は password を受け取らず、中継もしない。

`codex-cloud-ops-intake` が operation を分類し、approval boundary を確立した後に使う。この Skill は承認済みの SSH / doas execution path だけを実行し、承認された target、command、effect の範囲を広げない。

## 例外を認めないルール

- upload、install、restart、target の編集など remote state を変更する task は、事前に承認を得る。
- user に password を chat へ貼るよう求めない。
- password を command arguments、environment variables、files、scripts、process launch arguments、`sshpass`、`plink -pw`、stdin pipe、captured output に入れない。
- private key の内容を読まない、表示しない、要約しない、copy しない。承認済み private-key path を `ssh` / `scp` に渡すことは許容する。
- public key を `authorized_keys` に追加することは永続的な security change として扱う。内容を説明し、実行前に承認を得る。
- 自動化のために広範な一時 `NOPASS` doas rule を作らない。透明性のある one-shot script を1回だけ対話的に elevate する方法を優先する。
- doas authentication が SSH session や TTY をまたいで保持されると仮定しない。
- host-key checking を維持する。便宜上 `StrictHostKeyChecking=no` を使わない。

## 1. 2つの authentication layer を分離する

SSH login と privilege elevation を別々に診断する。

最初に noninteractive SSH を確認する。

```powershell
ssh -i "<private-key-path>" `
  -o BatchMode=yes `
  -o ConnectTimeout=7 `
  -o StrictHostKeyChecking=yes `
  <user>@<host> hostname
```

結果の解釈:

- 成功: SSH automation を利用できる。doas probe へ進む。
- `Permission denied`: public key が受け入れられていない。後述の public-key registration を使うか、user に interactive SSH session を操作してもらう。
- Host-key error: 停止し、想定する fingerprint または known-host entry と照合する。check を迂回しない。

prompt を出さずに doas を probe する。

```powershell
ssh -tt -i "<private-key-path>" `
  -o BatchMode=yes `
  -o StrictHostKeyChecking=yes `
  <user>@<host> "doas -n true"
```

結果の解釈:

- 成功: この command は noninteractive elevation が許可されている。
- `a tty is required`: privileged execution では `ssh -tt` を使う。
- `Authentication required`: key-based SSH は維持し、user が doas password を入力できる visible terminal を用意する。

## 2. Login password を露出させず key-based SSH を確立する

既存の dedicated key を優先する。必要なら key filename は一覧してよいが、private key は開かない。

remote host が key を受け入れない場合、public key だけを native SSH prompt に pipe する local command を user に実行してもらう。これが `authorized_keys` を永続的に変更することを伝える。

PowerShell の例:

```powershell
Get-Content "<public-key-path>" |
  ssh <user>@<host> 'umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys; chmod 700 ~/.ssh; chmod 600 ~/.ssh/authorized_keys'
```

SSH password は user が local prompt に入力する。agent は password を見ない。その後、`BatchMode=yes` probe を再実行する。

public key の永続登録が承認されない場合は、credential workaround を考案しない。最終的な interactive SSH command を user 自身に実行してもらう。

## 3. 透明性のある one-shot privileged script を作る

doas が password を必要とする場合、何度も prompt を発生させず、承認済みの privileged work を review 可能な1本の script にまとめる。

script は以下を満たすこと。

- `set -eu` で開始する。
- mutation 前に expected hostname、required files、service state、safety gates を assert する。
- sensitive target には明示的な absolute path を使う。
- verification に不要な secrets や configuration contents を読んだり表示したりしない。
- target が対応する場合は、永続化前に安全に stage する。
- user が明示的に承認しない限り、危険な capability は無効のままにする。
- integrated result を verify する。
- すべての必須 step が成功した後だけ success marker を書く。

例:

```sh
#!/bin/sh
set -eu

SUCCESS_MARKER=/tmp/example-deploy-success
rm -f "$SUCCESS_MARKER"

[ "$(hostname)" = "<expected-hostname>" ]
[ -f "<required-file>" ]

# Authorized install or maintenance steps go here.

<service-status-check>
date -Is > "$SUCCESS_MARKER"
echo "Deployment completed"
```

task-specific script は `apply_patch` で作り、local で syntax を validate し、SHA-256 hash を記録する。unprivileged SSH user として mode 0700 の dedicated staging directory に upload し、起動前に remote hash を照合する。multi-user host では、誰でも書き込める `/tmp` script を root として実行しない。script に password や secret を埋め込まない。

## 4. User が制御できる visible terminal で doas を実行する

user が password prompt を確認・操作できるよう、native visible terminal を使う。Windows では、interactive case に限り `Start-Process` で PowerShell を起動してよい。

elevated remote command は、構造的に以下と同等にする。

```powershell
ssh -tt -i "<private-key-path>" `
  -o BatchMode=yes `
  -o ConnectTimeout=7 `
  -o StrictHostKeyChecking=yes `
  <user>@<host> "doas sh /tmp/<one-shot-script>.sh"
```

multi-user target では、例の `/tmp` path を検証済み private staging path に置き換える。hash mismatch、unexpected owner、permissive mode は stop condition とする。

terminal を開く前に、user へ以下を伝える。

- どの window が開くか。
- 表示される prompt が remote doas prompt であること。
- password は chat ではなく、その window に入力すること。
- agent から入力内容は見えないこと。

GUI や visible-terminal mechanism がない場合は、exact command を user に渡して confirmation を待つ。password capture へ切り替えない。

## 5. 別の key-based channel から完了を観測する

interactive terminal を credential のために scrape せず、process exit だけにも依存しない。すでに動作している key-based SSH connection から、secret を含まない success marker を poll する。

```powershell
ssh -i "<private-key-path>" `
  -o BatchMode=yes `
  -o StrictHostKeyChecking=yes `
  <user>@<host> "test -f /tmp/<success-marker>"
```

待機中は以下に従う。

- interactive authentication がまだ進行中の可能性を伝える。
- 適度な interval で poll する。
- marker が現れない場合は、secret を含まない service state と process liveness だけを確認する。
- visible terminal が閉じただけで成功と判断しない。

marker が現れた後、acceptance criteria を独立して verify する。対象には service status、network state、process liveness、persistence、safety gates、uptime、範囲を限定した recent logs を含める。

## 6. 追加の elevation を安全に扱う

verification により別の privileged change が必要になった場合:

1. evidence と、提案する狭い remediation を説明する。
2. 2本目の小さく review 可能な script を作る。
3. validate して upload する。
4. 新しい visible `ssh -tt ... doas sh ...` session を開く。
5. 再度 password prompt が出ることを前提にする。
6. 別の success marker を poll し、再 verify する。

password を再利用または cache せず、2回目の prompt を避けるために doas policy を広げない。

## 7. きれいに終了する

- operation 専用に作成した local temporary script を削除する。
- 安全で承認済みなら、remote unprivileged temporary files を削除する。root-owned `/tmp` marker は、削除のためだけに不要な elevation が必要なら reboot まで残してよい。
- output が review に有用なら user の visible terminal は開いたままにし、確認後に閉じてよいと伝える。
- 何を変更したか、何を verify したか、どの safety gate が無効のままか、残存 issue を報告する。
- readiness を正直に分類する。install 成功後の verification で external HTTP、DNS、network、application failure が見つかった場合、その問題は消えたことにしない。
