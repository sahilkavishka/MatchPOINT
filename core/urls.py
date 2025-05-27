from django.urls import path
from django.conf.urls.static import static
from sports_manager import settings
from .views import (
    create_team, delete_tournament, load_more_comments, register_view, login_view, 
    logout_view, home_view, add_tournament, register_tournament
)
from core import views

urlpatterns = [
    # Auth
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Home
    path('', home_view, name='home'),

    # Tournament
    path('add/', add_tournament, name='add_tournament'),
    path('tournament/<int:tournament_id>/register/', register_tournament, name='register_tournament'),
    path('tournament/<int:tournament_id>/delete/', delete_tournament, name='delete_tournament'),
    path('tournament/<int:tournament_id>/registrations/', views.tournament_registrations, name='tournament_registrations'),

    # Likes & Comments
    path('like_tournament/<int:tournament_id>/', views.like_tournament, name='like_tournament'),
    path('comment_tournament/<int:tournament_id>/', views.comment_tournament, name='comment_tournament'),
    path('load_more_comments/<int:tournament_id>/', load_more_comments, name='load_more_comments'),

    # Teams
    path('create_team/', create_team, name='create_team'),
    path('teams/', views.team_list, name='team_list'),
    path('team/<int:team_id>/', views.team_detail_view, name='team_detail'),  
    path('team/<int:team_id>/', views.team_detail, name='team'),  
    path('team/<int:team_id>/add_member/', views.add_team_member, name='add_team_member'),
    path('member/<int:member_id>/delete/', views.delete_team_member, name='delete_team_member'),
    path('team/delete/<int:team_id>/', views.delete_team, name='delete_team'),

    # AJAX / JSON API
    path('get-team-members/<int:team_id>/', views.get_team_members, name='get_team_members'),

    # Password Reset
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('send-reset-otp/', views.send_resetOTP, name='send_resetOTP'),
    path('verify-otp/', views.verify_resetOTP, name='verify_resetOTP'),
    path('reset-password/', views.reset_password, name='reset_password'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



