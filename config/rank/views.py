from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from bingo.models import Bingo, User_Team
from .models import BingoProgress
from .serializers import BingoProgressSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

# Create your views here.
##우리팀 진행사항 반영
# class BingoProgressView(APIView):
#     @permission_classes([IsAuthenticated])
#     def get(self, request, *args, **kwargs):
#         # 쿼리 파라미터에서 bingo_id와 team_id를 가져옴
#         bingo_id = request.query_params.get('bingo_id')
#         team_id = request.query_params.get('team_id')

#         # 필수 파라미터가 누락된 경우 에러 응답 반환
#         if not bingo_id or not team_id:
#             return Response({'error': 'bingo_id나 team_id를 넘겨주세요'}, status=status.HTTP_400_BAD_REQUEST)
        
#         # bingo_id에 해당하는 Bingo 객체를 가져옵니다.
#         bingo = get_object_or_404(Bingo, id=bingo_id)
        
#         # team_id에 해당하는 Team 객체를 가져옵니다.
#         team = get_object_or_404(BingoProgress, team_id=team_id, bingo=bingo)
        
#         # 해당 팀의 사용자(User_Team) 정보를 가져옵니다.
#         user_team_members = User_Team.objects.filter(team=team.team, bingo=bingo)

#         # 해당 팀의 진행 상황과 유저 이름을 포함한 정보를 반환
#         result = {
#             'team_name': team.team.team_name,
#             'completed_bingo_count': team.completed_bingo_count,
#             'completed_cell_count': team.completed_cell_count
#         }

#         return Response(result, status=status.HTTP_200_OK)
    
##팀별 진행사항 반영
    #특정 bingo_id에 대한 팀별 진행 현황을 가져오고, 
    #completed_bingo_count 기준으로 정렬, 동률 시 completed_cell_count로 정렬.
    #그리고 각 팀에 속한 사용자의 이름도 반환.
class BingoProgressView(APIView):
    @permission_classes([IsAuthenticated])
    def get(self, request, *args, **kwargs):
        # 쿼리 파라미터에서 bingo_id를 가져옴
        bingo_id = request.query_params.get('bingo_id')

        # 필수 파라미터가 누락된 경우 에러 응답 반환
        if not bingo_id:
            return Response({'error': 'bingo_id를 넘겨주세요'}, status=status.HTTP_400_BAD_REQUEST)
        
        # bingo_id에 해당하는 Bingo 객체를 가져옵니다.
        bingo = get_object_or_404(Bingo, id=bingo_id)
        
        # 해당 Bingo와 관련된 모든 팀의 진행 현황을 가져오고 정렬합니다.
        progress_data = BingoProgress.objects.filter(bingo=bingo).order_by(
            '-completed_bingo_count', 
            '-completed_cell_count', 
            'team__team_name'
        ).values(
            'team__team_name', 'completed_bingo_count', 'completed_cell_count'
        )

        # 데이터 응답으로 반환
        return Response(list(progress_data), status=status.HTTP_200_OK)