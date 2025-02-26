from django.contrib import admin
from .models import  CreateTeam, Sport, Tournament, Registration ,User, City,TeamMembers

admin.site.register(Sport)
admin.site.register(Tournament)
admin.site.register(Registration)
admin.site.register(User)
admin.site.register(City)
admin.site.register(CreateTeam)
admin.site.register(TeamMembers)



