# salesforce-scroll-phat-hd
Salesforceに登録/更新したレコードを、変更データキャプチャにより検出し、レコードに含まれるメッセージをRaspberry Pi上の[Scroll pHAT HD](https://shop.pimoroni.com/products/scroll-phat-hd?variant=38472781450)にリアルタイムで出力します。

<img src="images/salesforce-scroll-phat-hd.gif" width="400">

## インストール
### Salesforce組織の設定
本プログラムはSalesforce組織が必要です(当プログラムはDeveloper組織で動作確認をしています)。  
システム管理者で組織にログイン後、以下の手順を実施します。

#### プロファイルの作成
1. 設定->ユーザ->プロファイルを選択
1. インデックスの'S'を押下し、「Salesforce API Only System Integrations」行のコピーリンクを押下
1. プロファイル名に「Custom Salesforce API Only System Integrations」を入れて保存ボタンを押下

#### 接続ユーザの作成
1. 設定->ユーザ->ユーザを選択
1. 新規ユーザボタンを押下
1. 名前とメールアドレスとユーザ名を任意の値で入力
1. ユーザライセンスはSalesforce Integrationを選択し、プロファイルはCustom Salesforce API Only System Integrationsを選択
1. 保存ボタンを押下(以降、Salesforceからメールが届き、パスワード設定を求められるが必須ではない)

#### 接続アプリケーションの作成
1. 設定->アプリケーション->アプリケーションマネージャを選択
1. 新規接続アプリケーションを押下
1. 以下を入力し、保存。次へボタンを押下。   
　　接続アプリケーション名: Scroll pHAT HD   
　　API参照名: Scroll_pHAT_HD  
　　OAuth 設定の有効化: 有効  
　　選択した OAuth 範囲: API を使用してユーザデータを管理 (api)  
　　コールバック URL: ダミーURL(https://dummy.com など任意のURL)  
　　クライアントログイン情報フローを有効化: 有効
1. コンシューマ鍵とコンシューマの秘密を取得　※settings.pyで必要

#### クライアントログイン情報フローの実行ユーザの指定
1. 設定->アプリケーション->接続アプリケーション->接続アプリケーションを管理するを選択
1. Scroll pHAT HDをクリックし、ポリシーを編集ボタンを押下
1. クライアントログイン情報フローの「別のユーザとして実行」に作成したユーザを設定
1. 保存ボタンを押下

#### カスタムオブジェクトの作成
1. 設定->オブジェクトマネージャ->を選択
1. 作成->カスタムオブジェクトを選択
1. 以下を入力し、保存を押下  
　　表示ラベル: 通知  
　　オブジェクト名: Notification  
　　データ型: 自動採番  
　　表示形式: NT-{0000000000}  
　　開始番号: 1  
1. 項目とリレーションを選択
1. 新規ボタンを押下
1. データ型にテキストを選択し次へ押下
1. 以下を入力し、次へ押下  
　　項目の表示ラベル: メッセージ  
　　文字数: 255  
　　項目名: Message  
1. 「Custom Salesforce API Only System Integrations」の参照可能にチェック有りであることを確認し、次へボタンを押下
1. 保存ボタンを押下

#### プラットフォームイベントの作成
1. 設定->インテグレーション->プラットフォームイベントを選択
1. 新規プラットフォームイベントを押下
1. 以下を入力し、保存を押下  
　　表示ラベル: 通知イベント  
　　オブジェクト名: NotificationEvent  
　　公開動作: コミット後に公開  
1. カスタム項目 & リレーションの新規ボタンを押下
1. データ型にテキストを選択し次へ押下
1. 以下を入力し、次へ押下  
　　項目の表示ラベル: メッセージ  
　　文字数: 255  
　　項目名: Message  

#### フローの作成
1. 設定->プロセスの自動化->フローを選択
1. 新規フローを押下
1. レコードトリガーフローを選択し、作成ボタンを押下
1. 以下を選択し、完了ボタンを押下  
　　オブジェクト: 通知  
　　フローをトリガする条件: レコードが作成されたまたは更新された  
　　フローを最適化: アクションと関連レコード  
1. 「+」を押下し、「レコードを作成」を押下  
1. 以下を入力  
　　表示ラベル: 通知イベント作成  
　　API 参照名: CreateNotificationEvent  
　　レコード項目の設定方法: 個別のリソースおよびリテラル値を使用  
　　オブジェクト: 通知イベント  
　　項目: Message__cを選択  
　　値: $Record->Message__cを選択  
1. 保存を押下
1. 以下を入力し、保存を押下  
　　フローの表示ラベル: 通知フロー  
　　フローの API 参照名: NotificationFlow  
1. 有効化ボタンを押下

#### プロファイルに通知イベントの参照権限を付与
1. 設定->ユーザ->プロファイルを選択
1. インデックスの'C'を押下し、「Custom Salesforce API Only System Integrations」行の編集を押下
1. プラットフォームイベント権限の通知イベントの参照を有効に変更
1. 保存ボタンを押下

#### カスタムタブの作成
1. 設定->ユーザインターフェース->タブを選択
1. カスタムオブジェクトタブの新規ボタンを押下
1. 以下を選択し、次へボタンを押下  
　　オブジェクト: 通知  
　　タブスタイル: 任意のアイコン選択  
1. 「1 つのタブ表示をすべてのプロファイルに適用する」で「デフォルトで表示」となっているので、そのまま次へボタンを押下  
　　※プロファイルを限定したければ、ここで選択してもよい  
1. デフォルトで全てのカスタムアプリケーションが「タブを含める」にチェックがついているので、そのまま保存ボタンを押下  
　　※アプリケーションを限定したければ、ここで選択してもよい  

#### マイドメインの確認
1. 設定->会社の設定->私のドメインを選択
2. 現在の [私のドメイン] の URLを取得　※settings.pyで必要

以上で、Salesforceの設定手順は終了です。

### ライブラリのインストール
Salesforce Streaming API clientのライブラリが必要なので、インストールします。

```
pip install aiosfstream
```

### プログラムの配置
以下のファイルを任意のディレクトリに配置します。日本語表示にmisaki.pyとMISAKI.FNTを利用していますので、[こちら](https://github.com/moguno/scroll_phat_hd-japanese-ticker/tree/master/bin
)以下よりダウンロードします。

* salesforce-scroll-phat-hd.py
* settings.py
* misaki.py
* MISAKI.FNT

### 設定ファイルの書き換え
settings.pyを編集し、YOUR DOMAIN、YOUR CONSUMER KEY、YOUR CONSUMER SECRETの部分をSalesforce組織の設定で取得した値に変更します。

```
token_url = "https://<YOUR DOMAIN>/services/oauth2/token"
consumer_key = "<YOUR CONSUMER KEY>"
consumer_secret = "<YOUR CONSUMER SECRET>"
platform_event_channel = "/event/NotificationEvent__e"
message_field = "Message__c"
brightness = 0.2
```

## 実行
以下のコマンドで実行し、Salesforceから通知オブジェクトに対してレコードの登録/更新をすれば、Scroll pHAT HDにメッセージが表示されます

```
python salesforce-scroll-phat-hd.py
```
## その他
- Salesforce Streaming API clientは、リソースオーナー・パスワード・クレデンシャルズのOAuthフローしか選択できなかったため、強引に別クラスを作成してクライアント・クレデンシャルフローに対応させています。

## ライセンス
salesforce-scroll-phat-hdはMITライセンスを適用しています。
