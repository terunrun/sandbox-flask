import os
from flask import Flask, render_template, redirect, request, url_for
from google.cloud import storage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)


@app.route("/", methods=["GET"])
def main():
    print("/ get")
    return redirect(url_for('input'))


@app.route("/input", methods=["GET"])
def input():
    print("input get")
    return render_template('input.html')

@app.route("/confirm", methods=["POST"])
def confirm():
    print("confirm post")
    project_name = request.form.get('project_name')
    members      = request.form.get('members')
    if not project_name:
        error_message = "プロジェクト名は必ず入力してください"
        return render_template(
            'input.html',
            project_name=project_name,
            members=members,
            error_message=error_message
        )
    if not members:
        error_message = "アサインメンバーは必ず入力してください"
        return render_template(
            'input.html',
            project_name=project_name,
            members=members,
            error_message=error_message
        )
    return render_template(
        'confirm.html',
        project_name=project_name,
        members=members)

@app.route("/complete", methods=["POST"])
def complete():
    print("complete post")
    project_name = request.form.get('project_name')
    members      = request.form.get('members')
    message = f'{project_name}に{members}を追加することに成功しました'
    return render_template('complete.html', message=message)


@app.route("/api", methods=["GET", "POST"])
def api():
    if(request.method == 'POST'):
        return render_template('api.html')
    return render_template('api.html')

@app.route("/api_gcs", methods=["POST"])
def api_gcs():
    print("api_gcs post")
    bucket_name = request.form.get('bucket_name')
    if not bucket_name:
        error_message = "バケット名は必ず入力してください"
        return render_template(
            'api.html',
            error_message=error_message
        )
    storage_client = storage.Client()
    storage_client.create_bucket(f"sandbox-terunrun-dev-{bucket_name}")
    buckets = storage_client.list_buckets()
    return render_template(
        'api.html',
        results=buckets,
    )

SCOPES = [
    'https://www.googleapis.com/auth/drive'
]
file_fields = [
    'parents', 'name', 'id', 'trashed', 'createdTime',
    'modifiedTime', 'webContentLink', 'webViewLink'
]

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
    return creds

def create_gws_drive(creds, drive_id, drive_name):
    try:
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            'name': drive_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [] if not drive_id else [drive_id]
        }
        drive = service.files().create(
            body = file_metadata,
            # fields = 'id'
            # NOTE: 共有ドライブ配下のフォルダをparentsに指定する場合にTrueを設定する
            supportsAllDrives = True,
        ).execute()
        print(f"drive: {drive}")
        return drive
    except Exception as error:
        print(f'An error occurred: {error}')
        return error

def get_drive_contents_list(creds, drive_id):
    try:
        service = build("drive", "v3", credentials=creds)
        page_token = None
        item_list = []
        while True:
            results = service.files().list(
                # https://developers.google.com/drive/api/v3/reference/files?hl=ja
                corpora="allDrives",
                # driveId=drive_id,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                q="mimeType='application/vnd.google-apps.folder'",
                # pageSize=10,
                fields=f'nextPageToken, files({", ".join(file_fields)})',
                pageToken=page_token
            ).execute()
            items = results.get("files", [])
            if not items:
                print("No files found.")
                return None
            for item in items:
                if not item["trashed"]:
                    item_list.append([
                        item["name"],
                        # item["id"],
                        # item["createdTime"],
                        # item["modifiedTime"],
                        # item["parents"] if "parents" in item else "",
                        # item["webContentLink"] if "webContentLink" in item else "",
                        item["webViewLink"] if 'webViewLink' in item else "",
                    ])
            page_token = results.get("nextPageToken", None)
            if page_token is None:
                break
        # 並べ替えてヘッダーをつける
        item_list_sorted = sorted(item_list, key=lambda x: (x[0], x[1]))
        return item_list_sorted
    except Exception as error:
        print(f'An error occurred: {error}')
        return error

@app.route("/api_gws", methods=["POST"])
def api_gws():
    print("api_gws post")
    folder_name = request.form.get('folder_name')
    if not folder_name:
        error_message = "フォルダ名は必ず入力してください"
        return render_template(
            'api.html',
            error_message=error_message
        )
    creds = get_credentials()
    drive = create_gws_drive(creds, '', folder_name)
    contents = get_drive_contents_list(creds, drive['id'])
    return render_template(
        'api.html',
        results=contents,
    )


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=5000, debug=True)
