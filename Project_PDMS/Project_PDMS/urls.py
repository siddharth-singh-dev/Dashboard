from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # Import settings to check DEBUG mode

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # Patients app (root-level routing)
    path('', include(('patients.urls', 'patients'), namespace='patients')),

    # Debug Toolbar (development only)
]

# Include debug toolbar URLs if in DEBUG mode
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
