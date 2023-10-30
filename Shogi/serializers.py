from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import CurrentUserDefault
from .models import Player, Game


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
        }
    
    def save(self):
        user = User(
            username = self.validated_data['username'],
            email = self.validated_data['email']
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Password must match.'})
        
        user.set_password(password)
        user.save()

        # Create a corresponding Player for this user
        Player.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'
        read_only_fields = ('our_player', 'opponent_player', 'winner', 'loser', 'status', 'game_record', 'binary_game', 'timestamp')


class GameJoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = []


class GameMovesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['game_record']
        read_only_fields = ('game_record',)