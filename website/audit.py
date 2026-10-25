from .models import AdminAuditLog, VisitorLog


def get_client_ip(request):
    """Extract real client IP address even when behind Nginx or proxy."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip or '127.0.0.1'


def parse_user_agent(user_agent_str):
    """Parse user agent into human-readable device and browser."""
    if not user_agent_str:
        return 'Nämälim enjam'
    ua = user_agent_str.lower()
    
    # Device category
    if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
        device = '📱 Telefon'
    elif 'ipad' in ua or 'tablet' in ua:
        device = '📱 Planşet'
    elif 'bot' in ua or 'spider' in ua or 'crawler' in ua:
        device = '🤖 Bot / Gözlegçi'
    else:
        device = '💻 Kompýuter'

    # Browser
    if 'edg/' in ua:
        browser = 'Edge'
    elif 'chrome/' in ua and 'opr' not in ua and 'edg' not in ua:
        browser = 'Chrome'
    elif 'safari/' in ua and 'chrome' not in ua:
        browser = 'Safari'
    elif 'firefox/' in ua:
        browser = 'Firefox'
    elif 'opera/' in ua or 'opr/' in ua:
        browser = 'Opera'
    elif 'bot' in ua:
        browser = 'Bot'
    else:
        browser = 'Brauzer'

    return f"{device} ({browser})"


def log_admin_action(request, action, module, object_repr='', details='', object_id=''):
    """
    Safely records an administrative activity in AdminAuditLog.
    Never raises an exception to avoid disrupting the main user request.
    """
    try:
        user = getattr(request, 'user', None)
        user_name = 'Anonim'
        user_obj = None
        if user and user.is_authenticated:
            user_name = user.username
            user_obj = user

        ip = get_client_ip(request)

        AdminAuditLog.objects.create(
            user=user_obj,
            user_name=user_name,
            action=action,
            module=module,
            object_id=str(object_id or '')[:100],
            object_repr=str(object_repr or '')[:255],
            details=str(details or ''),
            ip_address=ip,
        )
    except Exception as e:
        # Logging failure should not break administrative flow
        pass
