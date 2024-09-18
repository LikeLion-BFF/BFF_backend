from rest_framework import serializers
from .models import Bingo, BingoCell, Team, User_Team
from .models import User
from rank.models import BingoProgress

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']

class BingoCellSerializer(serializers.ModelSerializer):
    class Meta:
        model = BingoCell
        fields = ['id', 'bingo', 'team', 'row', 'col', 'content']

class BingoSerializer(serializers.ModelSerializer):
    content = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta:
        model = Bingo
        fields = ['title', 'size', 'teams', 'goal', 'end_date', 'content']

    def create(self, validated_data):
        size = validated_data.get('size')
        teams = validated_data.get('teams')
        content = validated_data.pop('content', [])

        if len(content) != size * size:
            raise serializers.ValidationError('Bingo 보드의 크기에 맞게 내용을 입력해주세요.')

        bingo = Bingo.objects.create(**validated_data)

        # #Team 인스턴스 생성
        # team_objects = [Team(bingo=bingo, team_name=f'Team {i+1}') for i in range(teams)]
        # Team.objects.bulk_create(team_objects)

        team_objects = []
        for i in range(teams):
            team = Team.objects.create(bingo=bingo, team_name=f'{i+1}팀')
            team_objects.append(team)

            # BingoProgress 인스턴스 생성
            BingoProgress.objects.create(bingo=bingo, team=team)

        # BingoCell 인스턴스 생성
        for team in team_objects:
            index = 0
            for row in range(1, size + 1):
                for col in range(1, size + 1):
                    BingoCell.objects.create(
                        bingo=bingo,
                        team=team,
                        row=row,
                        col=col,
                        content=content[index]
                    )
                    index += 1

        return bingo

class JoinTeamSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField()
    name = serializers.CharField()
    bingo_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = User_Team
        fields = ['team_name', 'name', 'bingo_id']

    def validate(self, attrs):
        team_name = attrs.get('team_name')
        bingo_id = attrs.get('bingo_id')

        try:
            team = Team.objects.get(team_name=team_name)
        except Team.DoesNotExist:
            raise serializers.ValidationError({'team_name': '유효하지 않은 팀 이름입니다.'})

        try:
            bingo = Bingo.objects.get(id=bingo_id)
        except Bingo.DoesNotExist:
            raise serializers.ValidationError({'bingo_id': '유효하지 않은 빙고 게임입니다.'})

        if User_Team.objects.filter(user=self.context['request'].user, bingo=bingo).exists():
            raise serializers.ValidationError({'non_field_errors': '이미 해당 빙고 게임에 참여하고 있습니다.'})

        attrs['team'] = team
        attrs['bingo'] = bingo  
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        team = validated_data.get('team')
        bingo = validated_data.get('bingo')
        name = validated_data.get('name')

        return User_Team.objects.create(user=user, team=team, bingo=bingo, name=name)
