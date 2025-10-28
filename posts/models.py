from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from tieba.models import Tieba

User = get_user_model()


class Post(models.Model):
    """帖子模型"""
    
    STATUS_CHOICES = [
        (0, '草稿'),
        (1, '已发布'),
        (2, '待审核'),
        (3, '已删除'),
        (4, '封禁'),
    ]
    
    TYPE_CHOICES = [
        ('normal', '普通帖'),
        ('vote', '投票帖'),
        ('image', '图片帖'),
        ('video', '视频帖'),
        ('link', '链接帖'),
    ]
    
    title = models.CharField('帖子标题', max_length=255)
    content = models.TextField('帖子内容')
    
    # 关联信息
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    tieba = models.ForeignKey(Tieba, on_delete=models.CASCADE, related_name='posts')
    
    # 帖子类型和状态
    post_type = models.CharField('帖子类型', max_length=20, choices=TYPE_CHOICES, default='normal')
    status = models.IntegerField('状态', choices=STATUS_CHOICES, default=0)
    
    # 统计信息
    view_count = models.IntegerField('浏览量', default=0)
    reply_count = models.IntegerField('回复数', default=0)
    like_count = models.IntegerField('点赞数', default=0)
    collect_count = models.IntegerField('收藏数', default=0)
    share_count = models.IntegerField('分享数', default=0)
    
    # 管理信息
    is_top = models.BooleanField('是否置顶', default=False)
    is_essence = models.BooleanField('是否精华', default=False)
    is_hot = models.BooleanField('是否热门', default=False)
    
    # 审核信息
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_posts')
    review_comment = models.TextField('审核意见', max_length=500, null=True, blank=True)
    reviewed_at = models.DateTimeField('审核时间', null=True, blank=True)
    
    # 时间信息
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    published_at = models.DateTimeField('发布时间', null=True, blank=True)
    last_reply_at = models.DateTimeField('最后回复时间', null=True, blank=True)
    
    class Meta:
        db_table = 'post'
        verbose_name = '帖子'
        verbose_name_plural = '帖子'
        indexes = [
            models.Index(fields=['tieba', 'status', 'created_at']),
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['is_top', 'created_at']),
            models.Index(fields=['is_essence', 'created_at']),
            models.Index(fields=['view_count']),
            models.Index(fields=['reply_count']),
            models.Index(fields=['last_reply_at']),
        ]
        ordering = ['-is_top', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """保存时自动设置发布时间"""
        if self.status == 1 and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def update_last_reply(self):
        """更新最后回复时间"""
        self.last_reply_at = timezone.now()
        self.save(update_fields=['last_reply_at'])


class PostImage(models.Model):
    """帖子图片"""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField('图片', upload_to='post_images/')
    caption = models.CharField('图片说明', max_length=200, null=True, blank=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    
    class Meta:
        db_table = 'post_image'
        verbose_name = '帖子图片'
        verbose_name_plural = '帖子图片'
        ordering = ['sort_order', 'created_at']


class PostAttachment(models.Model):
    """帖子附件"""
    
    TYPE_CHOICES = [
        ('file', '文件'),
        ('video', '视频'),
        ('audio', '音频'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField('附件', upload_to='post_attachments/')
    file_type = models.CharField('文件类型', max_length=20, choices=TYPE_CHOICES)
    file_name = models.CharField('文件名', max_length=255)
    file_size = models.BigIntegerField('文件大小')
    download_count = models.IntegerField('下载次数', default=0)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    
    class Meta:
        db_table = 'post_attachment'
        verbose_name = '帖子附件'
        verbose_name_plural = '帖子附件'


class PostLike(models.Model):
    """帖子点赞"""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    created_at = models.DateTimeField('点赞时间', default=timezone.now)
    
    class Meta:
        db_table = 'post_like'
        verbose_name = '帖子点赞'
        verbose_name_plural = '帖子点赞'
        unique_together = ('post', 'user')


class PostCollect(models.Model):
    """帖子收藏"""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='collects')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_collects')
    created_at = models.DateTimeField('收藏时间', default=timezone.now)
    
    class Meta:
        db_table = 'post_collect'
        verbose_name = '帖子收藏'
        verbose_name_plural = '帖子收藏'
        unique_together = ('post', 'user')


class PostReport(models.Model):
    """帖子举报"""
    
    REASON_CHOICES = [
        ('spam', '垃圾广告'),
        ('porn', '色情内容'),
        ('violence', '暴力内容'),
        ('illegal', '违法内容'),
        ('harassment', '骚扰内容'),
        ('misinformation', '虚假信息'),
        ('other', '其他原因'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('resolved', '已处理'),
        ('dismissed', '已驳回'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_reports')
    
    reason = models.CharField('举报原因', max_length=20, choices=REASON_CHOICES)
    description = models.TextField('举报描述', max_length=500, null=True, blank=True)
    status = models.CharField('处理状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 处理信息
    processor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_reports')
    process_comment = models.TextField('处理意见', max_length=500, null=True, blank=True)
    
    created_at = models.DateTimeField('举报时间', default=timezone.now)
    processed_at = models.DateTimeField('处理时间', null=True, blank=True)
    
    class Meta:
        db_table = 'post_report'
        verbose_name = '帖子举报'
        verbose_name_plural = '帖子举报'


class PostViewHistory(models.Model):
    """帖子浏览历史"""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='view_history')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_view_history')
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('用户代理', null=True, blank=True)
    viewed_at = models.DateTimeField('浏览时间', default=timezone.now)
    
    class Meta:
        db_table = 'post_view_history'
        verbose_name = '帖子浏览历史'
        verbose_name_plural = '帖子浏览历史'
        indexes = [
            models.Index(fields=['user', 'viewed_at']),
            models.Index(fields=['post', 'viewed_at']),
        ]