from builtins import object
from django.forms import ModelForm

from players.models import Game


class AddGameForm(ModelForm):
    class Meta(object):
        model = Game
        exclude = ['Main', 'owner', 'auth_token', 'completed', 'main_user', 'static_data']
