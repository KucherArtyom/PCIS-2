from django.http import Http404, FileResponse
from django.shortcuts import render

from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated, AllowAny
#from .models import CustomUser
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.db import connection
from .models import Clubs, Transfers, Games, GameEvents, Players
from .serializers import ClubSerializer, TransferSerializer, GameSerializer, GameEventSerializer, SimpleGameSerializer, ClubDetailSerializer, ClubPlayerSerializer, SimplePlayerSerializer, PlayerDetailSerializer
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer, AdminUserSerializer
from .serializers import GameCreateSerializer, GameAdminSerializer, GameUpdateSerializer
from .serializers import PlayerAdminSerializer, PlayerUpdateSerializer, PlayerCreateSerializer
from .serializers import ClubCreateSerializer, ClubUpdateSerializer, ClubAdminSerializer
from .serializers import TransferAdminSerializer, TransferCreateSerializer, TransferUpdateSerializer
from django.contrib.auth.models import User
from .models import UserProfile
import os


class ClubViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Clubs.objects.all().order_by('name')
    serializer_class = ClubSerializer

class TransferViewSet(viewsets.GenericViewSet):
    @action(detail=False, methods=['get'])
    def search(self, request):
        from_club_id = request.GET.get('from_club')
        to_club_id = request.GET.get('to_club')

        query = """
               SELECT player_name, from_club_id, to_club_id, 
                      transfer_date, transfer_season, market_value_in_eur
               FROM transfers 
               WHERE 1=1
           """
        params = []

        if from_club_id:
            query += " AND from_club_id = %s"
            params.append(from_club_id)

        if to_club_id:
            query += " AND to_club_id = %s"
            params.append(to_club_id)

        query += " ORDER BY transfer_date DESC LIMIT 100"

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = []
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))

                from_club_name = Clubs.objects.filter(club_id=row_dict['from_club_id']).first()
                to_club_name = Clubs.objects.filter(club_id=row_dict['to_club_id']).first()

                results.append({
                    'player_name': row_dict['player_name'],
                    'from_club_name': from_club_name.name if from_club_name else 'Unknown',
                    'to_club_name': to_club_name.name if to_club_name else 'Unknown',
                    'transfer_date': row_dict['transfer_date'],
                    'transfer_season': row_dict['transfer_season'],
                    'market_value_in_eur': row_dict['market_value_in_eur']
                })

        return Response(results)


class GameViewSet(viewsets.GenericViewSet):
    serializer_class = SimpleGameSerializer

    @action(detail=False, methods=['get'])
    def search_options(self, request):
        dates = Games.objects.dates('date', 'day', order='DESC')[:100]
        home_teams = Games.objects.values_list('home_club_name', flat=True).distinct().order_by('home_club_name')
        away_teams = Games.objects.values_list('away_club_name', flat=True).distinct().order_by('away_club_name')

        all_teams = sorted(set(list(home_teams) + list(away_teams)))

        return Response({
            'dates': [date.strftime('%Y-%m-%d') for date in dates],
            'teams': all_teams
        })

    @action(detail=False, methods=['get'])
    def filtered_options(self, request):
        home_team = request.GET.get('home_team', '')
        away_team = request.GET.get('away_team', '')
        date = request.GET.get('date', '')

        queryset = Games.objects.all()

        if home_team:
            queryset = queryset.filter(home_club_name=home_team)
        if away_team:
            queryset = queryset.filter(away_club_name=away_team)
        if date:
            queryset = queryset.filter(date=date)

        available_home_teams = queryset.values_list('home_club_name', flat=True).distinct().order_by('home_club_name')
        available_away_teams = queryset.values_list('away_club_name', flat=True).distinct().order_by('away_club_name')
        available_dates = queryset.dates('date', 'day', order='DESC')

        return Response({
            'home_teams': list(available_home_teams),
            'away_teams': list(available_away_teams),
            'dates': [d.strftime('%Y-%m-%d') for d in available_dates]
        })

    @action(detail=False, methods=['get'])
    def search(self, request):
        home_team = request.GET.get('home_team')
        away_team = request.GET.get('away_team')
        date = request.GET.get('date')

        queryset = Games.objects.select_related('home_club_id', 'away_club_id').all()

        if home_team:
            queryset = queryset.filter(home_club_name=home_team)
        if away_team:
            queryset = queryset.filter(away_club_name=away_team)
        if date:
            queryset = queryset.filter(date=date)

        game = queryset.first()

        if not game:
            return Response({'detail': 'Матч не найден'}, status=404)

        events = GameEvents.objects.filter(game_id=game.game_id).select_related(
            'player_id', 'club_id'
        ).order_by('minute')

        home_events = events.filter(club_id=game.home_club_id)
        away_events = events.filter(club_id=game.away_club_id)

        game_serializer = GameSerializer(game)
        home_events_serializer = GameEventSerializer(home_events, many=True)
        away_events_serializer = GameEventSerializer(away_events, many=True)

        return Response({
            'game': game_serializer.data,
            'home_events': home_events_serializer.data,
            'away_events': away_events_serializer.data
        })


class ClubViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Clubs.objects.all().order_by('name')
    serializer_class = ClubSerializer

    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        try:
            club = self.get_object()
            serializer = ClubDetailSerializer(club)
            return Response(serializer.data)
        except Clubs.DoesNotExist:
            return Response({'detail': 'Клуб не найден'}, status=404)

    @action(detail=True, methods=['get'])
    def players(self, request, pk=None):
        try:
            club = self.get_object()
            players = Players.objects.filter(current_club_id=club.club_id).order_by('name')
            serializer = ClubPlayerSerializer(players, many=True)
            return Response(serializer.data)
        except Clubs.DoesNotExist:
            return Response({'detail': 'Клуб не найден'}, status=404)

    @action(detail=False, methods=['get'])
    def search(self, request):
        club_id = request.GET.get('club_id')
        if not club_id:
            return Response({'detail': 'Не указан ID клуба'}, status=400)

        try:
            club = Clubs.objects.get(club_id=club_id)
            club_serializer = ClubDetailSerializer(club)

            players = Players.objects.filter(current_club_id=club_id).order_by('name')
            players_serializer = ClubPlayerSerializer(players, many=True)

            return Response({
                'club': club_serializer.data,
                'players': players_serializer.data
            })
        except Clubs.DoesNotExist:
            return Response({'detail': 'Клуб не найден'}, status=404)

    @action(detail=True, methods=['get'])
    def logo(self, request, pk=None):
        try:
            club = self.get_object()
            logo_path = f"D://club_logos/{club.club_id}.png"

            if not os.path.exists(logo_path):
                for ext in ['.jpg', '.jpeg', '.gif', '.webp']:
                    alt_path = f"D://club_logos/{club.club_id}{ext}"
                    if os.path.exists(alt_path):
                        logo_path = alt_path
                        break
                else:
                    raise Http404("Логотип не найден")

            return FileResponse(open(logo_path, 'rb'), content_type='image/png')

        except Clubs.DoesNotExist:
            return Response({'detail': 'Клуб не найден'}, status=404)
        except Exception as e:
            return Response({'detail': f'Ошибка при загрузке логотипа: {str(e)}'}, status=500)


class PlayerViewSet(viewsets.GenericViewSet):
    queryset = Players.objects.all()
    serializer_class = SimplePlayerSerializer

    @action(detail=False, methods=['get'])
    def clubs(self, request):
        clubs = Clubs.objects.all().order_by('name')
        serializer = ClubSerializer(clubs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def players_by_club(self, request):
        club_id = request.GET.get('club_id')
        if not club_id:
            return Response({'detail': 'Не указан ID клуба'}, status=400)

        players = Players.objects.filter(current_club_id=club_id).order_by('name')
        serializer = SimplePlayerSerializer(players, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        player_id = request.GET.get('player_id')
        if not player_id:
            return Response({'detail': 'Не указан ID игрока'}, status=400)

        try:
            player = Players.objects.get(player_id=player_id)
            serializer = PlayerDetailSerializer(player)
            return Response(serializer.data)
        except Players.DoesNotExist:
            return Response({'detail': 'Игрок не найден'}, status=404)
# Create your views here.

class AuthViewSet(viewsets.GenericViewSet):
    def get_permissions(self):
        if self.action == 'check_admin_status':
            return [IsAuthenticated()]
        return [AllowAny()]
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            user_data = UserSerializer(user).data
            return Response({
                'message': 'Регистрация успешна',
                'user': user_data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            user_data = UserSerializer(user).data
            return Response({
                'message': 'Вход выполнен успешно',
                'user': user_data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'message': 'Выход выполнен успешно'})

    @action(detail=False, methods=['get'])
    def user(self, request):
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        return Response({'detail': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def check_admin_status(self, request):
        print(f"Checking admin status for user: {request.user}, is_staff: {request.user.is_staff}")
        is_admin = request.user.is_staff
        if is_admin:
            serializer = AdminUserSerializer(request.user)
            return Response({
                'is_admin': True,
                'user': serializer.data
            })
        else:
            return Response({
                'is_admin': False,
                'message': 'Недостаточно прав'
            })

from rest_framework.permissions import IsAdminUser

'''
class AdminAuthViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @action(detail=False, methods=['get'])
    def check_admin(self, request):
        if request.user.is_staff:
            serializer = AdminUserSerializer(request.user)
            return Response({
                'is_admin': True,
                'user': serializer.data
            })
        else:
            return Response({
                'is_admin': False,
                'message': 'Недостаточно прав'
            }, status=status.HTTP_403_FORBIDDEN)
'''
'''
class AdminAuthViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @action(detail=False, methods=['get'])
    def check_admin(self, request):
        serializer = AdminUserSerializer(request.user)
        return Response({
            'is_admin': True,
            'user': serializer.data
        })
'''


class AdminAuthViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def check_admin(self, request):
        is_admin = request.user.is_staff or request.user.is_superuser

        if is_admin:
            serializer = AdminUserSerializer(request.user)
            return Response({
                'is_admin': True,
                'user': serializer.data
            })
        else:
            return Response({
                'is_admin': False,
                'message': 'Недостаточно прав'
            }, status=status.HTTP_403_FORBIDDEN)
'''
class AdminBaseViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
'''


class AdminBaseViewSet(viewsets.GenericViewSet):
    def get_permissions(self):
        permission_classes = [IsAuthenticated]

        if self.action != 'check_admin':
            permission_classes = [IsAuthenticated, IsAdminUser]

        return [permission() for permission in permission_classes]

class GamesAdminViewSet(viewsets.GenericViewSet):
    permission_classes = []
    authentication_classes = []
    serializer_class = GameAdminSerializer

    def get_queryset(self):
        return Games.objects.all().order_by('-date')

    @action(detail=False, methods=['get'])
    def options(self, request):
        home_teams = Games.objects.values_list('home_club_name', flat=True).distinct().order_by('home_club_name')
        away_teams = Games.objects.values_list('away_club_name', flat=True).distinct().order_by('away_club_name')
        dates = Games.objects.dates('date', 'day', order='DESC')[:100]

        return Response({
            'home_teams': list(home_teams),
            'away_teams': list(away_teams),
            'dates': [date.strftime('%Y-%m-%d') for date in dates]
        })

    @action(detail=False, methods=['get'])
    def search(self, request):
        home_team = request.GET.get('home_team')
        away_team = request.GET.get('away_team')
        date = request.GET.get('date')

        if not all([home_team, away_team, date]):
            return Response({'detail': 'Все параметры обязательны'}, status=400)

        try:
            game = Games.objects.get(
                home_club_name=home_team,
                away_club_name=away_team,
                date=date
            )
            serializer = self.get_serializer(game)
            return Response(serializer.data)
        except Games.DoesNotExist:
            return Response({'detail': 'Матч не найден'}, status=404)
        except Games.MultipleObjectsReturned:
            game = Games.objects.filter(
                home_club_name=home_team,
                away_club_name=away_team,
                date=date
            ).first()
            serializer = self.get_serializer(game)
            return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_game(self, request):
        serializer = GameCreateSerializer(data=request.data)
        if serializer.is_valid():
            last_game = Games.objects.order_by('-game_id').first()
            new_game_id = (last_game.game_id + 1) if last_game else 1

            game = serializer.save(game_id=new_game_id)
            return Response({
                'message': 'Матч успешно создан',
                'game': GameAdminSerializer(game).data
            }, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['put'])
    def update_game(self, request):
        game_id = request.data.get('game_id')
        if not game_id:
            return Response({'detail': 'ID матча обязателен'}, status=400)

        try:
            game = Games.objects.get(game_id=game_id)
            serializer = GameUpdateSerializer(game, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Матч успешно обновлен',
                    'game': GameAdminSerializer(game).data
                })
            return Response(serializer.errors, status=400)
        except Games.DoesNotExist:
            return Response({'detail': 'Матч не найден'}, status=404)

    @action(detail=False, methods=['delete'])
    def delete_game(self, request):
        game_id = request.GET.get('game_id')
        if not game_id:
            return Response({'detail': 'ID матча обязателен'}, status=400)

        try:
            game = Games.objects.get(game_id=game_id)
            game.delete()
            return Response({'message': 'Матч успешно удален'})
        except Games.DoesNotExist:
            return Response({'detail': 'Матч не найден'}, status=404)


class PlayersAdminViewSet(viewsets.GenericViewSet):
    permission_classes = []
    authentication_classes = []
    serializer_class = PlayerAdminSerializer

    def get_queryset(self):
        return Players.objects.all().order_by('name')

    @action(detail=False, methods=['get'])
    def options(self, request):
        user = User.objects.get(username='admin')
        print(f"is_staff: {user.is_staff}")
        print(f"is_superuser: {user.is_superuser}")
        clubs = Clubs.objects.values_list('name', flat=True).distinct().order_by('name')
        players = Players.objects.values_list('name', flat=True).distinct().order_by('name')

        return Response({
            'clubs': list(clubs),
            'players': list(players)
        })

    @action(detail=False, methods=['get'])
    def players_by_club(self, request):
        club_name = request.GET.get('club_name')
        if not club_name:
            return Response({'detail': 'Название клуба обязательно'}, status=400)

        players = Players.objects.filter(current_club_name=club_name).order_by('name')
        serializer = SimplePlayerSerializer(players, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        player_name = request.GET.get('player_name')

        if not player_name:
            return Response({'detail': 'Имя игрока обязательно'}, status=400)

        try:
            player = Players.objects.get(name=player_name)
            serializer = self.get_serializer(player)
            return Response(serializer.data)
        except Players.DoesNotExist:
            return Response({'detail': 'Игрок не найден'}, status=404)
        except Players.MultipleObjectsReturned:
            player = Players.objects.filter(name=player_name).first()
            serializer = self.get_serializer(player)
            return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_player(self, request):
        serializer = PlayerCreateSerializer(data=request.data)
        if serializer.is_valid():
            last_player = Players.objects.order_by('-player_id').first()
            new_player_id = (last_player.player_id + 1) if last_player else 1

            first_name = serializer.validated_data.get('first_name', '')
            last_name = serializer.validated_data.get('last_name', '')
            full_name = f"{first_name} {last_name}".strip()

            player_data = serializer.validated_data.copy()
            player_data['player_id'] = new_player_id
            player_data['name'] = full_name

            player = Players.objects.create(**player_data)
            return Response({
                'message': 'Игрок успешно создан',
                'player': PlayerAdminSerializer(player).data
            }, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['put'])
    def update_player(self, request):
        player_id = request.data.get('player_id')
        if not player_id:
            return Response({'detail': 'ID игрока обязательно'}, status=400)

        try:
            player = Players.objects.get(player_id=player_id)

            if 'first_name' in request.data or 'last_name' in request.data:
                first_name = request.data.get('first_name', player.first_name)
                last_name = request.data.get('last_name', player.last_name)
                request.data['name'] = f"{first_name} {last_name}".strip()

            serializer = PlayerUpdateSerializer(player, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Игрок успешно обновлен',
                    'player': PlayerAdminSerializer(player).data
                })
            return Response(serializer.errors, status=400)
        except Players.DoesNotExist:
            return Response({'detail': 'Игрок не найден'}, status=404)

    @action(detail=False, methods=['delete'])
    def delete_player(self, request):
        player_id = request.GET.get('player_id')
        if not player_id:
            return Response({'detail': 'ID игрока обязательно'}, status=400)

        try:
            player = Players.objects.get(player_id=player_id)
            player.delete()
            return Response({'message': 'Игрок успешно удален'})
        except Players.DoesNotExist:
            return Response({'detail': 'Игрок не найден'}, status=404)



class ClubsAdminViewSet(viewsets.GenericViewSet):
    permission_classes = []
    authentication_classes = []
    serializer_class = ClubAdminSerializer

    def get_queryset(self):
        return Clubs.objects.all().order_by('name')

    @action(detail=False, methods=['get'])
    def options(self, request):
        clubs = Clubs.objects.values_list('name', flat=True).distinct().order_by('name')

        return Response({
            'clubs': list(clubs)
        })

    @action(detail=False, methods=['get'])
    def search(self, request):
        club_name = request.GET.get('club_name')

        if not club_name:
            return Response({'detail': 'Название клуба обязательно'}, status=400)

        try:
            club = Clubs.objects.get(name=club_name)
            serializer = self.get_serializer(club)
            return Response(serializer.data)
        except Clubs.DoesNotExist:
            return Response({'detail': 'Клуб не найден'}, status=404)

    @action(detail=False, methods=['post'])
    def create_club(self, request):
        serializer = ClubCreateSerializer(data=request.data)
        if serializer.is_valid():
            last_club = Clubs.objects.order_by('-club_id').first()
            new_club_id = (last_club.club_id + 1) if last_club else 1

            club_data = serializer.validated_data.copy()
            club_data['club_id'] = new_club_id

            club = Clubs.objects.create(**club_data)
            return Response({
                'message': 'Клуб успешно создан',
                'club': ClubAdminSerializer(club).data
            }, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['put'])
    def update_club(self, request):
        club_id = request.data.get('club_id')
        if not club_id:
            return Response({'detail': 'ID клуба обязательно'}, status=400)

        try:
            club = Clubs.objects.get(club_id=club_id)
            serializer = ClubUpdateSerializer(club, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Клуб успешно обновлен',
                    'club': ClubAdminSerializer(club).data
                })
            return Response(serializer.errors, status=400)
        except Clubs.DoesNotExist:
            return Response({'detail': 'Клуб не найден'}, status=404)

    @action(detail=False, methods=['delete'])
    def delete_club(self, request):
        club_id = request.GET.get('club_id')
        if not club_id:
            return Response({'detail': 'ID клуба обязательно'}, status=400)

        try:
            club = Clubs.objects.get(club_id=club_id)

            players_count = Players.objects.filter(current_club_id=club_id).count()
            if players_count > 0:
                return Response({
                    'detail': f'Невозможно удалить клуб. В клубе есть игроки ({players_count} игроков)'
                }, status=400)

            club.delete()
            return Response({'message': 'Клуб успешно удален'})
        except Clubs.DoesNotExist:
            return Response({'detail': 'Клуб не найден'}, status=404)

    @action(detail=False, methods=['get'])
    def club_players_count(self, request):
        club_id = request.GET.get('club_id')
        if not club_id:
            return Response({'detail': 'ID клуба обязательно'}, status=400)

        try:
            players_count = Players.objects.filter(current_club_id=club_id).count()
            return Response({'players_count': players_count})
        except Exception as e:
            return Response({'detail': 'Ошибка при получении данных'}, status=400)



class TransfersAdminViewSet(viewsets.GenericViewSet):
    permission_classes = []
    authentication_classes = []
    serializer_class = TransferAdminSerializer

    def get_queryset(self):
        return Transfers.objects.all().order_by('-transfer_date')

    @action(detail=False, methods=['get'])
    def options(self, request):
        from_clubs = Transfers.objects.values_list('from_club_name', flat=True).distinct().order_by('from_club_name')
        to_clubs = Transfers.objects.values_list('to_club_name', flat=True).distinct().order_by('to_club_name')
        players = Transfers.objects.values_list('player_name', flat=True).distinct().order_by('player_name')

        return Response({
            'from_clubs': list(from_clubs),
            'to_clubs': list(to_clubs),
            'players': list(players)
        })

    @action(detail=False, methods=['get'])
    def search_by_clubs(self, request):
        from_club = request.GET.get('from_club')
        to_club = request.GET.get('to_club')

        if not from_club and not to_club:
            return Response({'detail': 'Укажите хотя бы один клуб'}, status=400)

        queryset = Transfers.objects.all()

        if from_club:
            queryset = queryset.filter(from_club_name=from_club)
        if to_club:
            queryset = queryset.filter(to_club_name=to_club)

        if queryset.count() > 1:
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'multiple_results': True,
                'transfers': serializer.data
            })
        elif queryset.count() == 1:
            serializer = self.get_serializer(queryset.first())
            return Response({
                'multiple_results': False,
                'transfer': serializer.data
            })
        else:
            return Response({'detail': 'Трансферы не найдены'}, status=404)

    @action(detail=False, methods=['get'])
    def search_by_player(self, request):
        player_name = request.GET.get('player_name')

        if not player_name:
            return Response({'detail': 'Имя игрока обязательно'}, status=400)

        transfers = Transfers.objects.filter(player_name=player_name).order_by('-transfer_date')

        if transfers.exists():
            serializer = self.get_serializer(transfers.first())
            return Response(serializer.data)
        else:
            return Response({'detail': 'Трансферы игрока не найдены'}, status=404)

    @action(detail=False, methods=['post'])
    def create_transfer(self, request):
        serializer = TransferCreateSerializer(data=request.data)
        if serializer.is_valid():
            player_name = serializer.validated_data.get('player_name')
            from_club_name = serializer.validated_data.get('from_club_name')
            to_club_name = serializer.validated_data.get('to_club_name')

            try:
                player = Players.objects.filter(name=player_name).first()
                player_id = player.player_id if player else None

                from_club = Clubs.objects.filter(name=from_club_name).first()
                from_club_id = from_club.club_id if from_club else None

                to_club = Clubs.objects.filter(name=to_club_name).first()
                to_club_id = to_club.club_id if to_club else None

                transfer_data = serializer.validated_data.copy()
                transfer_data['player_id'] = player_id
                transfer_data['from_club_id'] = from_club_id
                transfer_data['to_club_id'] = to_club_id

                transfer = Transfers.objects.create(**transfer_data)
                return Response({
                    'message': 'Трансфер успешно создан',
                    'transfer': TransferAdminSerializer(transfer).data
                }, status=201)

            except Exception as e:
                return Response({'detail': f'Ошибка при создании трансфера: {str(e)}'}, status=400)

        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['put'])
    def update_transfer(self, request):
        transfer_id = request.data.get('id')
        if not transfer_id:
            return Response({'detail': 'ID трансфера обязательно'}, status=400)

        try:
            transfer = Transfers.objects.get(id=transfer_id)

            if 'player_name' in request.data:
                player_name = request.data.get('player_name')
                player = Players.objects.filter(name=player_name).first()
                if player:
                    request.data['player_id'] = player.player_id

            if 'from_club_name' in request.data:
                from_club_name = request.data.get('from_club_name')
                from_club = Clubs.objects.filter(name=from_club_name).first()
                if from_club:
                    request.data['from_club_id'] = from_club.club_id

            if 'to_club_name' in request.data:
                to_club_name = request.data.get('to_club_name')
                to_club = Clubs.objects.filter(name=to_club_name).first()
                if to_club:
                    request.data['to_club_id'] = to_club.club_id

            serializer = TransferUpdateSerializer(transfer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Трансфер успешно обновлен',
                    'transfer': TransferAdminSerializer(transfer).data
                })
            return Response(serializer.errors, status=400)
        except Transfers.DoesNotExist:
            return Response({'detail': 'Трансфер не найден'}, status=404)

    @action(detail=False, methods=['delete'])
    def delete_transfer(self, request):
        transfer_id = request.GET.get('id')
        if not transfer_id:
            return Response({'detail': 'ID трансфера обязательно'}, status=400)

        try:
            transfer = Transfers.objects.get(id=transfer_id)
            transfer.delete()
            return Response({'message': 'Трансфер успешно удален'})
        except Transfers.DoesNotExist:
            return Response({'detail': 'Трансфер не найден'}, status=404)

    @action(detail=False, methods=['get'])
    def transfer_details(self, request):
        transfer_id = request.GET.get('id')
        if not transfer_id:
            return Response({'detail': 'ID трансфера обязательно'}, status=400)

        try:
            transfer = Transfers.objects.get(id=transfer_id)
            serializer = self.get_serializer(transfer)
            return Response(serializer.data)
        except Transfers.DoesNotExist:
            return Response({'detail': 'Трансфер не найден'}, status=404)