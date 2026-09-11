from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.index, name='index'),
    path('knowledge/', views.knowledge_list, name='knowledge'),
    path('knowledge/<int:pk>/', views.doc_detail, name='doc_detail'),
    path('knowledge/<int:pk>/download/', views.doc_download, name='doc_download'),
    path('scripts/', views.script_list, name='scripts'),
    path('scripts/<int:pk>/', views.script_detail, name='script_detail'),
    path('scripts/<int:pk>/download/', views.script_download, name='script_download'),
    path('notes/', views.note_list, name='notes'),
    path('notes/<int:pk>/', views.note_detail, name='note_detail'),
    path('tools/', views.tool_list, name='tools'),
]
