# 合成成果物サンプル

[`estimator-synthetic-sample.xlsx`](estimator-synthetic-sample.xlsx) は、`codex-effort-estimator` が出力する workbook の構成と監査線を確認するための固定サンプルです。

すべて架空のデータです。実在する社名、個人名、メールアドレス、案件金額、顧客資料、秘密情報は使用していません。数値も表示確認用に固定した合成値であり、実案件の精度や一般的な優位性を示すものではありません。

## 確認できるもの

- `00_結論`: raw baseline と AI 支援後レンジの別掲
- `01_内訳`: 工程別の raw / adjusted / 差分 / 削減率
- `03_WBS`: 行別の三点見積もり、`AI削減区分`、判断根拠
- `10_AI補正`: 固定係数、行別補正、判断者と係数権限、raw baseline の監査線
- `18_親統合`: 独立baselineと従属するAI補正の区別
- `15_前提リスク`: 合成データ、機密除外、適用範囲、限界

固定期待値は raw `17.0 / 23.0 / 32.0` 人日、AI 支援後 `14.3 / 19.4 / 27.1` 人日です。workbook内の集計値は入力表を参照する数式で計算しています。

## 検証

`test_estimator_sample.py` は、XLSX packageの完全性、必須シート、数式、固定係数、合成データ表示、README導線、メール・token・private key・端末パス等の機密パターン不在を検査します。CIの `Validate estimator workbook sample` で実行します。
