from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from core.email_manager import email_manager
from django.core.mail import EmailMessage
from decouple import config

def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def test_email_providers(request):
    """测试所有邮件提供商"""
    if request.method == 'POST':
        results = email_manager.test_all_providers()
        return JsonResponse({'results': results})
    
    return render(request, 'core/test_email.html')

@login_required
def send_test_email(request):
    """发送测试邮件"""
    if request.method == 'POST':
        recipient = request.POST.get('recipient')
        provider = request.POST.get('provider', 'AUTO')
        
        message = EmailMessage(
            subject='测试邮件',
            body='这是一封测试邮件，用于验证邮件系统是否正常工作。',
            from_email=config('DEFAULT_FROM_EMAIL'),
            to=[recipient],
        )
        
        try:
            if provider == 'AUTO':
                success = email_manager.send_email_with_fallback(message)
            else:
                connection = email_manager.get_connection(provider)
                result = connection.send_messages([message])
                success = result > 0
            
            if success:
                messages.success(request, f'邮件发送成功！使用提供商: {provider}')
            else:
                messages.error(request, '邮件发送失败')
        except Exception as e:
            messages.error(request, f'邮件发送失败: {str(e)}')
        
        return redirect('core:test_email')
    
    return render(request, 'core/send_test_email.html')
