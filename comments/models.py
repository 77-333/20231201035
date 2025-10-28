from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from posts.models import Post

User = get_user_model()


class Comment(models.Model):
    """评论模型"""
    
    STATUS_CHOICES = [
        (0, '正常'),
        (1, '待审核'),
        (2, '已删除'),
        (3, '封禁'),
    ]
    
    content = models.TextField('评论内容')
    
    # 关联信息
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # 楼层信息
    floor_number = models.IntegerField('楼层号', default=1)
    
    # 状态信息
    status = models.IntegerField('状态', choices=STATUS_CHOICES, default=0)
    
    # 统计信息
    like_count = models.IntegerField('点赞数', default=0)
    reply_count = models.IntegerField('回复数', default=0)
    
    # 审核信息
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_comments')
    review_comment = models.TextField('审核意见', max_length=500, null=True, blank=True)
    reviewed_at = models.DateTimeField('审核时间', null=True, blank=True)
    
    # 时间信息
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'comment'
        verbose_name = '评论'
        verbose_name_plural = '评论'
        indexes = [
            models.Index(fields=['post', 'floor_number']),
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['parent']),
        ]
        ordering = ['floor_number']
    
    def __str__(self):
        return f"{self.author.username} - {self.content[:50]}"
    
    def save(self, *args, **kwargs):
        """保存时自动设置楼层号"""
        if not self.floor_number:
            # 获取帖子的最大楼层号
            max_floor = Comment.objects.filter(post=self.post).aggregate(
                models.Max('floor_number')
            )['floor_number__max'] or 0
            self.floor_number = max_floor + 1
        super().save(*args, **kwargs)


class CommentLike(models.Model):
    """评论点赞"""
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    created_at = models.DateTimeField('点赞时间', default=timezone.now)
    
    class Meta:
        db_table = 'comment_like'
        verbose_name = '评论点赞'
        verbose_name_plural = '评论点赞'
        unique_together = ('comment', 'user')


class CommentImage(models.Model):
    """评论图片"""
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField('图片', upload_to='comment_images/')
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    
    class Meta:
        db_table = 'comment_image'
        verbose_name = '评论图片'
        verbose_name_plural = '评论图片'
        ordering = ['sort_order', 'created_at']


class CommentReport(models.Model):
    """评论举报"""
    
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
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_reports')
    
    reason = models.CharField('举报原因', max_length=20, choices=REASON_CHOICES)
    description = models.TextField('举报描述', max_length=500, null=True, blank=True)
    status = models.CharField('处理状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 处理信息
    processor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_comment_reports')
    process_comment = models.TextField('处理意见', max_length=500, null=True, blank=True)
    
    created_at = models.DateTimeField('举报时间', default=timezone.now)
    processed_at = models.DateTimeField('处理时间', null=True, blank=True)
    
    class Meta:
        db_table = 'comment_report'
        verbose_name = '评论举报'
        verbose_name_plural = '评论举报'


class Mention(models.Model):
    """@提及关系"""
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='mentions')
    mentioned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentions')
    created_at = models.DateTimeField('提及时间', default=timezone.now)
    
    class Meta:
        db_table = 'mention'
        verbose_name = '提及关系'
        verbose_name_plural = '提及关系'
        unique_together = ('comment', 'mentioned_user')


class CommentHistory(models.Model):
    """评论编辑历史"""
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='history')
    content = models.TextField('历史内容')
    editor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='edited_comments')
    edited_at = models.DateTimeField('编辑时间', default=timezone.now)
    
    class Meta:
        db_table = 'comment_history'
        verbose_name = '评论历史'
        verbose_name_plural = '评论历史'
        ordering = ['-edited_at']