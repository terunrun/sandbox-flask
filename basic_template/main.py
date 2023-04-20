import os
from flask import Flask, render_template, redirect, request, url_for, session
from google.cloud import storage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google_auth_oauthlib.flow

app = Flask(__name__)
app.secret_key = b'{INPUT HERE}'

@app.route("/", methods=["GET"])
def main():
    print("/ get")
    return redirect(url_for('input'))


@app.route("/input", methods=["GET"])
def input():
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

# def get_credentials():
#     creds = None
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         with open('token.json', 'w', encoding='utf-8') as token:
#             token.write(creds.to_json())
#     return creds

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

@app.route("/api_gws", methods=["GET", "POST"])
def api_gws():
    folder_name = session['folder_name']
    if not folder_name:
        error_message = "フォルダ名は必ず入力してください"
        return render_template(
            'api.html',
            error_message=error_message
        )

    if 'credentials' not in session:
        return redirect('authorize')

    # Load credentials from the session.
    creds = Credentials(**session['credentials'])

    # creds = get_credentials()
    drive = create_gws_drive(creds, '', folder_name)
    contents = get_drive_contents_list(creds, drive['id'])
    return render_template(
        'api.html',
        results=contents,
    )

@app.route('/authorize', methods=["POST"])
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file("client_secret.json", scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state

    session['folder_name'] = request.form.get('folder_name')
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    print("oauth2callback")
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        "client_secret.json", scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url.replace("http://", "https://")
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    print("oauth2callback2")
    return redirect(url_for('api_gws'))

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

if __name__ == "__main__":  # pragma: no cover
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 8080, debug=True)
