
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from sports_manager import settings
from .views import create_team, delete_tournament, load_more_comments,  register_view, login_view, logout_view
from .views import  home_view, add_tournament, register_tournament
from core import views


urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', home_view, name='home'),
    path('add/', add_tournament, name='add_tournament'),
    path('create _team/', create_team, name='create_team'),
    path('like_tournament/<int:tournament_id>/', views.like_tournament, name='like_tournament'),
    path('comment_tournament/<int:tournament_id>/', views.comment_tournament, name='comment_tournament'),
    path('load_more_comments/<int:tournament_id>/', load_more_comments, name='load_more_comments'),
    path('team/<int:team_id>/', views.team_detail_view , name='team_detail'),
    path('team/<int:team_id>/', views.team_detail, name='team'),
    path('team/<int:team_id>/add_member/', views.add_team_member, name='add_team_member'),
    path('member/<int:member_id>/delete/', views.delete_team_member, name='delete_team_member'),
    path('teams/',views.team_list, name='team_list'),
    path('register/<int:tournament_id>/', register_tournament, name='register_tournament'),
    path('team/delete/<int:team_id>/',views.delete_team, name='delete_team'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset.html'), name='password_reset_complete'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('tournament/<int:tournament_id>/delete/', delete_tournament, name='delete_tournament'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
