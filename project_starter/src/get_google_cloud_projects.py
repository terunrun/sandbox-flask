import csv
import sys

from google.cloud import resourcemanager_v3

SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
]

# 実行時引数として組織IDを受け取る
args = sys.argv
ORGANIZATION_ID = args[1]


def get_folder(folder_client, folders_list, all_folders_list):
    if not folders_list:
        return all_folders_list
    new_folders_list = []
    for folder in folders_list:
        request = resourcemanager_v3.ListFoldersRequest(parent=folder.name)
        folders = folder_client.list_folders(request=request)
        for folder in folders:
            new_folders_list.append(folder)
            all_folders_list.append(folder)
    return get_folder(folder_client, new_folders_list, all_folders_list)


def get_google_cloud_projects(organization_id):
    # Create a client
    organization_client = resourcemanager_v3.OrganizationsClient()
    folder_client = resourcemanager_v3.FoldersClient()
    project_client = resourcemanager_v3.ProjectsClient()

    # 組織を取得する
    request = resourcemanager_v3.GetOrganizationRequest(name=f'organizations/{organization_id}')
    organization = organization_client.get_organization(request=request)

    item_list = []
    # 組織直下のプロジェクトを取得する
    request = resourcemanager_v3.ListProjectsRequest(parent=f'organizations/{organization_id}')
    projects = project_client.list_projects(request=request)
    for project in projects:
        item_list.append([
            organization.display_name, '',
            project.project_id, project.display_name,
            project.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            project.update_time.strftime('%Y-%m-%d %H:%M:%S'),
            project.state
        ])

    # 組織配下のフォルダをすべて取得する
    request = resourcemanager_v3.ListFoldersRequest(parent=f'organizations/{organization_id}')
    folders = folder_client.list_folders(request=request)
    folders_list = []
    all_folders_list = []
    for folder in folders:
        folders_list.append(folder)
        all_folders_list.append(folder)
    all_folders_list = get_folder(folder_client, folders_list, all_folders_list)
    # print(all_folders_list)

    # フォルダ配下のプロジェクトを取得する
    for folder in all_folders_list:
        # print(f'Target folder: {folder.name}')
        request = resourcemanager_v3.ListProjectsRequest(parent=folder.name)
        projects = project_client.list_projects(request=request)
        for project in projects:
            # print(f'Target project: {project.project_id}')
            item_list.append([
                organization.display_name, folder.display_name,
                project.project_id, project.display_name,
                project.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                project.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                project.state
            ])

    # 並べ替えてヘッダーをつける
    item_list_sorted = sorted(item_list, key=lambda x: (x[0], x[1], x[2]))
    item_list_sorted.insert(0, ['organization', 'folder', 'project_id', 'project_name', 'created_time', 'update_time', 'state'])
    with open(f'projects_list_{organization_id}.csv', 'w', encoding='utf-8') as projects_list:
        writer = csv.writer(projects_list)
        writer.writerows(item_list_sorted)
    return f'projects_list_{organization_id}.csv'


if __name__ == '__main__':
    get_google_cloud_projects(ORGANIZATION_ID)
