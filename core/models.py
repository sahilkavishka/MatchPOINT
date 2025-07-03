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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES,default='Spectator')
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    def __str__(self):
        return self.username


class Sport(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Prevent duplicate sports

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Prevent duplicate cities

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
    capacity = models.PositiveIntegerField(default=1)  # Prevent negative values
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_tournaments")
    image = models.ImageField(upload_to='tournaments/', null=True, blank=True)

    class Meta:
        ordering = ['-date']  # Default order: newest tournaments first

    def __str__(self):
        return f"{self.name} ({self.city}) ({self.sport})"


class CreateTeam(models.Model):
    name = models.CharField(max_length=200)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="create_team")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="create_team")
    contact_details = models.CharField(max_length=200, null=True, blank=True)
    rules = models.TextField()
    capacity = models.PositiveIntegerField(default=1)  # Prevent negative values
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="create_team")
    created_date = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(upload_to='team/', null=True, blank=True)

    class Meta:
        ordering = ['-created_date']  # Default order: newest teams first

    def __str__(self):
        return f"{self.name} ({self.city}) ({self.sport})"


class TeamMembers(models.Model):
    team = models.ForeignKey(CreateTeam, on_delete=models.CASCADE, related_name="members")
    memberpic = models.ImageField(upload_to='member/', null=True, blank=True)
    name = models.CharField(max_length=200)
    age = models.PositiveIntegerField()  # Ensures a valid age (no negatives)
    height = models.FloatField()  # Consider adding `validators=[MinValueValidator(1.0)]` if needed
    position = models.CharField(max_length=200)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="team_members")

    def __str__(self):
        return f"{self.name} ({self.city})"


class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    team = models.ForeignKey(CreateTeam, on_delete=models.CASCADE)
    member_names = models.TextField()
    registered_at = models.DateTimeField(auto_now_add=True)  # optional


    def get_member_list(self):
        # helper to get list of names
        return self.member_names.split(",") if self.member_names else []

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'tournament'], name='unique_like')
        ]
        ordering = ['-created_at']  # Default order: newest likes first


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']  # Default order: newest comments first

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}{'...' if len(self.content) > 30 else ''}"


class Match(models.Model):
    team_a = models.ForeignKey(CreateTeam, related_name='team_a_matches', on_delete=models.CASCADE)
    team_b = models.ForeignKey(CreateTeam, related_name='team_b_matches', on_delete=models.CASCADE)
    team_a_score = models.IntegerField(default=0)
    team_b_score = models.IntegerField(default=0)
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.team_a.name} vs {self.team_b.name}"