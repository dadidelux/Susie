from django.urls import path
from . import views

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatSessionViewSet, ChatHistoryViewSet, AllRecordsView

router = DefaultRouter()
router.register(r"chatsessions", ChatSessionViewSet)
router.register(r"chathistories", ChatHistoryViewSet)

urlpatterns = [
    path("", views.home, name="home"),
    path("api/", include(router.urls)),
    path(
        "api/allrecords/", AllRecordsView.as_view({"get": "list"}), name="all-records"
    ),
    path("answer", views.answer, name="answer"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("upload/", views.upload_view, name="upload"),
    # path('markdown/', views.content , name='logout'),
    path("create_new_chat/", views.create_new_chat, name="create_new_chat"),
    path(
        "get_chat_history/<int:session_id>/",
        views.get_chat_history,
        name="get_chat_history",
    ),
    path(
        "change_session/<int:session_id>/", views.change_session, name="change_session"
    ),
]
