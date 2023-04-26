import os

from src.get_gws_group_users import get_gws_group_users
from src.get_gws_drives import get_gws_drives
from src.get_google_cloud_projects import get_google_cloud_projects
from src.create_resources import create_resources

from flask import Flask, render_template, request
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.customer",
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/cloud-platform',
]

app = Flask(__name__)


# 認証情報を作成する
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


# Home画面表示
@app.route("/", methods=["GET"])
def main():
    return render_template("main.html")


# Create Resources画面表示
@app.route("/create", methods=["GET"])
def create():
    return render_template("create_resources.html")


# Check Resources画面表示
@app.route("/check", methods=["GET"])
def check():
    return render_template("check_resources.html")


# プロジェクトリソース作成
@app.route("/project_starter", methods=["POST"])
def project_starter():
    # 画面からパラメータを受け取る
    project_name    = request.form.get('project_name', '')
    members         = request.form.get('members', '')
    customer_id     = request.form.get('customer_id', '')
    # drive_id        = request.form.get('drive_id', '')
    organization_id = request.form.get('organization_id', '')
    folder_id       = request.form.get('folder_id', '')
    billing_account = request.form.get('billing_account', '')

    # パラメータが与えられているかを精査する
    if not project_name:
        error_message = "プロジェクト名を入力してください"
        return render_template("create_resources.html", error_message=error_message)
    if not members:
        error_message = "アサインメンバーを入力してください"
        return render_template("create_resources.html", error_message=error_message)
    if not customer_id:
        error_message = "GWSの顧客IDを入力してください"
        return render_template("check_resources.html", error_message=error_message)
    # if not drive_id:
    #     error_message = "GWSの共有ドライブIDを入力してください"
    #     return render_template("main.html", error_message=error_message)
    if not organization_id:
        error_message = "GoogleCloud組織IDを入力してください"
        return render_template("create_resources.html", error_message=error_message)
    # if not folder_id:
    #     error_message = "GoogleCloudフォルダIDを入力してください"
    #     return render_template("main.html", error_message=error_message)
    if not billing_account:
        error_message = "GoogleCloud請求アカウントIDを入力してください"
        return render_template("create_resources.html", error_message=error_message)

    # 認証情報を取得する
    creds = get_credentials()

    # 各リソースを作成する
    print(f"Start process: {project_name}")
    members = members.split(",")
    try:
        create_resources(
            creds, project_name, members, customer_id, organization_id, folder_id, billing_account
        )
    except Exception as error:
        return render_template("create_resources.html", error_message=error)

    # 各リソース一覧を作成する
    get_gws_group_list(customer_id=customer_id)
    get_gws_drive_list()
    get_google_cloud_project_list(organization_id=organization_id)

    message = f"Successfully finish: {project_name}"
    print(message)
    return render_template("main.html", message=message)


# GWSグループ一覧取得
@app.route("/get_gws_group_list", methods=["POST"])
def get_gws_group_list(**kwargs):
    if request.form.get('customer_id'):
        customer_id = request.form.get('customer_id')
    elif 'customer_id' in kwargs:
        customer_id = kwargs['customer_id']
    if not customer_id:
        error_message = "GWSの顧客IDを入力してください"
        return render_template("check_resources.html", error_message=error_message)
    creds = get_credentials()
    try:
        groups_list = get_gws_group_users(creds, customer_id)
    except Exception as error:
        return render_template("check_resources.html", error_message=error)
    message = f"Successfully get gws group list: {groups_list}"
    return render_template("main.html", message=message)


# GWSフォルダ一覧取得
@app.route("/get_gws_drive_list", methods=["POST"])
def get_gws_drive_list(**kwargs):
    # drive_id = ''
    # if request.form.get('drive_id'):
    #     drive_id = request.form.get('drive_id')
    # elif 'drive_id' in kwargs:
    #     drive_id = kwargs['drive_id']
    # if not drive_id:
    #     error_message = "GWSの共有ドライブIDを入力してください"
    #     return render_template("main.html", error_message=error_message)
    creds = get_credentials()
    try:
        drives_list = get_gws_drives(creds)
    except Exception as error:
        return render_template("check_resources.html", error_message=error)
    message = f"Successfully get gws drive list: {drives_list}"
    return render_template("main.html", message=message)


# GoogleCloudプロジェクト一覧取得
@app.route("/get_google_cloud_project_list", methods=["POST"])
def get_google_cloud_project_list(**kwargs):
    organization_id = ''
    if request.form.get('organization_id'):
        organization_id = request.form.get('organization_id')
    elif 'organization_id' in kwargs:
        organization_id = kwargs['organization_id']
    if not organization_id:
        error_message = "GoogleCloudの組織IDを入力してください"
        return render_template("check_resources.html", error_message=error_message)
    try:
        projects_list = get_google_cloud_projects(organization_id)
    except Exception as error:
        return render_template("check_resources.html", error_message=error)
    message = f"Successfully get google cloud project list: {projects_list}"
    return render_template("main.html", message=message)
