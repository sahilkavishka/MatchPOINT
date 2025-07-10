

from django.urls import reverse

from core.utils import notify_user
from .models import Match, Notification, Result
import random
from django.http import  JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from .forms import    UserRegistrationForm, TournamentForm,TeamMemberForm 
from .models import City, CreateTeam, Like,  Tournament, Registration, Sport, Comment  ,TeamMembers, User
from django.shortcuts import render
from .models import Tournament, Sport, City, CreateTeam
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, update_session_auth_hash



from datetime import timedelta, timezone
from django.utils.timezone import now
from django.db.models import Q
from django.shortcuts import render
from .models import Tournament, Sport, City, CreateTeam

from django.shortcuts import render
from django.db.models import Q
from django.utils.timezone import now
from datetime import timedelta
from .models import Tournament, Sport, City, CreateTeam

def home_view(request):
    search_query = request.GET.get('q', '')  # Optional search query
    sport_id = request.GET.get('sport', '')
    city_id = request.GET.get('city', '')
    date_filter = request.GET.get('date', '')

    tournaments = Tournament.objects.all().order_by('-date')
    today = now().date()

    # Text search (optional)
    if search_query:
        tournaments = tournaments.filter(
            Q(name__icontains=search_query) |
            Q(city__name__icontains=search_query) |
            Q(sport__name__icontains=search_query)
        ).distinct()

    # Filter by sport
    if sport_id:
        tournaments = tournaments.filter(sport__id=sport_id)

    # Filter by city
    if city_id:
        tournaments = tournaments.filter(city__id=city_id)

    # Filter by date
    if date_filter == 'today':
        tournaments = tournaments.filter(date=today)
    elif date_filter == 'week':
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        tournaments = tournaments.filter(date__range=[start_of_week, end_of_week])
    elif date_filter == 'month':
        tournaments = tournaments.filter(date__month=today.month)

    # Optional: Teams for sidebar/search
    if search_query:
        teams = CreateTeam.objects.filter(
            Q(name__icontains=search_query) |
            Q(city__name__icontains=search_query) |
            Q(sport__name__icontains=search_query)
        ).distinct()
    else:
        teams = CreateTeam.objects.all()

    # Notification unread count (if logged in)
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(is_read=False).count()

    context = {
        'tournaments': tournaments,
        'teams': teams,
        'sports': Sport.objects.all(),
        'cities': City.objects.all(),
        'search_query': search_query,
        'selected_city': city_id,
        'selected_sport': sport_id,
        'selected_date': date_filter,
        'unread_count': unread_count,
    }

    return render(request, 'home.html', context)
    


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')  # redirect to login or homepage
    else:
        form = UserRegistrationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def add_tournament(request):
    if request.method == 'POST':
        form = TournamentForm(request.POST, request.FILES)
        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.created_by = request.user
            tournament.save()
            return redirect('home')
    else:
        form = TournamentForm()
    return render(request, 'add_tournament.html', {'form': form})


@login_required
def create_team(request):
    if request.method == 'POST':
       
        name = request.POST['name']
        sport = Sport.objects.get(id=request.POST['sport'])
        city = City.objects.get(id=request.POST['city'])
        contact_details = request.POST.get('contact_details', '')
        rules = request.POST['rules']
        capacity = request.POST['capacity']
        logo = request.FILES.get('logo', None)
        
        
        team = CreateTeam.objects.create(
            name=name,
            sport=sport,
            city=city,
            contact_details=contact_details,
            rules=rules,
            capacity=capacity,
            created_by=request.user,
            logo=logo
        )

       
        return redirect('team_detail', team_id=team.id)
    
    
    sports = Sport.objects.all()
    cities = City.objects.all()
    
    return render(request, 'create_team.html', {'sports': sports, 'cities': cities})


def add_team_member(request, team_id):
    team = get_object_or_404(CreateTeam, id=team_id)

    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save(commit=False)
            member.team = team
            member.save()
            messages.success(request, "Team member added successfully.")
            return redirect('team_detail', team.id)
    else:
     form = TeamMemberForm()

    return render(request, 'add_team_member.html', {'form': form, 'team': team}) 

def delete_team_member(request, member_id):
    member = get_object_or_404(TeamMembers, id=member_id)
    if request.user == member.team.created_by:
        member.delete()
        messages.success(request,"Member removed successfully.")
    else:
        messages.error(request, "You are not authorized to remove this member.")
    
    return redirect('team_detail')  


def get_team_members(request, team_id):
    team = get_object_or_404(CreateTeam, id=team_id)
    members = team.members.values_list('name', flat=True)
    return JsonResponse({'members': list(members)})


def delete_team(request, team_id):
    team = get_object_or_404(CreateTeam, id=team_id)  

   
    if request.user == team.created_by:
        team.delete()
        messages.success(request, "Team deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this team.")
    return redirect('home') 

def team_detail_view(request, team_id):
    team = get_object_or_404(CreateTeam, id=team_id)
    members = team.members.all()
    return render(request, 'team_detail.html', {'team': team, 'members': members})


def team_detail(request, team_id=None):
    teams = CreateTeam.objects.all()  
    team = get_object_or_404(CreateTeam, id=team_id) if team_id else None
    members = team.members.all() if team else None  
    return render(request, 'team.html', {'teams': teams, 'team': team, 'members': members})

def tournament_detail(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    return render(request, 'tournament_details.html',  {'tournament': tournament})



@login_required
def register_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    teams = CreateTeam.objects.filter(created_by=request.user)

    if request.method == 'POST':
        team_id = request.POST.get('team')
        member_names = request.POST.getlist('members')

        if team_id and member_names:
            team = get_object_or_404(CreateTeam, id=team_id)

            if Registration.objects.filter(team=team, tournament=tournament).exists():
                messages.warning(request, "This team is already registered.")
                return redirect('tournament_registrations', tournament_id=tournament.id)

            joined_names = ", ".join(member_names)

            Registration.objects.create(
                user=request.user,
                team=team,
                tournament=tournament,
                member_names=joined_names
            )

            notify_user(
                user=request.user,
                message=f"You have successfully registered for the tournament: {tournament.name}",
                link=reverse('tournament_detail', args=[tournament.id])
            )

            messages.success(request, "Team successfully registered!")
            return redirect('tournament_registrations', tournament_id=tournament.id)
        else:
            messages.error(request, "Please select a team and at least one member.")

    return render(request, 'register.html', {
        'tournament': tournament,
        'teams': teams
    })



def tournament_registrations(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    registrations = Registration.objects.filter(tournament=tournament)

    return render(request, 'tournament_registrations.html', {
        'tournament': tournament,
        'registrations': registrations
    })

def get_team_members(request, team_id):
    team = get_object_or_404(CreateTeam, id=team_id)
    members = team.members.values_list('name', flat=True)
    return JsonResponse({'members': list(members)})

def delete_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.user != tournament.created_by:
        messages.error(request, "You are not authorized to delete this tournament.")
        return redirect("home")
    tournament.delete()
    messages.success(request, "Tournament deleted successfully!")
    return redirect("home")


def like_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if not Like.objects.filter(user=request.user, tournament=tournament).exists():
        Like.objects.create(user=request.user, tournament=tournament)
    return redirect(request.META.get("HTTP_REFERER", "home"))

def team_list(request):
    teams = CreateTeam.objects.all()
    return render(request, 'team.html', {'teams': teams})



def comment_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(user=request.user, tournament=tournament, content=content)
    return redirect('home')


def load_more_comments(request, tournament_id):
    if request.method == "GET" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        tournament = get_object_or_404(Tournament, id=tournament_id)
        comments = tournament.comment_set.all()[3:]

        comments_data = []
        for c in comments:
            profile_picture_url = c.user.profile_picture.url if c.user.profile_picture else None
            comments_data.append({
                "user": c.user.username,
                "content": c.content,
                "user_profile_picture": profile_picture_url
            })

        return JsonResponse({
            "comments": comments_data,
            "has_more": tournament.comment_set.count() > len(comments) + 3
        })

    return JsonResponse({"error": "Invalid request"}, status=400)



User = get_user_model()

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        if User.objects.filter(email=email).exists():
            request.session['reset_email'] = email
            request.session.modified = True  # Force session save
            return redirect('send_resetOTP')
        messages.error(request, 'No account found with this email')
    return render(request, 'forgot_password.html')

def send_resetOTP(request):
    # Ensure email exists in session
    if not request.session.get('reset_email'):
        return redirect('forgot_password')
    
    email = request.session['reset_email']
    
    # Generate and store OTP
    otp_code = str(random.randint(100000, 999999))
    request.session['reset_otp'] = otp_code
    request.session.set_expiry(300)  # 5 minutes
    request.session.modified = True  # Force save
    
    # Send email
    try:
        send_mail(
            "MatchPoint - Password Reset OTP",
            f"Your OTP: {otp_code}\nExpires in 5 minutes.",
            "kavudaboy1@gmail.com",
            [email],
            fail_silently=False
        )
        messages.success(request, 'OTP sent successfully!')
        return redirect('verify_resetOTP')  # Changed to redirect
    except Exception as e:
        messages.error(request, f'Failed to send OTP: {str(e)}')
        return redirect('forgot_password')

def verify_resetOTP(request):
    # Session validation
    if not request.session.get('reset_email'):
        messages.error(request, 'Session expired')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        user_otp = request.POST.get('otp', '').strip()
        stored_otp = request.session.get('reset_otp')
        
        if user_otp == stored_otp:
            request.session['otp_verified'] = True
            request.session.modified = True
            return redirect('reset_password')
        messages.error(request, 'Invalid OTP')
    
    return render(request, 'otp_verification.html', {
        'email': request.session.get('reset_email')
    })

def reset_password(request):
    if not request.session.get('otp_verified'):
        messages.error(request, 'OTP verification required')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        email = request.session.get('reset_email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'reset_password.html')
        
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            # Clear session
            for key in ['reset_otp', 'reset_email', 'otp_verified']:
                request.session.pop(key, None)
            
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated!')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'User not found')
            return redirect('forgot_password')
    
    return render(request, 'reset_password.html')



from .models import Match, Tournament, CreateTeam, Result  # ensure Result is imported

def add_match_result(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    team_ids = Registration.objects.filter(tournament=tournament).values_list('team_id', flat=True)
    teams = CreateTeam.objects.filter(id__in=team_ids)

    if request.method == 'POST':
        winner_id = request.POST.get('winner')
        runner_up_id = request.POST.get('runner_up')

        if winner_id == runner_up_id:
            return render(request, 'add_result.html', {
                'tournament': tournament,
                'teams': teams,
                'error': "Winner and Runner-Up cannot be the same team."
            })

        winner = get_object_or_404(CreateTeam, id=winner_id)
        runner_up = get_object_or_404(CreateTeam, id=runner_up_id)

        # Save result
        Match.objects.create(
            tournament=tournament,
            winner=winner,
            runner_up=runner_up
        )

        # Update points and stats
        winner.points += 2
        winner.wins += 1
        winner.save()

        runner_up.points += 1
        runner_up.losses += 1
        runner_up.save()

        messages.success(request, "Match result added successfully.")
        return redirect('team_leaderboard')  # You can change this

    return render(request, 'add_result.html', {
        'tournament': tournament,
        'teams': teams
    })

def team_leaderboard(request):
    teams = CreateTeam.objects.all().order_by('-points', '-wins')
    return render(request, 'team_leaderboard.html', {'teams': teams})


@login_required
def user_notifications(request):  # ✅ renamed the view
    notes = Notification.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'notifications.html', {'notifications': notes})
