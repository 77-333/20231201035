from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Category, Tieba, TiebaMember, TiebaAnnouncement, TiebaApply
from .serializers import (
    CategorySerializer, TiebaSerializer, TiebaCreateSerializer,
    TiebaMemberSerializer, TiebaAnnouncementSerializer, 
    TiebaApplySerializer, TiebaApplyCreateSerializer
)
from users.models import UserActivity


class CategoryListView(APIView):
    """分类列表视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """获取分类列表"""
        categories = Category.objects.filter(is_active=True).order_by('sort_order')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class TiebaListView(APIView):
    """贴吧列表视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """获取贴吧列表"""
        tiebas = Tieba.objects.filter(status=1).order_by('-member_count', '-post_count')
        
        # 支持搜索和过滤
        search_query = request.GET.get('q', '')
        category_id = request.GET.get('category')
        
        if search_query:
            tiebas = tiebas.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
        
        if category_id:
            tiebas = tiebas.filter(category_id=category_id)
        
        # 分页
        page = self.paginate_queryset(tiebas, request)
        if page is not None:
            serializer = TiebaSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = TiebaSerializer(tiebas, many=True, context={'request': request})
        return Response(serializer.data)
    
    def paginate_queryset(self, queryset, request):
        """简单的分页实现"""
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        return paginator.paginate_queryset(queryset, request)


class TiebaCreateView(APIView):
    """创建贴吧视图"""
    
    @method_decorator(login_required)
    def post(self, request):
        """创建贴吧"""
        serializer = TiebaCreateSerializer(data=request.data)
        if serializer.is_valid():
            tieba = serializer.save(owner=request.user)
            
            # 创建者自动成为吧主
            TiebaMember.objects.create(
                tieba=tieba,
                user=request.user,
                role='owner'
            )
            
            # 记录活动
            UserActivity.objects.create(
                user=request.user,
                action='tieba_create',
                target_type='tieba',
                target_id=tieba.id
            )
            
            return Response({
                'message': '贴吧创建成功，等待审核',
                'tieba': TiebaSerializer(tieba, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TiebaDetailView(APIView):
    """贴吧详情视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, tieba_id):
        """获取贴吧详情"""
        try:
            tieba = Tieba.objects.get(id=tieba_id, status=1)
            serializer = TiebaSerializer(tieba, context={'request': request})
            return Response(serializer.data)
        except Tieba.DoesNotExist:
            return Response({'error': '贴吧不存在'}, status=status.HTTP_404_NOT_FOUND)


class JoinTiebaView(APIView):
    """加入贴吧视图"""
    
    @method_decorator(login_required)
    def post(self, request, tieba_id):
        """加入贴吧"""
        try:
            tieba = Tieba.objects.get(id=tieba_id, status=1)
            
            # 检查是否已加入
            if TiebaMember.objects.filter(tieba=tieba, user=request.user).exists():
                return Response({'error': '已加入该贴吧'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建成员关系
            member = TiebaMember.objects.create(
                tieba=tieba,
                user=request.user,
                role='member'
            )
            
            # 更新贴吧统计
            tieba.member_count += 1
            tieba.save()
            
            # 记录活动
            UserActivity.objects.create(
                user=request.user,
                action='join_tieba',
                target_type='tieba',
                target_id=tieba.id
            )
            
            return Response({
                'message': '加入贴吧成功',
                'member': TiebaMemberSerializer(member).data
            })
            
        except Tieba.DoesNotExist:
            return Response({'error': '贴吧不存在'}, status=status.HTTP_404_NOT_FOUND)


class LeaveTiebaView(APIView):
    """离开贴吧视图"""
    
    @method_decorator(login_required)
    def post(self, request, tieba_id):
        """离开贴吧"""
        try:
            tieba = Tieba.objects.get(id=tieba_id)
            
            # 检查是否为吧主（吧主不能离开）
            member = TiebaMember.objects.filter(tieba=tieba, user=request.user).first()
            if not member:
                return Response({'error': '未加入该贴吧'}, status=status.HTTP_400_BAD_REQUEST)
            
            if member.role == 'owner':
                return Response({'error': '吧主不能离开贴吧'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 删除成员关系
            member.delete()
            
            # 更新贴吧统计
            tieba.member_count -= 1
            tieba.save()
            
            # 记录活动
            UserActivity.objects.create(
                user=request.user,
                action='leave_tieba',
                target_type='tieba',
                target_id=tieba.id
            )
            
            return Response({'message': '已离开贴吧'})
            
        except Tieba.DoesNotExist:
            return Response({'error': '贴吧不存在'}, status=status.HTTP_404_NOT_FOUND)


class TiebaMembersView(APIView):
    """贴吧成员列表视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, tieba_id):
        """获取贴吧成员列表"""
        try:
            tieba = Tieba.objects.get(id=tieba_id)
            members = TiebaMember.objects.filter(tieba=tieba, is_active=True).select_related('user')
            
            # 按角色排序
            role_order = {'owner': 0, 'admin': 1, 'moderator': 2, 'member': 3}
            members = sorted(members, key=lambda x: role_order.get(x.role, 4))
            
            page = self.paginate_queryset(members, request)
            if page is not None:
                serializer = TiebaMemberSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = TiebaMemberSerializer(members, many=True)
            return Response(serializer.data)
            
        except Tieba.DoesNotExist:
            return Response({'error': '贴吧不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    def paginate_queryset(self, queryset, request):
        """简单的分页实现"""
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 50
        return paginator.paginate_queryset(queryset, request)


class TiebaAnnouncementsView(APIView):
    """贴吧公告列表视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, tieba_id):
        """获取贴吧公告列表"""
        try:
            tieba = Tieba.objects.get(id=tieba_id)
            announcements = TiebaAnnouncement.objects.filter(
                tieba=tieba, is_active=True
            ).order_by('-is_pinned', '-created_at')
            
            serializer = TiebaAnnouncementSerializer(announcements, many=True)
            return Response(serializer.data)
            
        except Tieba.DoesNotExist:
            return Response({'error': '贴吧不存在'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def recommended_tiebas(request):
    """推荐贴吧"""
    tiebas = Tieba.objects.filter(
        status=1, is_recommended=True
    ).order_by('-member_count')[:10]
    
    serializer = TiebaSerializer(tiebas, many=True, context={'request': request})
    return Response({'recommended_tiebas': serializer.data})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def hot_tiebas(request):
    """热门贴吧"""
    tiebas = Tieba.objects.filter(status=1).order_by('-today_post_count', '-member_count')[:20]
    
    serializer = TiebaSerializer(tiebas, many=True, context={'request': request})
    return Response({'hot_tiebas': serializer.data})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_tiebas(request):
    """搜索贴吧"""
    query = request.GET.get('q', '').strip()
    if not query:
        return Response({'error': '搜索关键词不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    
    tiebas = Tieba.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        status=1
    ).order_by('-member_count', '-post_count')
    
    serializer = TiebaSerializer(tiebas[:20], many=True, context={'request': request})
    return Response({'results': serializer.data})