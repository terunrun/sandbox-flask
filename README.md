## [Flask](https://msiz07-flask-docs-ja.readthedocs.io/ja/latest/)

### 環境構築
1. pythonインストール
1. pip3インストール
1. flaskインストール
```sh
pip3 install flask
```

### 実行
```sh
export FLASK_APP={アプリ名}
export FLASK_ENV=development # デバッグモード
flask run
```

### 参考
- [とほほのFlask入門](https://www.tohoho-web.com/ex/flask.html#about)
- [FlaskでFormを用いてPOSTリクエストを行い、送信された値を取得する](https://www.nblog09.com/w/2021/11/26/flask_post/)
- [[Flask]フォームとの連携](https://fuji-pocketbook.net/flask-form/)
- [Flaskでフォーム送信部分を実装しよう](https://www.manajob.jp/python/python-app/flask-form)

### 初期構想
- [x] 画面から案件名を入力する
- [ ] 画面からアサインメンバーを入力する
  - [ ] 案件オーナーを指定する
  - [ ] メールアドレスとgithubアカウントを入力する
- [ ] gwsグループ作成
  - [ ] 入力された案件名でAdminSDKAPIで作成する
  - [ ] 入力されたアサインメンバーを追加する
  - [ ] 案件オーナーをグループオーナーに設定する
- [ ] googleドライブ作成
  - [ ] 入力された案件名でDrive APIで作成する
  - [ ] ドライブの共有にmanagementグループとmanagerグループとgwsグループをコンテンツ管理者で追加する
- [ ] googleCloudプロジェクト作成
  - [ ] 入力された案件名でResourceManagerAPIで作成する
  - [ ] gwsグループにオーナーロールを付与する
- [ ] githubリポジトリ作成
  - [ ] 入力された案件名でGithub RES APIで作成する
  - [ ] 入力されたアサインメンバーを追加する
  - [ ] 案件オーナーをリポジトリオーナーに設定する
