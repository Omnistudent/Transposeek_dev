from django.contrib import admin

from .models import UserProfile

from .models import genomeEntry
from .models import Footprint



admin.site.register(UserProfile)

admin.site.register(genomeEntry)
admin.site.register(Footprint)

