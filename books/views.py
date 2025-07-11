from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.utils import timezone
import json
import random
from decouple import config
from .models import BookFeedback, UserRecommendation

# Initialize OpenAI with error handling
try:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=config('OPENAI_API_KEY', default='')
    )
except Exception as e:
    llm = None
    print(f"Warning: OpenAI not initialized: {e}")

genres = ['fantasy', 'science', 'crime', 'history', 'horror', 'thriller',
          'psychology', 'romance', 'sports', 'travel']

suggestion_books = [
    "To Kill a Mockingbird", "1984", "Harry Potter and the Philosopher's Stone",
    "The Hobbit", "Pride and Prejudice", "The Da Vinci Code", "The Catcher in the Rye",
    "The Alchemist", "The Great Gatsby", "Moby Dick", "Crime and Punishment",
    "Brave New World", "Gone Girl", "The Shining", "The Girl with the Dragon Tattoo",
    "Thinking, Fast and Slow", "Twilight", "Moneyball", "Eat, Pray, Love", "Inferno"
]

def index(request):
    if request.user.is_authenticated:
        suggestions = random.sample(suggestion_books, 5)
        return render(request, 'books/index.html', {'suggestions': suggestions})
    else:
        return render(request, 'books/login.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('index')
        else:
            messages.error(request, 'Error creating account. Please try again.')
    else:
        form = UserCreationForm()
    return render(request, 'books/signup.html', {'form': form})

@login_required
def predict_genre(request):
    if request.method == 'POST':
        book_name = request.POST.get('book_name')
        book_description = request.POST.get('book_description')
        
        if not book_name or not book_description:
            messages.error(request, 'Please provide both book name and description.')
            return redirect('index')
        
        if not llm:
            messages.error(request, 'OpenAI API is not configured. Please set your OPENAI_API_KEY in the .env file.')
            return redirect('index')
        
        messages = [
            (
                "system",
                "You are a helpful assistant that predicts the genre of a book based on its name and description. "
                f"Choose one genre only from this list: {genres}. "
                "Also provide a confidence score between 30 and 79 (not more than 80). "
                "Then, recommend 5 famous books from that genre.\n\n"
                "Respond ONLY in the following JSON format:\n"
                "{\n"
                "  \"genre\": \"chosen_genre\",\n"
                "  \"confidence\": number,\n"
                "  \"recommended_books\": [\"book1\", \"book2\", \"book3\", \"book4\", \"book5\"]\n"
                "}\n"
                "Do not add any explanation, only output valid JSON."
            ),
            (
                "human", 
                f"Book Name: {book_name}\nDescription: {book_description}"
            ),
        ]

        try:
            ai_msg = llm.invoke(messages)
            clean_content = ai_msg.content.replace('```json', '').replace('```', '').strip()
            result = json.loads(clean_content)
            result['book_name'] = book_name
            result['book_description'] = book_description
            return render(request, 'books/result.html', {'result': result})
        except Exception as e:
            messages.error(request, f'Error predicting genre: {str(e)}')
            return redirect('index')
    
    return redirect('index')

@csrf_exempt
@require_http_methods(["POST"])
def save_feedback(request):
    try:
        data = json.loads(request.body)
        feedback = BookFeedback.objects.create(
            user=request.user if request.user.is_authenticated else None,
            book_name=data.get("book_name", ""),
            book_description=data.get("book_description", ""),
            predicted_genre=data.get("genre", ""),
            confidence=data.get("confidence", 0),
            recommended_books=json.dumps(data.get("recommended_books", [])),
            user_satisfied=data.get("satisfied"),
            user_recommend=data.get("recommend")
        )
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

@login_required
def add_recommendation(request):
    if request.method == 'POST':
        book_name = request.POST.get('book_name')
        comment = request.POST.get('comment')
        
        if book_name and comment:
            UserRecommendation.objects.create(
                user=request.user,
                book_name=book_name,
                comment=comment
            )
            messages.success(request, 'Recommendation added successfully!')
        else:
            messages.error(request, 'Please provide both book name and comment.')
    
    return redirect('index')

@login_required
def my_recommendations(request):
    recommendations = UserRecommendation.objects.filter(user=request.user)
    return render(request, 'books/my_recommendations.html', {'recommendations': recommendations})

@login_required
def feedback_history(request):
    feedbacks = BookFeedback.objects.filter(user=request.user)
    return render(request, 'books/feedback_history.html', {'feedbacks': feedbacks})
