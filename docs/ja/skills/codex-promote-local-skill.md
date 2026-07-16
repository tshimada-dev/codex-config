---
source: skills/codex-promote-local-skill/SKILL.md
source_blob: 77253b758c21b60869d893480750bef2353c9431
canonical: false
---

# codex-promote-local-skill 日本語参考訳

この文書は `skills/codex-promote-local-skill/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

リポジトリ外のlocal Skillを一貫した基準で評価し、repository管理へ昇格する場合の変更、commit、install、旧Skill削除を回復可能かつ監査可能にする。

## 共有開発契約

`rules/development-workflow.md`に従う。repository evidenceには`codex-repo-scout`、永続的な変更には`codex-implementation-loop`、stageとcommit readinessには`codex-pr-readiness`を使う。Skillの新規作成や大幅な再構成では`$skill-creator`を使う。

## Authority mode

userの依頼を変更前に分類する。

- `assess`: `promote`、`merge`、`keep-local`を評価・報告するだけで、編集、commit、install、rename、deleteを行わない。
- `promote`: repository管理Skillを実装してcommitするが、依頼されていなければinstallやlocal source削除を行わない。
- `full-migration`: 完全なworkflowを明示依頼された場合、評価、実装、commit、commitからのinstall、verify、旧Skill削除まで行う。

評価依頼だけから永久削除の権限を推測しない。

## Safety invariant

- original local Skillは、最終削除がverify・承認されるまでuser-ownedとして扱う。
- `.env`、credential、private key、auth fileなどの内容をinspect・reportしない。
- symbolic link、junction、sensitive-looking file、unexpected fileは追跡・copy・deleteせず拒否する。
- `__pycache__`、`.pyc`、`.DS_Store`、`Thumbs.db`などruntime noiseをrepositoryへ入れない。
- install前にcommitし、repository `HEAD`のtracked contentだけをinstallする。
- 旧Skillは最後に削除する。installed tree、managed manifest、commit、original snapshotのいずれかが一致しなければ削除しない。
- unrelated dirty-worktree changeと無関係なSkillを保持する。

## 1. Local sourceをsnapshotする

repository、`CODEX_HOME`、source Skill、repository target、installed targetのabsolute pathを解決する。snapshotはsource Skill外かつtracked repository path外へ保存する。

```powershell
python scripts/audit_skill_promotion.py snapshot `
  --path "$OldSkill" `
  --output "$AuditSnapshot"
```

snapshotはfile内容を公開せず、relative path、size、hash、sensitive-looking path名を記録する。sensitive-looking pathやunsupported linkがあれば停止する。promotionを通すために実在source fileを黙って除外しない。

## 2. 管理価値を判定する

`codex-repo-scout`でlocal Skillとrepository Skillのdescription、role、dependency、script、testを比較する。

次を満たす場合に`promote`を選ぶ。

- 一時的な単発taskを超えて再利用可能
- private data、secret、偶発的な端末状態へ依存しない
- repositoryでの保守、配布、version historyに価値がある
- distinct triggerを持ち、既存Skillと実質重複しない
- deterministic testか明示的なcredible checkを用意できる
- authorityとfailure ruleでoperation riskを限定できる

既存Skillが同じtriggerやworkflowを所有し、有用部分を一貫性を壊さず吸収できる場合は`merge`を選ぶ。

personal、ephemeral、secret-bearing、machine-specific、保守するには狭すぎる、独立してtestできない場合は`keep-local`を選ぶ。

判定とevidenceを報告する。`assess` modeではここで停止する。

## 3. Promotionまたはmergeを実装する

promotionでは次を行う。

1. 64文字未満の簡潔な`codex-*`名を選ぶ。convention、trigger、collision回避を改善する場合だけrenameする。
2. `$skill-creator`で新Skillをscaffoldし、original local directoryをmove・mutationしない。
3. essential instruction、script、reference、assetだけを移行する。absolute machine pathとpersonal assumptionはparameterかdocumented prerequisiteへ置き換える。
4. `agents/openai.yaml`を追加・更新する。
5. scriptと壊れやすいworkflow ruleへfocused testを追加する。
6. `config/development-skills.json`、関連CI、`docs/ja/skills/<skill-name>.md`、`docs/ja/README.md`へ統合する。
7. `scripts/check-ja-source-commits.ps1 -Update`で日本語source metadataを更新する。

mergeでは`codex-implementation-loop`を通じて所有Skillを編集し、regression evidenceを追加して、重複Skillを作らない。

## 4. Install前にverifyしてcommitする

`quick_validate.py`、focused test、repository workflow validation、installer dry run、Copilot packaging、日本語metadata検査を必要に応じて実行する。

`codex-pr-readiness`でscoped diffをreviewし、promotion fileだけをstageする。installed targetへ触れる前にcommitする。uncommittedまたはpartially stagedなSkill treeからinstallしない。

## 5. Commit済みSkillをinstallする

repository installerを最初に`-WhatIf -Overwrite`で実行する。planned overwriteがpromoted Skillとmanaged manifestだけの場合に続行し、無関係なmanaged fileが変更される場合は停止する。

```powershell
pwsh -NoProfile -File "$RepoRoot/scripts/install.ps1" `
  -CodexHome "$CodexHome" -Overwrite
```

commit済みrepository tree、installed tree、managed manifestをverifyする。

```powershell
python scripts/audit_skill_promotion.py verify-install `
  --repo-root "$RepoRoot" `
  --skill-name "$SkillName" `
  --codex-home "$CodexHome"
```

local sourceが最初からfinal Skill名だった場合はin-place promotionとして扱い、別の旧directory削除を行わない。

## 6. Rename前の旧Skillを最後に削除する

`full-migration` modeで旧Skill削除が明示承認されている場合だけ進む。assessment以降old sourceが変わっておらず、installed targetがcommit済みSkillと完全一致することを確認する。

```powershell
python scripts/audit_skill_promotion.py verify-removal `
  --repo-root "$RepoRoot" `
  --skill-name "$SkillName" `
  --codex-home "$CodexHome" `
  --old-skill-path "$OldSkill" `
  --source-snapshot "$AuditSnapshot"
```

`ready_for_old_skill_removal: true`を必須とする。old pathを再解決し、`CODEX_HOME/skills`のdirect childで、installed targetと異なり、監査pathと完全一致することを確認する。そのliteral directoryだけをplatform-native commandで削除する。Windowsではpath検証と`Remove-Item -LiteralPath -Recurse -Force`を同じPowerShell process内で行う。

削除後はold directory不在、`verify-install`成功、unexpected repository change不在を確認し、commit、installed file数、削除したold path、保持したunrelated worktree stateを報告する。

## Failure handling

- snapshot後にsourceが変化したら停止し、変更をreviewしてからreplacement snapshotを作る。
- 管理価値が不明なら`keep-local`か`merge`を優先し、local directoryをすべてrepositoryへmirrorしない。
- testかrepository validationが失敗したらcommit・installしない。
- installがcommit済みtreeやmanifestと異なる場合は両Skillを保持して診断する。
- removal verificationが失敗したら旧Skillを保持し、delete scopeを広げない。

## Bundled script

- `scripts/audit_skill_promotion.py`: content-blind source snapshot、committed-install verification、旧Skill削除準備の完全監査
- `scripts/test_audit_skill_promotion.py`: sensitive path、runtime noise、tree mismatch、manifest coverage、source preservationのdisposable regression test
