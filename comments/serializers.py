from rest_framework import serializers
from .models import Comment, CommentLike, CommentImage, CommentReport, Mention, CommentHistory
from users.serializers import UserSimpleSerializer
from posts.serializers import PostListSerializer


class CommentImageSerializer(serializers.ModelSerializer):
    """评论图片序列化器"""
    
    class Meta:
        model = CommentImage
        fields = ['id', 'image', 'description', 'created_at']


class CommentCreateSerializer(serializers.ModelSerializer):
    """创建评论序列化器"""
    
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )
    parent_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Comment
        fields = [
            'content', 'post', 'parent_id', 'is_anonymous', 'images'
        ]
    
    def create(self, validated_data):
        images = validated_data.pop('images', [])
        parent_id = validated_data.pop('parent_id', None)
        
        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id)
                validated_data['parent'] = parent_comment
            except Comment.DoesNotExist:
                pass
        
        comment = Comment.objects.create(**validated_data)
        
        # 处理图片
        for image in images:
            CommentImage.objects.create(comment=comment, image=image)
        
        return comment


class CommentListSerializer(serializers.ModelSerializer):
    """评论列表序列化器"""
    
    author = UserSimpleSerializer(read_only=True)
    parent = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    images = CommentImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'parent', 'created_at',
            'like_count', 'reply_count', 'is_liked', 'images', 'is_anonymous'
        ]
    
    def get_parent(self, obj):
        if obj.parent:
            return {
                'id': obj.parent.id,
                'content': obj.parent.content,
                'author': UserSimpleSerializer(obj.parent.author).data
            }
        return None
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CommentLike.objects.filter(comment=obj, user=request.user).exists()
        return False


class CommentDetailSerializer(serializers.ModelSerializer):
    """评论详情序列化器"""
    
    author = UserSimpleSerializer(read_only=True)
    post = PostListSerializer(read_only=True)
    parent = CommentListSerializer(read_only=True)
    images = CommentImageSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'post', 'parent', 'created_at', 'updated_at',
            'like_count', 'reply_count', 'is_liked', 'is_author', 'images',
            'is_anonymous', 'replies'
        ]
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CommentLike.objects.filter(comment=obj, user=request.user).exists()
        return False
    
    def get_is_author(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False
    
    def get_replies(self, obj):
        """获取回复列表"""
        replies = Comment.objects.filter(parent=obj, status=1).order_by('created_at')
        return CommentListSerializer(replies, many=True, context=self.context).data


class CommentUpdateSerializer(serializers.ModelSerializer):
    """更新评论序列化器"""
    
    class Meta:
        model = Comment
        fields = ['content', 'is_anonymous']


class CommentLikeSerializer(serializers.ModelSerializer):
    """评论点赞序列化器"""
    
    user = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = CommentLike
        fields = ['id', 'user', 'created_at']


class CommentReportSerializer(serializers.ModelSerializer):
    """评论举报序列化器"""
    
    reporter = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = CommentReport
        fields = ['id', 'reporter', 'reason', 'description', 'status', 'created_at']


class CommentReportCreateSerializer(serializers.ModelSerializer):
    """创建评论举报序列化器"""
    
    class Meta:
        model = CommentReport
        fields = ['comment', 'reason', 'description']


class MentionSerializer(serializers.ModelSerializer):
    """@提及序列化器"""
    
    from_user = UserSimpleSerializer(read_only=True)
    to_user = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = Mention
        fields = ['id', 'from_user', 'to_user', 'comment', 'created_at']


class CommentHistorySerializer(serializers.ModelSerializer):
    """评论历史序列化器"""
    
    class Meta:
        model = CommentHistory
        fields = ['id', 'content', 'created_at']