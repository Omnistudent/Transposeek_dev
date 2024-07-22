from django.contrib import admin

from .models import UserProfile

from .models import genomeEntry
from .models import Footprint
from .models import NCBIentry
from .models import NCBISubentry



admin.site.register(UserProfile)

admin.site.register(genomeEntry)
admin.site.register(Footprint)
admin.site.register(NCBIentry)
admin.site.register(NCBISubentry)

