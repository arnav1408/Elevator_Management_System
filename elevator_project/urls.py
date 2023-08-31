from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('elevator_app.urls')),  # Adding the elevator app API endpoints
]
