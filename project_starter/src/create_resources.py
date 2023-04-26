import time
import uuid
from googleapiclient.discovery import build


# グループを作成
def create_gws_group(creds, group_address, group_name, customer_id):
    print(f'Start create group: {group_address}')
    service = build('admin', 'directory_v1', credentials=creds)
    # https://developers.google.com/admin-sdk/directory/reference/rest/v1/customers?hl=ja#Customer
    customer = service.customers().get(customerKey=customer_id,).execute()
    # https://developers.google.com/admin-sdk/directory/reference/rest/v1/groups/insert?hl=ja
    group = service.groups().insert(
        # https://developers.google.com/admin-sdk/directory/reference/rest/v1/groups?hl=ja#Group
        # NOTE: emailはドメイン名を含めて指定する必要がある
        body = {'email': f'{group_address}@{customer["customerDomain"]}', 'name': group_name,}
    ).execute()
    # print(f'group: {group["id"]}, {group["name"]}')
    print(f'Finish create group: {group_address}')
    return group


# グループにメンバーを追加
def add_members_to_gws_group(creds, group_id, members):
    print(f'Start add member to group: {group_id}')
    service = build('admin', 'directory_v1', credentials=creds)
    for member in members:
        # https://developers.google.com/admin-sdk/directory/reference/rest/v1/members/insert?hl=ja
        result = service.members().insert(
            # https://developers.google.com/admin-sdk/directory/reference/rest/v1/members?hl=ja#Member
            body = {'email': member, 'role': 'MEMBER'},
            groupKey = group_id
        ).execute()
        # print(f'Add member result: {result}')
    print(f'Finish add member to group: {group_id}')


# 共有フォルダを作成
# https://developers.google.com/drive/api/guides/manage-shareddrives?hl=ja
def create_gws_drive(creds, drive_name):
    print(f'Start create gws drive')
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': drive_name,}
    request_id = str(uuid.uuid4())
    drive = service.drives().create(
        requestId = request_id,
        body = file_metadata,
    ).execute()
    # print(f'drive: {drive}')
    print(f'Finish create gws drive')
    return drive

# def create_gws_drive(creds, drive_id, drive_name):
#     print(f'Start create gws drive: {drive_id}')
#     service = build('drive', 'v3', credentials=creds)
#     file_metadata = {
#         'name': drive_name,
#         'mimeType': 'application/vnd.google-apps.folder',
#         'parents': [] if not drive_id else [drive_id]
#     }
#     drive = service.files().create(
#         body = file_metadata,
#         # fields = 'id'
#         # 共有ドライブ配下のフォルダをparentsに指定する場合にTrueを設定する
#         supportsAllDrives = True,
#     ).execute()
#     # print(f'drive: {drive}')
#     print(f'Finish create gws drive: {drive_id}')
#     return drive


# 共有ドライブにメンバーを追加
def add_member_to_gws_drive(creds, drive_id, members):
    print(f'Start add member to gws drive: {drive_id}')
    service = build('drive', 'v3', credentials=creds)
    for member in members:
        permission = service.permissions().create(
            fileId = drive_id,
            # https://developers.google.com/drive/api/v3/reference/permissions?hl=ja#resource
            body = {
                'type': 'group',
                # NOTE: fileOrganizerはコンテンツ管理者を指す
                # https://developers.google.com/drive/api/guides/ref-roles?hl=ja
                'role': 'fileOrganizer',
                'emailAddress': member,
            },
            # 共有ドライブ配下のコンテンツを指定する場合にTrueを設定する
            supportsAllDrives = True,
        ).execute()
        # print(f'permission: {permission}')
        print(f'Finish add member to gws drive: {drive_id}')


# GoogleCloudプロジェクトを作成
def create_google_cloud_project(creds, organization_id, folder_id, project_id):
    print(f'Start create google cloud project: {project_id}')
    service = build('cloudresourcemanager', 'v3', credentials=creds)
    parent = ''
    if organization_id:
        parent = f'organizations/{organization_id}'
    if folder_id:
        parent = f'folders/{folder_id}'
    # https://cloud.google.com/resource-manager/reference/rest/v3/projects/create
    operation = service.projects().create(
        # https://cloud.google.com/resource-manager/reference/rest/v3/projects#Project
        body = {'projectId': project_id, 'displayName': project_id, 'parent': parent,}
    ).execute()
    print(f'operation: {operation}')

    # NOTE: 後続処理がエラーとならないようプロジェクト作成が完了するまで待つ
    operation_done = False
    while True:
        print(f'Waiting {operation["name"]} finish...')
        # https://cloud.google.com/resource-manager/reference/rest/v3/operations/get
        operation = service.operations().get(
            name = operation['name']
        ).execute()
        if 'done' in operation:
            operation_done = operation['done']
        if operation_done:
            break
        # NOTE: 指数バックオフの方が本来はいいかもしれない
        time.sleep(10)
    # print(f'operation: {operation}')
    print(f'{operation["name"]} finish.')


# GoogleCloudプロジェクトにプリンシパルとIAMロールをバインド
def add_iam_to_gcp_project(creds, project_id, role, principals):
    print(f'Start add principal to google cloud project: {project_id}')
    # https://cloud.google.com/resource-manager/reference/rest/Shared.Types/Policy
    policies_json = {
        'bindings': [{
            'role': role,
            # NOTE: 指定するプリンシパルに応じてtypeを変更する（例：グループの場合はgroup）
            # 'members': list(map(lambda principal: f'type:{principal}', principals))
            'members': list(map(lambda principal: f'group:{principal}', principals))
        }],
    }
    service = build('cloudresourcemanager', 'v3', credentials=creds)
    # https://cloud.google.com/resource-manager/reference/rest/v3/projects/setIamPolicy
    policy = service.projects().setIamPolicy(
        resource = f'projects/{project_id}',
        body = {'policy': policies_json},
    ).execute()
    # print(f'policy: {policy}')
    print(f'Finish add principal to google cloud project: {project_id}')


# 請求先アカウントを設定
def set_billing_account(creds, project_id, billing_account):
    print(f'Start set billing account to google cloud project: {project_id}')
    # https://cloud.google.com/billing/docs/reference/rest/v1/projects/updateBillingInfo
    service = build('cloudbilling', 'v1', credentials=creds)
    updateBillingInfo = service.projects().updateBillingInfo(
        # https://cloud.google.com/billing/docs/reference/rest/v1/ProjectBillingInfo
        name = f'projects/{project_id}',
        body = {'billingAccountName': f'billingAccounts/{billing_account}',}
    ).execute()
    # print(f'updateBillingInfo: {updateBillingInfo}')
    print(f'Finish set billing account to google cloud project: {project_id}')


# プロジェクトリソースを作成する
def create_resources(creds, project_name, members, customer_id, organization_id, folder_id, billing_account):
    # GoogleWorkspaceグループ
    group = create_gws_group(creds, project_name, project_name, customer_id)
    add_members_to_gws_group(creds, group['id'], members)

    # GoogleWorkspaceドライブ
    # drive = create_gws_drive(creds, drive_id, project_name)
    drive = create_gws_drive(creds, project_name)
    add_member_to_gws_drive(creds, drive['id'], [group['email']])

    # GoogleCloudプロジェクト
    create_google_cloud_project(creds, organization_id, folder_id, project_name)
    # NOTE: プロジェクト作成直後だとエラーになる可能性がある
    # NOTE: 第２引数は与えたいロールに変更する
    add_iam_to_gcp_project(creds, project_name, 'roles/owner', [group['email']])
    # NOTE: プロジェクト作成直後だとエラーになる可能性がある
    set_billing_account(creds, project_name, billing_account)
