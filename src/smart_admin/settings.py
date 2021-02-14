from django.conf import settings

_SMART_ADMIN_SECTIONS = {
    'Security': ['auth',
                 ],
    'Logs': ['admin.LogEntry',
             ],
    'Other': [],
    '_hidden_': []
}

SECTIONS = getattr(settings, 'SMART_ADMIN_SECTIONS', _SMART_ADMIN_SECTIONS)
BOOKMARKS = getattr(settings, 'SMART_ADMIN_BOOKMARKS', [])
ENABLE_SWITCH = getattr(settings, 'SMART_ADMIN_SWITCH', True)
