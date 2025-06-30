# トラブルシューティング・FAQ

## 🚀 正しい実行順序

### 完全なセットアップ手順

```bash
# 1. セットアップ実行
./setup.sh

# 2. APIキー設定
nano .env

# 3. 仮想環境有効化
source graphrag-env/bin/activate

# 4. スクリプト実行
python graphrag_script.py
```

### 期待される出力

```
🚀 Starting GraphRAG Generator...
✅ .env file found
✅ OpenAI API key loaded from .env
Choose LLM provider (openai/google) [openai]:
✅ Using OpenAI API key from .env file
✅ Successfully connected to Memgraph!
🔄 Generating knowledge graph from text...
```

## ❓ よくある質問

### Q: Memgraph のユーザーネームとパスワードはどこで設定しますか？

**A: 設定は不要です。**

このプロジェクトでは、開発環境用に Memgraph の認証を無効にしています：

- ✅ ユーザーネーム・パスワードは空文字列のまま
- ✅ アカウント登録やサインアップは不要
- ✅ そのまま接続できます

### Q: なぜ.env に API キーがあるのに入力を求められるのですか？

**A: 修正済みです。**

最新版では `load_dotenv()` で .env ファイルを自動読み込みします。もし問題が発生する場合は：

```bash
# 仮想環境を再有効化
source graphrag-env/bin/activate

# 環境変数を確認
echo $OPENAI_API_KEY
```

### Q: OpenAI と Google Generative AI、どちらを選べばいいですか？

**A: どちらでも同じ結果が得られます。**

- **OpenAI (GPT-4o-mini)**: より安定した結果、豊富なドキュメント
- **Google Generative AI (Gemini)**: コストが安い場合がある

### Q: 日本語のテキストでも動作しますか？

**A: はい、動作します。**

LLM が日本語テキストからエンティティと関係性を抽出し、自然言語での質問も日本語で可能です。

## 🐛 エラーとその解決方法

### "Failed to connect to Memgraph"エラー

**解決方法:**

1. Docker が起動していることを確認:

   ```bash
   docker ps
   ```

2. Memgraph コンテナが実行中か確認:

   ```bash
   ./memgraph.sh status
   ```

3. Memgraph を再起動:

   ```bash
   ./memgraph.sh restart
   ```

4. ポート競合の確認:
   ```bash
   lsof -i :7687
   ```

### "allow_dangerous_requests" エラー

**エラーメッセージ:**

```
Error: In order to use this chain, you must acknowledge that it can make dangerous requests by setting `allow_dangerous_requests` to `True`.
```

**解決方法:** 修正済みです。LangChain v0.1 以降のセキュリティアップデートに対応済み。

### パッケージのインストールエラー

**解決方法:**

```bash
# 仮想環境を再作成
rm -rf graphrag-env
python3 -m venv graphrag-env
source graphrag-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### API キーが認識されない

**解決方法:**

1. `.env`ファイルの確認:

   ```bash
   cat .env
   ```

2. API キーに余分なスペースや改行がないか確認

3. 環境変数の確認:
   ```bash
   echo $OPENAI_API_KEY
   echo $GOOGLE_API_KEY
   ```

### Jupyter Notebook が起動しない

**解決方法:**

```bash
# 仮想環境を有効化
source graphrag-env/bin/activate

# Jupyter Labを再インストール
pip install --upgrade jupyterlab

# 別のポートで起動
jupyter lab --port=8889
```

## 🔧 Memgraph 管理

### Memgraph の状態確認

```bash
./memgraph.sh status
```

### Memgraph が停止している場合

```bash
./memgraph.sh start
```

### Memgraph の再起動

```bash
./memgraph.sh restart
```

### Memgraph データのクリア

```bash
./memgraph.sh stop
./memgraph.sh start
```

## 🔄 実行フロー

```
1. setup.sh 実行
   ↓
2. Memgraph 自動起動
   ↓
3. .env ファイル編集 (APIキー設定)
   ↓
4. 仮想環境有効化
   ↓
5. graphrag_script.py 実行
   ↓
6. .env からAPIキー自動読み込み
   ↓
7. Memgraph に接続
   ↓
8. GraphRAG システム起動
```

## 💡 使用のヒント

### 独自のデータを使用したい場合

1. `create_sample_data()` 関数内のテキストデータを変更
2. エンティティタイプを適切に調整
3. few-shot の例を自分のドメインに合わせて修正

### パフォーマンスを向上させたい場合

- `temperature=0` で LLM の出力を安定化
- より具体的な few-shot 例を追加
- プロンプトをドメイン特化型に調整

### グラフを視覚化したい場合

Memgraph Lab (http://localhost:3000) で以下のクエリを実行：

```cypher
MATCH (n)-[r]->(m) RETURN n,r,m
```

## 🛡️ セキュリティについて

### `allow_dangerous_requests=True` について

**なぜ必要？**

- Cypher クエリは強力で、データベースの全データを削除することも可能
- LangChain がセキュリティリスクを明示するため

**安全性**

- このプロジェクトはローカル開発環境用
- 機密データは扱わない想定
- 適切なスコープのデータベース権限を使用

**本番環境では**

- より制限的なデータベース権限を設定
- 入力検証の強化
- 監査ログの実装を推奨

## 🛠️ トラブルシューティングフロー

```
問題発生
   ↓
1. Memgraph状態確認: ./memgraph.sh status
   ↓
2. 停止している場合: ./memgraph.sh start
   ↓
3. .envファイル確認: cat .env
   ↓
4. 仮想環境確認: source graphrag-env/bin/activate
   ↓
5. 再実行: python graphrag_script.py
```

## 🔧 修正履歴

### 修正された主要な問題

1. **`.env`ファイル読み込み**: `load_dotenv()` 追加
2. **LangChain セキュリティエラー**: `allow_dangerous_requests=True` 追加
3. **GPT-4-turbo 構造化出力警告**: モデルを `gpt-4o-mini` に変更

これらの修正により、エラーなく動作するようになっています。
