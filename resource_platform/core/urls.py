from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.index, name='index'),
    path('knowledge/', views.knowledge_list, name='knowledge'),
    path('knowledge/upload/', views.doc_upload, name='doc_upload'),
    path('knowledge/<int:pk>/', views.doc_detail, name='doc_detail'),
    path('knowledge/<int:pk>/edit/', views.doc_edit, name='doc_edit'),
    path('knowledge/<int:pk>/delete/', views.doc_delete, name='doc_delete'),
    path('knowledge/<int:pk>/download/', views.doc_download, name='doc_download'),
    path('scripts/', views.script_list, name='scripts'),
    path('scripts/upload/', views.script_upload, name='script_upload'),
    path('scripts/<int:pk>/', views.script_detail, name='script_detail'),
    path('scripts/<int:pk>/edit/', views.script_edit, name='script_edit'),
    path('scripts/<int:pk>/delete/', views.script_delete, name='script_delete'),
    path('scripts/<int:pk>/download/', views.script_download, name='script_download'),
    path('notes/', views.note_list, name='notes'),
    path('notes/create/', views.note_create, name='note_create'),
    path('notes/<int:pk>/', views.note_detail, name='note_detail'),
    path('notes/<int:pk>/edit/', views.note_edit, name='note_edit'),
    path('notes/<int:pk>/download/', views.note_download, name='note_download'),
    path('notes/<int:pk>/delete/', views.note_delete, name='note_delete'),
    path('tools/', views.tool_list, name='tools'),
]

