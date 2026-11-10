from django.contrib import admin
from .models import Banner, KnowledgeDoc, Script, Note, Tool, Announcement


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'sort_order', 'is_active', 'created_at']
    list_editable = ['sort_order', 'is_active']
    list_filter = ['is_active']


@admin.register(KnowledgeDoc)
class KnowledgeDocAdmin(admin.ModelAdmin):
    list_display = ['title', 'doc_type', 'category', 'views', 'is_shared', 'uploaded_at']
    list_editable = ['is_shared']
    list_filter = ['doc_type', 'category', 'is_shared']
    search_fields = ['title', 'summary']


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'downloads', 'is_shared', 'updated_at']
    list_editable = ['is_shared']
    search_fields = ['name', 'scene']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'tag', 'author', 'is_shared', 'published_at']
    list_editable = ['is_shared']
    list_filter = ['tag', 'is_shared']
    search_fields = ['title', 'content']


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_hot', 'is_new', 'created_at']
    list_editable = ['is_hot', 'is_new']
    list_filter = ['category', 'is_hot', 'is_new']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'ann_type', 'created_at']
    list_filter = ['ann_type']
