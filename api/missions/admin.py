from django.contrib import admin
from missions.models import (
    Location,
    Mission,
    MissionCategory,
    MissionJIAParticipant,
    Report,
    MissionGallery
)


admin.site.register(Location)
admin.site.register(Mission)
admin.site.register(MissionCategory)
admin.site.register(MissionJIAParticipant)
admin.site.register(Report)
admin.site.register(MissionGallery)
