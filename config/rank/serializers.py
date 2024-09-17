from rest_framework import serializers
from .models import BingoProgress

class BingoProgressSerializer(serializers.Serializer):
    class Meta:
        model = BingoProgress
        fields = ['id', 'bingo', 'team', 'completed_bingo_count', 'completed_cell_count']

