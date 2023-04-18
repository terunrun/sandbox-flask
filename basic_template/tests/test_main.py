import pytest
from main import app

def test_main_route():
    response = app.test_client().get('/')
    assert response.status_code == 302


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
