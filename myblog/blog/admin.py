from django.contrib import admin
from .models import Post, Comment, Like, Category

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
