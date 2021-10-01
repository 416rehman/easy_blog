from django.contrib import admin
from .models import Post, Profile, Report


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_on', 'status', 'slug')
    list_filter = ('status',)
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}


class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'user', 'post', 'reason', 'created_on', 'comment')
    list_filter = ('reason',)
    search_fields = ['comment', 'user', 'post', 'reporter', 'closing_comment']



admin.site.register(Post, PostAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Profile)
