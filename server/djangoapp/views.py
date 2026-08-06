import json
from datetime import date

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import CarMake, CarModel


DEALERS = [
    {"id": 1, "full_name": "Best Cars Chicago", "city": "Chicago", "address": "100 Michigan Ave", "zip": "60601", "state": "IL", "lat": 41.8781, "long": -87.6298},
    {"id": 2, "full_name": "Best Cars Topeka", "city": "Topeka", "address": "725 Kansas Ave", "zip": "66603", "state": "KS", "lat": 39.0473, "long": -95.6752},
    {"id": 3, "full_name": "Best Cars Wichita", "city": "Wichita", "address": "455 Douglas Ave", "zip": "67202", "state": "KS", "lat": 37.6872, "long": -97.3301},
    {"id": 4, "full_name": "Best Cars Austin", "city": "Austin", "address": "210 Congress Ave", "zip": "78701", "state": "TX", "lat": 30.2672, "long": -97.7431},
    {"id": 5, "full_name": "Best Cars Seattle", "city": "Seattle", "address": "500 Pine St", "zip": "98101", "state": "WA", "lat": 47.6062, "long": -122.3321},
]

REVIEWS = [
    {"id": 1, "dealership": 2, "name": "Alicia Morgan", "review": "Fantastic services and a friendly sales team.", "purchase": True, "purchase_date": "2026-06-20", "car_make": "Toyota", "car_model": "Camry", "car_year": 2023, "sentiment": "positive"},
    {"id": 2, "dealership": 2, "name": "Marcus Lee", "review": "Clear pricing and a smooth test drive.", "purchase": True, "purchase_date": "2026-05-12", "car_make": "Ford", "car_model": "Explorer", "car_year": 2022, "sentiment": "positive"},
    {"id": 3, "dealership": 4, "name": "Sofia Patel", "review": "The wait was long, but the staff resolved my issue.", "purchase": False, "purchase_date": "2026-04-05", "car_make": "Honda", "car_model": "Civic", "car_year": 2021, "sentiment": "neutral"},
]


def dealers_page(request, state="All"):
    matches = DEALERS if state in ("", "All") else [dealer for dealer in DEALERS if dealer["state"].lower() == state.lower()]
    return render(request, "dealers_page.html", {"dealers": matches, "states": sorted({d["state"] for d in DEALERS}), "selected_state": state})


def dealer_page(request, dealer_id):
    dealer = next((item for item in DEALERS if item["id"] == dealer_id), None)
    if dealer is None:
        return redirect("/dealers/")
    reviews = [dict(item, sentiment=_sentiment(item["review"])) for item in REVIEWS if item["dealership"] == dealer_id]
    return render(request, "dealer_page.html", {"dealer": dealer, "reviews": reviews})


def postreview_page(request, dealer_id):
    dealer = next((item for item in DEALERS if item["id"] == dealer_id), None)
    if dealer is None:
        return redirect("/dealers/")
    return render(request, "postreview_page.html", {"dealer": dealer})


def _payload(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return {}


def _sentiment(text):
    value = text.lower()
    positive = ("fantastic", "excellent", "great", "friendly", "smooth", "love", "helpful")
    negative = ("bad", "poor", "terrible", "awful", "rude", "hate")
    if any(word in value for word in positive):
        return "positive"
    if any(word in value for word in negative):
        return "negative"
    return "neutral"


@csrf_exempt
def registration(request):
    data = _payload(request)
    username = data.get("userName", "")
    if not username or not data.get("password"):
        return JsonResponse({"status": "Error", "message": "Username and password are required"}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"status": "Error", "message": "User already exists"}, status=409)
    user = User.objects.create_user(
        username=username,
        password=data["password"],
        email=data.get("email", ""),
        first_name=data.get("firstName", ""),
        last_name=data.get("lastName", ""),
    )
    login(request, user)
    return JsonResponse({"status": "Authenticated", "userName": user.username, "firstName": user.first_name, "lastName": user.last_name})


@csrf_exempt
def login_user(request):
    data = _payload(request)
    user = authenticate(username=data.get("userName"), password=data.get("password"))
    if user is None:
        return JsonResponse({"status": "Error", "message": "Invalid credentials"}, status=401)
    login(request, user)
    return JsonResponse({"status": "Authenticated", "userName": user.username, "firstName": user.first_name, "lastName": user.last_name})


def logout_request(request):
    username = request.user.username if request.user.is_authenticated else "guest"
    logout(request)
    return JsonResponse({"status": "Logged out", "userName": username})


def get_dealerships(request, state="All"):
    matches = DEALERS if state in ("", "All") else [dealer for dealer in DEALERS if dealer["state"].lower() == state.lower()]
    return JsonResponse({"status": 200, "dealers": matches})


def get_dealer_details(request, dealer_id):
    dealer = next((dealer for dealer in DEALERS if dealer["id"] == dealer_id), None)
    if dealer is None:
        return JsonResponse({"status": 404, "message": "Dealer not found"}, status=404)
    return JsonResponse({"status": 200, "dealer": [dealer]})


def get_dealer_reviews(request, dealer_id):
    matches = [dict(review, sentiment=_sentiment(review["review"])) for review in REVIEWS if review["dealership"] == dealer_id]
    return JsonResponse({"status": 200, "reviews": matches})


def get_cars(request):
    models = list(CarModel.objects.select_related("car_make").all())
    if not models:
        fallback = [("Toyota", "Camry", "Sedan", 2023), ("Ford", "Explorer", "SUV", 2022), ("Honda", "Civic", "Sedan", 2021)]
        cars = [{"CarMake": make, "CarModel": model, "CarType": car_type, "CarYear": year} for make, model, car_type, year in fallback]
    else:
        cars = [{"CarMake": item.car_make.name, "CarModel": item.name, "CarType": item.car_type, "CarYear": item.year} for item in models]
    return JsonResponse({"status": 200, "CarModels": cars})


def analyze_review(request, text):
    return JsonResponse({"sentiment": _sentiment(text), "text": text})


@csrf_exempt
def add_review(request):
    data = _payload(request)
    review = {
        "id": max(item["id"] for item in REVIEWS) + 1,
        "dealership": int(data.get("dealership", 1)),
        "name": data.get("name") or (request.user.get_full_name() if request.user.is_authenticated else "Guest"),
        "review": data.get("review", ""),
        "purchase": bool(data.get("purchase", False)),
        "purchase_date": data.get("purchase_date", str(date.today())),
        "car_make": data.get("car_make", "Toyota"),
        "car_model": data.get("car_model", "Camry"),
        "car_year": int(data.get("car_year", 2023)),
    }
    review["sentiment"] = _sentiment(review["review"])
    REVIEWS.append(review)
    return JsonResponse({"status": 200, "review": review})
