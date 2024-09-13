from django.db import models
from django.contrib.auth.models import User

class Bingo(models.Model):
    title = models.CharField(max_length=60)
    size = models.CharField(max_length=10)
    end_date = models.DateTimeField()
    team_count = models.IntegerField()
    winner_bingo_count = models.IntegerField()
    enter_code = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  #유저와의 연결
    created_at = models.DateField(auto_now_add=True)
