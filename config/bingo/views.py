import random, string
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from .models import Bingo, Team, User_Team, BingoCell
from rank.models import BingoProgress
from .serializers import BingoSerializer, JoinTeamSerializer, UserSerializer
from django.shortcuts import get_object_or_404

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
                'bingo_id':bingo.id,
                'code': bingo.code,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BingoJoinView(APIView):
    # 빙고판 참여 (1단계: 코드 검증 및 팀 목록 반환)
    @permission_classes([IsAuthenticated])
    def post(self, request):
        code = request.data.get('code')

        if not code:
            return Response({'error': '코드를 제공해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bingo = Bingo.objects.get(code=code)
        except Bingo.DoesNotExist:
            return Response({'error': '해당 코드를 가진 빙고를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        # 코드가 일치하면 빙고에 속한 팀 목록 반환
        teams = Team.objects.filter(bingo=bingo)
        team_names = teams.values_list('team_name', flat=True)

        return Response({
            'bingo_id': bingo.id, 
            'teams': team_names
        }, status=status.HTTP_200_OK)
    
class JoinTeamView(APIView):
    # 빙고판 참여 (2단계: 팀 선택 및 참여 완료)
    @permission_classes([IsAuthenticated])
    def post(self, request):
        bingo_id = request.data.get('bingo_id')
        team_name = request.data.get('team_name')
        name = request.data.get('name')

        if not bingo_id or not team_name or not name:
            return Response({'error': '빙고 ID, 팀 이름 및 닉네임을 제공해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bingo = Bingo.objects.get(id=bingo_id)
        except Bingo.DoesNotExist:
            return Response({'error': '해당 빙고를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # 특정 빙고 게임에 속하는 팀을 필터링
            team = Team.objects.get(bingo=bingo, team_name=team_name)
        except Team.DoesNotExist:
            return Response({'error': '해당 팀을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        except Team.MultipleObjectsReturned:
            return Response({'error': '여러 팀이 발견되었습니다. 팀 이름을 확인해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = JoinTeamSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user_team = serializer.save(user=request.user, bingo=bingo, team=team)  # team 인자 추가
            return Response({
                'message': '팀 참여가 완료되었습니다.',
                'team': user_team.team.team_name,
                'name': user_team.name
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
            'bingo_title':bingo.title,
            'team_name': team.team_name,
            'member_count': len(members),
            'members': members
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

class CreatorDetailView(APIView):
    # 빙고 생성자 정보
    permission_classes = [IsAuthenticated]

    def get(self, request, bingo_id):
        try:
            bingo = Bingo.objects.get(id=bingo_id)
        except Bingo.DoesNotExist:
            return Response({'message': '해당 빙고 게임이 존재하지 않습니다.'}, status=404)

        if bingo.creator == request.user:
            return Response({'message': '해당 빙고의 생성자입니다.'})
        else:
            return Response({'message': '해당 빙고의 생성자가 아닙니다.'})

class BingoBoardView(APIView):
    # 빙고판 정보 + 랭킹정보 반환
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
        # BingoProgressTotalView와 유사한 진행 상황 데이터 가져오기
        progress_data = BingoProgress.objects.filter(bingo=bingo).order_by(
            '-completed_bingo_count',
            '-completed_cell_count',
            'team__team_name'
        ).values(
            'team__team_name', 'completed_bingo_count', 'completed_cell_count'
        )

       # BingoBoard의 응답 데이터에 진행 상황 데이터 추가
        return Response({
            "bingo_cells": cells_data,
            "rank": list(progress_data)  # 진행 상황 데이터를 추가
        }, status=status.HTTP_200_OK)

        # return Response({
        #     "bingo_cells": cells_data
        # })

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

        # 사용자가 속한 모든 User_Team 가져오기
        user_teams = User_Team.objects.filter(user=user)
        if not user_teams.exists():
            return Response({'error': '해당 사용자가 참여한 팀이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        # 각 빙고판과 그에 속한 팀의 빙고 셀 정보 수집
        bingo_data = []
        for user_team in user_teams:
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

            bingo_data.append({
                "bingo_id": bingo.id,
                "bingo_title": bingo.title,
                "code": bingo.code,
                "team_id": team.id,
                "bingo_cells": cells_data
            })

        return Response(bingo_data, status=status.HTTP_200_OK)
    
class EndTimeView(APIView):
    # 빙고 종료 시간 정보 반환
    @permission_classes([IsAuthenticated])
    def get(self, request):
        bingo_id = request.query_params.get('bingo_id')
        try:
            bingo = Bingo.objects.get(id=bingo_id)
        except Bingo.DoesNotExist:
            return Response({'error': '해당 빙고 게임을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"end_date": bingo.end_date}, status=status.HTTP_200_OK)
    
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
    
## 빙고판 완료 인증
    #step1. 해당 빙고판의 해당 셀을 찾아가 is_completed_yn,photo,text업데이트
    #step2. BingoProgress의 completed_cell_count +1
    #step3. BingoProgress의 completed_bingo_count검증해서 빙고가 완성되면 +1
class UpdateProgressView(APIView):
    @permission_classes([IsAuthenticated])
    
    def post(self, request, *args, **kwargs):
        # 요청 데이터에서 필요한 값을 가져옴
        bingo_id = request.data.get('bingo_id')
        team_id = request.data.get('team_id')
        row = request.data.get('row')
        col = request.data.get('col')
        completed_photo = request.FILES.get('completed_photo')  # 파일은 FILES에서 가져옴
        completed_text = request.data.get('completed_text', '')  # 값이 없을 때 빈 문자열로 저장

        # 필수 파라미터가 없는 경우 에러 응답
        if not bingo_id or not team_id or row is None or col is None:
            return Response({'error': '필수 파라미터가 누락되었습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        # Bingo, Team 객체 확인
        bingo = get_object_or_404(Bingo, id=bingo_id)
        team = get_object_or_404(Team, id=team_id, bingo=bingo)

        # BingoCell 찾기
        try:
            bingo_cell = BingoCell.objects.get(bingo=bingo, team=team, row=row, col=col)
        except BingoCell.DoesNotExist:
            return Response({'error': '해당 빙고 셀을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        # BingoCell 업데이트
        bingo_cell.is_completed_yn = True
        bingo_cell.completed_photo = completed_photo if completed_photo else bingo_cell.completed_photo
        bingo_cell.completed_text = completed_text  # 값이 없을 때 빈 문자열 저장
        bingo_cell.save()  # 변경 사항 저장

        # BingoProgress 업데이트: completed_cell_count 값을 +1
        try:
            bingo_progress = BingoProgress.objects.get(bingo=bingo, team=team)
            bingo_progress.completed_cell_count += 1
            bingo_progress.save()
        except BingoProgress.DoesNotExist:
            return Response({'error': '빙고 진행 데이터를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        # 빙고 완성 여부 검사 및 completed_bingo_count 업데이트
        calculated_bingo_count = self.check_bingo_completion(bingo, team)

        # 계산된 빙고 카운트와 DB에 저장된 값 비교
        if calculated_bingo_count != bingo_progress.completed_bingo_count:
            bingo_progress.completed_bingo_count = calculated_bingo_count
            bingo_progress.save()  # 값이 다를 때만 업데이트

        return Response({'message': '빙고 셀이 성공적으로 업데이트되었습니다.'}, status=status.HTTP_200_OK)

    def check_bingo_completion(self, bingo, team):
        """
        빙고판에서 가로, 세로, 대각선이 완전히 완료되었는지 확인하는 메서드.
        완성된 빙고의 개수를 반환.
        """
        size = int(bingo.size)  # 빙고판 크기 (예: 3x3, 4x4, 5x5 등)
        
        # 빙고판의 모든 칸 가져오기
        bingo_cells = BingoCell.objects.filter(bingo=bingo, team=team)

        completed_bingo_count = 0  # 완성된 빙고 개수

        # 1. 가로 검사
        for row in range(1, size + 1):
            row_cells = bingo_cells.filter(row=row)
            if all(cell.is_completed_yn for cell in row_cells):
                completed_bingo_count += 1  # 가로 줄이 완성되었으면 빙고 추가

        # 2. 세로 검사
        for col in range(1, size + 1):
            col_cells = bingo_cells.filter(col=col)
            if all(cell.is_completed_yn for cell in col_cells):
                completed_bingo_count += 1  # 세로 줄이 완성되었으면 빙고 추가

        # 3. 대각선 검사 (왼쪽 위에서 오른쪽 아래)
        diagonal1_cells = [bingo_cells.get(row=i, col=i) for i in range(1, size + 1)]
        if all(cell.is_completed_yn for cell in diagonal1_cells):
            completed_bingo_count += 1  # 왼쪽 위에서 오른쪽 아래로 대각선 완성

        # 4. 대각선 검사 (오른쪽 위에서 왼쪽 아래)
        diagonal2_cells = [bingo_cells.get(row=i, col=(size - i + 1)) for i in range(1, size + 1)]
        if all(cell.is_completed_yn for cell in diagonal2_cells):
            completed_bingo_count += 1  # 오른쪽 위에서 왼쪽 아래로 대각선 완성

        return completed_bingo_count
