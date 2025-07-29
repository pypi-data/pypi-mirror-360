from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'admin', 'practet.admin_urls', name='admin'),
    host(r'api', 'practet.api_urls', name='api'),
    host('', 'practet.urls', name='default')
)
