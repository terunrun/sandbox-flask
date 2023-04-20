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
export FLASK_DEBUG=True # デバッグモード
flask run
```

Flask.secret_keyの生成
```sh
python -c 'import secrets; print(secrets.token_hex())'
```

### 参考
- [とほほのFlask入門](https://www.tohoho-web.com/ex/flask.html#about)
- [FlaskでFormを用いてPOSTリクエストを行い、送信された値を取得する](https://www.nblog09.com/w/2021/11/26/flask_post/)
- [[Flask]フォームとの連携](https://fuji-pocketbook.net/flask-form/)
- [Flaskでフォーム送信部分を実装しよう](https://www.manajob.jp/python/python-app/flask-form)
- [flaskでWebアプリ開発、テストを記述する5、ブログ機能のテスト](https://panda-clip.com/flask-test5/)
