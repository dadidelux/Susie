from django.urls import path
from .import views


urlpatterns = [
    path('', views.home, name='home' ),
    path('answer', views.answer, name='answer'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_view, name='upload'),
    
    # path('markdown/', views.content , name='logout'),
    path('create_new_chat/', views.create_new_chat, name='create_new_chat'),
    path('get_chat_history/<int:session_id>/', views.get_chat_history, name='get_chat_history'),
    path('change_session/<int:session_id>/', views.change_session, name='change_session'),

]