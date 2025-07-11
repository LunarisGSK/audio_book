from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class BookFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    book_name = models.CharField(max_length=255)
    book_description = models.TextField()
    predicted_genre = models.CharField(max_length=100)
    confidence = models.IntegerField()
    recommended_books = models.TextField()  # Stored as JSON string
    user_satisfied = models.BooleanField(null=True)  # True for like, False for dislike
    user_recommend = models.BooleanField(null=True)  # True for recommend, False for not recommend
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.book_name} - {self.predicted_genre}"

class UserRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_name = models.CharField(max_length=255)
    comment = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.book_name}"
