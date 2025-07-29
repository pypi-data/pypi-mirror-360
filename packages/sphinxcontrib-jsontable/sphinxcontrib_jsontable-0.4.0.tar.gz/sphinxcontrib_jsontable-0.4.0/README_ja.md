# sphinxcontrib-jsontable

[![Tests](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml/badge.svg)](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable/graph/badge.svg)](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable)
[![Python](https://img.shields.io/pypi/pyversions/sphinxcontrib-jsontable.svg)](https://pypi.org/project/sphinxcontrib-jsontable/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/sasakama-code/sphinxcontrib-jsontable)

**言語:** [English](README.md) | [日本語](README_ja.md)

**JSONデータおよびExcelファイル**（ファイルまたはインラインコンテンツ）を美しくフォーマットされたreStructuredTextテーブルとしてレンダリングする強力なSphinx拡張機能です。構造化データ、APIサンプル、設定リファレンス、データ駆動型コンテンツを表示するドキュメントに最適です。

✨ **完全なExcel対応**: Excelファイル（.xlsx/.xls）を36+の高度な処理メソッドでレンダリング。シート選択、範囲指定、結合セル処理、自動範囲検出、階層ヘッダー、パフォーマンスキャッシュを含みます。

## 背景・動機

近年、Retrieval Augmented Generation（RAG）のデータソースとしてドキュメントを活用する傾向が強まっています。しかし、ドキュメント内の表形式データは、RAGシステムに取り込まれる過程で構造的な関連性を失うことが多く、元の構造化データが持つ価値を十分に活用できないという課題がありました。

このような背景から、JSONなどの構造化データをSphinxで生成されるドキュメントに直接、意味のあるテーブルとして埋め込むことで、可読性とデータソースとしての価値を効果的に両立させることを目的として、sphinxcontrib-jsontableが開発されました。

## 機能

✨ **柔軟なデータソース**
* Sphinxプロジェクト内のJSONファイルの読み込み
* **Excelファイル（.xlsx/.xls）の高度な処理による直接読み込み**
* ドキュメントに直接JSONを埋め込み
* 安全なパス解決機能付きの相対ファイルパス対応

📊 **複数のデータ形式**
* JSONオブジェクト（単一または配列）
* オプションヘッダー付きの2次元配列
* **複雑な構造を持つExcelスプレッドシート**
* 自動文字列変換機能付きの混合データ型
* ネストされたデータ構造（適切にフラット化）

📋 **Excel専用機能**
* **シート選択**: 名前またはインデックスで特定のシートを指定
* **範囲指定**: 特定のセル範囲からデータを抽出（A1:D10）
* **スマートヘッダー検出**: 自動ヘッダー行識別
* **結合セル処理**: 様々な戦略で結合セルを処理
* **行スキップ**: 柔軟なパターンで不要な行をスキップ
* **自動範囲検出**: インテリジェントなデータ境界検出
* **JSONキャッシュ**: パフォーマンス向上のためにデータをキャッシュ

🎛️ **カスタマイズ可能な出力**
* 自動キー抽出機能付きのオプションヘッダー行
* 大規模データセット用の行制限
* カスタムファイルエンコーディング対応
* レスポンシブテーブルフォーマット

🔒 **堅牢で安全**
* パストラバーサル攻撃防止
* 包括的なエラーハンドリング
* エンコーディング検証
* デバッグ用詳細ログ

⚡ **パフォーマンス最適化**
* 大量データセットの自動行制限（デフォルト10,000行）
* 設定可能なパフォーマンス制限
* メモリ安全な処理
* 大量データ検出時のユーザーフレンドリーな警告

## インストール

### UV使用（推奨）

**UVインストール:**
```bash
# UVパッケージマネージャーのインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# 新しいプロジェクト用
uv init my-sphinx-project
cd my-sphinx-project
uv add sphinxcontrib-jsontable

# Excel対応付き
uv add "sphinxcontrib-jsontable[excel]"
```

**開発環境:**
```bash
# リポジトリのクローンと開発環境セットアップ
git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
cd sphinxcontrib-jsontable
uv sync
uv run pytest
```

### PyPIから

**基本インストール（JSON対応のみ）:**
```bash
pip install sphinxcontrib-jsontable
```

**Excel対応付き:**
```bash
pip install sphinxcontrib-jsontable[excel]
```

**完全インストール（全機能）:**
```bash
pip install sphinxcontrib-jsontable[all]
```

### ソースから
```bash
git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
cd sphinxcontrib-jsontable
pip install -e .[excel]  # Excel対応付き
```

### 依存関係

**コア:** Python 3.10+、Sphinx 3.0+、docutils 0.18+

**Excel対応:** pandas 2.0+、openpyxl 3.1+

## クイックスタート

### 1. 拡張機能を有効化

`conf.py`に追加：

```python
extensions = [
    # ... その他の拡張機能
    'sphinxcontrib.jsontable',
]

# オプション: パフォーマンス制限を設定
jsontable_max_rows = 5000  # デフォルト: 10000
```

### 2. サンプルデータを作成

`data/users.json`を作成：
```json
[
  {
    "id": 1,
    "name": "田中太郎",
    "email": "tanaka@example.com",
    "department": "エンジニアリング",
    "active": true
  },
  {
    "id": 2,
    "name": "佐藤花子",
    "email": "sato@example.com", 
    "department": "マーケティング",
    "active": false
  }
]
```

### 3. ドキュメントに追加

**reStructuredText (.rst) でのJSON例：**
```rst
ユーザーデータベース
==================

.. jsontable:: data/users.json
   :header:
   :limit: 10
```

**reStructuredText (.rst) でのExcel例：**
```rst
売上データ分析
==============

.. jsontable:: data/sales_report.xlsx
   :header:
   :sheet: "Q1データ"
   :range: A1:E50
   :skip-rows: 2,4
   :merge-cells: expand
   :json-cache:
```

**高度なExcel処理:**
```rst
財務レポート
============

.. jsontable:: reports/financial.xlsx
   :sheet-index: 1
   :header-row: 2
   :detect-range: auto
   :merge-headers: 
   :limit: 100
```

**Markdown（myst-parser使用）の場合：**
````markdown
# ユーザーデータベース

```{jsontable} data/users.json
:header:
:limit: 10
```

# Excelセールスデータ

```{jsontable} data/quarterly_sales.xlsx
:header:
:sheet: サマリー
:header-row: 2
```
````

### 4. ドキュメントをビルド

```bash
sphinx-build -b html docs/ build/html/
```

## 包括的な使用ガイド

### データ形式サポート

#### オブジェクトの配列（最も一般的）

データベースレコード、APIレスポンス、設定リストに最適：

```json
[
  {"name": "Redis", "port": 6379, "ssl": false},
  {"name": "PostgreSQL", "port": 5432, "ssl": true},
  {"name": "MongoDB", "port": 27017, "ssl": true}
]
```

```rst
.. jsontable:: data/services.json
   :header:
```

**出力：** オブジェクトキー（name、port、ssl）から自動的にヘッダーを生成。

#### ヘッダー付き2次元配列

CSV形式のデータ、レポート、マトリックスに最適：

```json
[
  ["サービス", "ポート", "プロトコル", "状態"],
  ["HTTP", 80, "TCP", "アクティブ"],
  ["HTTPS", 443, "TCP", "アクティブ"],
  ["SSH", 22, "TCP", "非アクティブ"]
]
```

```rst
.. jsontable:: data/ports.json
   :header:
```

**出力：** 最初の行がテーブルヘッダーになります。

#### ヘッダーなし2次元配列

シンプルな表形式データ：

```json
[
  ["月曜日", "晴れ", "24°C"],
  ["火曜日", "曇り", "20°C"],
  ["水曜日", "雨", "17°C"]
]
```

```rst
.. jsontable:: data/weather.json
```

**出力：** すべての行がデータとして扱われます（ヘッダーなし）。

#### 単一オブジェクト

設定オブジェクト、設定、メタデータ：

```json
{
  "database_host": "localhost",
  "database_port": 5432,
  "debug_mode": true,
  "max_connections": 100
}
```

```rst
.. jsontable:: data/config.json
   :header:
```

**出力：** キーが1つの列、値が別の列になります。

## Excel対応ガイド

### Excelファイル処理

sphinxcontrib-jsontableは、複雑なスプレッドシート構造を処理する高度な機能を備えた包括的なExcelファイル対応を提供します。

#### 基本的なExcel使用

```rst
.. jsontable:: data/employees.xlsx
   :header:
```

#### シート選択

**シート名による選択:**
```rst
.. jsontable:: data/financial_report.xlsx
   :header:
   :sheet: 四半期結果
```

**シートインデックスによる選択（0ベース）:**
```rst
.. jsontable:: data/financial_report.xlsx
   :header:
   :sheet-index: 2
```

#### 範囲指定

**特定のセル範囲:**
```rst
.. jsontable:: data/large_dataset.xlsx
   :header:
   :range: A1:F25
```

**特定のセルから開始:**
```rst
.. jsontable:: data/data_with_headers.xlsx
   :header:
   :range: B3:H50
```

#### 高度なヘッダー設定

**カスタムヘッダー行:**
```rst
.. jsontable:: data/complex_report.xlsx
   :header:
   :header-row: 3
```

**不要な行をスキップ:**
```rst
.. jsontable:: data/messy_data.xlsx
   :header:
   :skip-rows: 0-2,5,7-9
```

#### 結合セル処理

**結合セルを展開:**
```rst
.. jsontable:: data/formatted_report.xlsx
   :header:
   :merge-cells: expand
```

**結合セルを無視:**
```rst
.. jsontable:: data/formatted_report.xlsx
   :header:
   :merge-cells: ignore
```

#### 自動範囲検出

**スマートデータ検出:**
```rst
.. jsontable:: data/unstructured.xlsx
   :header:
   :detect-range: auto
```

**手動オーバーライド:**
```rst
.. jsontable:: data/complex_layout.xlsx
   :header:
   :detect-range: manual
   :range: C5:J30
```

#### パフォーマンス最適化

**JSONキャッシュを有効化:**
```rst
.. jsontable:: data/large_workbook.xlsx
   :header:
   :json-cache:
```

### Excelオプション一覧

| オプション | 型 | 説明 | 例 |
|-----------|----|-----------|---------|
| `sheet` | 文字列 | 読み取るシート名 | `:sheet: セールスデータ` |
| `sheet-index` | 整数 | シートインデックス（0ベース） | `:sheet-index: 1` |
| `range` | 文字列 | セル範囲（A1:D10） | `:range: B2:F20` |
| `header-row` | 整数 | ヘッダー行番号（0ベース） | `:header-row: 2` |
| `skip-rows` | 文字列 | スキップする行 | `:skip-rows: 0-2,5,7-9` |
| `detect-range` | 文字列 | 自動検出モード | `:detect-range: auto` |
| `merge-cells` | 文字列 | 結合セル処理 | `:merge-cells: expand` |
| `merge-headers` | 文字列 | 複数行ヘッダー結合 | `:merge-headers: true` |
| `json-cache` | フラグ | キャッシュ有効化 | `:json-cache:` |
| `auto-header` | フラグ | 自動ヘッダー検出 | `:auto-header:` |

### 完全ディレクティブオプション

`jsontable`ディレクティブは最大限の柔軟性のため以下すべてのオプションをサポートします：

```rst
.. jsontable:: data.xlsx
   :header:              # ヘッダー行を含める
   :encoding: utf-8      # ファイルエンコーディング指定  
   :limit: 1000          # 表示行数制限
   :sheet: "データシート"  # シート名選択
   :sheet-index: 0       # シートインデックス選択（0ベース）
   :range: A1:E50        # セル範囲（Excel形式）
   :header-row: 1        # ヘッダー行番号（0ベース）
   :skip-rows: 2,4,6-10  # 特定行をスキップ
   :detect-range: auto   # データ範囲を自動検出（auto/smart/manual）
   :auto-header:         # 自動ヘッダー検出
   :merge-cells: expand  # 結合セル処理（expand/ignore/first-value）
   :merge-headers:       # 階層ヘッダー結合
   :json-cache:          # パフォーマンス向上のためJSONキャッシュ有効化
```

## 包括的な使用ガイド

### ディレクティブオプション一覧

| オプション | 型 | デフォルト | 説明 | 例 |
|------------|----|-----------|----|---|
| `header` | フラグ | off | 最初の行をテーブルヘッダーとして含める | `:header:` |
| `encoding` | 文字列 | `utf-8` | JSONファイルのファイルエンコーディング | `:encoding: utf-16` |
| `limit` | 正の整数/0 | 自動 | 表示する最大行数（0=無制限） | `:limit: 50` |

## 設定オプション

`conf.py`でsphinxcontrib-jsontableを設定：

### パフォーマンス設定

```python
# 自動制限が有効になる最大行数（デフォルト: 10000）
jsontable_max_rows = 5000

# 異なる用途向けの設定例:

# 主に小さなデータセット用のドキュメント
jsontable_max_rows = 100

# 大量データ用のドキュメント
jsontable_max_rows = 50000

# 自動制限を完全に無効化（Webデプロイには非推奨）
# jsontable_max_rows = None  # デフォルトで無制限使用
```

### 高度な例

#### 自動パフォーマンス保護

`:limit:`が指定されていない場合、拡張機能は自動的に大量データセットから保護します：

```rst
.. jsontable:: data/huge_dataset.json
   :header:

# データセットが10,000行を超える場合、自動的に最初の10,000行を警告付きで表示
# ユーザーには以下が表示されます: "大量データセット検出（25,000行）。パフォーマンスのため
# 最初の10,000行を表示。:limit:オプションでカスタマイズしてください。"
```

#### 明示的な無制限処理

サイズに関係なく全データを表示する必要がある場合：

```rst
.. jsontable:: data/large_but_manageable.json
   :header:
   :limit: 0

# ⚠️ 全行表示 - Webデプロイには注意が必要
```

#### ページネーション付き大規模データセット

大規模データセットでのパフォーマンスと可読性のため：

```rst
.. jsontable:: data/large_dataset.json
   :header:
   :limit: 100

.. note::
   このテーブルは50,000+件のうち最初の100エントリを表示しています。
   完全なデータセットをダウンロード：:download:`large_dataset.json <data/large_dataset.json>`
```

#### 非UTF8エンコーディング

レガシーシステムや特定の文字エンコーディングでの作業：

```rst
.. jsontable:: data/legacy_data.json
   :encoding: iso-8859-1
   :header:
```

#### サンプル用インラインJSON

APIドキュメント、サンプル、チュートリアルに最適：

```rst
APIレスポンス形式
================

ユーザーエンドポイントは以下の形式でデータを返します：

.. jsontable::

   {
     "user_id": 12345,
     "username": "tanaka_taro",
     "email": "tanaka@example.com",
     "created_at": "2024-01-15T10:30:00Z",
     "is_verified": true,
     "profile": {
       "first_name": "太郎",
       "last_name": "田中",
       "avatar_url": "https://example.com/avatar.jpg"
     }
   }
```

#### 複雑なネストされたデータ

ネストされたJSONの場合、拡張機能は適切にフラット化します：

```rst
.. jsontable::

   [
     {
       "id": 1,
       "name": "製品A",
       "category": {"name": "電子機器", "id": 10},
       "tags": ["人気", "セール"],
       "price": 99.99
     }
   ]
```

**注意：** 値内のオブジェクトと配列は文字列表現に変換されます。

### 統合例

#### Sphinx Tabsとの連携

sphinx-tabsと組み合わせて多形式ドキュメント作成：

```rst
.. tabs::

   .. tab:: JSONデータ

      .. jsontable:: data/api_response.json
         :header:

   .. tab:: 生JSON

      .. literalinclude:: data/api_response.json
         :language: json
```

#### コードブロックとの連携

リクエスト/レスポンス例でAPIエンドポイントを文書化：

```rst
ユーザー取得エンドポイント
========================

**リクエスト：**

.. code-block:: http

   GET /api/v1/users HTTP/1.1
   Host: api.example.com
   Authorization: Bearer <token>

**レスポンス：**

.. jsontable::

   [
     {
       "id": 1,
       "username": "alice",
       "email": "alice@example.com",
       "status": "active"
     },
     {
       "id": 2, 
       "username": "bob",
       "email": "bob@example.com",
       "status": "inactive"
     }
   ]
```

#### MyST Markdownでの使用

モダンなドキュメントワークフロー用の完全なMyST Markdownサポート：

````markdown
# 設定リファレンス

## データベース設定

```{jsontable} config/database.json
:header:
:encoding: utf-8
```

## 機能フラグ

```{jsontable}
[
  {"feature": "ダークモード", "enabled": true, "rollout": "100%"},
  {"feature": "新ダッシュボード", "enabled": false, "rollout": "0%"},
  {"feature": "高度な検索", "enabled": true, "rollout": "50%"}
]
```
````

### ファイル構成のベストプラクティス

#### 推奨ディレクトリ構造

```
docs/
├── conf.py
├── index.rst
├── data/
│   ├── users.json
│   ├── products.json
│   ├── config/
│   │   ├── database.json
│   │   └── features.json
│   └── examples/
│       ├── api_responses.json
│       └── error_codes.json
└── api/
    └── endpoints.rst
```

#### 命名規則

- 説明的なファイル名を使用：`data1.json`ではなく`user_permissions.json`
- 関連データをサブディレクトリにグループ化：`config/`、`examples/`、`test_data/`
- 適切な場合はバージョンや日付を含める：`api_v2_responses.json`

### パフォーマンス考慮事項

#### 大量データセットの自動保護

拡張機能は自動的にパフォーマンス問題から保護します：

- **デフォルト制限**: デフォルトで最大10,000行
- **スマート検出**: データセットサイズを自動推定
- **ユーザー警告**: 制限が適用された際の明確なメッセージ
- **設定可能**: `jsontable_max_rows`設定で制限を調整

#### パフォーマンス動作

| データセットサイズ | デフォルト動作 | 必要なユーザーアクション |
|-------------------|---------------|----------------------|
| ≤ 10,000行 | ✅ 全行表示 | なし |
| > 10,000行 | ⚠️ 自動制限+警告 | `:limit:`でカスタマイズ |
| `:limit: 0`指定時 | 🚨 全表示（無制限） | 注意して使用 |

#### ビルド時間の最適化

**小さなデータセット（< 1,000行）:**
```rst
.. jsontable:: data/small_dataset.json
   :header:
   # 制限不要 - 高速処理
```

**中規模データセット（1,000-10,000行）:**
```rst
.. jsontable:: data/medium_dataset.json
   :header:
   # 自動保護適用 - 良好なパフォーマンス
```

**大規模データセット（> 10,000行）:**
```rst
.. jsontable:: data/large_dataset.json
   :header:
   :limit: 100
   # 予測可能なパフォーマンスのため明示的制限を推奨
```

#### メモリ考慮事項

**安全な設定:**
```python
# 保守的（低メモリ環境向け）
jsontable_max_rows = 1000

# バランス型（デフォルト - ほとんどの用途に適用）
jsontable_max_rows = 10000

# アグレッシブ（高メモリ環境のみ）
jsontable_max_rows = 100000
```

**メモリ使用量ガイドライン:**
- **~1MB JSON**: ~1,000-5,000行（全環境で安全）
- **~10MB JSON**: ~10,000-50,000行（十分なメモリが必要）
- **>50MB JSON**: データ前処理またはデータベースソリューションを検討

#### 大量データのベストプラクティス

1. **適切な制限を使用**:
   ```rst
   .. jsontable:: data/sales_data.json
      :header:
      :limit: 50
      
   *上位50件の売上記録を表示。完全データはソースファイルで利用可能。*
   ```

2. **データ前処理を検討**:
   - 大きなファイルを論理的なチャンクに分割
   - ドキュメント用のサマリーデータセットを作成
   - 静的ファイルの代わりにデータベースビューを使用

3. **ビルドパフォーマンスの最適化**:
   ```python
   # conf.py内 - 大規模プロジェクトの高速ビルド
   jsontable_max_rows = 100
   ```

4. **制限されたデータのコンテキスト提供**:
   ```rst
   .. jsontable:: data/user_activity.json
      :header:
      :limit: 20
      
   .. note::
      このテーブルは最近のアクティビティのみ表示。完全ログは
      :doc:`admin-dashboard`参照、または
      :download:`完全データセット <data/user_activity.json>`をダウンロード。
   ```

### 移行ガイド

#### 以前のバージョンからのアップグレード

**破壊的変更なし**: 既存のドキュメントは変更なしで動作継続。

**利用可能な新機能**:
```rst
# 以前: 大量データセットには手動制限が必要
.. jsontable:: large_data.json
   :header:
   :limit: 100

# 以降: 自動保護（手動制限も継続サポート）
.. jsontable:: large_data.json
   :header:
   # ユーザー警告付きで自動的に10,000行に制限
```

**推奨設定更新**:
```python
# カスタマイズされた動作のためconf.pyに追加
jsontable_max_rows = 5000  # ニーズに応じて調整
```

## ⚠️ 破壊的変更のお知らせ

### ExcelDataLoader 削除（v0.4.0）- **完了**

**重要：** `ExcelDataLoader`クラスは非推奨化タイムラインに従って**v0.4.0で完全に削除**されました。すべてのExcel処理機能は、大幅なパフォーマンス向上と保守性の向上を実現するため、モダンなコンポーネントベースアーキテクチャを使用するようになりました。

#### 移行が必要 - **即座の対応が必要**

コード内で`ExcelDataLoader`を直接インポートしている場合、新しいAPIに**必ず**更新してください：

```python
# ❌ v0.4.0で削除 - ImportErrorが発生します
from sphinxcontrib.jsontable.excel_data_loader import ExcelDataLoader

# ✅ v0.4.0以降で必須 - 代わりにこちらを使用
from sphinxcontrib.jsontable.facade.excel_data_loader_facade import ExcelDataLoaderFacade
```

#### 移行のメリット

- **40%のパフォーマンス向上**: 9つの専門コンポーネントによるモダンなモジュラーアーキテクチャ
- **25%のメモリ削減**: ストリーミング対応の最適化処理パイプライン
- **型安全性の強化**: 包括的な型注釈とインターフェース
- **セキュリティ向上**: 高度な検証とエラーハンドリング
- **将来対応**: 非同期対応基盤とモダンなPythonパターン

#### 移行スケジュール - **完了**

- **v0.3.1**: 非推奨警告追加、両APIが動作
- **v0.4.0**（**現在**）: `ExcelDataLoader`完全削除、`ExcelDataLoaderFacade`のみ
- **v0.4.1+**: 完全なモダンAPI安定化進行中

#### 移行サポート

以下を含む包括的な[MIGRATION.md](MIGRATION.md)ガイドをご覧ください：
- **ステップバイステップの移行手順** とコード例
- **パフォーマンス比較チャート** による定量的改善の表示
- **完全なAPIマッピング** 旧メソッドから新メソッドへの対応
- **トラブルシューティングガイド** よくある移行問題の解決方法
- **自動移行ツール** より高速な変換のためのツール

#### クイック移行例

```python
# 旧版（v0.3.x）- v0.4.0でImportErrorが発生
from sphinxcontrib.jsontable.excel_data_loader import ExcelDataLoader
loader = ExcelDataLoader(base_path="./data", macro_security="strict")
result = loader.load_from_excel_with_range("file.xlsx", "A1:C10")

# 新版（v0.4.0+）- 必須の実装
from sphinxcontrib.jsontable.facade.excel_data_loader_facade import ExcelDataLoaderFacade
from sphinxcontrib.jsontable.security.security_scanner import SecurityScanner

security_scanner = SecurityScanner(macro_security="strict")
facade = ExcelDataLoaderFacade(security_validator=security_scanner)
result = facade.load_from_excel("./data/file.xlsx", range_spec="A1:C10")
```

#### ディレクティブの使用方法は変更なし

**重要**: `jsontable`ディレクティブの使用方法は**完全に変更されません**。この破壊的変更は直接PythonAPI使用にのみ影響します：

```rst
# これはv0.4.0でも全く同じように動作し続けます
.. jsontable:: data.xlsx
   :header:
   :sheet: "データ"
   :range: A1:E50
```

**📝 移行サポート**: 移行に関するサポートが必要な場合は、「migration」タグを付けて[GitHub Discussions](https://github.com/sasakama-code/sphinxcontrib-jsontable/discussions)をご利用ください。

### トラブルシューティング

#### 一般的な問題

**エラー：「No JSON data source provided」**
```rst
# ❌ ファイルパスまたはコンテンツが不足
.. jsontable::

# ✅ ファイルパスまたはインラインコンテンツを提供  
.. jsontable:: data/example.json
```

**エラー：「JSON file not found」**
- ソースディレクトリからの相対ファイルパスを確認
- ファイルが存在し、正しい権限があることを確認
- ファイル名のタイプミスがないことを確認

**エラー：「Invalid inline JSON」**
- オンラインバリデーターでJSON構文を検証
- 末尾カンマ、引用符なしキーをチェック
- 特殊文字の適切なエスケープを確認

**Excel固有エラー:**

**エラー：「Excel file not found」**
```rst
# ❌ 間違ったパス
.. jsontable:: data/missing_file.xlsx

# ✅ 正しいパスでファイルが存在
.. jsontable:: data/actual_file.xlsx
```

**エラー：「Invalid Excel file format」**
- ファイルに.xlsxまたは.xls拡張子があることを確認
- ファイルが破損していないことを確認
- ファイルが実際にExcelファイルかチェック（リネームされたCSVでない）

**エラー：「Sheet not found」**
```rst
# ❌ 存在しないシート名
.. jsontable:: data/report.xlsx
   :sheet: NonExistentSheet

# ✅ 有効なシート名またはインデックス
.. jsontable:: data/report.xlsx
   :sheet: Sheet1
```

**エラー：「Invalid range specification」**
```rst
# ❌ 無効な範囲形式
.. jsontable:: data/report.xlsx
   :range: Z99:AA1000

# ✅ 有効な範囲形式
.. jsontable:: data/report.xlsx
   :range: A1:F25
```

**エラー：「No data found in specified range」**
- 指定した範囲にデータが含まれているかチェック
- 範囲座標がシート境界内にあることを確認
- 範囲指定形式が正しいことを確認（A1:D10）

**パフォーマンス警告**
```
WARNING: 大量データセット検出（25,000行）。パフォーマンスのため最初の10,000行を表示。
```
**解決方法:**
- 明示的な`:limit:`オプション追加: `:limit: 50`
- 無制限に`:limit: 0`使用（必要時）
- グローバル制限増加: `jsontable_max_rows = 25000`
- より小さなファイル用のデータ前処理を検討

**エンコーディング問題**
```rst
# 非UTF8ファイルの場合
.. jsontable:: data/legacy.json
   :encoding: iso-8859-1
```

**空のテーブル**
- JSONファイルが空またはnullでないかチェック
- JSON構造を確認（配列またはオブジェクトである必要）
- 自動制限がデータを隠していないかチェック

#### デバッグモード

`conf.py`で詳細ログを有効化：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Sphinx固有のログの場合
extensions = ['sphinxcontrib.jsontable']

# パフォーマンス監視
jsontable_max_rows = 1000  # デバッグ用低制限
```

#### 設定テスト

セットアップを確認するシンプルなテストファイルを作成：

```json
[{"test": "success", "status": "ok"}]
```

```rst
.. jsontable:: test.json
   :header:
```

### セキュリティ考慮事項

#### パストラバーサル攻撃の防止

拡張機能は自動的にディレクトリトラバーサル攻撃を防止します：

```rst
# ❌ これはブロックされます
.. jsontable:: ../../etc/passwd

# ✅ 安全な相対パスのみ
.. jsontable:: data/safe_file.json
```

#### ファイルアクセス

- Sphinxソースディレクトリ内のファイルのみアクセス可能
- ネットワークURLや絶対システムパスは許可されません
- システムによってファイル権限が尊重されます

#### パフォーマンスセキュリティ

- デフォルト制限が偶発的なリソース枯渇を防止
- メモリ使用量は設定可能な制限で制約
- 大量データセット警告が意図しないパフォーマンス影響を防止

### 移行ガイド

#### 他の拡張機能から

**sphinx-jsonschemaから：**
- `.. jsonschema::`を`.. jsontable::`に置換
- スキーマ検証オプションを削除
- 必要に応じて`:header:`オプションを追加
- 自動パフォーマンス保護とキー順序保持の恩恵を享受

**カスタムソリューションから：**
- データをJSON形式またはExcel形式にエクスポート
- カスタムテーブル生成を`.. jsontable::`に置換
- ファイルパスをソースディレクトリ相対に更新
- Excelファイル用の高度な処理機能を活用

#### バージョン互換性

- **Sphinx：** 3.0+（推奨：4.0+）
- **Python：** 3.10+（推奨：3.11+）
- **Docutils：** 0.14+

## 開発者ドキュメント

### アーキテクチャ概要

sphinxcontrib-jsontableは、拡張性と保守性のために設計されたモジュラー、階層化アーキテクチャに従います：

```
┌─────────────────────────────────────────────────────────────┐
│                    Sphinx統合                               │
├─────────────────────────────────────────────────────────────┤
│              JsonTableDirective (メインエントリ)            │
├─────────────────────┬───────────────────────────────────────┤
│   JsonDataLoader    │        ExcelDataLoader               │
│   (JSON対応)        │        (Excel対応)                   │
├─────────────────────┴───────────────────────────────────────┤
│                   TableConverter                            │
│              (フォーマット非依存処理)                        │
├─────────────────────────────────────────────────────────────┤
│                    TableBuilder                             │
│                (Docutils統合)                               │
└─────────────────────────────────────────────────────────────┘
```

### APIリファレンス

#### コアクラス

**`JsonTableDirective`** (`sphinxcontrib/jsontable/directives.py:596`)
- メインのSphinxディレクティブクラス
- オプション解析と実行を処理
- データ読み込み、変換、レンダリングを調整
- **オプション**: Excel専用機能を含む13の総オプション

**`JsonDataLoader`** (`sphinxcontrib/jsontable/directives.py:112`)
- ファイルまたはインラインコンテンツからJSONを読み込み
- エンコーディングとファイルパスを検証
- パストラバーサル防止による安全なファイルアクセスを提供

**`ExcelDataLoader`** (`sphinxcontrib/jsontable/excel_data_loader.py`)
- 包括的なExcelファイル処理
- **メソッド**: `load_from_excel()`, `validate_excel_file()`, `header_detection()`
- **機能**: シート選択、範囲指定、結合セル処理
- **エラーハンドリング**: 多言語対応による強化されたエラークラス

**`TableConverter`** (`sphinxcontrib/jsontable/directives.py:204`)
- JSON/ExcelデータをJ2Dテーブル形式に変換
- 異なるデータ形式を処理（オブジェクト、配列、混合）
- ヘッダー抽出と行制限を管理
- 自動パフォーマンス制限を適用（デフォルト10,000行）

**`TableBuilder`** (`sphinxcontrib/jsontable/directives.py:403`)
- Sphinxレンダリング用のDocutilsテーブルノードを生成
- ヘッダー/ボディ付きの適切なテーブル構造を作成
- セルフォーマットとパディングを処理

#### Excel専用クラス

**強化されたエラークラス** (`excel_data_loader.py:29-143`)
```python
class EnhancedExcelError(Exception):
    """多言語対応による強化されたExcelエラーのベースクラス"""
    
class ExcelFileNotFoundError(EnhancedExcelError):
    """復旧提案付きのExcelファイル見つからないエラー"""
    
class ExcelFileFormatError(EnhancedExcelError):
    """ユーザーフレンドリーなガイダンス付きの無効なExcel形式エラー"""
```

#### オプション仕様

```python
option_spec = {
    # コアオプション
    "header": directives.flag,
    "encoding": directives.unchanged,
    "limit": directives.nonnegative_int,
    
    # Excel専用オプション  
    "sheet": directives.unchanged,
    "sheet-index": directives.nonnegative_int,
    "range": directives.unchanged,
    "header-row": directives.nonnegative_int,
    "skip-rows": directives.unchanged,
    "detect-range": directives.unchanged,
    "auto-header": directives.flag,
    "merge-cells": directives.unchanged,
    "merge-headers": directives.unchanged,
    "json-cache": directives.flag,
}
```

### テストフレームワーク

**テスト構成**:
```
tests/
├── excel/              # Excel専用テスト（18ファイル）
├── unit/               # コアコンポーネント単体テスト  
├── integration/        # コンポーネント間統合テスト
├── performance/        # パフォーマンス・ベンチマークテスト
└── coverage/           # カバレッジ専用テスト
```

**テスト実行**:
```bash
# 標準テスト実行
uv run python -m pytest

# Excel専用テスト
uv run python -m pytest tests/excel/

# パフォーマンステスト
uv run python -m pytest --benchmark-only
```

#### エラーハンドリング

すべてのエラーはドメイン固有のベースクラスから継承：
- `JsonTableError`：ベースエラークラス
- `EnhancedExcelError`：Excel専用強化エラー
- 復旧提案付きファイルアクセスエラー
- ユーザーガイダンス付き入力検証エラー

### コントリビューション

コントリビューションを歓迎します！詳細は[CONTRIBUTING.md](CONTRIBUTING.md)を参照：
- 開発環境セットアップ
- コードスタイルガイドライン
- テスト手順
- プルリクエストプロセス

#### 開発環境セットアップ

```bash
git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
cd sphinxcontrib-jsontable
pip install -e ".[dev]"
pytest
```

#### テスト実行

```bash
# 全テスト実行
pytest

# カバレッジ付き実行
pytest --cov=sphinxcontrib.jsontable

# 特定テスト実行
pytest tests/test_directives.py::test_json_table_basic
```

### 拡張開発

#### 新しいデータソースの追加

新しいデータ形式のサポートを追加するには、このパターンに従ってください：

1. **データローダークラスの作成**:
```python
class NewFormatDataLoader:
    def __init__(self, source_dir: str):
        self.source_dir = source_dir
        
    def load_from_format(self, file_path: str, **options) -> dict:
        """ロードしてJSON互換形式に変換"""
        # ここに実装
        return {"data": converted_data, "headers": headers}
```

2. **JsonTableDirectiveの更新**:
```python
def run(self) -> list[nodes.Node]:
    # 形式検出の追加
    if file_path.endswith('.newformat'):
        loader = NewFormatDataLoader(self.env.srcdir)
        result = loader.load_from_format(file_path, **options)
```

3. **オプション仕様の追加**:
```python
option_spec["new-option"] = directives.unchanged
```

#### パフォーマンス考慮事項

**メモリ管理**:
- 大規模データセットは自動的に制限（設定可能）
- Excelファイルのストリーミング処理
- パフォーマンス向上のためのJSONキャッシュ

**セキュリティ機能**:
- `is_safe_path()`によるパストラバーサル防止
- ソースディレクトリに制限されたファイルアクセス
- 全オプションの入力検証

### サンプルリポジトリ

[`examples/`](examples/)ディレクトリで以下を参照：
- 完全なSphinxプロジェクトセットアップ
- 様々なデータ形式の例  
- 他の拡張機能との統合
- 高度な設定例

```bash
cd examples/
sphinx-build -b html . _build/html/
```

### 開発ツール

[`scripts/`](scripts/)ディレクトリには、パフォーマンス機能開発時に使用された開発・分析ツールが含まれています：

- **`performance_benchmark.py`** - パフォーマンス測定・分析ツール
- **`memory_analysis.py`** - 異なるデータセットサイズのメモリ使用量分析
- **`competitive_analysis.py`** - 業界標準調査とベストプラクティス
- **`validate_ci_tests.py`** - CI環境テスト・検証
- **`test_integration.py`** - 包括的統合テスト

これらのツールは、パフォーマンス制限の科学的基盤確立と企業レベルの信頼性確保において重要な役割を果たしました。継続的なパフォーマンス監視と分析に活用できます。

```bash
# パフォーマンス分析実行
python scripts/performance_benchmark.py

# CI環境検証
python scripts/validate_ci_tests.py
```

### サンプルリポジトリ

[`examples/`](examples/)ディレクトリで以下を参照：
- 完全なSphinxプロジェクトセットアップ
- 様々なデータ形式の例（JSON、Excel） 
- 他の拡張機能との統合
- 高度な設定例

```bash
cd examples/
sphinx-build -b html . _build/html/
```

### 変更履歴

詳細なバージョン履歴とリリースノートは[CHANGELOG.md](CHANGELOG.md)を参照してください。

### ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下でライセンスされています。

### サポート

- **ドキュメント：** [GitHub Pages](https://sasakama-code.github.io/sphinxcontrib-jsontable/)
- **問題報告：** [GitHub Issues](https://github.com/sasakama-code/sphinxcontrib-jsontable/issues)
- **ディスカッション：** [GitHub Discussions](https://github.com/sasakama-code/sphinxcontrib-jsontable/discussions)
