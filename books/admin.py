from django.contrib import admin
from .models import BookFeedback, UserRecommendation

@admin.register(BookFeedback)
class BookFeedbackAdmin(admin.ModelAdmin):
    list_display = ('book_name', 'predicted_genre', 'confidence', 'user_satisfied', 'user_recommend', 'timestamp', 'user')
    list_filter = ('predicted_genre', 'user_satisfied', 'user_recommend', 'timestamp')
    search_fields = ('book_name', 'book_description', 'predicted_genre')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

@admin.register(UserRecommendation)
class UserRecommendationAdmin(admin.ModelAdmin):
    list_display = ('book_name', 'user', 'comment', 'timestamp')
    list_filter = ('timestamp', 'user')
    search_fields = ('book_name', 'comment', 'user__username')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
