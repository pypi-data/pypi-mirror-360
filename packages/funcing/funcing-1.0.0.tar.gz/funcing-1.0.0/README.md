# Funcing - Python向け簡単並列実行ライブラリ

Pythonの標準threadingを超簡略化＆エラー安全にした薄型並列実行ツール

## 🚀 なぜFuncing？

Pythonの`threading`モジュールは強力ですが、複雑になりがちです。Funcingは**超簡単**なAPIで並列実行を可能にし、自動エラーハンドリングを提供します。

```python
from funcing import run_in_parallel

def task1():
    return "Hello"

def task2():
    return "World"

# たったこれだけ！一行で並列実行
result = run_in_parallel([task1, task2])
print(result.results)  # ['Hello', 'World']
```

## ✨ 特徴

- **超簡単API**: `run_in_parallel([func1, func2])` だけ
- **エラー安全**: 自動例外処理とレポート機能
- **結果収集**: 全ての結果とエラーを一箇所で管理
- **タイムアウト対応**: 組み込みタイムアウト処理
- **依存関係ゼロ**: Python標準ライブラリのみ使用
- **包括的な統計**: 成功率、実行時間など詳細情報

## 📦 インストール

```bash
pip install funcing
```

## 🔥 クイックスタート

### 基本的な使い方

```python
from funcing import run_in_parallel

def fetch_data():
    # 何らかの処理をシミュレート
    import time
    time.sleep(1)
    return "データを取得しました"

def process_data():
    import time
    time.sleep(1)
    return "データを処理しました"

def save_data():
    import time
    time.sleep(1)
    return "データを保存しました"

# 全てのタスクを並列実行
result = run_in_parallel([fetch_data, process_data, save_data])

print(f"成功: {result.success_count}")  # 成功: 3
print(f"実行時間: {result.total_time:.2f}秒")   # 実行時間: ~1.00秒 (逐次実行なら3.00秒)
print(f"結果: {result.results}")        # 結果: ['データを取得しました', 'データを処理しました', 'データを保存しました']
```

### エラーハンドリング

```python
from funcing import run_in_parallel

def working_task():
    return "成功！"

def failing_task():
    raise ValueError("何かがうまくいきませんでした！")

result = run_in_parallel([working_task, failing_task])

print(f"成功: {result.success_count}")  # 成功: 1
print(f"エラー: {result.error_count}")       # エラー: 1
print(f"成功率: {result.success_rate:.1f}%")  # 成功率: 50.0%
print(f"全て成功: {result.all_successful}")   # 全て成功: False
```

### 引数付き関数

```python
from funcing import run_with_args

def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def greet(name, greeting="こんにちは"):
    return f"{greeting}、{name}さん！"

# 引数付き関数
pairs = [
    (add, (1, 2)),
    (multiply, (3, 4)),
    (greet, ("太郎",), {"greeting": "やあ"})
]

result = run_with_args(pairs)
print(result.results)  # [3, 12, 'やあ、太郎さん！']
```

### 高度なオプション

```python
from funcing import run_in_parallel

functions = [task1, task2, task3, task4, task5]

result = run_in_parallel(
    functions,
    timeout=30.0,           # 最大30秒
    max_workers=3,          # 3つのスレッドのみ使用
    return_exceptions=True  # エラーを収集（例外を発生させない）
)

print(f"{result.total_time:.2f}秒で完了")
print(f"成功率: {result.success_rate:.1f}%")
```

## 📊 結果オブジェクト

`FuncingResult`オブジェクトは包括的な情報を提供します：

```python
result = run_in_parallel([func1, func2, func3])

# プロパティ
result.results          # 成功した結果のリスト
result.errors           # 例外のリスト
result.success_count    # 成功した関数の数
result.error_count      # 失敗した関数の数
result.total_time       # 総実行時間
result.function_names   # 実行された関数の名前
result.success_rate     # 成功率（パーセント）
result.all_successful   # エラーが無い場合True
```

## 🎯 使用例

- **Webスクレイピング**: 複数のURLを同時に取得
- **API呼び出し**: 複数のAPIリクエストを並列実行
- **ファイル処理**: 複数のファイルを同時に処理
- **データベース操作**: 独立したクエリを並列実行
- **データ検証**: 複数の入力を同時に検証

## 🛡️ エラー安全性

Funcingはデフォルトでエラー安全に設計されています：

- 個別の関数の失敗が全体の実行をクラッシュさせない
- 元の例外による詳細なエラー報告
- タイムアウト処理でハングを防止
- 自動的なリソースクリーンアップ

## 🔧 高度な機能

### カスタムスレッドプールサイズ

```python
# I/O集約的なタスクには多くのスレッドを使用
result = run_in_parallel(io_functions, max_workers=50)

# CPU集約的なタスクには少ないスレッドを使用
result = run_in_parallel(cpu_functions, max_workers=4)
```

### タイムアウト処理

```python
# 全体の実行にタイムアウトを設定
result = run_in_parallel(functions, timeout=10.0)

if result.errors:
    print("いくつかの関数がタイムアウトしました！")
```

### 例外処理モード

```python
# 例外を収集（デフォルト）
result = run_in_parallel(functions, return_exceptions=True)

# 最初の例外で停止
try:
    result = run_in_parallel(functions, return_exceptions=False)
except Exception as e:
    print(f"実行失敗: {e}")
```

## 📜 ライセンス

MIT License - 詳細はLICENSEファイルをご覧ください。
