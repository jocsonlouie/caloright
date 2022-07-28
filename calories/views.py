from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.http import HttpResponse
from .forms import SelectFoodForm, AddFoodForm, CreateUserForm, ProfileForm
from .models import *
from datetime import timedelta
from django.utils import timezone
from datetime import date
from datetime import datetime
from .filters import FoodFilter


def BasePageView(request):
    current_user = request.user.is_staff
    context = {
        "current_user": current_user
    }
    return render(request, 'base.html', context)


def allGender(request):
    if request.method == 'GET':
        current_gender = request.GET['gender']
        current_user = request.user
        u = Gender(gender=current_gender, user=request.user)
        result = Gender.objects.filter(Q(user__icontains=current_user))
        if len(result) == 1:
            print("User Exist ")
        elif len(result) > 1:
            print("Many users ")
        else:
            u.save()
            return HttpResponse("Success!")
    else:
        return HttpResponse("Request method is not a GET")


@login_required(login_url='login')
def AnalyticsPageView(request):
    users = User.objects.all()
    today = datetime.today().date()
    now = timezone.now()
    # new_register = User.objects.filter(date_joined__date=today)
    new_register = User.objects.filter(
        date_joined__gte=datetime.now()-timedelta(days=7)).count()

    guess_users = Count.objects.all().count()

    calories = Profile.objects.filter(person_of=request.user).last()
    all_food_today = PostFood.objects.filter(profile=calories)

    genderOtherCount = Gender.objects.filter(gender='Rather not say').count()
    genderMaleCount = Gender.objects.filter(gender='Male').count()
    genderFemaleCount = Gender.objects.filter(gender='Female').count()

    context = {
        "users": users,
        "users_count": users.count,
        "user_new_count": new_register,
        "guess_users": guess_users,
        "food_for_today": all_food_today,
        "genderOtherCount": genderOtherCount,
        "genderMaleCount": genderMaleCount,
        "genderFemaleCount": genderFemaleCount
    }
    return render(request, 'analytics.html', context)


# home page view


def HomePageView(request):
    def get_ip(request):
        address = request.META.get('HTTP_X_FORWARDED_FOR')
        if address:
            ip = address.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    ip = get_ip(request)
    u = Count(count=ip)
    result = Count.objects.filter(Q(count__icontains=ip))
    if len(result) == 1:
        print("User Exist ")
    elif len(result) > 1:
        print("Many users ")
    else:
        u.save()
        print("User unique ")

    guess_users = Count.objects.all().count()
    # # taking the latest profile object
    # calories = Profile.objects.filter(person_of=request.user).last()
    # calorie_goal = calories.calorie_goal

    # # creating one profile each day
    # if date.today() > calories.date:
    #     profile = Profile.objects.create(person_of=request.user)
    #     profile.save()

    # calories = Profile.objects.filter(person_of=request.user).last()

    # # showing all food consumed present day

    # all_food_today = PostFood.objects.filter(profile=calories)

    # calorie_goal_status = calorie_goal - calories.total_calorie
    # over_calorie = 0
    # if calorie_goal_status < 0:
    #     over_calorie = abs(calorie_goal_status)

    # context = {
    #     'total_calorie': calories.total_calorie,
    #     'calorie_goal': calorie_goal,
    #     'calorie_goal_status': calorie_goal_status,
    #     'over_calorie': over_calorie,
    #     'food_selected_today': all_food_today
    # }

    context = {
        "guess_users": guess_users
    }
    # return render(request, 'home.html', context)
    return render(request, 'home.html', context)
# signup page changes


def RegisterPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, "Account was created for " + user)
                return redirect('login')

        context = {'form': form}
        return render(request, 'register.html', context)

# login page


def LoginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:

        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username or password is incorrect')
        context = {}
        return render(request, 'login.html', context)

# logout page


def LogOutPage(request):
    logout(request)
    return redirect('login')

# for selecting food each day


@login_required(login_url='login')
def select_food(request):
    person = Profile.objects.filter(person_of=request.user).last()
    # for showing all food items available
    food_items = Food.objects.filter(person_of=request.user)
    form = SelectFoodForm(request.user, instance=person)

    if request.method == 'POST':
        form = SelectFoodForm(request.user, request.POST, instance=person)
        if form.is_valid():

            form.save()
            return redirect('tracker')
    else:
        form = SelectFoodForm(request.user)

    context = {'form': form, 'food_items': food_items}
    return render(request, 'select_food.html', context)

# for adding new food


@login_required(login_url='login')
def add_food(request):
    # for showing all food items available
    food_items = Food.objects.filter(person_of=request.user)
    form = AddFoodForm(request.POST)
    if request.method == 'POST':
        form = AddFoodForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.person_of = request.user
            profile.save()
            return redirect('add_food')
    else:
        form = AddFoodForm()
    # for filtering food
    myFilter = FoodFilter(request.GET, queryset=food_items)
    food_items = myFilter.qs
    context = {'form': form, 'food_items': food_items, 'myFilter': myFilter}
    return render(request, 'add_food.html', context)

# for updating food given by the user


@login_required(login_url='login')
def update_food(request, pk):
    food_items = Food.objects.filter(person_of=request.user)

    food_item = Food.objects.get(id=pk)
    form = AddFoodForm(instance=food_item)
    if request.method == 'POST':
        form = AddFoodForm(request.POST, instance=food_item)
        if form.is_valid():
            form.save()
            return redirect('profile')
    myFilter = FoodFilter(request.GET, queryset=food_items)
    context = {'form': form, 'food_items': food_items, 'myFilter': myFilter}

    return render(request, 'add_food.html', context)

# for deleting food given by the user


@login_required(login_url='login')
def delete_food(request, pk):
    food_item = Food.objects.get(id=pk)
    if request.method == "POST":
        food_item.delete()
        return redirect('profile')
    context = {'food': food_item, }
    return render(request, 'delete_food.html', context)

# profile page of user


@login_required(login_url='login')
def ProfilePage(request):
    # getting the lastest profile object for the user
    person = Profile.objects.filter(person_of=request.user).last()
    food_items = Food.objects.filter(person_of=request.user)
    form = ProfileForm(instance=person)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=person)

    # querying all records for the last seven days
    some_day_last_week = timezone.now().date() - timedelta(days=7)
    records = Profile.objects.filter(
        date__gte=some_day_last_week, date__lt=timezone.now().date(), person_of=request.user)

    labelsProfile = []
    dataProfile = []

    for entry in records:
        dateStr = entry.date.strftime("%d %b, %Y")
        labelsProfile.append(dateStr)
        dataProfile.append(entry.total_calorie)

    labelsCalorie = []
    dataCalorie = []
    dataCalorieTotal = []

    for calorie in records:
        dateStr = calorie.date.strftime("%d %b, %Y")
        labelsCalorie.append(dateStr)
        dataCalorie.append(calorie.calorie_goal)
        dataCalorieTotal.append(calorie.total_calorie)

    labelsFoodItem = []
    dataFoodItems = []

    for items in food_items:
        labelsFoodItem.append(items.name)
        dataFoodItems.append(items.calorie)

    context = {'form': form, 'food_items': food_items, 'records': records,
               "labelsProfile": labelsProfile, "dataProfile": dataProfile,
               "labelsCalorie": labelsCalorie, "dataCalorie": dataCalorie, "dataCalorieTotal": dataCalorieTotal,
               "labelsFoodItem": labelsFoodItem, "dataFoodItems": dataFoodItems
               }

    return render(request, 'profile.html', context)


def developers(request):
    return render(request, 'developers.html')


@login_required(login_url='login')
def tracker(request):
    # taking the latest profile object
    calories = Profile.objects.filter(person_of=request.user).last()
    calorie_goal = calories.calorie_goal

    # creating one profile each day
    if date.today() > calories.date:
        profile = Profile.objects.create(person_of=request.user)
        profile.save()

    calories = Profile.objects.filter(person_of=request.user).last()

    # showing all food consumed present day

    all_food_today = PostFood.objects.filter(profile=calories)

    calorie_goal_status = calorie_goal - calories.total_calorie
    over_calorie = 0
    if calorie_goal_status < 0:
        over_calorie = abs(calorie_goal_status)

    labels = []
    data = []

    for entry in all_food_today:
        labels.append(entry.food.name)
        data.append(entry.calorie_amount)

    labelCount = []
    dataCount = []

    foodCarbs = Food.objects.filter(nutrition='Carbs').count()
    foodFats = Food.objects.filter(nutrition='Fats').count()
    foodProtein = Food.objects.filter(nutrition='Protein').count()

    filtering = all_food_today.filter()

    for num in all_food_today:
        labelCount.append(num.amount)
        dataCount.append(num.food.name)

    context = {
        'total_calorie': calories.total_calorie,
        'calorie_goal': calorie_goal,
        'calorie_goal_status': calorie_goal_status,
        'over_calorie': over_calorie,
        'food_selected_today': all_food_today,
        'labels': labels,
        'data': data,
        'labelsCount': labelCount,
        'dataCount': dataCount
    }
    return render(request, 'tracker.html', context)


def calculator(request):
    return render(request, 'calculator.html')


def about(request):
    return render(request, 'about.html')
