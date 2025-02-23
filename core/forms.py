from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import TeamMembers, Tournament,  User,CreateTeam


class TournamentForm(forms.ModelForm):

    class Meta:
        model = Tournament
        fields = [
            'name', 'city', 'sport',  'registration_fee', 'contact_details',
            'venue', 'champions_prize', 'runners_up_prize', 'date', 'rules', 'capacity', 'image',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'rules': forms.Textarea(attrs={ 'rows': 5,'placeholder': "1) Rule 01\n2) Rule 02\n3) Rule 03"}),
            'contact_details': forms.TextInput(attrs={'placeholder': 'Phone or Email'}),
            'champions_prize': forms.NumberInput(attrs={'placeholder': 'Add 1st place prize'}),
            'champions_prize': forms.NumberInput(attrs={'placeholder': 'Add 2nd place prize'}),
            'capacity': forms.NumberInput(attrs={'placeholder': 'maximum team'}),
        }
class CreateTeam(forms.ModelForm):

    class Meta:
        model = CreateTeam
        fields = [
            'name', 'city', 'sport',  'contact_details',
             'rules', 'capacity', 'logo'
        ]
        widgets = {
            'name':forms.TextInput(attrs={'placeholder':'team name'}),
            'rules': forms.Textarea(attrs={ 'rows': 5,'placeholder': "1) Rule 01\n2) Rule 02\n3) Rule 03"}),
            'contact_details': forms.TextInput(attrs={'placeholder': 'Phone or Email'}),
            'capacity': forms.NumberInput(attrs={'placeholder': 'maximum team'}),
        }

    def clean(self):
        data = self.cleaned_data
        if data.get('registration_fee','champions_prize','champions_prize','capacity', 0) < 0:
            raise forms.ValidationError({"registration_fee": " cannot be negative."})
        return data
class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMembers
        fields = ['memberpic', 'name', 'age', 'height', 'position', 'city']
    
    
        
        
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    # Role choices
    ROLE_CHOICES = [
        ('Organizer', 'Organizer'),
        ('Player', 'Player'),
        ('Spectator', 'Spectator'),
    ]

    # Custom fields
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    contact_number = forms.CharField(max_length=15, required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'contact_number', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter your username', 'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter your email', 'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter your password', 'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm your password', 'class': 'form-control'})
        self.fields['contact_number'].widget.attrs.update({'placeholder': 'Enter your contact number', 'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})

