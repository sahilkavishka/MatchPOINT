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
            'rules': forms.Textarea(attrs={'rows': 5, 'placeholder': "1) Rule 01\n2) Rule 02\n3) Rule 03"}),
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
            'rules': forms.Textarea(attrs={'rows': 5, 'placeholder': "1) Rule 01\n2) Rule 02\n3) Rule 03"}),
            'contact_details': forms.TextInput(attrs={'placeholder': 'Phone or Email'}),
            'capacity': forms.NumberInput(attrs={'placeholder': 'Maximum team'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('capacity', 0) < 0:
            raise forms.ValidationError({"capacity": "Capacity cannot be negative."})
        return cleaned_data


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMembers
        fields = ['memberpic', 'name', 'age', 'height', 'position', 'city']

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
        for field_name, placeholder in {
            'username': 'Enter your username',
            'email': 'Enter your email',
            'password1': 'Enter your password',
            'password2': 'Confirm your password',
            'contact_number': 'Enter your contact number'
        }.items():
            self.fields[field_name].widget.attrs.update({'placeholder': placeholder, 'class': 'form-control'})
        
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})
