from rest_framework import serializers
from .models import Category, Tieba, TiebaMember, TiebaAnnouncement, TiebaApply
from users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'sort_order', 'is_active']


class TiebaSerializer(serializers.ModelSerializer):
    """贴吧序列化器"""
    owner = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    is_member = serializers.SerializerMethodField()
    member_role = serializers.SerializerMethodField()
    
    class Meta:
        model = Tieba
        fields = [
            'id', 'name', 'description', 'avatar', 'banner', 'owner', 'category',
            'member_count', 'post_count', 'today_post_count', 'total_view_count',
            'status', 'is_recommended', 'is_official', 'join_rule', 'post_rule',
            'created_at', 'updated_at', 'last_activity_at', 'is_member', 'member_role'
        ]
    
    def get_is_member(self, obj):
        """检查当前用户是否为该贴吧成员"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return TiebaMember.objects.filter(
                tieba=obj, user=request.user, is_active=True
            ).exists()
        return False
    
    def get_member_role(self, obj):
        """获取当前用户在贴吧中的角色"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            member = TiebaMember.objects.filter(
                tieba=obj, user=request.user, is_active=True
            ).first()
            return member.role if member else None
        return None


class TiebaCreateSerializer(serializers.ModelSerializer):
    """贴吧创建序列化器"""
    
    class Meta:
        model = Tieba
        fields = ['name', 'description', 'category', 'join_rule', 'post_rule']
    
    def validate_name(self, value):
        """验证贴吧名称"""
        if Tieba.objects.filter(name=value).exists():
            raise serializers.ValidationError('贴吧名称已存在')
        return value


class TiebaMemberSerializer(serializers.ModelSerializer):
    """贴吧成员序列化器"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TiebaMember
        fields = ['id', 'user', 'role', 'join_reason', 'is_active', 'post_count', 
                 'comment_count', 'joined_at', 'last_visit_at']


class TiebaAnnouncementSerializer(serializers.ModelSerializer):
    """贴吧公告序列化器"""
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = TiebaAnnouncement
        fields = ['id', 'title', 'content', 'author', 'is_pinned', 'is_important', 
                 'is_active', 'created_at', 'updated_at', 'expire_at']


class TiebaApplySerializer(serializers.ModelSerializer):
    """贴吧申请序列化器"""
    applicant = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    
    class Meta:
        model = TiebaApply
        fields = ['id', 'tieba', 'applicant', 'apply_reason', 'status', 
                 'reviewer', 'review_comment', 'applied_at', 'reviewed_at']


class TiebaApplyCreateSerializer(serializers.ModelSerializer):
    """贴吧申请创建序列化器"""
    
    class Meta:
        model = TiebaApply
        fields = ['apply_reason']