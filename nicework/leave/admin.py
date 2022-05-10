from django.contrib import admin
from .models import Annleave, Rwdleave, LeavePaid, UserLeave, Leave
# Register your models here.

admin.site.register(Annleave)
admin.site.register(Rwdleave)
admin.site.register(LeavePaid)
admin.site.register(UserLeave)
admin.site.register(Leave)