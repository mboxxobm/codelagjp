# Board-Chart Suite

**Tick → Multi-TF Candle Viewer + フル板・歩み値パネル リニューアル版**

マルチ時間足ビューアーに、フル板シミュレーター（板・歩み値表示）を統合したリニューアルバージョンです。

## 機能

- **マルチ時間足チャート**: 2分足 / 5分足 / 10分足 / 日足を同時表示
- **VWAP / 水平線 / レイライン / RR計測** など元バージョンの全描画ツールを継承
- **フル板サイドバー**: CSV歩み値から現在値を中心とした板を合成表示
- **歩み値（テープ）**: カーソル位置までのティックをリアルタイム表示
- **CSV選択で自動読込・自動再生**: ファイル選択だけで先頭からチャート再生を開始
- **銘柄表示**: JPX公式の東証上場銘柄一覧から生成した辞書で、`9984` や `285A` などを銘柄名へ自動変換
- **1列ツールバー**: 通常は1列表示。必要な時だけ「2列」ボタンで折り返し表示
- **進捗表示の移動/非表示**: 青い進捗ラベルを列内・左上・右上へ移動、または非表示に切替
- **Z/X で ← → 進む**, **A:先頭 / E:末尾 / S:再生** のキーボード操作
- **📋 板/歩み値** ボタンでサイドバーのON/OFF切替

## ファイル構成

```
board-chart-suite/
├── index.html          # 統合レイアウト
├── app.js              # チャート描画ロジック（元の app.js を継承、hook追加）
├── board.js            # 板・歩み値パネル（新規）
├── jp-symbols.js       # JPX公式ソースから生成した日本株コード → 銘柄名辞書
├── css/style.css       # （参考用、index.html内のスタイルを優先）
├── img/                # ロゴ等（元プロジェクト由来）
├── favicon.ico
├── netlify.toml        # Netlify デプロイ設定
├── vercel.json         # Vercel デプロイ設定
└── qr-*.csv            # サンプル歩み値データ
```

## ローカル動作確認

```bash
cd /Users/th/Downloads/board-chart-suite
python3 -m http.server 8080
# ブラウザで http://localhost:8080 を開く
```

または単純に `index.html` を直接ブラウザで開く（ファイル読込も動作します）。

## 別サブドメインへのデプロイ

### オプションA: Netlify（推奨・最速）

1. [netlify.com](https://netlify.com) にログイン
2. 「Add new site → Deploy manually」
3. このフォルダ（`board-chart-suite`）をまるごとドラッグ&ドロップ
4. 自動でURLが発行される（例: `https://random-name.netlify.app`）
5. 「Domain settings → Add custom domain」で自分のサブドメインを設定
   - 例: `chart.yourdomain.com`
   - DNS に CNAME レコード `chart → apex-xyz.netlify.app` を追加

**CLI での継続デプロイ**:
```bash
npm install -g netlify-cli
cd /Users/th/Downloads/board-chart-suite
netlify deploy --prod --dir .
```

### オプションB: Vercel

```bash
npm install -g vercel
cd /Users/th/Downloads/board-chart-suite
vercel --prod
```

発行後、Vercel ダッシュボード → Settings → Domains でサブドメイン追加。

### オプションC: Cloudflare Pages

1. [dash.cloudflare.com](https://dash.cloudflare.com) → Pages → Upload assets
2. フォルダをアップロード
3. カスタムドメインでサブドメイン割当

### オプションD: GitHub Pages

```bash
cd /Users/th/Downloads/board-chart-suite
git init
git add .
git commit -m "Initial renewal version"
gh repo create board-chart-suite --public --source=. --push
# GitHub → Settings → Pages → Branch: main / root
```

`https://<username>.github.io/board-chart-suite/` で公開。カスタムサブドメインは CNAME ファイル追加で設定可能。

### オプションE: 既存のVPS / 自社サーバー（nginx）

`/etc/nginx/sites-available/chart.yourdomain.com`:

```nginx
server {
    listen 80;
    server_name chart.yourdomain.com;
    root /var/www/board-chart-suite;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location ~* \.(js|css|png|ico)$ {
        expires 1h;
        add_header Cache-Control "public";
    }
}
```

```bash
rsync -avz ./ user@server:/var/www/board-chart-suite/
sudo ln -s /etc/nginx/sites-available/chart.yourdomain.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d chart.yourdomain.com  # HTTPS化
```

## CSVフォーマット

```csv
値段,株数,金額,時刻
5762,1812400,10443048800,15:30:00
5791,1500,8686500,15:24:59
...
```

ファイル名に `YYYYMMDD` を含めると日付自動認識（例: `qr-6269-20260213.csv`）。
ファイル名に4桁の銘柄コード、または `285A` のような3桁+英字コードを含めると銘柄表示欄へ反映されます。
銘柄名は `jp-symbols.js` の `window.JP_STOCK_SYMBOLS` から検索します。
辞書の元データはJPX公式「東証上場銘柄一覧（2026年4月末）」です。

## 元バージョンとの差分

| 項目 | 元 `code20260419ver` | 本リニューアル |
|---|---|---|
| チャート表示 | 4分割マルチTF | ✅ 同一 |
| CSV読込 | ✅ | ✅ |
| 描画ツール | VWAP / 水平線 / レイ / RR | ✅ 同一 |
| **フル板表示** | ❌ | ✅ 新規追加 |
| **歩み値テープ** | ❌ | ✅ 新規追加 |
| **売買比インジケータ** | ❌ | ✅ 新規追加 |
| サイドバー切替 | ❌ | ✅ |
| デプロイ設定 | ❌ | ✅ Netlify/Vercel対応 |

## 元の app.js との差分

1行のみ追加：

```js
// render() の末尾
if (window.__boardSync) window.__boardSync(ticks, cursor);
```

これ以外は一切変更していないので、元プロジェクトの機能・ショートカットは完全互換です。
