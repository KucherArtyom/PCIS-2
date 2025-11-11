from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Clubs, Transfers, Players, Games, GameEvents
#from .models import CustomUser
from django.contrib.auth.models import User
from .models import UserProfile

class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clubs
        fields = ['club_id', 'name']

class TransferSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source='player_id.name', read_only=True)
    from_club_name = serializers.CharField(source='from_club_id.name', read_only=True)
    to_club_name = serializers.CharField(source='to_club_id.name', read_only=True)

    class Meta:
        model = Transfers
        fields = [
            'player_name',
            'from_club_name',
            'to_club_name',
            'transfer_date',
            'transfer_season',
            'market_value_in_eur'
        ]


class GameSerializer(serializers.ModelSerializer):
    home_club_name = serializers.CharField(source='home_club_id.name', read_only=True)
    away_club_name = serializers.CharField(source='away_club_id.name', read_only=True)
    home_club_id = serializers.IntegerField(source='home_club_id.club_id', read_only=True)
    away_club_id = serializers.IntegerField(source='away_club_id.club_id', read_only=True)

    class Meta:
        model = Games
        fields = [
            'game_id', 'date', 'home_club_name', 'away_club_name',
            'home_club_goals', 'away_club_goals', 'aggregate',
            'home_club_formation', 'away_club_formation',
            'stadium', 'attendance', 'referee',
            'home_club_id', 'away_club_id'
        ]


class GameEventSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source='player_id.name', read_only=True)
    club_name = serializers.CharField(source='club_id.name', read_only=True)

    class Meta:
        model = GameEvents
        fields = [
            'minute', 'player_name', 'type', 'description', 'club_name'
        ]


class SimpleGameSerializer(serializers.ModelSerializer):
    home_club_name = serializers.CharField(source='home_club_id.name', read_only=True)
    away_club_name = serializers.CharField(source='away_club_id.name', read_only=True)

    class Meta:
        model = Games
        fields = ['game_id', 'date', 'home_club_name', 'away_club_name']


class ClubDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clubs
        fields = [
            'club_id', 'name', 'average_age', 'stadium_name',
            'stadium_seats', 'squad_size', 'total_market_value',
            'coach_name', 'foreigners_percentage'
        ]

class ClubPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Players
        fields = ['player_id', 'name', 'sub_position', 'position', 'market_value_in_eur']


class PlayerDetailSerializer(serializers.ModelSerializer):
    current_club_name = serializers.CharField(source='current_club_id.name', read_only=True)

    class Meta:
        model = Players
        fields = [
            'player_id', 'name', 'first_name', 'last_name',
            'country_of_birth', 'city_of_birth', 'date_of_birth',
            'sub_position', 'position', 'foot', 'height_in_cm',
            'market_value_in_eur', 'current_club_name',
            'country_of_citizenship', 'contract_expiration_date'
        ]


class SimplePlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Players
        fields = ['player_id', 'name', 'current_club_id']



class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    phone = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'phone')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs

    def create(self, validated_data):
        phone = validated_data.pop('phone')
        validated_data.pop('password_confirm')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        UserProfile.objects.create(user=user, phone=phone)

        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Неверные учетные данные')
            if not user.is_active:
                raise serializers.ValidationError('Аккаунт деактивирован')
            attrs['user'] = user
        return attrs

class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source='userprofile.phone', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'first_name', 'last_name')



class AdminUserSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(source='is_staff', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_admin')


class GameCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Games
        fields = [
            'home_club_name', 'away_club_name', 'aggregate', 'date',
            'stadium', 'attendance', 'home_club_formation', 'away_club_formation'
        ]

class GameUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Games
        fields = [
            'home_club_name', 'away_club_name', 'aggregate', 'date',
            'stadium', 'attendance', 'home_club_formation', 'away_club_formation'
        ]

class GameAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Games
        fields = [
            'game_id', 'home_club_name', 'away_club_name', 'aggregate', 'date',
            'stadium', 'attendance', 'home_club_formation', 'away_club_formation'
        ]


class PlayerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Players
        fields = [
            'first_name', 'last_name', 'current_club_name', 'country_of_birth',
            'date_of_birth', 'sub_position', 'height_in_cm', 'foot', 'market_value_in_eur'
        ]

class PlayerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Players
        fields = [
            'first_name', 'last_name', 'current_club_name', 'country_of_birth',
            'date_of_birth', 'sub_position', 'height_in_cm', 'foot', 'market_value_in_eur'
        ]

class PlayerAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Players
        fields = [
            'player_id', 'first_name', 'last_name', 'name', 'current_club_name',
            'country_of_birth', 'date_of_birth', 'sub_position', 'position',
            'height_in_cm', 'foot', 'market_value_in_eur'
        ]

class SimplePlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Players
        fields = ['player_id', 'name', 'current_club_id']


class ClubCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clubs
        fields = [
            'name', 'average_age', 'squad_size', 'stadium_name',
            'stadium_seats', 'coach_name'
        ]

class ClubUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clubs
        fields = [
            'name', 'average_age', 'squad_size', 'stadium_name',
            'stadium_seats', 'coach_name'
        ]

class ClubAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clubs
        fields = [
            'club_id', 'name', 'average_age', 'squad_size', 'stadium_name',
            'stadium_seats', 'coach_name', 'total_market_value', 'foreigners_percentage'
        ]

class TransferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfers
        fields = [
            'player_name', 'from_club_name', 'to_club_name',
            'transfer_date', 'transfer_season', 'market_value_in_eur'
        ]

class TransferUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfers
        fields = [
            'player_name', 'from_club_name', 'to_club_name',
            'transfer_date', 'transfer_season', 'market_value_in_eur'
        ]

class TransferAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfers
        fields = [
            'id', 'player_name', 'from_club_name', 'to_club_name',
            'transfer_date', 'transfer_season', 'market_value_in_eur',
            'player_id', 'from_club_id', 'to_club_id'
        ]