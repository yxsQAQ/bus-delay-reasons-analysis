"""data_visualization URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from app01 import views
from django.conf import settings
from django.views.static import serve
from app01.views import admin,account,chart
from django.views.generic.base import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(url='/login/'), name='index_redirect'),
    # path('admin/', admin.site.urls),

    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}, name='media'),

    # User management
    path('admin/home/', admin.admin_home),
    path('admin/about/', admin.admin_about),
    path('admin/list/', admin.admin_list),
    path('admin/add/', admin.admin_add),
    path('admin/<int:nid>/delete/', admin.admin_delete),
    path('admin/<int:nid>/reset/', admin.admin_reset),

    # Login system
    path('login/', account.login),
    path('logout/', account.logout),
    path('img/code/', account.img_code),

    # Operators
    path('chart/operator/', chart.operator),

    # Lines
    path('chart/line/', chart.line),

    # Directions
    path('chart/direction/', chart.direction),

    # Times
    path('chart/time/', chart.time),

    # maps
    path('chart/map/', chart.map),

    # heatmap
    path('chart/heatmap/', chart.heatmap),
]
