from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    """贴吧分类"""
    
    name = models.CharField('分类名称', max_length=50, unique=True)
    description = models.TextField('分类描述', max_length=500, null=True, blank=True)
    icon = models.CharField('图标', max_length=100, null=True, blank=True)
    sort_order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    
    class Meta:
        db_table = 'category'
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return self.name


class Tieba(models.Model):
    """贴吧模型"""
    
    STATUS_CHOICES = [
        (0, '待审核'),
        (1, '正常'),
        (2, '封禁'),
        (3, '隐藏'),
    ]
    
    name = models.CharField('贴吧名称', max_length=100, unique=True)
    description = models.TextField('贴吧描述', max_length=1000)
    avatar = models.ImageField('贴吧头像', upload_to='tieba_avatars/', null=True, blank=True)
    banner = models.ImageField('贴吧横幅', upload_to='tieba_banners/', null=True, blank=True)
    
    # 关联信息
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_tiebas')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    # 统计信息
    member_count = models.IntegerField('成员数', default=0)
    post_count = models.IntegerField('帖子数', default=0)
    today_post_count = models.IntegerField('今日帖子数', default=0)
    total_view_count = models.BigIntegerField('总浏览量', default=0)
    
    # 管理信息
    status = models.IntegerField('状态', choices=STATUS_CHOICES, default=0)
    is_recommended = models.BooleanField('是否推荐', default=False)
    is_official = models.BooleanField('是否官方', default=False)
    
    # 规则设置
    join_rule = models.TextField('加入规则', max_length=500, null=True, blank=True)
    post_rule = models.TextField('发帖规则', max_length=500, null=True, blank=True)
    
    # 时间信息
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    last_activity_at = models.DateTimeField('最后活动时间', null=True, blank=True)
    
    class Meta:
        db_table = 'tieba'
        verbose_name = '贴吧'
        verbose_name_plural = '贴吧'
        indexes = [
            models.Index(fields=['status', 'is_recommended']),
            models.Index(fields=['member_count']),
            models.Index(fields=['post_count']),
            models.Index(fields=['last_activity_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def update_last_activity(self):
        """更新最后活动时间"""
        self.last_activity_at = timezone.now()
        self.save(update_fields=['last_activity_at'])


class TiebaMember(models.Model):
    """贴吧成员关系"""
    
    ROLE_CHOICES = [
        ('member', '普通成员'),
        ('moderator', '小吧主'),
        ('admin', '大吧主'),
        ('owner', '吧主'),
    ]
    
    tieba = models.ForeignKey(Tieba, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tieba_memberships')
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='member')
    
    # 成员信息
    join_reason = models.CharField('加入理由', max_length=200, null=True, blank=True)
    is_active = models.BooleanField('是否活跃', default=True)
    
    # 统计信息
    post_count = models.IntegerField('发帖数', default=0)
    comment_count = models.IntegerField('评论数', default=0)
    
    # 时间信息
    joined_at = models.DateTimeField('加入时间', default=timezone.now)
    last_visit_at = models.DateTimeField('最后访问时间', null=True, blank=True)
    
    class Meta:
        db_table = 'tieba_member'
        verbose_name = '贴吧成员'
        verbose_name_plural = '贴吧成员'
        unique_together = ('tieba', 'user')
        indexes = [
            models.Index(fields=['tieba', 'role']),
            models.Index(fields=['user', 'joined_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.tieba.name}"


class TiebaAnnouncement(models.Model):
    """贴吧公告"""
    
    tieba = models.ForeignKey(Tieba, on_delete=models.CASCADE, related_name='announcements')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tieba_announcements')
    
    title = models.CharField('公告标题', max_length=200)
    content = models.TextField('公告内容')
    
    # 显示设置
    is_pinned = models.BooleanField('是否置顶', default=False)
    is_important = models.BooleanField('是否重要', default=False)
    is_active = models.BooleanField('是否有效', default=True)
    
    # 时间信息
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    expire_at = models.DateTimeField('过期时间', null=True, blank=True)
    
    class Meta:
        db_table = 'tieba_announcement'
        verbose_name = '贴吧公告'
        verbose_name_plural = '贴吧公告'
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return self.title


class TiebaApply(models.Model):
    """贴吧申请记录"""
    
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]
    
    tieba = models.ForeignKey(Tieba, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tieba_applications')
    
    apply_reason = models.TextField('申请理由', max_length=500)
    status = models.CharField('审核状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 审核信息
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    review_comment = models.TextField('审核意见', max_length=500, null=True, blank=True)
    
    # 时间信息
    applied_at = models.DateTimeField('申请时间', default=timezone.now)
    reviewed_at = models.DateTimeField('审核时间', null=True, blank=True)
    
    class Meta:
        db_table = 'tieba_apply'
        verbose_name = '贴吧申请'
        verbose_name_plural = '贴吧申请'
        unique_together = ('tieba', 'applicant')
    
    def __str__(self):
        return f"{self.applicant.username} - {self.tieba.name}"