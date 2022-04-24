from django.urls import path, re_path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
	re_path(r'^$', views.home, name="redirect"),
	path("register/", views.register, name="register"),
	re_path(r'^password/$', views.change_password, name="change_password"),
	re_path(r'^logout/$', views.logout_, name="logout_"),
	path('', include("django.contrib.auth.urls")),

	path("home/", views.home, name="home"),
	path("create/", views.create, name="create"),
	path("quick-post/", views.quickpost, name="quick-post"),

	path("collections/<str:username>/", views.collections, name="collections"),
	path("collections/<int:id>", views.delete_collection, name="delete_collection"),

	path("data/<int:id>", views.data, name="data"),
	path("all_stats/", views.all_stats, name="data2"),
	path("accurate_data/<int:id>", views.accurate_data, name="accurate_data")
]

