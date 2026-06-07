from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    # Strona główna
    path('', views.home, name='home'),

    # Przepisy
    path('przepisy/', views.recipe_list, name='recipe_list'),
    path('przepis/nowy/', views.recipe_create, name='recipe_create'),
    path('przepis/<slug:slug>/', views.recipe_detail, name='recipe_detail'),
    path('przepis/<slug:slug>/edytuj/', views.recipe_update, name='recipe_update'),
    path('przepis/<slug:slug>/usun/', views.recipe_delete, name='recipe_delete'),

    # Kategorie
    path('kategorie/', views.category_list, name='category_list'),
    path('kategoria/<slug:slug>/', views.category_detail, name='category_detail'),

    # Wyszukiwanie
    path('szukaj/', views.search, name='search'),

    # Użytkownicy
    path('rejestracja/', views.register, name='register'),
    path('logowanie/', views.user_login, name='login'),
    path('wyloguj/', views.user_logout, name='logout'),
    path('profil/<str:username>/', views.profile, name='profile'),
    path('profil/<str:username>/edytuj/', views.profile_edit, name='profile_edit'),

    #ULUBIONE 
    path('przepis/<slug:slug>/ulubione/', views.add_to_favorites, name='add_to_favorites'),
    path('ulubione/', views.favorite_list, name='favorite_list'),
]