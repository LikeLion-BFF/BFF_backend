from django.db import models
from django.conf import settings
from django.utils import timezone
from users.models import User

class Bingo(models.Model):
    title = models.CharField(max_length=255)
    size = models.PositiveIntegerField()
    teams = models.PositiveIntegerField()
    goal = models.PositiveIntegerField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.title
    
class Team(models.Model):
    bingo = models.ForeignKey(Bingo, related_name='teams_set', on_delete=models.CASCADE)
    team_name = models.CharField(max_length=255)

    def __str__(self):
        return self.team_name

class User_Team(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User 테이블 참조
    team = models.ForeignKey(Team, on_delete=models.CASCADE)  # Team 테이블 참조
    bingo = models.ForeignKey(Bingo, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user} - {self.team} - {self.name}"

class BingoCell(models.Model):
    bingo = models.ForeignKey(Bingo, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    row = models.PositiveIntegerField()
    col = models.PositiveIntegerField()
    content  = models.CharField(max_length=100)
    is_completed_yn = models.BooleanField(default=False)
    completed_photo = models.ImageField(upload_to='images/',blank=True,null=True) 
    ##여기서 blank=true옵션만 주면 NULL 값을 허용하지 않기 때문에, 값이 입력되지 않은 경우 빈 문자열 ('')로 저장
    ##ImageField의 경우에는 파일 경로를 저장하기 때문에, 빈 문자열을 사용하는 것이 적절하지 않음 so,null=true옵션 같이 줌
    completed_text = models.TextField(blank=True)

    def __str__(self):
        return f"{self.bingo.title} - {self.row}, {self.col}"