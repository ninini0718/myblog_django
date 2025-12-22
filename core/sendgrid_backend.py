from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import os
from base64 import b64encode
from django.conf import settings

class SendGridBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = settings.SENDGRID_API_KEY
    
    def send_messages(self, email_messages):
        """发送邮件"""
        if not self.api_key:
            if not self.fail_silently:
                raise ValueError('SENDGRID_API_KEY not configured')
            return 0
        
        sent_count = 0
        for message in email_messages:
            try:
                self._send_message(message)
                sent_count += 1
            except Exception as e:
                if not self.fail_silently:
                    raise
                print(f"Failed to send email via SendGrid: {e}")
        
        return sent_count
    
    def _send_message(self, email_message):
        """发送单个邮件"""
        # 处理多个收件人
        to_emails = email_message.to
        if isinstance(to_emails, str):
            to_emails = [to_emails]
        
        message = Mail(
            from_email=email_message.from_email,
            to_emails=to_emails,
            subject=email_message.subject,
            html_content=email_message.body if email_message.content_subtype == 'html' else None,
            plain_text_content=email_message.body if email_message.content_subtype == 'plain' else None
        )
        
        # 添加抄送和密送
        if email_message.cc:
            message.cc = email_message.cc
        if email_message.bcc:
            message.bcc = email_message.bcc
        
        # 添加附件
        for attachment in email_message.attachments:
            filename, content, mimetype = attachment
            encoded = b64encode(content).decode()
            attached_file = Attachment(
                FileContent(encoded),
                FileName(filename),
                FileType(mimetype),
                Disposition('attachment')
            )
            message.add_attachment(attached_file)
        
        sg = SendGridAPIClient(self.api_key)
        response = sg.send(message)
        
        if response.status_code not in [200, 202]:
            raise Exception(f"SendGrid API error: {response.status_code} - {response.body}")
