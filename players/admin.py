from __future__ import absolute_import
from django.contrib import admin

from .models import Avatar, Game

admin.site.register(Avatar)
admin.site.register(Game)
