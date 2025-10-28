from rest_framework import serializers
from .models import Post, PostImage, PostAttachment, PostLike, PostCollect, PostReport, PostViewHistory
from users.serializers import UserSimpleSerializer
from tieba.serializers import TiebaSimpleSerializer


class PostImageSerializer(serializers.ModelSerializer):
    """帖子图片序列化器"""
    
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'description', 'created_at']


class PostAttachmentSerializer(serializers.ModelSerializer):
    """帖子附件序列化器"""
    
    class Meta:
        model = PostAttachment
        fields = ['id', 'file', 'filename', 'file_size', 'created_at']


class PostCreateSerializer(serializers.ModelSerializer):
    """创建帖子序列化器"""
    
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'tieba', 'is_anonymous', 'images', 'attachments'
        ]
    
    def create(self, validated_data):
        images = validated_data.pop('images', [])
        attachments = validated_data.pop('attachments', [])
        
        post = Post.objects.create(**validated_data)
        
        # 处理图片
        for image in images:
            PostImage.objects.create(post=post, image=image)
        
        # 处理附件
        for attachment in attachments:
            PostAttachment.objects.create(post=post, file=attachment)
        
        return post


class PostListSerializer(serializers.ModelSerializer):
    """帖子列表序列化器"""
    
    author = UserSimpleSerializer(read_only=True)
    tieba = TiebaSimpleSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_collected = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content_preview', 'author', 'tieba', 'created_at',
            'like_count', 'comment_count', 'view_count', 'is_essence', 'is_top',
            'is_liked', 'is_collected'
        ]
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(post=obj, user=request.user).exists()
        return False
    
    def get_is_collected(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostCollect.objects.filter(post=obj, user=request.user).exists()
        return False


class PostDetailSerializer(serializers.ModelSerializer):
    """帖子详情序列化器"""
    
    author = UserSimpleSerializer(read_only=True)
    tieba = TiebaSimpleSerializer(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    attachments = PostAttachmentSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_collected = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'tieba', 'created_at', 'updated_at',
            'like_count', 'comment_count', 'view_count', 'is_essence', 'is_top',
            'is_anonymous', 'images', 'attachments', 'is_liked', 'is_collected', 'is_author'
        ]
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(post=obj, user=request.user).exists()
        return False
    
    def get_is_collected(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostCollect.objects.filter(post=obj, user=request.user).exists()
        return False
    
    def get_is_author(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False


class PostUpdateSerializer(serializers.ModelSerializer):
    """更新帖子序列化器"""
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'is_anonymous']


class PostLikeSerializer(serializers.ModelSerializer):
    """帖子点赞序列化器"""
    
    user = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = PostLike
        fields = ['id', 'user', 'created_at']


class PostCollectSerializer(serializers.ModelSerializer):
    """帖子收藏序列化器"""
    
    user = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = PostCollect
        fields = ['id', 'user', 'created_at']


class PostReportSerializer(serializers.ModelSerializer):
    """帖子举报序列化器"""
    
    reporter = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = PostReport
        fields = ['id', 'reporter', 'reason', 'description', 'status', 'created_at']


class PostReportCreateSerializer(serializers.ModelSerializer):
    """创建帖子举报序列化器"""
    
    class Meta:
        model = PostReport
        fields = ['post', 'reason', 'description']


class PostViewHistorySerializer(serializers.ModelSerializer):
    """帖子浏览历史序列化器"""
    
    post = PostListSerializer(read_only=True)
    
    class Meta:
        model = PostViewHistory
        fields = ['id', 'post', 'viewed_at']