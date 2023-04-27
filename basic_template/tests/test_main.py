from main import app

def test_main_route():
    response = app.test_client().get('/')
    assert response.status_code == 200
    assert "画面遷移テンプレート".encode("utf-8") in response.data


def test_input_route():
    response = app.test_client().get('/input')
    assert response.status_code == 200
    assert "プロジェクト名とアサインメンバーを入力してください。".encode("utf-8") in response.data


def test_confirm_route():
    response = app.test_client().post('/confirm', data={
        "project_name": "test",
        "members": "test1,test2",
    })
    assert response.status_code == 200
    assert "以下でよろしいですか？".encode("utf-8") in response.data


def test_confirm_error_route_empty_project_name():
    response = app.test_client().post('/confirm', data={
        "members": "test1,test2",
    })
    assert response.status_code == 200
    assert "プロジェクト名は必ず入力してください".encode("utf-8") in response.data


def test_confirm_route_empty_members():
    response = app.test_client().post('/confirm', data={
        "project_name": "test",
    })
    assert response.status_code == 200
    assert "アサインメンバーは必ず入力してください".encode("utf-8") in response.data


def test_complete_route():
    response = app.test_client().post('/complete', data={
        "project_name": "test",
        "members": "test1,test2",
    })
    assert response.status_code == 200
    assert 'testにtest1,test2を追加することに成功しました'.encode("utf-8") in response.data


def test_api_route():
    response = app.test_client().get('/api')
    assert response.status_code == 200
    assert 'バケット名を入力してください。'.encode("utf-8") in response.data


test_bucket = {
    'id': '1a2b3c4d5e6f7g8h9i0j1a2b3c4d5e6f7',
    'name': 'cloud-storage-test-bucket',
}

# def test_api_gcs_route(mocker):
#     # NOTE: Github Actionsでエラーとなった
#     # NOTE: google.auth.exceptions.DefaultCredentialsError: File test was not found.
#     # NOTE: 暫定対応としてstorage.Clientをmockにしたかったがそうするとテストが通らない
#     # mocker.patch("main.storage.Client")
#     mocker.patch("main.storage.Client.create_bucket")
#     # NOTE: return_valueとしてバケットオブジェクトを返すようにしたい
#     # NOTE: テスト用のmockオブジェクトを用意する必要がある？
#     mocker.patch("main.storage.Client.list_buckets", return_value=[test_bucket])
#     response = app.test_client().post('/api_gcs', data={
#         "bucket_name": "test",
#     })
#     assert response.status_code == 200
#     assert 'cloud-storage-test-bucket'.encode("utf-8") in response.data


def test_api_gcs_route_empty_bucket_name():
    response = app.test_client().post('/api_gcs', data={
        "bucket_name": "",
    })
    assert response.status_code == 200
    assert 'バケット名は必ず入力してください'.encode("utf-8") in response.data


test_folder = {
    'kind': 'drive#file',
    'id': '1a2b3c4d5e6f7g8h9i0j1a2b3c4d5e6f7',
    'name': 'gws-test-folder',
    'mimeType': 'application/vnd.google-apps.folder'
}
test_folder2 = {
    'kind': 'drive#file',
    'id': '1a2b3c4d5e6f7g8h9i0j1a2b3c4d5e6f7',
    'name': 'gws-test-folder2',
    'mimeType': 'application/vnd.google-apps.folder'
}
test_folders = [test_folder, test_folder2]

def test_api_gws_route(mocker):
    # NOTE: credentialを使用する場合のtestはどう記述するべきか？
    # NOTE: ローカルでのテストは問題ないがGithub Actionsなどcredentialを保持できない場合など。
    # mocker.patch("main.get_credentials", return_value="cred")
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['credentials'] = {'key': 'dummy user'}
            session['folder_name'] = 'test'
        mocker.patch("main.Credentials", return_value="")
        mocker.patch("main.create_gws_drive", return_value=test_folder)
        mocker.patch("main.get_drive_contents_list", return_value=test_folders)
        response = client.post('/api_gws', data={
            "folder_name": "test",
        })
        assert response.status_code == 200
        assert 'gws-test-folder'.encode("utf-8") in response.data
        assert 'gws-test-folder2'.encode("utf-8") in response.data


def test_api_gws_route_empty_foleder_name():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['credentials'] = 'dummy user'
            session['folder_name'] = ''
        response = client.post('/api_gws')
        assert response.status_code == 200
        assert 'フォルダ名は必ず入力してください'.encode("utf-8") in response.data
