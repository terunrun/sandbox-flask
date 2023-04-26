## プロジェクトリソース作成ツール
### 機能概要
- 画面からプロジェクト名とアサインメンバーなどを入力すると、プロジェクトに必要なリソースが作成される。
- 作成が完了すると作成される各種リソースの一覧がCSVで出力される。

### 作成されるリソース
- GoogleWorkspaceグループ
  - 画面から入力したプロジェクト名をメールアドレス、グループ名に持つgoogleグループが作成される。
  - 画面から入力したGWS顧客IDから動的にドメイン名が取得される。
  - 画面から入力したメンバーがMEMBERロールでそのグループに追加される。
  - メンバーをMEMBERロール以外で追加場合はコード修正が必要。
- Googleドライブ共有フォルダ
  - 画面から入力したプロジェクト名をフォルダ名に持つGoogleフォルダが共有ドライブ直下に作成される。
    - TODO: GWSユーザーでない場合はどうなる？
  - 特定フォルダの配下に作成したい場合はコード修正が必要。
- GoogleCloudプロジェクト
  - 画面から入力したプロジェクト名をプロジェクトID、プロジェクト名に持つGoogleCloudプロジェクトが作成される。
  - 組織、フォルダが画面から入力された場合は、その配下に作成される。
    - TODO: 組織がない場合はどうなる？
  - 請求先アカウントIDがプロジェクトの請求情報に設定される。
  - はじめに作成されたgoogleグループにオーナーロールが付与される。
  - 付与したいロールをオーナー以外にしたい場合はコード修正が必要。

### 技術スタック
- プログラミング言語：Python3.9.7
- WEBアプリケーションフレームワーク：Flask
- アプリケーション基盤：ローカルまたはCloudRun（WIP）

### 環境構築
- ローカル環境
  - pythonをインストール
    - バージョンは3.9以降が望ましい
  - pip3をインストール
    - バージョンは21.2以降が望ましい
  - ソースコードを取得
  - 必要なライブラリをインストール
  ```sh
  # ソースコードが存在する場所で実行する
  pip3 install -r requirements.txt
  ```
  - cloud SDK（GoogleCloudリソースを操作するツール）をインストール
    - [gcloud CLI をインストールする](https://cloud.google.com/sdk/docs/install?hl=ja)
- GoogleCloudプロジェクト環境
  - プロジェクトを作成
    - 対象のGWS組織配下に作成する
  - 必要なAPIを有効化
    - [Admin SDK API](https://console.cloud.google.com/apis/api/admin.googleapis.com/)
    - [Google Drive API]()
    - [Cloud Resource Manager API]()
    - [Cloud Billing API]()
  - [OAuth同意画面](https://console.cloud.google.com/apis/credentials/consent?hl=ja)を作成
    - ここでスコープを「組織内」にすると同一GWS組織内のアカウントでの実行のみを許可する
  - [OAuthクライアントシークレット](https://console.cloud.google.com/apis/credentials?hl=ja)を作成しJSONをダウンロード
    - アプリケーションの種類は「デスクトップアプリ」を選択する
    - ソースコードが存在するパスに移動し、名前をcredentials.jsonに変更する


### 実行
- ローカルで以下コマンドを実行する。
```sh
# 認証情報を設定
# 実行するとブラウザでGoogleアカウントのログイン画面が開くので、適切なアカウントを選択する。
gcloud auth application-default login

# アプリケーション起動
# ソースコードが存在する場所で実行する
flask run -p 8080
```

- ブラウザで[ここ](http://localhost:8080)にアクセスする。
- 「リソース作成」「リソース取得」どちらかのボタンを押す。
- それぞれの遷移先でフォームに入力してボタンを押すと機能が実行される。
- ボタンを押すとブラウザでOAuth同意画面が開くので、画面の指示に従ってアクセスを許可する。


#### クラウド
1.


