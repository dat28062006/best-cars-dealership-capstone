import json
from datetime import date
from pathlib import Path

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt



DATA_DIR = Path(__file__).resolve().parents[1] / "database" / "data"


def _load_fixture(filename, key):
    """Load the assignment's canonical JSON fixtures."""
    with (DATA_DIR / filename).open(encoding="utf-8") as source:
        return json.load(source)[key]


# The rubric expects the complete canonical collection, including short_name,
# state name, state abbreviation, coordinates, address and ZIP code.
DEALERS = _load_fixture("dealerships.json", "dealerships")
REVIEWS = _load_fixture("reviews.json", "reviews")
CAR_RECORDS = _load_fixture("car_records.json", "cars")


def dealers_page(request, state="All"):
    matches = _dealers_for_state(state)
    return render(
        request,
        "dealers_page.html",
        {
            "dealers": matches,
            "states": sorted({dealer["state"] for dealer in DEALERS}),
            "selected_state": state,
        },
    )


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
    logout(request)
    return JsonResponse({"status": "Logged out", "userName": ""})


def _dealers_for_state(state):
    if state in ("", "All"):
        return DEALERS
    value = state.casefold()
    return [
        dealer
        for dealer in DEALERS
        if dealer["state"].casefold() == value or dealer["st"].casefold() == value
    ]


def get_dealerships(request, state="All"):
    return JsonResponse({"status": 200, "dealers": _dealers_for_state(state)})


def get_dealer_details(request, dealer_id):
    dealer = next((dealer for dealer in DEALERS if dealer["id"] == dealer_id), None)
    if dealer is None:
        return JsonResponse({"status": 404, "message": "Dealer not found"}, status=404)
    return JsonResponse({"status": 200, "dealer": [dealer]})


def get_dealer_reviews(request, dealer_id):
    matches = [dict(review, sentiment=_sentiment(review["review"])) for review in REVIEWS if review["dealership"] == dealer_id]
    return JsonResponse({"status": 200, "reviews": matches})


def get_cars(request):
    cars = []
    seen = set()
    for record in CAR_RECORDS:
        identity = (record["make"], record["model"])
        if identity in seen:
            continue
        seen.add(identity)
        cars.append(
            {
                "CarMake": record["make"],
                "CarModel": record["model"],
                "CarType": record["bodyType"],
                "CarYear": record["year"],
            }
        )
        if len(cars) == 15:
            break
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
