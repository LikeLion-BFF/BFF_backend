import random, string
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from .models import Bingo, Team, User_Team, BingoCell
from .serializers import BingoSerializer, JoinTeamSerializer

# 빙고판 입장 code 생성
def generate_random_code(length=8):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class CreateBingoView(APIView):
    # 빙고판 생성
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def post(self, request):
        user = request.user

        serializer = BingoSerializer(data=request.data)
        if serializer.is_valid():
            code = generate_random_code()
            bingo = serializer.save(creator=user, code=code)

            return Response({
                'code': bingo.code,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class JoinTeamView(APIView):
    # 빙고판 참여
    @permission_classes([IsAuthenticated])
    def post(self, request):
        bingo_id = request.data.get('bingo_id')

        if not bingo_id:
            return Response({'error': '빙고 ID를 제공해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bingo = Bingo.objects.get(id=bingo_id)
        except Bingo.DoesNotExist:
            return Response({'error': '해당 빙고 게임을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = JoinTeamSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user_team = serializer.save(user=request.user, bingo=bingo)
            return Response({
                'message': '팀 참여가 완료되었습니다.',
                'team': user_team.team.team_name,
                'bingo': user_team.bingo.title
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TeamDetailView(APIView):
    # 빙고판 참여 팀 정보
    @permission_classes([IsAuthenticated])
    def get(self, request):
        bingo_id = request.query_params.get('bingo_id')
        team_id = request.query_params.get('team_id')


        if not team_id:
            return Response({'error': '팀 이름을 제공해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        if not bingo_id:
            return Response({'error': '빙고 ID를 제공해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            bingo = Bingo.objects.get(id=bingo_id)
        except Bingo.DoesNotExist:
            return Response({'error': '해당 빙고 게임을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            team = Team.objects.get(id=team_id, bingo=bingo)
        except Team.DoesNotExist:
            return Response({'error': '해당 팀을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        user_teams = User_Team.objects.filter(team=team)
        members = [user_team.name for user_team in user_teams]

        response_data = {
            'team_name': team.team_name,
            'member_count': len(members),
            'members': members
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    # def post(self, request):
    #     bingo_id = request.data.get('bingo_id')
    #     team_name = request.data.get('team_name')

        # if not team_id:
        #     return Response({'error': '팀 이름을 제공해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        # if not bingo_id:
        #     return Response({'error': '빙고 ID를 제공해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # try:
        #     bingo = Bingo.objects.get(id=bingo_id)
        # except Bingo.DoesNotExist:
        #     return Response({'error': '해당 빙고 게임을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        # try:
        #     team = Team.objects.get(bingo=bingo, team_name=team_id)
        # except Team.DoesNotExist:
        #     return Response({'error': '팀을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        # user_teams = User_Team.objects.filter(team=team)
        # members = [user_team.name for user_team in user_teams]

        # response_data = {
        #     'team_name': team.team_name,
        #     'member_count': len(members),
        #     'members': members
        # }
        
        # return Response(response_data, status=status.HTTP_200_OK)
    
class BingoBoardView(APIView):
    # 빙고판 정보
    @permission_classes([IsAuthenticated])
    def get(self, request):
        bingo_id = request.query_params.get('bingo_id')
        team_id = request.query_params.get('team_id')

        if not team_id:
            return Response({'error': '팀 이름을 제공해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        if not bingo_id:
            return Response({'error': '빙고 ID를 제공해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bingo = Bingo.objects.get(id=bingo_id)
        except Bingo.DoesNotExist:
            return Response({'error': '해당 빙고 게임을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            team = Team.objects.get(id=team_id, bingo=bingo)
        except Team.DoesNotExist:
            return Response({'error': '해당 팀을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        bingo_cells = BingoCell.objects.filter(bingo=bingo, team=team)
        cells_data = [
            {
                "row": cell.row,
                "col": cell.col,
                "content": cell.content,
                "is_completed": cell.is_completed_yn,
                "completed_photo": cell.completed_photo.url if cell.completed_photo else None,
                "completed_text": cell.completed_text
            }
            for cell in bingo_cells
        ]

        return Response({
            "bingo_cells": cells_data
        })

    # def post(self, request):
    #     bingo_id = request.data.get('bingo_id')
    #     team_name = request.data.get('team_name')

        # if not team_id:
        #     return Response({'error': '팀 이름을 제공해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        # if not bingo_id:
        #     return Response({'error': '빙고 ID를 제공해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        # try:
        #     bingo = Bingo.objects.get(id=bingo_id)
        # except Bingo.DoesNotExist:
        #     return Response({'error': '해당 빙고 게임을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        # try:
        #     team = Team.objects.get(bingo=bingo, team_name=team_id)
        # except Team.DoesNotExist:
        #     return Response({'error': '해당 팀을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        # bingo_cells = BingoCell.objects.filter(bingo=bingo, team=team)
        # cells_data = [
        #     {
        #         "row": cell.row,
        #         "col": cell.col,
        #         "content": cell.content,
        #         "is_completed": cell.is_completed_yn,
        #         "completed_photo": cell.completed_photo.url if cell.completed_photo else None,
        #         "completed_text": cell.completed_text
        #     }
        #     for cell in bingo_cells
        # ]

        # return Response({
        #     "bingo_cells": cells_data
        # })
    
    # 빙고판 설정 수정
    @permission_classes([IsAuthenticated])
    def patch(self, request):
        bingo_id = request.data.get('bingo_id')
        title = request.data.get('title')
        size = request.data.get('size')
        teams = request.data.get('teams')
        goal = request.data.get('goal')
        end_time = request.data.get('end_date')

        if not bingo_id:
            return Response({'error': '빙고 ID를 제공해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bingo = Bingo.objects.get(id=bingo_id)
        except Bingo.DoesNotExist:
            return Response({'error': '해당 빙고 게임을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        if bingo.creator != request.user:
            return Response({'error': '해당 빙고의 수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

        data = {
            'title': title,
            'size': size,
            'teams': teams,
            'goal': goal,
            'end_time': end_time
        }

        serializer = BingoSerializer(bingo, data={k: v for k, v in data.items() if v is not None}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class MyBingoBoardView(APIView):
    # 나의 빙고판 list
    @permission_classes([IsAuthenticated])
    def get(self, request):
        user = request.user

        try:
            user_team = User_Team.objects.get(user=user)
        except User_Team.DoesNotExist:
            return Response({'error': '해당 사용자가 참여한 팀이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        team = user_team.team
        bingo = user_team.bingo

        bingo_cells = BingoCell.objects.filter(bingo=bingo, team=team)
        cells_data = [
            {
                "row": cell.row,
                "col": cell.col,
                "content": cell.content,
                "is_completed": cell.is_completed_yn,
                "completed_photo": cell.completed_photo.url if cell.completed_photo else None,
                "completed_text": cell.completed_text
            }
            for cell in bingo_cells
        ]

        return Response({
            "bingo_title": bingo.title,
            "team_name": team.team_name,
            "bingo_cells": cells_data
        }, status=status.HTTP_200_OK)
    
class DeleteBingoView(APIView):
    # 빙고판 삭제
    @permission_classes([IsAuthenticated])
    def delete(self, request):
        bingo_id = request.data.get('bingo_id')
        try:
            bingo = Bingo.objects.get(id=bingo_id)
        except Bingo.DoesNotExist:
            return Response({'error': '해당 빙고 게임을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        if bingo.creator != request.user:
            return Response({'error': '해당 빙고의 삭제 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

        bingo.delete()
        return Response({'빙고 게임이 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
