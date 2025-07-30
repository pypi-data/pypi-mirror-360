# Minimal Client Usage Example

Middleman.ai の ToolsClient メソッドを直接使用する最小限のサンプルです。

## 必要条件

- Python 3.10 以上
- [uv](https://github.com/astral-sh/uv)

## セットアップ

1. 環境変数の設定:

```bash
export MIDDLEMAN_API_KEY="YOUR_API_KEY"
export MIDDLEMAN_PDF_TEMPLATE_ID="YOUR_TEMPLATE_ID"   # マークダウン to PDFのテンプレートIDを必要に応じて設定
export MIDDLEMAN_PPTX_TEMPLATE_ID="YOUR_TEMPLATE_ID"  # JSON to PPTXの機能を使用する場合sample_template.pptxをMiddleman.aiにアップロードしてそのIDを設定
```

2. 依存関係のインストール:

```bash
uv sync
```

## 使用方法

```bash
uv run main.py
```

各 API メソッドの呼び出し結果（生成されたファイルの URL）が表示されます。

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。
