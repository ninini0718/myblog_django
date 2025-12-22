from django.core.mail import get_connection
from django.conf import settings
from decouple import config
import logging

logger = logging.getLogger(__name__)

class EmailManager:
    """邮件管理器，支持多个邮件提供商"""
    
    PROVIDERS = {
        'GMAIL': {
            'backend': 'core.email_backends.GmailAPIBackend',
            'priority': 1
        },
        'QQ': {
            'backend': 'django.core.mail.backends.smtp.EmailBackend',
            'priority': 2
        },
        'SENDGRID': {
            'backend': 'core.sendgrid_backend.SendGridBackend',
            'priority': 3
        }
    }
    
    def __init__(self):
        self.primary_provider = config('EMAIL_PRIMARY_PROVIDER', default='QQ').upper()
        self.fallback_providers = [
            p for p in self.PROVIDERS.keys() 
            if p != self.primary_provider
        ]
    
    def get_connection(self, provider=None):
        """获取邮件连接"""
        if not provider:
            provider = self.primary_provider
        
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unknown email provider: {provider}")
        
        provider_config = self.PROVIDERS[provider]
        
        # 动态配置邮件设置
        if provider == 'GMAIL':
            return self._get_gmail_connection()
        elif provider == 'QQ':
            return self._get_qq_connection()
        elif provider == 'SENDGRID':
            return self._get_sendgrid_connection()
    
    def _get_gmail_connection(self):
        """获取Gmail连接"""
        return get_connection(
            backend='core.email_backends.GmailAPIBackend',
            fail_silently=False
        )
    
    def _get_qq_connection(self):
        """获取QQ邮箱连接"""
        return get_connection(
            host=config('EMAIL_HOST_QQ'),
            port=config('EMAIL_PORT_QQ', cast=int),
            username=config('EMAIL_HOST_USER_QQ'),
            password=config('EMAIL_HOST_PASSWORD_QQ'),
            use_tls=config('EMAIL_USE_TLS_QQ', cast=bool, default=False),
            use_ssl=config('EMAIL_USE_SSL_QQ', cast=bool, default=True),
            fail_silently=False
        )
    
    def _get_sendgrid_connection(self):
        """获取SendGrid连接"""
        return get_connection(
            backend='core.sendgrid_backend.SendGridBackend',
            fail_silently=False
        )
    
    def send_email_with_fallback(self, message, providers=None):
        """使用备用方案发送邮件"""
        if not providers:
            providers = [self.primary_provider] + self.fallback_providers
        
        last_exception = None
        
        for provider in providers:
            try:
                connection = self.get_connection(provider)
                result = connection.send_messages([message])
                if result > 0:
                    logger.info(f"Email sent successfully via {provider}")
                    return True
            except Exception as e:
                last_exception = e
                logger.warning(f"Failed to send email via {provider}: {e}")
                continue
        
        # 所有提供商都失败
        if last_exception:
            logger.error(f"All email providers failed. Last error: {last_exception}")
            raise last_exception
        
        return False
    
    def test_all_providers(self):
        """测试所有邮件提供商"""
        from django.core.mail import EmailMessage
        
        test_message = EmailMessage(
            subject='邮件系统测试',
            body='这是一封测试邮件，用于验证邮件配置是否正常。',
            from_email=config('DEFAULT_FROM_EMAIL'),
            to=[config('TEST_EMAIL_ADDRESS', default=config('DEFAULT_FROM_EMAIL'))],
        )
        
        results = {}
        
        for provider in self.PROVIDERS.keys():
            try:
                connection = self.get_connection(provider)
                result = connection.send_messages([test_message])
                results[provider] = {
                    'status': 'success' if result > 0 else 'failed',
                    'message': f'Sent {result} messages'
                }
            except Exception as e:
                results[provider] = {
                    'status': 'error',
                    'message': str(e)
                }
        
        return results

# 创建全局邮件管理器实例
email_manager = EmailManager()
