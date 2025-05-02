from django.contrib import admin
from .models import User, Subscription, Drug, DrugGroup, SideEffect  # и др.

admin.site.register(User)
admin.site.register(Subscription)
admin.site.register(DrugGroup)
admin.site.register(Drug)
admin.site.register(SideEffect)
# по желанию — Inline для DrugSideEffect, IntakeDuration и т.п.