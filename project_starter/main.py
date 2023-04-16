import os
import time
from flask import Flask, render_template, request
# from google.cloud import storage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/drive',
]

app = Flask(__name__)


# def create_cloud_storage_buckets(project_name):
#     storage_client = storage.Client(project_name)
#     storage_client.create_bucket(f"{project_name}-flask-app")

# def list_cloud_storage_buckets(project_name):
#     storage_client = storage.Client(project_name)
#     buckets = storage_client.list_buckets()
#     return buckets


def create_gws_group(creds, group_address, group_name):
    print(f'Start create group')
    try:
        service = build('admin', 'directory_v1', credentials=creds)
        # グループを作成
        # https://developers.google.com/admin-sdk/directory/reference/rest/v1/groups/insert?hl=ja
        # emailはドメイン名を含めて指定する必要がある
        group = service.groups().insert(
            # https://developers.google.com/admin-sdk/directory/reference/rest/v1/groups?hl=ja#Group
            body = {"email": f'{group_address}@googlegroups.com', "name": group_name,}
        ).execute()
        print(f'group: {group["id"]}, {group["name"]}')
        return group
    except Exception as error:
        return error

def add_members_to_gws_group(creds, group_id, members):
    print(f'Start add member to group')
    try:
        service = build('admin', 'directory_v1', credentials=creds)
        # グループにメンバーを追加
        # https://developers.google.com/admin-sdk/directory/reference/rest/v1/members/insert?hl=ja
        for member in members:
            result = service.members().insert(
                # https://developers.google.com/admin-sdk/directory/reference/rest/v1/members?hl=ja#Member
                body = {"email": member, "role": "MEMBER"},
                groupKey = group_id,
            ).execute()
            print(f'Add member result: {result}')
    except Exception as error:
        return error

# def list_gws_groups(organization_id):
#     groups = []
#     return groups


def create_gws_drive(creds, drive_id, drive_name):
    print(f'Start create gws drive')
    try:
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            'name': drive_name,
            'mimeType': 'application/vnd.google-apps.folder',
            # TODO: 共有ドライブ直下の場合はdrive_idに何を指定する？
            'parents': [] if not drive_id else [drive_id]
        }
        drive = service.files().create(
            body = file_metadata,
            # fields = 'id'
            # 共有ドライブ配下のフォルダをparentsに指定する場合にTrueを設定する
            supportsAllDrives = True,
        ).execute()
        print(f"drive: {drive}")
        return drive
    except Exception as error:
        return error

def add_member_to_gws_drive(creds, drive_id, members):
    print(f'Start add member to gws drive')
    try:
        service = build('drive', 'v3', credentials=creds)
        for member in members:
            permission = service.permissions().create(
                fileId = drive_id,
                # https://developers.google.com/drive/api/v3/reference/permissions?hl=ja#resource
                body = {
                    "type": "group",
                    # NOTE: fileOrganizerはコンテンツ管理者を指す
                    # https://developers.google.com/drive/api/guides/ref-roles?hl=ja
                    "role": "fileOrganizer",
                    "emailAddress": member,
                },
                # 共有ドライブ配下のコンテンツを指定する場合にTrueを設定する
                supportsAllDrives = True,
            ).execute()
            print(f"permission: {permission}")
    except Exception as error:
        return error

# def list_gws_drives(drive_id):
#     drives = []
#     return drives


def create_google_cloud_project(creds, organization_id, folder_id, project_id):
    print(f'Start create google cloud project')
    # プロジェクトを作成
    # https://cloud.google.com/resource-manager/reference/rest/v3/projects/create
    try:
        service = build('cloudresourcemanager', 'v3', credentials=creds)
        parent = ""
        if organization_id:
            parent = f"organizations/{organization_id}"
        if folder_id:
            parent = f"folders/{folder_id}"
        print(f"parent: {parent}")
        operation = service.projects().create(
            # https://cloud.google.com/resource-manager/reference/rest/v3/projects#Project
            body = {"projectId": project_id, "displayName": project_id, "parent": parent,}
        ).execute()
        print(f'operation: {operation}')
    except Exception as error:
        return error

    # NOTE: 後続処理がエラーとならないようプロジェクト作成が完了するまで待つ
    operation_done = False
    try:
        while True:
            print(f'Waiting {operation["name"]} finish...')
            operation = service.operations().get(
                # https://cloud.google.com/resource-manager/reference/rest/v3/operations/get
                name = operation['name']
            ).execute()
            if 'done' in operation:
                operation_done = operation['done']
            if operation_done:
                break
            time.sleep(10)
        print(f'operation: {operation}')
        print(f'response: {operation["response"]}')
    except Exception as error:
        return error

def set_billng_account(creds, project_id, billing_account):
    print(f'Start set billing account to google cloud project')
    # 請求先アカウントを設定
    # https://cloud.google.com/billing/docs/reference/rest/v1/projects/updateBillingInfo
    try:
        service = build('cloudbilling', 'v1', credentials=creds)
        updateBillingInfo = service.projects().updateBillingInfo(
            # https://cloud.google.com/billing/docs/reference/rest/v1/ProjectBillingInfo
            name = f"projects/{project_id}",
            body = {"billingAccountName": f"billingAccounts/{billing_account}",}
        ).execute()
        print(f'updateBillingInfo: {updateBillingInfo}')
    except Exception as error:
        return error

def add_iam_to_gcp_project(creds, project_id, role, principals):
    # プリンシパルにIAMロールを付与
    print(f'Start add principal to google cloud project')
    # https://cloud.google.com/resource-manager/reference/rest/Shared.Types/Policy
    policies_json = {
        "bindings": [{
            "role": role,
            # NOTE: 指定するプリンシパルに応じてtypeを変更する（例：グループの場合はgroup）
            # "members": list(map(lambda principal: f"type:{principal}", principals))
            "members": list(map(lambda principal: f"group:{principal}", principals))
        }],
    }
    # https://cloud.google.com/resource-manager/reference/rest/v3/projects/setIamPolicy
    service = build('cloudresourcemanager', 'v3', credentials=creds)
    policy = service.projects().setIamPolicy(
        resource = f"projects/{project_id}",
        body = {"policy": policies_json},
    ).execute()
    print(f'policy: {policy}')

# def google_cloud_project(organization_id):
#     projects = []
#     return projects


@app.route("/", methods=["GET", "POST"])
def main():
    if(request.method == 'POST'):
        project_name = request.form.get('project_name')
        members      = request.form.get('members')

        organization_id = request.form.get('organization_id', '')
        folder_id = request.form.get('folder_id', '')
        billing_account  = request.form.get('billing_account', '')

        if not project_name:
            error_message = "プロジェクト名を入力してください"
            return render_template("main.html", error_message=error_message)
        if not members:
            error_message = "アサインメンバーを入力してください"
            return render_template("main.html", error_message=error_message)

        # 認証情報の作成
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        print(f"Start process: {project_name}")
        members = members.split(",")
        # try:
        #     create_cloud_storage_buckets(project_name)
        # except Exception as e:
        #     return render_template("main.html", error_message=e)
        # buckets = list_cloud_storage_buckets(project_name)
        try:
            group = create_gws_group(creds, project_name, project_name)
        except Exception as e:
            return render_template("main.html", error_message=e)
        try:
            add_members_to_gws_group(creds, group['id'], members)
        except Exception as e:
            return render_template("main.html", error_message=e)
        try:
            # NOTE: 第２引数は作成したい親フォルダのドライブIDに変更する
            drive = create_gws_drive(creds, '', project_name)
        except Exception as e:
            return render_template("main.html", error_message=e)
        try:
            add_member_to_gws_drive(creds, drive['id'], [group['email']])
        except Exception as e:
            return render_template("main.html", error_message=e)
        try:
            create_google_cloud_project(creds, organization_id, folder_id, project_name, billing_account)
        except Exception as e:
            return render_template("main.html", error_message=e)
        # NOTE: プロジェクト作成直後だとエラーになる可能性がある
        try:
            # NOTE: 第２引数は与えたいロールに変更する
            add_iam_to_gcp_project(creds, project_name, "roles/owner", [group['email']])
        except Exception as e:
            return render_template("main.html", error_message=e)
        # NOTE: プロジェクト作成直後だとエラーになる可能性がある
        try:
            set_billng_account(creds, project_name, billing_account)
        except Exception as e:
            return render_template("main.html", error_message=e)
        # print(f"Successfully finish: {project_name}")
        message = f"Successfully finish: {project_name}"
        return render_template(
            "main.html",
            message=message,
        )
    return render_template("main.html")
