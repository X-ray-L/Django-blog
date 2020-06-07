from django.contrib import admin
from .models import Post,Category,Tag,UserInfo
# Register your models here.

class PostAdmin(admin.ModelAdmin):

    list_display = ['title', 'created_time', 'modified_time', 'category', 'author']
    fields = ['title', 'body', 'excerpt', 'category', 'author', 'tags']

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        super().save_model(request, obj, form, change)

class UserInfoAdmin(admin.ModelAdmin):

    list_display = ['username', 'gender', 'email', 'created_time', 'modified_time']
    fields = ['username', 'gender', 'email','password']

admin.site.register(Post,PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(UserInfo,UserInfoAdmin)