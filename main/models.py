from django.db import models
from django.contrib.auth.models import User

class Competitions(models.Model):
    competition_id = models.TextField(primary_key=True)
    competition_code = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    sub_type = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    country_id = models.IntegerField(blank=True, null=True)
    country_name = models.TextField(blank=True, null=True)
    domestic_league_code = models.TextField(blank=True, null=True)
    confederation = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    is_major_national_league = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'competitions'
        #managed = False

class Clubs(models.Model):
    club_id = models.IntegerField(primary_key=True)
    club_code = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    domestic_competition_id = models.ForeignKey(
        Competitions,
        on_delete=models.DO_NOTHING,
        db_column='domestic_competition_id',
        blank=True,
        null=True
    )
    total_market_value = models.FloatField(blank=True, null=True)
    squad_size = models.IntegerField(blank=True, null=True)
    average_age = models.FloatField(blank=True, null=True)
    foreigners_number = models.IntegerField(blank=True, null=True)
    foreigners_percentage = models.FloatField(blank=True, null=True)
    national_team_players = models.IntegerField(blank=True, null=True)
    stadium_name = models.TextField(blank=True, null=True)
    stadium_seats = models.IntegerField(blank=True, null=True)
    net_transfer_record = models.TextField(blank=True, null=True)
    coach_name = models.TextField(blank=True, null=True)
    last_season = models.IntegerField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'clubs'
        #managed = False

class Games(models.Model):
    game_id = models.IntegerField(primary_key=True)
    competition_id = models.ForeignKey(
        Competitions,
        on_delete=models.DO_NOTHING,
        db_column='competition_id',
        blank=True,
        null=True
    )
    season = models.IntegerField(blank=True, null=True)
    round = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    home_club_id = models.ForeignKey(
        Clubs,
        on_delete=models.DO_NOTHING,
        db_column='home_club_id',
        related_name='home_games',
        blank=True,
        null=True
    )
    away_club_id = models.ForeignKey(
        Clubs,
        on_delete=models.DO_NOTHING,
        db_column='away_club_id',
        related_name='away_games',
        blank=True,
        null=True
    )
    home_club_goals = models.IntegerField(blank=True, null=True)
    away_club_goals = models.IntegerField(blank=True, null=True)
    home_club_position = models.IntegerField(blank=True, null=True)
    away_club_position = models.IntegerField(blank=True, null=True)
    home_club_manager_name = models.TextField(blank=True, null=True)
    away_club_manager_name = models.TextField(blank=True, null=True)
    stadium = models.TextField(blank=True, null=True)
    attendance = models.IntegerField(blank=True, null=True)
    referee = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    home_club_formation = models.TextField(blank=True, null=True)
    away_club_formation = models.TextField(blank=True, null=True)
    home_club_name = models.TextField(blank=True, null=True)
    away_club_name = models.TextField(blank=True, null=True)
    aggregate = models.TextField(blank=True, null=True)
    competition_type = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'games'
        #managed = False

class Players(models.Model):
    player_id = models.IntegerField(primary_key=True)
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    last_season = models.IntegerField(blank=True, null=True)
    current_club_id = models.ForeignKey(
        Clubs,
        on_delete=models.DO_NOTHING,
        db_column='current_club_id',
        blank=True,
        null=True
    )
    player_code = models.TextField(blank=True, null=True)
    country_of_birth = models.TextField(blank=True, null=True)
    city_of_birth = models.TextField(blank=True, null=True)
    country_of_citizenship = models.TextField(blank=True, null=True)
    date_of_birth = models.DateTimeField(blank=True, null=True)
    sub_position = models.TextField(blank=True, null=True)
    position = models.TextField(blank=True, null=True)
    foot = models.TextField(blank=True, null=True)
    height_in_cm = models.IntegerField(blank=True, null=True)
    contract_expiration_date = models.DateTimeField(blank=True, null=True)
    agent_name = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    current_club_domestic_competition_id = models.ForeignKey(
        Competitions,
        on_delete=models.DO_NOTHING,
        db_column='current_club_domestic_competition_id',
        blank=True,
        null=True
    )
    current_club_name = models.TextField(blank=True, null=True)
    market_value_in_eur = models.IntegerField(blank=True, null=True)
    highest_market_value_in_eur = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'players'
        #managed = False

class Appearances(models.Model):
    appearance_id = models.TextField(primary_key=True)
    game_id = models.ForeignKey(
        Games,
        on_delete=models.DO_NOTHING,
        db_column='game_id',
        blank=True,
        null=True
    )
    player_id = models.ForeignKey(
        Players,
        on_delete=models.DO_NOTHING,
        db_column='player_id',
        blank=True,
        null=True
    )
    player_club_id = models.ForeignKey(
        Clubs,
        on_delete=models.DO_NOTHING,
        db_column='player_club_id',
        related_name='appearances_as_player_club',
        blank=True,
        null=True
    )
    player_current_club_id = models.ForeignKey(
        Clubs,
        on_delete=models.DO_NOTHING,
        db_column='player_current_club_id',
        related_name='appearances_as_current_club',
        blank=True,
        null=True
    )
    date = models.DateField(blank=True, null=True)
    player_name = models.TextField(blank=True, null=True)
    competition_id = models.ForeignKey(
        Competitions,
        on_delete=models.DO_NOTHING,
        db_column='competition_id',
        blank=True,
        null=True
    )
    yellow_cards = models.IntegerField(blank=True, null=True)
    red_cards = models.IntegerField(blank=True, null=True)
    goals = models.IntegerField(blank=True, null=True)
    assists = models.IntegerField(blank=True, null=True)
    minutes_played = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'appearances'
        #managed = False

class ClubGames(models.Model):
    game_id = models.ForeignKey(
        Games,
        on_delete=models.DO_NOTHING,
        db_column='game_id',
        blank=True,
        null=True
    )
    club_id = models.ForeignKey(
        Clubs,
        on_delete=models.DO_NOTHING,
        db_column='club_id',
        blank=True,
        null=True
    )
    own_goals = models.IntegerField(blank=True, null=True)
    own_position = models.IntegerField(blank=True, null=True)
    own_manager_name = models.TextField(blank=True, null=True)
    opponent_id = models.ForeignKey(
        Clubs,
        on_delete=models.DO_NOTHING,
        db_column='opponent_id',
        related_name='club_games_as_opponent',
        blank=True,
        null=True
    )
    opponent_goals = models.IntegerField(blank=True, null=True)
    opponent_position = models.IntegerField(blank=True, null=True)
    opponent_manager_name = models.TextField(blank=True, null=True)
    hosting = models.TextField(blank=True, null=True)
    is_win = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'club_games'
        managed = False

class GameEvents(models.Model):
    game_event_id = models.TextField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    game_id = models.ForeignKey(
        Games,
        on_delete=models.DO_NOTHING,
        db_column='game_id',
        blank=True,
        null=True
    )
    minute = models.IntegerField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    club_id = models.ForeignKey(
        Clubs,
        on_delete=models.DO_NOTHING,
        db_column='club_id',
        blank=True,
        null=True
    )
    player_id = models.ForeignKey(
        Players,
        on_delete=models.DO_NOTHING,
        db_column='player_id',
        blank=True,
        null=True
    )
    description = models.TextField(blank=True, null=True)
    player_in_id = models.ForeignKey(
        Players,
        on_delete=models.DO_NOTHING,
        db_column='player_in_id',
        related_name='game_events_as_substitute',
        blank=True,
        null=True
    )
    player_assist_id = models.ForeignKey(
        Players,
        on_delete=models.DO_NOTHING,
        db_column='player_assist_id',
        related_name='game_events_as_assister',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'game_events'
        #managed = False

class GameLineups(models.Model):
    game_lineups_id = models.TextField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    game_id = models.ForeignKey(
        Games,
        on_delete=models.DO_NOTHING,
        db_column='game_id',
        blank=True,
        null=True
    )
    player_id = models.ForeignKey(
        Players,
        on_delete=models.DO_NOTHING,
        db_column='player_id',
        blank=True,
        null=True
    )
    club_id = models.ForeignKey(
        Clubs,
        on_delete=models.DO_NOTHING,
        db_column='club_id',
        blank=True,
        null=True
    )
    player_name = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    position = models.TextField(blank=True, null=True)
    number = models.TextField(blank=True, null=True)
    team_captain = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'game_lineups'
        #managed = False

class PlayerValuations(models.Model):
    player_id = models.ForeignKey(
        Players,
        on_delete=models.DO_NOTHING,
        db_column='player_id',
        blank=True,
        null=True
    )
    date = models.DateField(blank=True, null=True)
    market_value_in_eur = models.IntegerField(blank=True, null=True)
    current_club_id = models.ForeignKey(
        Clubs,
        on_delete=models.DO_NOTHING,
        db_column='current_club_id',
        blank=True,
        null=True
    )
    player_club_domestic_competition_id = models.ForeignKey(
        Competitions,
        on_delete=models.DO_NOTHING,
        db_column='player_club_domestic_competition_id',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'player_valuations'
        managed = False

class Transfers(models.Model):
    player_id = models.ForeignKey(
        Players,
        on_delete=models.DO_NOTHING,
        db_column='player_id',
        blank=True,
        null=True
    )
    transfer_date = models.DateField(blank=True, null=True)
    transfer_season = models.TextField(blank=True, null=True)
    from_club_id = models.ForeignKey(
        Clubs,
        on_delete=models.DO_NOTHING,
        db_column='from_club_id',
        related_name='transfers_from',
        blank=True,
        null=True
    )
    to_club_id = models.ForeignKey(
        Clubs,
        on_delete=models.DO_NOTHING,
        db_column='to_club_id',
        related_name='transfers_to',
        blank=True,
        null=True
    )
    from_club_name = models.TextField(blank=True, null=True)
    to_club_name = models.TextField(blank=True, null=True)
    transfer_fee = models.FloatField(blank=True, null=True)
    market_value_in_eur = models.FloatField(blank=True, null=True)
    player_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'transfers'
        managed = False


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"
# Create your models here.
