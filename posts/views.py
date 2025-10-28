from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Post, PostImage, PostAttachment, PostLike, PostCollect, PostReport, PostViewHistory
from .serializers import (
    PostCreateSerializer, PostListSerializer, PostDetailSerializer,
    PostUpdateSerializer, PostLikeSerializer, PostCollectSerializer,
    PostReportSerializer, PostReportCreateSerializer, PostViewHistorySerializer
)
from tieba.models import Tieba, TiebaMember
from users.models import UserActivity


class PostListView(APIView):
    """帖子列表视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """获取帖子列表"""
        posts = Post.objects.filter(status=1).select_related('author', 'tieba').prefetch_related('images')
        
        # 支持多种过滤条件
        tieba_id = request.GET.get('tieba')
        author_id = request.GET.get('author')
        search_query = request.GET.get('q', '')
        sort_by = request.GET.get('sort', 'latest')  # latest, hot, essence
        
        if tieba_id:
            posts = posts.filter(tieba_id=tieba_id)
        
        if author_id:
            posts = posts.filter(author_id=author_id)
        
        if search_query:
            posts = posts.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
        
        # 排序
        if sort_by == 'hot':
            posts = posts.order_by('-view_count', '-like_count', '-created_at')
        elif sort_by == 'essence':
            posts = posts.filter(is_essence=True).order_by('-created_at')
        else:  # latest
            posts = posts.order_by('-created_at')
        
        # 分页
        page = self.paginate_queryset(posts, request)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PostListSerializer(posts[:20], many=True, context={'request': request})
        return Response(serializer.data)
    
    def paginate_queryset(self, queryset, request):
        """简单的分页实现"""
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        return paginator.paginate_queryset(queryset, request)


class PostCreateView(APIView):
    """创建帖子视图"""
    
    @method_decorator(login_required)
    def post(self, request):
        """创建帖子"""
        serializer = PostCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # 检查用户是否加入了该贴吧
            tieba_id = serializer.validated_data.get('tieba').id
            if not TiebaMember.objects.filter(tieba_id=tieba_id, user=request.user).exists():
                return Response(
                    {'error': '请先加入该贴吧才能发帖'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            post = serializer.save(author=request.user)
            
            # 更新贴吧统计
            tieba = post.tieba
            tieba.post_count += 1
            tieba.today_post_count += 1
            tieba.save()
            
            # 记录活动
            UserActivity.objects.create(
                user=request.user,
                action='post_create',
                target_type='post',
                target_id=post.id
            )
            
            return Response({
                'message': '帖子创建成功',
                'post': PostDetailSerializer(post, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    """帖子详情视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, post_id):
        """获取帖子详情"""
        try:
            post = Post.objects.get(id=post_id, status=1)
            
            # 记录浏览历史（仅登录用户）
            if request.user.is_authenticated:
                PostViewHistory.objects.get_or_create(
                    user=request.user,
                    post=post,
                    defaults={'viewed_at': post.created_at}
                )
            
            # 更新浏览计数
            post.view_count += 1
            post.save()
            
            serializer = PostDetailSerializer(post, context={'request': request})
            return Response(serializer.data)
            
        except Post.DoesNotExist:
            return Response({'error': '帖子不存在'}, status=status.HTTP_404_NOT_FOUND)


class PostUpdateView(APIView):
    """更新帖子视图"""
    
    @method_decorator(login_required)
    def put(self, request, post_id):
        """更新帖子"""
        try:
            post = Post.objects.get(id=post_id, author=request.user)
            serializer = PostUpdateSerializer(post, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                
                # 记录活动
                UserActivity.objects.create(
                    user=request.user,
                    action='post_update',
                    target_type='post',
                    target_id=post.id
                )
                
                return Response({
                    'message': '帖子更新成功',
                    'post': PostDetailSerializer(post, context={'request': request}).data
                })
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Post.DoesNotExist:
            return Response({'error': '帖子不存在或无权操作'}, status=status.HTTP_404_NOT_FOUND)


class PostDeleteView(APIView):
    """删除帖子视图"""
    
    @method_decorator(login_required)
    def delete(self, request, post_id):
        """删除帖子"""
        try:
            post = Post.objects.get(id=post_id, author=request.user)
            post.status = 0  # 软删除
            post.save()
            
            # 更新贴吧统计
            tieba = post.tieba
            tieba.post_count -= 1
            tieba.save()
            
            # 记录活动
            UserActivity.objects.create(
                user=request.user,
                action='post_delete',
                target_type='post',
                target_id=post.id
            )
            
            return Response({'message': '帖子删除成功'})
            
        except Post.DoesNotExist:
            return Response({'error': '帖子不存在或无权操作'}, status=status.HTTP_404_NOT_FOUND)


class PostLikeView(APIView):
    """帖子点赞视图"""
    
    @method_decorator(login_required)
    def post(self, request, post_id):
        """点赞/取消点赞帖子"""
        try:
            post = Post.objects.get(id=post_id, status=1)
            like, created = PostLike.objects.get_or_create(post=post, user=request.user)
            
            if not created:
                # 取消点赞
                like.delete()
                post.like_count -= 1
                message = '取消点赞成功'
            else:
                # 点赞成功
                post.like_count += 1
                message = '点赞成功'
                
                # 记录活动
                UserActivity.objects.create(
                    user=request.user,
                    action='post_like',
                    target_type='post',
                    target_id=post.id
                )
            
            post.save()
            
            return Response({
                'message': message,
                'like_count': post.like_count,
                'is_liked': created
            })
            
        except Post.DoesNotExist:
            return Response({'error': '帖子不存在'}, status=status.HTTP_404_NOT_FOUND)


class PostCollectView(APIView):
    """帖子收藏视图"""
    
    @method_decorator(login_required)
    def post(self, request, post_id):
        """收藏/取消收藏帖子"""
        try:
            post = Post.objects.get(id=post_id, status=1)
            collect, created = PostCollect.objects.get_or_create(post=post, user=request.user)
            
            if not created:
                # 取消收藏
                collect.delete()
                post.collect_count -= 1
                message = '取消收藏成功'
            else:
                # 收藏成功
                post.collect_count += 1
                message = '收藏成功'
                
                # 记录活动
                UserActivity.objects.create(
                    user=request.user,
                    action='post_collect',
                    target_type='post',
                    target_id=post.id
                )
            
            post.save()
            
            return Response({
                'message': message,
                'collect_count': post.collect_count,
                'is_collected': created
            })
            
        except Post.DoesNotExist:
            return Response({'error': '帖子不存在'}, status=status.HTTP_404_NOT_FOUND)


class PostReportView(APIView):
    """帖子举报视图"""
    
    @method_decorator(login_required)
    def post(self, request, post_id):
        """举报帖子"""
        try:
            post = Post.objects.get(id=post_id, status=1)
            
            # 检查是否已举报
            if PostReport.objects.filter(post=post, reporter=request.user).exists():
                return Response({'error': '您已经举报过该帖子'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = PostReportCreateSerializer(data=request.data)
            if serializer.is_valid():
                report = serializer.save(post=post, reporter=request.user)
                
                return Response({
                    'message': '举报成功，我们会尽快处理',
                    'report': PostReportSerializer(report).data
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Post.DoesNotExist:
            return Response({'error': '帖子不存在'}, status=status.HTTP_404_NOT_FOUND)


class UserPostHistoryView(APIView):
    """用户帖子浏览历史视图"""
    
    @method_decorator(login_required)
    def get(self, request):
        """获取用户浏览历史"""
        history = PostViewHistory.objects.filter(user=request.user).order_by('-viewed_at')
        
        page = self.paginate_queryset(history, request)
        if page is not None:
            serializer = PostViewHistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PostViewHistorySerializer(history[:20], many=True)
        return Response(serializer.data)
    
    def paginate_queryset(self, queryset, request):
        """简单的分页实现"""
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        return paginator.paginate_queryset(queryset, request)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def hot_posts(request):
    """热门帖子"""
    posts = Post.objects.filter(status=1).order_by('-view_count', '-like_count')[:20]
    
    serializer = PostListSerializer(posts, many=True, context={'request': request})
    return Response({'hot_posts': serializer.data})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def recommended_posts(request):
    """推荐帖子"""
    posts = Post.objects.filter(status=1, is_essence=True).order_by('-created_at')[:10]
    
    serializer = PostListSerializer(posts, many=True, context={'request': request})
    return Response({'recommended_posts': serializer.data})