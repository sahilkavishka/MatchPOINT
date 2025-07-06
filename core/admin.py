from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CreateTeam, Sport, Tournament, Registration, User, City, TeamMembers

# 🌿 Sport Admin
@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# 🏙️ City Admin
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# 🏆 Tournament Admin
@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'sport', 'city', 'date', 'created_by')
    list_filter = ('sport', 'city', 'date')
    search_fields = ('name', 'sport__name', 'city__name')

# 📋 Registration Admin
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'tournament', 'registered_at')
    list_filter = ('tournament',)
    search_fields = ('user__username', 'team__name')

# 🧑‍🤝‍🧑 CreateTeam Admin
@admin.register(CreateTeam)
class CreateTeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'sport', 'city', 'points', 'created_by')
    list_filter = ('sport', 'city')
    search_fields = ('name', 'created_by__username')

# 👥 TeamMembers Admin
@admin.register(TeamMembers)
class TeamMembersAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'position')
    list_filter = ('team',)
    search_fields = ('name', 'team__name')

# 👤 Custom User Admin
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

    # Optional: To show more in user form
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Extra Info', {
            'fields': ('profile_picture', 'role',)
        }),
    )
