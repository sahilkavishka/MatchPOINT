from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from .forms import  UserRegistrationForm, TournamentForm,TeamMemberForm 
from .models import City, CreateTeam, Like,  Tournament, Registration, Sport, Comment  ,TeamMembers


from django.shortcuts import render
from django.db.models import Q
from .models import Tournament, Sport, City, CreateTeam

def home_view(request):
    tournaments = Tournament.objects.all().order_by('-date')
    sports = Sport.objects.all()
    cities = City.objects.all()

    search_query = request.GET.get('q', '')  
    sport = request.GET.get('sport', '')  
    city = request.GET.get('city', '')  

    # Search in Tournaments
    if search_query:
        tournaments = tournaments.filter(
            Q(name__icontains=search_query) |
            Q(city__name__icontains=search_query) |
            Q(sport__name__icontains=search_query)
        ).distinct()

    if sport:
        tournaments = tournaments.filter(sport__id=sport).order_by('-date')
    
    if city:
        tournaments = tournaments.filter(city__id=city).order_by('-date')

    # 🔹 Search in Teams (CreateTeam model)
    teams = CreateTeam.objects.filter(
        Q(name__icontains=search_query) |
        Q(city__name__icontains=search_query) |
        Q(sport__name__icontains=search_query)
    ).distinct() if search_query else CreateTeam.objects.all()

    return render(request, 'home.html', {
        'tournaments': tournaments,
        'teams': teams,  # Pass teams to the template
        'sports': sports,
        'cities': cities,
        'search_query': search_query,
        'selected_city': city
    })



# Registration View
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'signup.html', {'form': form})


# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
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
        # Get the form data
        name = request.POST['name']
        sport = Sport.objects.get(id=request.POST['sport'])
        city = City.objects.get(id=request.POST['city'])
        contact_details = request.POST.get('contact_details', '')
        rules = request.POST['rules']
        capacity = request.POST['capacity']
        logo = request.FILES.get('logo', None)
        
        # Create the team
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

        # Redirect to the team detail page or success page
        return redirect('team_detail', team_id=team.id)
    
    # Pass the sports and cities to the template
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
    
    # Optional: Check if the user has permission to delete
    if request.user == member.team.created_by:
        member.delete()
        messages.success(request, "Member removed successfully.")
    else:
        messages.error(request, "You are not authorized to remove this member.")
    
    return redirect('team_detail')  # Change to the correct redirect URL

def delete_team(request, team_id):
    team = get_object_or_404(CreateTeam, id=team_id)  # Corrected: 'Team' instead of 'team'

    # Ensure only the team creator can delete the team
    if request.user == team.created_by:
        team.delete()
        messages.success(request, "Team deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this team.")

    return redirect('home')  # Redirect to the home page

def team_detail_view(request, team_id):
    team = get_object_or_404(CreateTeam, id=team_id)
    members = team.members.all()
    return render(request, 'team_detail.html', {'team': team, 'members': members})


def team_detail(request, team_id=None):
    teams = CreateTeam.objects.all()  # ✅ Use the actual model name
    team = get_object_or_404(CreateTeam, id=team_id)
    members = None
    if team_id:
        team = get_object_or_404(CreateTeam, id=team_id)
        members = team.members.all()  # Assuming a ForeignKey or ManyToMany relation

    return render(request, 'team.html', {'teams': teams, 'team': team, 'members': members})


@login_required
def register_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    registration, created = Registration.objects.get_or_create(user=request.user, tournament=tournament)

    # Fetch the user's team if they have one
    team = CreateTeam.objects.filter(created_by=request.user).first()

    return render(request, 'register.html', {
        'tournament': tournament,
        'team': team  # Pass the team details to the template
    })




def delete_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    
    # Optional: Ensure only the creator can delete the tournament
    if request.user != tournament.created_by:
        messages.error(request, "You are not authorized to delete this tournament.")
        return redirect("home")  # Redirect to the tournament list page
    
    tournament.delete()
    messages.success(request, "Tournament deleted successfully!")
    return redirect("home")  # Redirect after deletion


@login_required
def like_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    # Check if the user has already liked the tournament
    if not Like.objects.filter(user=request.user, tournament=tournament).exists():
        Like.objects.create(user=request.user, tournament=tournament)
    return redirect(request.META.get("HTTP_REFERER", "home"))

def team_list(request):
    """View to display all teams."""
    teams = CreateTeam.objects.all()
    return render(request, 'team.html', {'teams': teams})



@login_required
def comment_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:  # Ensure the comment is not empty
            Comment.objects.create(user=request.user, tournament=tournament, content=content)
    
    return redirect('home')  # Redirect to refresh the page and show the new comment


def load_more_comments(request, tournament_id):
    """ Load more comments via AJAX when the user clicks 'See More' """
    if request.method == "GET" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        tournament = get_object_or_404(Tournament, id=tournament_id)
        comments = tournament.comment_set.all()[3:]  # Fetch comments **AFTER** the first 3

        comments_data = [
            {"user": comment.user.username, "content": comment.content}
            for comment in comments
        ]

        return JsonResponse({"comments": comments_data})  # Send JSON response
    
    return JsonResponse({"error": "Invalid request"}, status=400)


