from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q

from .models import User, UserProfile, FollowRelation, UserActivity
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, FollowRelationSerializer,
    UserProfileSerializer
)


class UserRegistrationView(APIView):
    """用户注册视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # 创建用户资料
            UserProfile.objects.create(user=user)
            
            # 记录用户活动
            UserActivity.objects.create(
                user=user,
                action='register',
                ip_address=self.get_client_ip(request)
            )
            
            return Response({
                'message': '注册成功',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserLoginView(APIView):
    """用户登录视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            
            # 记录登录活动
            UserActivity.objects.create(
                user=user,
                action='login',
                ip_address=self.get_client_ip(request)
            )
            
            return Response({
                'message': '登录成功',
                'user': UserSerializer(user).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserLogoutView(APIView):
    """用户登出视图"""
    
    @method_decorator(login_required)
    def post(self, request):
        # 记录登出活动
        UserActivity.objects.create(
            user=request.user,
            action='logout',
            ip_address=self.get_client_ip(request)
        )
        
        logout(request)
        return Response({'message': '登出成功'})
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileView(APIView):
    """用户个人资料视图"""
    
    @method_decorator(login_required)
    def get(self, request):
        """获取当前用户信息"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @method_decorator(login_required)
    def put(self, request):
        """更新用户信息"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': '更新成功',
                'user': UserSerializer(request.user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """用户详情视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, user_id):
        """获取指定用户信息"""
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)


class PasswordChangeView(APIView):
    """密码修改视图"""
    
    @method_decorator(login_required)
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            # 验证旧密码
            if not request.user.check_password(old_password):
                return Response({'error': '旧密码错误'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 设置新密码
            request.user.set_password(new_password)
            request.user.save()
            
            return Response({'message': '密码修改成功'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowUserView(APIView):
    """关注用户视图"""
    
    @method_decorator(login_required)
    def post(self, request, user_id):
        """关注用户"""
        try:
            target_user = User.objects.get(id=user_id)
            
            # 不能关注自己
            if target_user == request.user:
                return Response({'error': '不能关注自己'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查是否已关注
            if FollowRelation.objects.filter(follower=request.user, following=target_user).exists():
                return Response({'error': '已关注该用户'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建关注关系
            follow_relation = FollowRelation.objects.create(
                follower=request.user,
                following=target_user
            )
            
            # 更新用户统计
            request.user.following_count += 1
            request.user.save()
            target_user.follower_count += 1
            target_user.save()
            
            # 记录活动
            UserActivity.objects.create(
                user=request.user,
                action='follow',
                target_type='user',
                target_id=target_user.id
            )
            
            return Response({
                'message': '关注成功',
                'follow_relation': FollowRelationSerializer(follow_relation).data
            })
            
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)


class UnfollowUserView(APIView):
    """取消关注用户视图"""
    
    @method_decorator(login_required)
    def post(self, request, user_id):
        """取消关注用户"""
        try:
            target_user = User.objects.get(id=user_id)
            
            # 检查是否已关注
            follow_relation = FollowRelation.objects.filter(
                follower=request.user, 
                following=target_user
            ).first()
            
            if not follow_relation:
                return Response({'error': '未关注该用户'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 删除关注关系
            follow_relation.delete()
            
            # 更新用户统计
            request.user.following_count -= 1
            request.user.save()
            target_user.follower_count -= 1
            target_user.save()
            
            # 记录活动
            UserActivity.objects.create(
                user=request.user,
                action='unfollow',
                target_type='user',
                target_id=target_user.id
            )
            
            return Response({'message': '取消关注成功'})
            
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)


class UserFollowersView(APIView):
    """用户粉丝列表视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, user_id):
        """获取用户的粉丝列表"""
        try:
            user = User.objects.get(id=user_id)
            followers = FollowRelation.objects.filter(following=user).select_related('follower')
            
            page = self.paginate_queryset(followers, request)
            if page is not None:
                serializer = FollowRelationSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = FollowRelationSerializer(followers, many=True)
            return Response(serializer.data)
            
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    def paginate_queryset(self, queryset, request):
        """简单的分页实现"""
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        return paginator.paginate_queryset(queryset, request)


class UserFollowingView(APIView):
    """用户关注列表视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, user_id):
        """获取用户的关注列表"""
        try:
            user = User.objects.get(id=user_id)
            following = FollowRelation.objects.filter(follower=user).select_related('following')
            
            page = self.paginate_queryset(following, request)
            if page is not None:
                serializer = FollowRelationSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = FollowRelationSerializer(following, many=True)
            return Response(serializer.data)
            
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    def paginate_queryset(self, queryset, request):
        """简单的分页实现"""
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        return paginator.paginate_queryset(queryset, request)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_users(request):
    """搜索用户"""
    query = request.GET.get('q', '').strip()
    if not query:
        return Response({'error': '搜索关键词不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(nickname__icontains=query) | 
        Q(email__icontains=query)
    ).filter(status=1)
    
    serializer = UserSerializer(users[:20], many=True)  # 限制返回20条结果
    return Response({'results': serializer.data})