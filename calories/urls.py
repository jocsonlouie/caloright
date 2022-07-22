from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . views import HomePageView, LoginPage, LogOutPage, select_food, add_food, RegisterPage, ProfilePage, update_food, delete_food, developers, tracker, about, calculator, AnalyticsPageView

urlpatterns = [
    path('', HomePageView, name='home'),
    path('login/', LoginPage, name='login'),
    path('logout/', LogOutPage, name='logout'),
    path('select_food/', select_food, name='select_food'),
    path('add_food/', add_food, name='add_food'),
    path('update_food/<str:pk>/', update_food, name='update_food'),
    path('delete_food/<str:pk>/', delete_food, name='delete_food'),
    path('register/', RegisterPage, name='register'),
    path('profile/', ProfilePage, name='profile'),
    path('developers/', developers, name='developers'),
    path('tracker/', tracker, name='tracker'),
    path('about/', about, name='about'),
    path('analytics/', AnalyticsPageView, name='analytics'),
    path('calculator/', calculator, name='calculator'),

]

urlpatterns += staticfiles_urlpatterns()
