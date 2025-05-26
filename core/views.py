
import random
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from .forms import  UserRegistrationForm, TournamentForm,TeamMemberForm 
from .models import City, CreateTeam, Like,  Tournament, Registration, Sport, Comment  ,TeamMembers, User
from django.shortcuts import render
from .models import Tournament, Sport, City, CreateTeam
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, update_session_auth_hash

def home_view(request):
    search_query = request.GET.get('q', '')  
    sport_id = request.GET.get('sport', '')  
    city_id = request.GET.get('city', '')  

    tournaments = Tournament.objects.all().order_by('-date')
    if search_query:
        tournaments = tournaments.filter(
            Q(name__icontains=search_query) |
            Q(city__name__icontains=search_query) |
            Q(sport__name__icontains=search_query)
        ).distinct()
    if sport_id:
        tournaments = tournaments.filter(sport__id=sport_id)
    if city_id:
        tournaments = tournaments.filter(city__id=city_id)

    teams = CreateTeam.objects.filter(
        Q(name__icontains=search_query) |
        Q(city__name__icontains=search_query) |
        Q(sport__name__icontains=search_query)
    ).distinct() if search_query else CreateTeam.objects.all()

    return render(request, 'home.html', {
        'tournaments': tournaments,
        'teams': teams,
        'sports': Sport.objects.all(),
        'cities': City.objects.all(),
        'search_query': search_query,
        'selected_city': city_id
    })

def register_view(request):
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Account created successfully! You can now log in.')
        return redirect('login')
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



@login_required
def register_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    # Show only teams created by this user
    teams = CreateTeam.objects.filter(created_by=request.user)

    if request.method == 'POST':
        team_id = request.POST.get('team')
        member_names = request.POST.getlist('members[]')  # Fetch list of selected members

        if team_id and member_names:
            team = get_object_or_404(CreateTeam, id=team_id)

            # Prevent duplicate registration
            if Registration.objects.filter(team=team, tournament=tournament).exists():
                messages.warning(request, "This team is already registered.")
                return redirect('home')

            # Save registration (modify based on your model structure)
            registration = Registration.objects.create(
                user=request.user,
                team=team,
                tournament=tournament
            )

            # If your model supports storing members, do it here.
            # Otherwise, log them or show them in the front-end only.

            messages.success(request, "Successfully registered!")
            return redirect("home")
        else:
            messages.error(request, "Please select a team and members.")

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

