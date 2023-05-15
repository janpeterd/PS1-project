"""djangoProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from MyPlanner import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", views.form, name="form"),
    path("gids-toewijzen/<str:id>", views.assignGuide, name="assignGuide"),
    path("nieuwe-gids/", views.createGuideUser, name="createGuideUser"),
    path("bezoek-verwijderen/<str:id>", views.delete_visit, name="delete_visit"),
    path("bezoek/<str:id>", views.visits, name="visits"),
    path("bezoeken/", views.all_visits, name="all_visits"),
    path("filter-bezoeken/", views.all_guide_visits, name="all_guide_visits"),
    path("archief-bezoeken/", views.all_archived_visits, name="all_archived_visits"),
    path(
        "archive-and-notify/<str:id>",
        views.archive_and_notify,
        name="archive_and_notify",
    ),
    path("bezoek-bewerken/<str:id>", views.edit_visit, name="edit_visit"),
    path("api/checkvisits/", views.checkvisits, name="checkvisits"),
]
