# Research: Wikipedia RAG System

**Date**: 2025-11-02
**Feature**: 001-wikipedia-rag-system
**Status**: Completed

## Executive Summary

このリサーチは、Wikipedia RAGシステムの実装に必要な技術選定を行い、月額$50以下の予算制約内で運用可能な構成を提案します。主要な推奨事項:

- **LLMプラットフォーム**: Ollama (デプロイの簡便性と管理性)
- **ベクトルDB**: FAISS (S3互換性と高速検索)
- **IaCツール**: AWS CDK (AWS特化と開発者体験)
- **埋め込みモデル**: all-MiniLM-L6-v2 (速度とコストのバランス)
- **推定月額コスト**: $35-45 (予算内)

## Decision 1: LLM Platform - Ollama

### Rationale

Ollamaを推奨します。以下の理由により、このプロジェクトに最適です:

**1. デプロイの簡便性**
- シングルコマンドでのセットアップが可能
- 自動的なモデル管理とハンドリング
- 設定の複雑さを排除し、数時間でデプロイ可能
- EC2インスタンスでの起動が容易

**2. パフォーマンス特性**
- llama.cppをベースとした最適化されたC++実装
- 最大化された推論速度 (制御環境で平均70ms/リクエスト)
- GGUF形式サポートで4-bit〜16-bit量子化に対応
- 動的KV-cacheとGPU/CPU加速 (CUDA、Metal、OpenCL)

**3. プライバシー重視のアプリケーションに最適**
- ローカル実行が容易
- 外部API呼び出し不要
- Constitution原則II「Privacy First」に完全準拠

**4. 開発者体験**
- 直感的なAPIとコマンドライン
- LangChainとの良好な統合
- Pythonバインディングが充実
- MITライセンスでオープンソース

### Alternatives Considered

**Llama.cpp (却下理由)**

Llama.cppは以下の特性を持ちますが、Ollamaと比較して運用上の課題があります:

- **利点**:
  - より細かいカスタマイズが可能
  - わずかに高速 (制御環境で平均50ms/リクエスト)
  - 最大限の制御と柔軟性

- **欠点**:
  - 手動での設定が必要
  - モデル管理を自分で実装する必要がある
  - デプロイの学習曲線が急峻
  - 開発コストと時間が増加

**判断**: このプロジェクトは個人開発で迅速なデプロイを重視するため、Ollamaの簡便性が優先されます。パフォーマンス差(20ms)は、Success Criteria SC-002の2秒応答時間に対して無視できます。

### Recommended Model

**Llama 3.2 3B Instruct (Q4量子化)**

- **モデルサイズ**: 約1.8GB (Q4量子化)
- **パラメータ数**: 3B
- **メモリ要件**: 約2-3GB RAM (推論時)
- **推論速度**: ARM CPUで約19.92 tokens/sec (最適化カーネル使用時)
- **コンテキスト長**: 8K tokens

**選定理由**:
1. t4g.mediumインスタンス (4GB RAM) で快適に動作
2. Q4量子化により、精度を維持しながらメモリ使用量を削減
3. CPU推論に最適化されており、GPU不要でコスト削減
4. 英語Wikipediaコンテンツに十分な品質を提供
5. 小規模モデルながら、2秒以内の応答時間目標を達成可能

**代替オプション**:
- Llama 3.2 1B: より小規模だが、品質面で妥協の可能性
- Llama 3.1 8B: より高品質だが、メモリ要件が高く、より大きなインスタンスが必要

## Decision 2: Vector Database - FAISS

### Rationale

FAISSを推奨します。以下の理由により、このプロジェクトの要件に最適です:

**1. 高速検索パフォーマンス**
- Facebook AI Researchが開発した高性能ライブラリ
- 大規模ベクトル検索に最適化
- 数百万ベクトルでも効率的な類似検索
- CPUとGPU両方の加速をサポート

**2. S3互換性とストレージ**
- ファイルベースの永続化メカニズム
- S3への保存と読み込みが容易
- インデックスファイルのシリアライズ/デシリアライズが簡単
- Constitution原則III「Cost Efficiency」に適合 (データベース不要)

**3. LangChainとの統合**
- `langchain-community`パッケージで完全サポート
- `FAISS.from_documents()`などの便利なメソッド
- Pythonで簡単に利用可能
- 成熟したコミュニティとドキュメント

**4. メモリフットプリント**
- インメモリ動作で高速
- 必要に応じてディスクベースのインデックスも可能
- 50KBのWikipedia記事で推定500-1000ベクトル
- 384次元 (all-MiniLM-L6-v2使用時) で約1-2MB/記事

**5. ライセンスとコスト**
- MITライセンス、完全無料
- 追加のホスティングコスト不要
- シンプルな依存関係

### Alternatives Considered

**Chroma (却下理由)**

Chromaは以下の特性を持ちますが、このプロジェクトには過剰です:

- **利点**:
  - 開発者フレンドリーなAPI
  - プロトタイピングに最適
  - データベース機能を内蔵 (永続化、メタデータ管理)
  - S3などのオブジェクトストレージをサポート

- **欠点**:
  - データベース機能がこのプロジェクトには不要
  - FAISSと比較して検索速度で劣る可能性
  - 追加の複雑性 (クライアント-サーバーアーキテクチャオプション)
  - より重いランタイム

**判断**: このプロジェクトはシンプルなRAGセッション管理のみを必要とし、S3でのファイルベース保存で十分です。FAISSの高速検索とシンプルさが、Chromaの追加機能より優先されます。

### Implementation Notes

**推奨構成**:
```python
# IndexFlatL2 または IndexIVFFlat を使用
# 小規模データセット: IndexFlatL2 (完全精度)
# 中規模以上: IndexIVFFlat (速度と精度のトレードオフ)
```

**S3統合パターン**:
1. RAG構築時: ローカルでFAISSインデックス作成 → S3へアップロード
2. クエリ時: S3からダウンロード → メモリにロード → 検索実行

## Decision 3: Infrastructure as Code - AWS CDK

### Rationale

AWS CDKを推奨します。以下の理由により、このプロジェクトに最適です:

**1. AWS特化の利点**
- AWS サービスとのシームレスな統合
- Lambda、API Gateway、DynamoDB などの定義が容易
- CloudFormationの抽象化により高レベルの構造を提供
- AWS ベストプラクティスの組み込み

**2. 開発者体験**
- Python 3.11+ を使用可能 (Constitution準拠)
- アプリケーションコードと同じ言語で IaC を記述
- IDEのコード補完、型チェック、リンティングのサポート
- ユニットテストフレームワークとの統合

**3. Lambda デプロイの簡便性**
- Lambdaソースコードのパスをマッピングするだけで自動パッケージング
- `lambda.Function` コンストラクトで簡単にデプロイ
- 追加のzipパッケージング手順が不要
- インフラとアプリのコードを統合管理可能

**4. 高レベル抽象化**
- ボイラープレートコードを削減
- サーバーレスアプリケーション (Lambda、API Gateway、DynamoDB) の一般的なパターン向け
- 複雑なセットアップを数行で実現

**5. 学習リソースとコミュニティ**
- 豊富なドキュメントとサンプルコード
- 活発なコミュニティとGitHub リポジトリ
- AWS公式サポート

### Alternatives Considered

**Terraform (却下理由)**

Terraformは以下の特性を持ちますが、このプロジェクトには以下の理由で不適切です:

- **利点**:
  - クラウド中立的 (マルチクラウド対応)
  - 宣言的なHCL構文
  - 明示的なステート管理
  - 成熟したエコシステムとプロバイダー
  - チームコラボレーションツールが充実

- **欠点**:
  - Lambdaデプロイに追加のzipパッケージング手順が必要
  - S3にソースコードを配置する代替手法も追加ステップが必要
  - EC2のuser-dataスクリプト変更時に新しいインスタンスを作成しない (CDKは作成)
  - Python開発者が新たにHCLを学習する必要がある
  - 高レベル抽象化が少ない

**判断**:
- このプロジェクトはAWS専用 (マルチクラウド不要)
- Python開発者がPythonでインフラを記述できる利点が大きい
- Lambda中心のアーキテクチャでCDKの簡便性が活きる
- Constitution原則IV「Infrastructure as Code」の要件を満たす

### Implementation Notes

**推奨アプローチ**:
1. 単一のCDKアプリケーションでスタック管理
2. 開発環境とプロダクション環境で環境分離
3. `cdk.json` でコンテキスト値を設定
4. GitHubリポジトリ内の `infrastructure/` ディレクトリに配置

## Decision 4: Embedding Model

### Rationale

**all-MiniLM-L6-v2** を推奨します。

このモデルは速度、品質、コストのバランスが最適です:

**1. 高速な推論速度**
- 14.7ms / 1K tokens (ベンチマーク測定値)
- エンドツーエンドレイテンシ: 68ms
- リアルタイムアプリケーションに最適
- Success Criteria SC-001 (60秒以内のRAG構築) を余裕で達成

**2. 軽量アーキテクチャ**
- 蒸留された小型モデル (約22百万パラメータ)
- 6層のTransformer
- 384次元の埋め込みベクトル
- メモリフットプリント: 約90MB

**3. 十分な品質**
- 精度スコア: 約80.04%
- Wikipedia コンテンツの意味検索に十分
- 文レベルの埋め込みに最適化
- HuggingFaceで最もダウンロードされているモデルの一つ

**4. LangChain統合**
- `langchain-huggingface` パッケージで簡単に利用
- `HuggingFaceEmbeddings` クラスでサポート
- ローカル実行が容易 (外部API不要)

**5. コスト効率**
- 完全無料、オープンソース
- ローカル実行でAPI コスト不要
- t4g.medium インスタンスで十分に動作

### Alternatives Considered

**nomic-embed-text (却下理由)**

- **利点**:
  - わずかに高い精度 (81.2% vs 80.04%)
  - 長いコンテキストウィンドウに最適化
  - 詳細なドキュメント向けの高品質埋め込み

- **欠点**:
  - 推論速度が遅い (MiniLMの約5倍遅い)
  - より大きなモデルサイズ
  - Wikipediaの50KB記事には過剰なスペック

**判断**: Wikipedia記事は既にチャンクに分割されるため、長いコンテキストの優位性は不要です。MiniLMの速度優位性が、わずかな精度差(1.16%)よりも重要です。

**all-mpnet-base-v2 (検討対象)**

- より大きなモデル (768次元ベクトル)
- より高い精度
- しかし速度とメモリ使用量がトレードオフ
- 50KB記事で2倍のストレージコスト

**判断**: ストレージコストとクエリ速度を考慮し、MiniLMの384次元で十分です。

### Recommended Model

**sentence-transformers/all-MiniLM-L6-v2**

- **HuggingFace**: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- **ライセンス**: Apache 2.0
- **インストール**: `pip install sentence-transformers`
- **使用法**:
```python
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
```

## Decision 5: Wikipedia Scraping

### Rationale

Wikipedia スクレイピングには **Python標準ライブラリ + BeautifulSoup + requests** の組み合わせを推奨します。

**1. 推奨ライブラリ**

**Primary: wikipedia-api (推奨)**
- `pip install wikipedia-api`
- Wikipedia公式APIのPythonラッパー
- 倫理的なスクレイピングを保証 (APIエンドポイント使用)
- レート制限を自動的に遵守
- クリーンなテキスト抽出
- 構造化されたデータアクセス

```python
import wikipediaapi

wiki = wikipediaapi.Wikipedia('en')
page = wiki.page('Python_(programming_language)')
text = page.text  # クリーンなテキスト
```

**Secondary: BeautifulSoup + requests (複雑な抽出向け)**
- `pip install beautifulsoup4 requests lxml`
- HTML パースが必要な場合 (テーブル、インフォボックス)
- より細かい制御が可能
- wikipedia-apiで取得できないコンテンツに使用

```python
import requests
from bs4 import BeautifulSoup

response = requests.get(url)
soup = BeautifulSoup(response.content, 'lxml')
```

**2. ベストプラクティス**

**倫理的なスクレイピング**:
- Wikipedia の robots.txt に準拠
- User-Agent ヘッダーを設定 (プロジェクト名とコンタクト情報)
- レート制限を実装 (最低1秒/リクエスト)
- APIエンドポイントを優先 (HTMLスクレイピングは最小限)

```python
headers = {
    'User-Agent': 'WikiRAGBot/1.0 (your-email@example.com)'
}
```

**コンテンツ抽出**:
- メインコンテンツのみを抽出 (ナビゲーション、フッター除外)
- テーブルとインフォボックスの処理方針:
  - Phase 1: テキストコンテンツのみ (シンプル)
  - Phase 2: テーブルを構造化データとして抽出 (将来の拡張)
- 参照リンクとメタデータは除外
- セクション見出しは保持 (コンテキストに有用)

**エラーハンドリング**:
- 404、ネットワークタイムアウトを適切に処理
- リトライロジックを実装 (exponential backoff)
- 無効なURLの検証 (Wikipedia ドメインチェック)

**3. データ前処理**

```python
# チャンキング戦略
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # 約200-250 words
    chunk_overlap=200,  # コンテキスト保持
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)
```

**4. パフォーマンス考慮事項**

- 50KB記事: 約50,000文字
- チャンクサイズ1000文字: 約50-60チャンク
- 埋め込み生成時間: 約3-5秒 (all-MiniLM-L6-v2)
- 合計RAG構築時間: 10-20秒 (Success Criteria SC-001の60秒以内)

### Recommended Libraries

**必須**:
- `wikipedia-api==0.6.0` - メインのWikipedia取得
- `beautifulsoup4==4.12.3` - HTML パース (必要時)
- `requests==2.31.0` - HTTP リクエスト
- `lxml==5.1.0` - 高速XMLパーサー

**オプション**:
- `html2text` - HTMLをMarkdownに変換 (クリーンな出力)

## Decision 6: AWS Cost Optimization

### EC2 Instance Type

**推奨: t4g.medium (ARM-based Graviton2)**

**スペック**:
- vCPU: 2
- メモリ: 4GB
- ネットワーク: 最大5Gbps
- アーキテクチャ: ARM64 (Graviton2)

**コスト** (us-east-1):
- オンデマンド: $0.0336/時間
- 月額 (24/7): $24.50
- スポットインスタンス: $0.0101/時間 (70%割引)
- 月額 (スポット): $7.37

**選定理由**:
1. **メモリ十分性**:
   - Llama 3.2 3B (Q4): 約2-3GB
   - 埋め込みモデル: 約90MB
   - OS + アプリケーション: 約1GB
   - 合計: 約3-4GB (4GBで収まる)

2. **ARM最適化**:
   - Llamaモデルは ARM で良好なパフォーマンス
   - x86比で最大40%のコストパフォーマンス向上
   - Ollamaは ARM ネイティブサポート

3. **無料枠活用**:
   - 2025年12月31日まで t4g.small が750時間/月無料
   - 初期開発とテストに活用可能

4. **スケーラビリティ**:
   - 必要に応じて t4g.small (2GB) へのダウングレード可能
   - t4g.large (8GB) へのアップグレードも容易

**代替案**:
- **t4g.small** (2GB, $12.26/月): ぎりぎり動作可能だが余裕が少ない
- **t4g.large** (8GB, $49/月): より快適だが予算上限に近い
- **g4dn.xlarge** (GPU, $526/月): 完全に予算オーバー

### Lambda Configuration

**推奨設定**:

**RAG構築Lambda**:
- メモリ: 1024 MB
- タイムアウト: 300秒 (5分)
- アーキテクチャ: ARM64 (Graviton2, 20% cost reduction)
- 実行時間想定: 10-20秒/記事

**チャット クエリLambda**:
- メモリ: 512 MB
- タイムアウト: 30秒
- アーキテクチャ: ARM64
- 実行時間想定: 2-5秒/クエリ

**コスト計算** (月間100記事 + 1000クエリ):
- リクエスト: (100 + 1000) × $0.20 / 1M = $0.00022
- RAG構築コンピュート: 100回 × 15秒 × 1024MB = 1,500GB-秒
  - コスト: 1,500 × $0.0000166667 = $0.025
- クエリコンピュート: 1000回 × 3秒 × 512MB = 1,536GB-秒
  - コスト: 1,536 × $0.0000166667 = $0.026
- **Lambda合計: $0.051/月** (事実上無料、無料枠内)

**最適化ポイント**:
1. ARM64 アーキテクチャで20%コスト削減
2. 無料枠活用: 月間1M リクエスト + 400K GB-秒
3. 適切なメモリ割り当てで実行時間短縮

### Storage Strategy

**S3ストレージクラス選択**:

**ベクトルインデックス (頻繁アクセス)**:
- クラス: S3 Standard
- 理由: クエリごとにFAISSインデックスをダウンロード
- コスト: $0.023/GB/月

**Wikipedia生コンテンツ (低頻度アクセス)**:
- クラス: S3 Standard-IA (Infrequent Access)
- 理由: 保存後の参照は少ない
- コスト: $0.0125/GB/月

**アーカイブデータ (将来)**:
- クラス: S3 Glacier Flexible Retrieval
- 理由: 30日以上アクセスのないRAGセッション
- コスト: $0.0036/GB/月

**ストレージ見積もり** (100記事):
- 生テキスト: 100記事 × 50KB = 5MB → $0.00006/月
- FAISSインデックス: 100記事 × 2MB = 200MB → $0.0046/月
- **S3合計: $0.005/月** (事実上無料)

**ライフサイクルポリシー**:
```yaml
Rules:
  - Id: ArchiveOldSessions
    Status: Enabled
    Transitions:
      - Days: 30
        StorageClass: GLACIER_FLEXIBLE_RETRIEVAL
    Expiration:
      Days: 90
```

### Estimated Monthly Cost Breakdown

**ベースライン構成** (開発環境):

| サービス | 設定 | 月額コスト |
|---------|------|-----------|
| EC2 (LLM) | t4g.medium (24/7) | $24.50 |
| Lambda | 100記事 + 1000クエリ | $0.05 |
| S3 | 200MB Standard | $0.005 |
| Data Transfer | 10GB out | $0.90 |
| CloudWatch Logs | 1GB/月 | $0.50 |
| **合計** | | **$25.96** |

**最適化構成** (スポットインスタンス使用):

| サービス | 設定 | 月額コスト |
|---------|------|-----------|
| EC2 (LLM) | t4g.medium Spot (24/7) | $7.37 |
| Lambda | 100記事 + 1000クエリ | $0.05 |
| S3 | 200MB Standard | $0.005 |
| Data Transfer | 10GB out | $0.90 |
| CloudWatch Logs | 1GB/月 | $0.50 |
| **合計** | | **$8.83** |

**スケールアップ構成** (月間1000記事 + 10,000クエリ):

| サービス | 設定 | 月額コスト |
|---------|------|-----------|
| EC2 (LLM) | t4g.medium (24/7) | $24.50 |
| Lambda | 1000記事 + 10,000クエリ | $0.51 |
| S3 | 2GB Standard | $0.046 |
| Data Transfer | 50GB out | $4.50 |
| CloudWatch Logs | 5GB/月 | $2.50 |
| **合計** | | **$32.06** |

**予算達成ステータス**: ✅ **全構成が$50/月以内**

### Cost Optimization Strategies

**1. スポットインスタンス活用**
- EC2スポットインスタンスで70%コスト削減
- 中断対策: 自動再起動スクリプト + 状態の永続化
- 推奨リージョン: us-east-1 (最も安定したスポット価格)

**2. 無料枠の最大活用**
- Lambda: 月間1M リクエスト無料 (永続)
- Lambda: 月間400K GB-秒無料 (永続)
- t4g.small: 2025年12月まで750時間無料
- データ転送: 月間100GB out 無料

**3. Auto-Scaling (将来)**
- 低トラフィック時間帯にEC2を停止 (夜間など)
- Lambda関数でEC2起動/停止を自動化
- 推定節約: 50% (12時間/日運用の場合)

**4. Reserved Instances (プロダクション)**
- 1年契約で約40%割引
- 3年契約で約60%割引
- t4g.medium 1年RI: 約$175/年 ($14.58/月)

**5. Data Transfer最適化**
- CloudFrontエッジキャッシング活用
- S3 Transfer Accelerationは不要 (小ファイル)
- 同一リージョン内通信で転送料無料

**6. モニタリングコスト削減**
- CloudWatch Logs のログ保持期間を7日に制限
- 重要でないログは無効化
- メトリクスフィルターを最小限に

### Risk Mitigation

**コスト超過リスク**:
- AWS Budgets アラート設定: $40, $45, $50
- CloudWatch Billing アラーム
- 毎週のコストレビュー

**可用性リスク**:
- スポットインスタンス中断に備えた状態管理
- S3への定期バックアップ
- Lambda関数での自動復旧

## Implementation Roadmap

### Phase 1: 基盤構築 (Week 1-2)
1. AWS CDK セットアップ
2. t4g.medium EC2 + Ollama デプロイ
3. Llama 3.2 3B モデルのダウンロードと設定
4. 基本的なヘルスチェック実装

### Phase 2: RAG機能 (Week 3-4)
1. Wikipedia-API統合
2. all-MiniLM-L6-v2 埋め込みモデル統合
3. FAISS ベクトルストア実装
4. S3への永続化

### Phase 3: API & UI (Week 5-6)
1. Lambda関数デプロイ (RAG構築、チャット)
2. API Gateway設定
3. フロントエンドUI開発 (Svelte)
4. CloudFront + S3 ホスティング

### Phase 4: 最適化 & 監視 (Week 7-8)
1. パフォーマンステスト
2. コスト監視ダッシュボード
3. ログとメトリクス設定
4. ドキュメント作成

## References

### Research Sources
- [Ollama vs Llama.cpp Comparison 2025](https://www.houseoffoss.com/post/ollama-vs-llama-cpp-vs-vllm-local-llm-deployment-in-2025)
- [FAISS vs Chroma Vector Database](https://medium.com/algomart/chroma-vs-faiss-making-sense-of-your-vector-database-choices-3299d46774ce)
- [AWS CDK vs Terraform](https://spacelift.io/blog/aws-cdk-vs-terraform)
- [Embedding Models Guide 2025](https://www.bentoml.com/blog/a-guide-to-open-source-embedding-models)
- [AWS Lambda Pricing 2025](https://costq.ai/blog/aws-lambda/)
- [AWS EC2 T4g Instances](https://aws.amazon.com/ec2/instance-types/t4/)

### Technical Documentation
- [Ollama Documentation](https://github.com/ollama/ollama)
- [LangChain FAISS Integration](https://python.langchain.com/docs/integrations/vectorstores/faiss)
- [AWS CDK Python Guide](https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html)
- [sentence-transformers](https://www.sbert.net/)
- [Wikipedia API](https://wikipedia-api.readthedocs.io/)

## Constitution Compliance

このリサーチは以下のConstitution原則に準拠しています:

- ✅ **I. Modularity**: RAG構築とチャット機能の分離 (Lambda関数で実装)
- ✅ **II. Privacy First**: 全てのLLM推論がAWS内で完結 (Ollama使用)
- ✅ **III. Cost Efficiency**: 月額$25.96 (スポット利用で$8.83) → $50予算内
- ✅ **IV. Infrastructure as Code**: AWS CDK採用
- ✅ **V. Observability**: CloudWatch Logs/Metricsで監視

### Technology Stack Compliance

- ✅ **Cloud Platform**: AWS (EC2, Lambda, S3, CloudFront)
- ✅ **Backend**: Python 3.11+, LangChain, Ollama, FAISS
- ✅ **Frontend**: Svelte (推奨)
- ✅ **Data Storage**: S3 (RDB不要)
- ✅ **IaC**: AWS CDK (Python)

## Next Steps

1. このリサーチを基に `data-model.md` を作成
2. API契約を `contracts/` ディレクトリに定義
3. `quickstart.md` で開発環境セットアップ手順を記述
4. `/speckit.tasks` コマンドで実装タスクを生成

---

**Research Status**: ✅ Complete
**Ready for Phase 1 (Design)**: Yes
**Budget Validation**: ✅ Passed ($25.96 < $50)
**Constitution Check**: ✅ Passed (All principles satisfied)
