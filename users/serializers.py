from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile, FollowRelation


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password', 'password_confirm', 'nickname']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("两次密码不一致")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('用户名或密码错误')
            if not user.is_active:
                raise serializers.ValidationError('用户已被禁用')
        else:
            raise serializers.ValidationError('用户名和密码不能为空')
        
        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    
    class Meta:
        model = UserProfile
        fields = ['real_name', 'id_card', 'email_verified', 'phone_verified', 
                 'show_real_name', 'show_birthday', 'theme', 'language',
                 'email_notifications', 'push_notifications']


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'avatar', 'nickname', 
                 'gender', 'birthday', 'bio', 'post_count', 'comment_count',
                 'follower_count', 'following_count', 'profile', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'post_count', 'comment_count', 
                           'follower_count', 'following_count']


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器"""
    
    class Meta:
        model = User
        fields = ['avatar', 'nickname', 'gender', 'birthday', 'bio']


class PasswordChangeSerializer(serializers.Serializer):
    """密码修改序列化器"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("两次新密码不一致")
        return attrs


class FollowRelationSerializer(serializers.ModelSerializer):
    """关注关系序列化器"""
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)
    
    class Meta:
        model = FollowRelation
        fields = ['id', 'follower', 'following', 'created_at']


class UserActivitySerializer(serializers.ModelSerializer):
    """用户活动序列化器"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'nickname']