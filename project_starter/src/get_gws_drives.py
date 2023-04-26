import csv
from datetime import datetime
from googleapiclient.discovery import build


def get_gws_drives(creds):
    service = build('drive', 'v3', credentials=creds)
    page_token = None
    item_list = []
    while True:
        # https://developers.google.com/drive/api/guides/search-shareddrives?hl=ja
        results = service.drives().list(
            pageSize=10,
            pageToken=page_token,
            # q='organizerCount != 0',
            useDomainAdminAccess=True,
            fields=f'drives({", ".join("*")})',
        ).execute()
        items = results.get('drives', [])
        for item in items:
            item_list.append([
                item['name'], item['id'],
                # NOTE: Python3.11以前だとISO8601形式の日付の末尾にZがあるとエラーになるため置換
                (datetime.fromisoformat(item['createdTime'].replace('Z', '+00:00'))).strftime('%Y-%m-%d %H:%M:%S')
            ])
        page_token = results.get('nextPageToken', None)
        if page_token is None:
            break

    # # 並べ替えてヘッダーをつける
    item_list_sorted = sorted(item_list, key=lambda x: (x[0], x[1]))
    item_list_sorted.insert(0, ['name', 'id', 'createdTime'])
    with open(f'shared_drives_list', 'w', encoding='utf-8') as drives_list:
        writer = csv.writer(drives_list)
        writer.writerows(item_list_sorted)
    return f'shared_drives_list.csv'
