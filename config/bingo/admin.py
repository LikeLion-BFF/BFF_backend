from django.contrib import admin
from .models import Bingo, Team, User_Team, BingoCell

@admin.register(Bingo)
class BingoAdmin(admin.ModelAdmin):
    list_display = ('title', 'size', 'teams', 'goal', 'end_date', 'created_at', 'creator', 'code')
    search_fields = ('title', 'code')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('bingo', 'team_name')
    search_fields = ('team_name',)

@admin.register(User_Team)
class UserTeamAdmin(admin.ModelAdmin):
    list_display = ('bingo','user', 'team', 'name')
    search_fields = ('bingo','user__username', 'team__name', 'name')

@admin.register(BingoCell)
class BingoCellAdmin(admin.ModelAdmin):
    list_display = ('bingo', 'team', 'row', 'col', 'content', 'is_completed_yn')
    search_fields = ('bingo__title', 'team__team_name', 'content')
