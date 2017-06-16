from django.conf.urls import include, url
from django.contrib import admin

from aim.views import IndexView 

urlpatterns = [
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', IndexView.as_view(),name="index" ),

    url(r'^aim/', include('aim.urls') ),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/', include('allauth.urls')),

    url(r'^graph/', include('graphs.urls')),

]
