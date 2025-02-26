from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone
from sports_manager import settings


class User(AbstractUser):
    ROLE_CHOICES = [
        ('Organizer', 'Organizer'),
        ('Player', 'Player'),
        ('Spectator', 'Spectator'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Spectator')
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    def __str__(self):
        return self.username


class Sport(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tournament(models.Model):
    name = models.CharField(max_length=200)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="tournaments")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="tournaments")
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    contact_details = models.CharField(max_length=200, null=True, blank=True)
    venue = models.CharField(max_length=200)
    champions_prize = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    runners_up_prize = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(blank=True, null=True)
    rules = models.TextField()
    capacity = models.IntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_tournaments")
    image = models.ImageField(upload_to='tournaments/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.city}) ({self.sport})"


class CreateTeam(models.Model):
    name = models.CharField(max_length=200)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="create_team")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="create_team")
    contact_details = models.CharField(max_length=200, null=True, blank=True)
    rules = models.TextField()
    capacity = models.IntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="create_team")
    created_date = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(upload_to='team/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.city}) ({self.sport})"


class TeamMembers(models.Model):
    team = models.ForeignKey(CreateTeam, on_delete=models.CASCADE, related_name="members")
    memberpic = models.ImageField(upload_to='member/', null=True, blank=True)
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    height = models.FloatField()
    position = models.CharField(max_length=200)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="team_members")

    def __str__(self):
        return f"{self.name} ({self.city})"

class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.tournament.name}"


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'tournament'], name='unique_like')
        ]


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"
