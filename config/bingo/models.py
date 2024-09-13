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

class Team(models.Model):
    bingo = models.ForeignKey(Bingo, on_delete=models.CASCADE)  # Bingo 테이블의 id를 참조하는 외래키
    team_name = models.CharField(max_length=100)

class User_Team(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User 테이블 참조
    team = models.ForeignKey(Team, on_delete=models.CASCADE)  # Team 테이블 참조

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'team'], name='unique_user_team')
        ]  # user_id와 team_id의 조합이 고유하도록 설정

class BingoCell(models.Model):
    bingo_id = models.ForeignKey(User, on_delete=models.CASCADE)
    team_id = models.ForeignKey(Team, on_delete=models.CASCADE)
    row = models.IntegerField()
    col = models.IntegerField()
    content  = models.CharField(max_length=100)
    is_completed_yn = models.BooleanField(default=False)
    completed_photo = qs_perform_image = models.ImageField(upload_to='images/',blank=True,null=True) 
    ##여기서 blank=true옵션만 주면 NULL 값을 허용하지 않기 때문에, 값이 입력되지 않은 경우 빈 문자열 ('')로 저장
    ##ImageField의 경우에는 파일 경로를 저장하기 때문에, 빈 문자열을 사용하는 것이 적절하지 않음 so,null=true옵션 같이 줌
    completed_text = qs_perform_content = models.TextField(blank=True)