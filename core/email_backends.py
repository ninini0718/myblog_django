from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import os
import pickle
from django.conf import settings

class GmailAPIBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """认证Gmail API"""
        creds = None
        token_path = settings.GMAIL_TOKEN_PATH
        credentials_path = settings.GMAIL_CREDENTIALS_PATH
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = Flow.from_client_secrets_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/gmail.send']
                )
                # 修改为使用localhost的固定端口
                flow.redirect_uri = 'http://localhost:8080/'
                auth_url, _ = flow.authorization_url(prompt='consent')
                
                print(f"\n请访问以下URL进行Gmail授权:")
                print(f"{auth_url}\n")
                
                # 在生产环境中，应该使用web界面获取授权码
                # 这里简化处理，需要手动输入授权码
                auth_code = input("请输入授权码: ")
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
            
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
    
    def send_messages(self, email_messages):
        """发送邮件"""
        if not self.service:
            return False
        
        sent_count = 0
        for message in email_messages:
            try:
                self._send_message(message)
                sent_count += 1
            except Exception as e:
                if not self.fail_silently:
                    raise
                print(f"Failed to send email via Gmail: {e}")
        
        return sent_count
    
    def _send_message(self, email_message):
        """发送单个邮件"""
        if isinstance(email_message, EmailMessage):
            message = MIMEMultipart()
            message['to'] = ', '.join(email_message.to)
            message['from'] = email_message.from_email
            message['subject'] = email_message.subject
            
            # 添加正文
            if email_message.content_subtype == 'html':
                msg = MIMEText(email_message.body, 'html')
            else:
                msg = MIMEText(email_message.body, 'plain')
            message.attach(msg)
            
            # 添加附件
            for attachment in email_message.attachments:
                self._add_attachment(message, attachment)
            
            # 编码消息
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # 发送
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
    
    def _add_attachment(self, message, attachment):
        """添加附件"""
        from email.mime.base import MIMEBase
        from email import encoders
        
        filename, content, mimetype = attachment
        part = MIMEBase(*mimetype.split('/'))
        part.set_payload(content)
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )
        message.attach(part)
