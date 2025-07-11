from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('predict/', views.predict_genre, name='predict_genre'),
    path('feedback/', views.save_feedback, name='save_feedback'),
    path('add-recommendation/', views.add_recommendation, name='add_recommendation'),
    path('my-recommendations/', views.my_recommendations, name='my_recommendations'),
    path('feedback-history/', views.feedback_history, name='feedback_history'),
] 