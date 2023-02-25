from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarMake, CarModel
from .restapis import get_dealers_from_cf, get_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import datetime

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.

# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request,'./djangoapp/about_us.html',context)

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    return render(request,'./djangoapp/contact_us.html',context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://us-east.functions.appdomain.cloud/api/v1/web/992fb9ea-d250-4950-a077-7c45c08512cc/dealership-package/get-dealership.json"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealerships'] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == 'GET':
        context = {}
        url_reviews = "https://us-east.functions.appdomain.cloud/api/v1/web/992fb9ea-d250-4950-a077-7c45c08512cc/dealership-package/get-review.json?id=" + str(dealer_id)
        url_dealers = "https://us-east.functions.appdomain.cloud/api/v1/web/992fb9ea-d250-4950-a077-7c45c08512cc/dealership-package/get-dealership.json" 
        reviews = get_reviews_from_cf(url_reviews,dealer_id)
        dealer = get_dealers_from_cf(url_dealers, dealer_id = dealer_id)
        context['reviews'] = reviews
        context['dealer'] = dealer
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method == 'POST':
        user = request.user
        url_post = "https://us-east.functions.appdomain.cloud/api/v1/web/992fb9ea-d250-4950-a077-7c45c08512cc/dealership-package/post-review"
        username = None
        if request.user.is_authenticated:
            review  = dict()
            review["name"] = request.user.get_username()
            review["dealership"] = dealer_id
            review["review"] = request.POST['reviewContent']
            review["purchase"] = request.POST.get('purchasecheck', False)

            if request.POST.get('purchasecheck', False):
                car_model = CarModel.objects.get(id = int(request.POST["car"]))
                review["purchase_date"] = datetime.datetime.strptime(request.POST['purchasedate'], "%Y-%m-%d").strftime("%d/%m/%Y")
                review["car_make"] = car_model.carMake.name
                review["car_model"] = car_model.name
                review["car_year"] = car_model.year.strftime("%Y")
            json_payload = dict()
            json_payload["review"] = review
            response = post_request(url_post, json_payload, dealerId=dealer_id)
            if response.status_code == 200:
                return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
            else:
                return HttpResponse("Could not add the review")
    elif request.method == 'GET':
        context = {}
        url_dealers = "https://us-east.functions.appdomain.cloud/api/v1/web/992fb9ea-d250-4950-a077-7c45c08512cc/dealership-package/get-dealership.json"
        dealer = get_dealers_from_cf(url_dealers, dealer_id = dealer_id)
        context["dealer"] = dealer
        car_models = []
        for model in CarModel.objects.filter(dealerId = dealer_id):
            car = {}
            car["id"] = model.id
            car["year"] = model.year
            car["name"] = model.name
            car["make"] = model.carMake.name
            car_models.append(car)
        context["car_models"] = car_models
        return render(request, 'djangoapp/add_review.html', context)