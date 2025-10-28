from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Comment, CommentLike, CommentImage, CommentReport, Mention, CommentHistory
from .serializers import (
    CommentCreateSerializer, CommentListSerializer, CommentDetailSerializer,
    CommentUpdateSerializer, CommentLikeSerializer, CommentReportSerializer,
    CommentReportCreateSerializer, MentionSerializer, CommentHistorySerializer
)
from posts.models import Post
from users.models import UserActivity


class CommentListView(APIView):
    """评论列表视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, post_id):
        """获取帖子评论列表"""
        try:
            post = Post.objects.get(id=post_id, status=1)
            
            # 获取顶级评论（没有父评论的评论）
            comments = Comment.objects.filter(
                post=post, parent__isnull=True, status=1
            ).select_related('author').prefetch_related('images').order_by('-is_top', 'created_at')
            
            # 分页
            page = self.paginate_queryset(comments, request)
            if page is not None:
                serializer = CommentListSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
            
            serializer = CommentListSerializer(comments[:20], many=True, context={'request': request})
            return Response(serializer.data)
            
        except Post.DoesNotExist:
            return Response({'error': '帖子不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    def paginate_queryset(self, queryset, request):
        """简单的分页实现"""
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        return paginator.paginate_queryset(queryset, request)


class CommentCreateView(APIView):
    """创建评论视图"""
    
    @method_decorator(login_required)
    def post(self, request):
        """创建评论"""
        serializer = CommentCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # 检查帖子是否存在
            post_id = serializer.validated_data.get('post').id
            try:
                post = Post.objects.get(id=post_id, status=1)
            except Post.DoesNotExist:
                return Response({'error': '帖子不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            comment = serializer.save(author=request.user)
            
            # 更新帖子评论计数
            post.comment_count += 1
            post.save()
            
            # 记录活动
            UserActivity.objects.create(
                user=request.user,
                action='comment_create',
                target_type='comment',
                target_id=comment.id
            )
            
            return Response({
                'message': '评论创建成功',
                'comment': CommentDetailSerializer(comment, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    """评论详情视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, comment_id):
        """获取评论详情"""
        try:
            comment = Comment.objects.get(id=comment_id, status=1)
            serializer = CommentDetailSerializer(comment, context={'request': request})
            return Response(serializer.data)
            
        except Comment.DoesNotExist:
            return Response({'error': '评论不存在'}, status=status.HTTP_404_NOT_FOUND)


class CommentUpdateView(APIView):
    """更新评论视图"""
    
    @method_decorator(login_required)
    def put(self, request, comment_id):
        """更新评论"""
        try:
            comment = Comment.objects.get(id=comment_id, author=request.user)
            
            # 保存历史版本
            CommentHistory.objects.create(
                comment=comment,
                content=comment.content
            )
            
            serializer = CommentUpdateSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                
                # 记录活动
                UserActivity.objects.create(
                    user=request.user,
                    action='comment_update',
                    target_type='comment',
                    target_id=comment.id
                )
                
                return Response({
                    'message': '评论更新成功',
                    'comment': CommentDetailSerializer(comment, context={'request': request}).data
                })
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Comment.DoesNotExist:
            return Response({'error': '评论不存在或无权操作'}, status=status.HTTP_404_NOT_FOUND)


class CommentDeleteView(APIView):
    """删除评论视图"""
    
    @method_decorator(login_required)
    def delete(self, request, comment_id):
        """删除评论"""
        try:
            comment = Comment.objects.get(id=comment_id, author=request.user)
            comment.status = 0  # 软删除
            comment.save()
            
            # 更新帖子评论计数
            post = comment.post
            post.comment_count -= 1
            post.save()
            
            # 记录活动
            UserActivity.objects.create(
                user=request.user,
                action='comment_delete',
                target_type='comment',
                target_id=comment.id
            )
            
            return Response({'message': '评论删除成功'})
            
        except Comment.DoesNotExist:
            return Response({'error': '评论不存在或无权操作'}, status=status.HTTP_404_NOT_FOUND)


class CommentLikeView(APIView):
    """评论点赞视图"""
    
    @method_decorator(login_required)
    def post(self, request, comment_id):
        """点赞/取消点赞评论"""
        try:
            comment = Comment.objects.get(id=comment_id, status=1)
            like, created = CommentLike.objects.get_or_create(comment=comment, user=request.user)
            
            if not created:
                # 取消点赞
                like.delete()
                comment.like_count -= 1
                message = '取消点赞成功'
            else:
                # 点赞成功
                comment.like_count += 1
                message = '点赞成功'
                
                # 记录活动
                UserActivity.objects.create(
                    user=request.user,
                    action='comment_like',
                    target_type='comment',
                    target_id=comment.id
                )
            
            comment.save()
            
            return Response({
                'message': message,
                'like_count': comment.like_count,
                'is_liked': created
            })
            
        except Comment.DoesNotExist:
            return Response({'error': '评论不存在'}, status=status.HTTP_404_NOT_FOUND)


class CommentReportView(APIView):
    """评论举报视图"""
    
    @method_decorator(login_required)
    def post(self, request, comment_id):
        """举报评论"""
        try:
            comment = Comment.objects.get(id=comment_id, status=1)
            
            # 检查是否已举报
            if CommentReport.objects.filter(comment=comment, reporter=request.user).exists():
                return Response({'error': '您已经举报过该评论'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = CommentReportCreateSerializer(data=request.data)
            if serializer.is_valid():
                report = serializer.save(comment=comment, reporter=request.user)
                
                return Response({
                    'message': '举报成功，我们会尽快处理',
                    'report': CommentReportSerializer(report).data
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Comment.DoesNotExist:
            return Response({'error': '评论不存在'}, status=status.HTTP_404_NOT_FOUND)


class CommentRepliesView(APIView):
    """评论回复列表视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, comment_id):
        """获取评论的回复列表"""
        try:
            comment = Comment.objects.get(id=comment_id, status=1)
            replies = Comment.objects.filter(parent=comment, status=1).order_by('created_at')
            
            page = self.paginate_queryset(replies, request)
            if page is not None:
                serializer = CommentListSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
            
            serializer = CommentListSerializer(replies, many=True, context={'request': request})
            return Response(serializer.data)
            
        except Comment.DoesNotExist:
            return Response({'error': '评论不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    def paginate_queryset(self, queryset, request):
        """简单的分页实现"""
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        return paginator.paginate_queryset(queryset, request)


class UserCommentsView(APIView):
    """用户评论列表视图"""
    
    @method_decorator(login_required)
    def get(self, request):
        """获取用户发表的评论"""
        comments = Comment.objects.filter(author=request.user, status=1).order_by('-created_at')
        
        page = self.paginate_queryset(comments, request)
        if page is not None:
            serializer = CommentListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = CommentListSerializer(comments[:20], many=True, context={'request': request})
        return Response(serializer.data)
    
    def paginate_queryset(self, queryset, request):
        """简单的分页实现"""
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        return paginator.paginate_queryset(queryset, request)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def comment_likes(request, comment_id):
    """获取评论的点赞用户列表"""
    try:
        comment = Comment.objects.get(id=comment_id, status=1)
        likes = CommentLike.objects.filter(comment=comment).select_related('user').order_by('-created_at')
        
        serializer = CommentLikeSerializer(likes, many=True)
        return Response({'likes': serializer.data})
        
    except Comment.DoesNotExist:
        return Response({'error': '评论不存在'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_comments(request):
    """搜索评论"""
    query = request.GET.get('q', '').strip()
    if not query:
        return Response({'error': '搜索关键词不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    
    comments = Comment.objects.filter(
        Q(content__icontains=query),
        status=1
    ).order_by('-created_at')
    
    serializer = CommentListSerializer(comments[:20], many=True, context={'request': request})
    return Response({'results': serializer.data})