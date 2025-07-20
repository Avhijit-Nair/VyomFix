import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import csv
import logging
logging.basicConfig(level=logging.INFO)

SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_google_creds():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def create_or_update_report_doc(report_title, initial_content, doc_id=None, table_csv_path=None):
    creds = get_google_creds()
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    try:
        if doc_id is None:
            logging.info('Creating new Google Doc...')
            doc = docs_service.documents().create(body={"title": report_title}).execute()
            doc_id = doc['documentId']
            requests = []
            # Insert initial content at end
            requests.append({
                "insertText": {
                    "endOfSegmentLocation": {"segmentId": ""},
                    "text": initial_content + '\n'
                }
            })
            # Insert compliance mapping as plain text if available
            mapping_txt_path = None
            if table_csv_path:
                mapping_txt_path = table_csv_path.replace('_report.csv', '_report.txt')
            if mapping_txt_path and os.path.exists(mapping_txt_path):
                with open(mapping_txt_path, encoding='utf-8') as f:
                    mapping_text = f.read()
                requests.append({
                    "insertText": {
                        "endOfSegmentLocation": {"segmentId": ""},
                        "text": '\nCompliance Mapping Report:\n' + mapping_text + '\n'
                    }
                })
            logging.info('Sending batchUpdate to Google Docs API (insert content and mapping text)...')
            docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
            # Set sharing to anyone with the link can edit (optional, can be changed)
            drive_service.permissions().create(
                fileId=doc_id,
                body={"type": "anyone", "role": "writer"},
                fields='id'
            ).execute()
        else:
            # Update existing doc (append content)
            requests = [
                {"insertText": {"endOfSegmentLocation": {"segmentId": ""}, "text": initial_content + '\n'}}
            ]
            docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
        doc_url = f'https://docs.google.com/document/d/{doc_id}/edit'
        logging.info(f'Google Doc created/updated: {doc_url}')
        return doc_id, doc_url
    except Exception as e:
        logging.error(f'Error in create_or_update_report_doc: {e}')
        raise 