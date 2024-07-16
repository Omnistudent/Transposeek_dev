from django.contrib import admin
from .models import Environment
from .models import Square
from .models import MyPlayer
from .models import Venue
from .models import MyClubUser
from .models import Event
from .models import UserProfile
from .models import UserProfile2
from .models import Question
from .models import Beacon
from .models import genomeEntry
from .models import Footprint

admin.site.register(Environment)
admin.site.register(Square)
admin.site.register(MyPlayer)
admin.site.register(Venue)
admin.site.register(MyClubUser)
admin.site.register(Event)
admin.site.register(UserProfile)
admin.site.register(UserProfile2)
admin.site.register(Question)
admin.site.register(Beacon)
admin.site.register(genomeEntry)
admin.site.register(Footprint)

