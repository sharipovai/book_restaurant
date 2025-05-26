import apiclient
import httplib2
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
from collections import defaultdict

import config
from datetime import datetime

from googleapiclient.discovery import build


def get_service_sacc():
    creds_json = config.creds_json
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    return apiclient.discovery.build('sheets', 'v4', http=creds_service)


def get_sheet_dict(my_hall, people_cnt, date):
    time_dict = defaultdict(list)
    if 'караоке' in my_hall.lower():
        sheet_range = 'A21:H38'
    else:
        sheet_range = 'A2:I19'
    resp = get_service_sacc().spreadsheets().values().get(spreadsheetId=config.spreadsheet_id, range=f"{date}!{sheet_range}").execute()
    for i in range(len(resp['values'][1])):
        num = resp['values'][1][i]
        if not num.isdigit() or int(num) < int(people_cnt):
            continue
        for row in resp['values'][3:]:
            if len(row) <= i or len(row)>=i and row[i] == '':
                time_dict[row[0]].append(resp['values'][0][i])
    return time_dict


def write_sheet(my_hall, my_date, my_time, my_name, my_table, is_deleting=0):
    if 'караоке' in my_hall.lower():
        sheet_range = 'A21:H38'
    else:
        sheet_range = 'A2:I19'
    resp = get_service_sacc().spreadsheets().values().get(spreadsheetId=config.spreadsheet_id,
                                                          range=f"{my_date}!{sheet_range}").execute()
    error = 0
    i = 0
    for i in range(len(resp['values'][0])):
        if resp['values'][0][i] == my_table:
            break
    for j in range(len(resp['values'])):
        row = resp['values'][j]
        if row[0] == my_time:
            for cnt in range(config.book_record_cnt):
                if cnt+j >= len(resp['values']):
                    break
                book_record = resp['values'][j+cnt]
                if len(book_record) > i:
                    if book_record[i] == '' or is_deleting == 1:
                        book_record[i] = my_name
                    else:
                        error = 1
                else:
                    while len(resp['values'][j+cnt]) <= i:
                        resp['values'][j+cnt].append('')
                    resp['values'][j+cnt][i] = my_name
    if error == 0:
        body = {'values': resp['values']}
        resp2 = get_service_sacc().spreadsheets().values().update(spreadsheetId=config.spreadsheet_id, range=f"{my_date}!{sheet_range}",
                                      valueInputOption="RAW", body=body).execute()
    return error


def create_new_list():
    title = datetime.now().strftime("%d.%m.%y")
    body = {
        "requests": {
            "addSheet": {
                "properties": {
                    "title": f"{title}"
                }
            }
        }
    }
    resp = get_service_sacc().spreadsheets().values().get(spreadsheetId=config.spreadsheet_id, range="new!A1:K40").execute()
    new_body = {}
    new_body["values"] = resp['values']

    resp1 = get_service_sacc().spreadsheets().batchUpdate(spreadsheetId=config.spreadsheet_id, body=body).execute()

    resp2 = get_service_sacc().spreadsheets().values().update(spreadsheetId=config.spreadsheet_id,
                                                              range=f"{title}!A1:K40",
                                                              valueInputOption="RAW", body=new_body).execute()


def copy_sheet(title):
    new_worksheetid = get_service_sacc().spreadsheets().sheets().copyTo(
        spreadsheetId=config.spreadsheet_id,
        sheetId="2028955748",
        body={'destinationSpreadsheetId': config.spreadsheet_id}
    ).execute()
    print(new_worksheetid)

    requests = {
        "updateSheetProperties": {
            "properties": {
                "sheetId": new_worksheetid['sheetId'],
                "title": title,
            },
            "fields": "title",
        }
    }
    body = {
        'requests': requests
    }
    get_service_sacc().spreadsheets().batchUpdate(spreadsheetId=config.spreadsheet_id, body=body).execute()


if __name__ == "__main__":
  # Pass: title
  for i in range(1, 7):
    copy_sheet(main.get_date(datetime.now(), i))

