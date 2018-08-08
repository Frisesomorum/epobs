"""epobs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from epobs import views as indexViews
from finance.views import terms as termViews
from students import views as studentViews

urlpatterns = [
    re_path(r'^$', indexViews.index, name='index'),
    path('admin/', admin.site.urls, name='admin'),

    re_path(r'finance/terms/create/$', termViews.create.as_view(), name='create_term'),
    re_path(r'finance/terms/edit/(?P<pk>\d+)/$', termViews.edit.as_view(), name='edit_term'),
    re_path(r'finance/terms/$', termViews.list.as_view(), name='list_term'),

    re_path(r'students/add/$', studentViews.add.as_view(), name='add_students'),
    re_path(r'students/edit/(?P<pk>\d+)/$', studentViews.edit.as_view(), name='edit_students'),
    re_path(r'students/$', studentViews.list, name='list_students'),
]
