from django.db import models
from users.models import User
from bingo.models import Bingo,Team

# Create your models here.
class BingoProgress(models.Model):
    bingo = models.ForeignKey(Bingo, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    completed_bingo_count = models.PositiveIntegerField(default=0)
    completed_cell_count = models.PositiveIntegerField(default=0)

