import csv
from googleapiclient.discovery import build


def get_gws_group_users(creds, customer_id):
    service = build('admin', 'directory_v1', credentials=creds)

    item_list = []
    page_token = None
    while True:
        results = service.groups().list(customer=customer_id,
                                        # maxResults=10,
                                        orderBy='email',
                                        pageToken=page_token,
                                    ).execute()
        groups = results.get('groups', [])
        if not groups:
            print('No groups in the domain.')
        else:
            for group in groups:
                page_token_members = None
                while True:
                    results = service.members().list(groupKey=group['id'],
                                                    # maxResults=10,
                                                    pageToken=page_token_members,
                                                    ).execute()
                    members = results.get('members', [])

                    if not members:
                        print(f'No members in {group["name"]}.')
                        item_list.append(
                            [group['id'], group['email'], group['name'], '', '', '',]
                        )
                    else:
                        for member in members:
                            user = service.users().get(userKey=member['id'],).execute()
                            # print(user)
                            if not user:
                                print(f'\nNo user id: {member["id"]}.')
                            else:
                                # 取得したい項目は以下を参照に変更する
                                # https://developers.google.com/admin-sdk/directory/reference/rest/v1/users?hl=ja#User
                                # https://developers.google.com/admin-sdk/directory/reference/rest/v1/groups?hl=ja#Group
                                # https://developers.google.com/admin-sdk/directory/reference/rest/v1/members?hl=ja#Member
                                item_list.append([
                                    group['id'], group['email'], group['name'], member['role'],
                                    member['email'], user['name']['fullName']
                                ])
                    page_token_members = results.get('nextPageToken', None)
                    if page_token_members is None:
                        break
        page_token = results.get('nextPageToken', None)
        if page_token is None:
            break

    # 並べ替えてヘッダーをつける
    item_list_sorted = sorted(item_list, key=lambda x: (x[1], x[3], x[4]))
    item_list_sorted.insert(0, ['group_id', 'email', 'name', 'role', 'user_id', 'email', 'fullName'])
    with open(f'groups_list_{customer_id}.csv', 'w', encoding='utf-8') as groups_list:
        writer = csv.writer(groups_list)
        writer.writerows(item_list_sorted)
    return f'groups_list_{customer_id}.csv'
