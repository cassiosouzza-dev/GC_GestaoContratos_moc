import os.path
import io
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
# Mudamos aqui: trocamos MediaFileUpload por MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

class DriveConector:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.creds = None
        self.service = None
        
    def conectar(self):
        """Gerencia login e tokens"""
        # 1. Tenta carregar token existente
        if os.path.exists('token.json'):
            try:
                self.creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
            except:
                self.creds = None
        
        # 2. Se não tem credencial válida, faz login
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except:
                    self.creds = None

            if not self.creds:
                if not os.path.exists('credentials.json'):
                    raise Exception("ERRO: 'credentials.json' não encontrado!")
                
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                # Tenta abrir navegador, se falhar, use run_console()
                self.creds = flow.run_local_server(port=0)
            
            # Salva o novo token
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('drive', 'v3', credentials=self.creds)

    def buscar_id_arquivo(self, nome_arquivo):
        if not self.service: self.conectar()
        query = f"name = '{nome_arquivo}' and trashed = false"
        results = self.service.files().list(q=query, pageSize=1, fields="files(id, name)").execute()
        items = results.get('files', [])
        return items[0] if items else None

    def baixar_json(self, file_id):
        if not self.service: self.conectar()
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False: 
            status, done = downloader.next_chunk()
        fh.seek(0)
        return json.load(fh)

    def subir_json(self, nome_arquivo, dados_dict, file_id_existente=None):
        if not self.service: self.conectar()
        
        # --- MUDANÇA CRUCIAL AQUI ---
        # Não criamos mais arquivo no disco. Criamos na memória RAM.
        arquivo_na_memoria = io.BytesIO(json.dumps(dados_dict, indent=4, ensure_ascii=False).encode('utf-8'))
        
        media = MediaIoBaseUpload(arquivo_na_memoria, mimetype='application/json', resumable=True)

        if file_id_existente:
            self.service.files().update(fileId=file_id_existente, media_body=media).execute()
        else:
            self.service.files().create(body={'name': nome_arquivo}, media_body=media).execute()
        
        # Não precisa mais de os.remove(), pois nada foi gravado no HD.