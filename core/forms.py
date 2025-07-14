from .models import Match
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Registration, TeamMembers, Tournament, User, CreateTeam


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = [
            'name', 'city', 'sport', 'registration_fee', 'contact_details',
            'venue', 'champions_prize', 'runners_up_prize', 'date', 'rules', 'capacity', 'image',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'rules': forms.Textarea(attrs={'rows': 5}),
            'contact_details': forms.TextInput(attrs={'placeholder': 'Phone or Email'}),
            'champions_prize': forms.NumberInput(attrs={'placeholder': 'Add 1st place prize'}),
            'runners_up_prize': forms.NumberInput(attrs={'placeholder': 'Add 2nd place prize'}),
            'capacity': forms.NumberInput(attrs={'placeholder': 'Maximum teams'}),
        }


class CreateTeamForm(forms.ModelForm):
    class Meta:
        model = CreateTeam
        fields = ['name', 'city', 'sport', 'contact_details', 'rules', 'capacity', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Team name'}),
            'rules': forms.Textarea(attrs={'rows': 5}),
            'contact_details': forms.TextInput(attrs={'placeholder': 'Phone or Email'}),
            'capacity': forms.NumberInput(attrs={'placeholder': 'Maximum team'}),
        }

    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')
        if capacity is not None and capacity < 1:
            raise forms.ValidationError("Capacity must be at least 1.")
        return capacity


class TeamMemberForm(forms.ModelForm):
    memberpic = forms.ImageField(required=False)  # Ensuring it's optional
   
    class Meta:
        model = TeamMembers
        fields = ['memberpic', 'name', 'age', 'height', 'position', 'city']
        widgets = {
            'height': forms.NumberInput(attrs={'placeholder': 'cm'}),
        }

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = []


class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('Organizer', 'Organizer'),
        ('Player', 'Player'),
        ('Spectator', 'Spectator'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    contact_number = forms.CharField(max_length=15, required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'contact_number', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_placeholders = {
            'username': 'Enter your username',
            'email': 'Enter your email',
            'password1': 'Enter your password',
            'password2': 'Confirm your password',
            'contact_number': 'Enter your contact number'
        }
        for field_name, placeholder in field_placeholders.items():
            self.fields[field_name].widget.attrs.update({'placeholder': placeholder, 'class': 'form-control'})

        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        if contact_number and not contact_number.isdigit():
            raise forms.ValidationError("Contact number should contain only digits.")
        if contact_number and len(contact_number) not in [10, 11, 12]:  
            raise forms.ValidationError("Enter a valid contact number.")
        return contact_number




class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['tournament', 'winner', 'runner_up']

    def clean(self):
        cleaned_data = super().clean()
        winner = cleaned_data.get('winner')
        runner_up = cleaned_data.get('runner_up')

        if winner == runner_up:
            raise forms.ValidationError("Winner and runner-up cannot be the same team.")
