
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from .forms import  UserRegistrationForm, TournamentForm,TeamMemberForm 
from .models import City, CreateTeam, Like,  Tournament, Registration, Sport, Comment  ,TeamMembers
from django.shortcuts import render
from .models import Tournament, Sport, City, CreateTeam

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

# Logout View
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



def register_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        members = request.POST.get('members')  # comma-separated

        team = CreateTeam.objects.create(
            name=team_name,
            tournament=tournament,
            created_by=request.user
        )

        # Optional: Store members as text or create separate TeamMember model
        team.members = members
        team.save()

        return redirect('tournament_detail', tournament.id)  # Or wherever

    return render(request, 'register.html', {'tournament': tournament})




def registered_teams_list(request):
    registered_teams = Registration.objects.filter(user=request.user)
    return render(request, 'registered_teams.html', {'registered_teams': registered_teams})

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
        comments_data = [{"user": c.user.username, "content": c.content} for c in tournament.comment_set.all()[3:]]
        return JsonResponse({"comments": comments_data})
    return JsonResponse({"error": "Invalid request"}, status=400)


