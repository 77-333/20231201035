from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """自定义用户模型"""
    
    GENDER_CHOICES = [
        (0, '未知'),
        (1, '男'),
        (2, '女'),
    ]
    
    STATUS_CHOICES = [
        (0, '禁用'),
        (1, '正常'),
        (2, '未激活'),
    ]
    
    # 扩展字段
    phone = models.CharField('手机号', max_length=20, unique=True, null=True, blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    nickname = models.CharField('昵称', max_length=50, null=True, blank=True)
    gender = models.IntegerField('性别', choices=GENDER_CHOICES, default=0)
    birthday = models.DateField('生日', null=True, blank=True)
    bio = models.TextField('个人简介', max_length=500, null=True, blank=True)
    status = models.IntegerField('状态', choices=STATUS_CHOICES, default=1)
    last_login_ip = models.GenericIPAddressField('最后登录IP', null=True, blank=True)
    
    # 统计字段
    post_count = models.IntegerField('发帖数', default=0)
    comment_count = models.IntegerField('评论数', default=0)
    follower_count = models.IntegerField('粉丝数', default=0)
    following_count = models.IntegerField('关注数', default=0)
    
    # 时间字段
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户'
    
    def __str__(self):
        return self.username
    
    @property
    def display_name(self):
        """显示名称，优先使用昵称"""
        return self.nickname or self.username


class UserProfile(models.Model):
    """用户详细资料"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # 个人信息
    real_name = models.CharField('真实姓名', max_length=50, null=True, blank=True)
    id_card = models.CharField('身份证号', max_length=18, null=True, blank=True)
    
    # 联系信息
    email_verified = models.BooleanField('邮箱已验证', default=False)
    phone_verified = models.BooleanField('手机已验证', default=False)
    
    # 隐私设置
    show_real_name = models.BooleanField('显示真实姓名', default=False)
    show_birthday = models.BooleanField('显示生日', default=False)
    
    # 偏好设置
    theme = models.CharField('主题', max_length=20, default='light')
    language = models.CharField('语言', max_length=10, default='zh')
    
    # 通知设置
    email_notifications = models.BooleanField('邮件通知', default=True)
    push_notifications = models.BooleanField('推送通知', default=True)
    
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'user_profile'
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'


class FollowRelation(models.Model):
    """用户关注关系"""
    
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_relations')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_relations')
    created_at = models.DateTimeField('关注时间', default=timezone.now)
    
    class Meta:
        db_table = 'follow_relation'
        unique_together = ('follower', 'following')
        verbose_name = '关注关系'
        verbose_name_plural = '关注关系'


class UserActivity(models.Model):
    """用户活动记录"""
    
    ACTION_CHOICES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('post_create', '发帖'),
        ('post_like', '点赞帖子'),
        ('comment_create', '评论'),
        ('follow', '关注'),
        ('unfollow', '取消关注'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField('操作类型', max_length=20, choices=ACTION_CHOICES)
    target_type = models.CharField('目标类型', max_length=50, null=True, blank=True)
    target_id = models.BigIntegerField('目标ID', null=True, blank=True)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('用户代理', null=True, blank=True)
    created_at = models.DateTimeField('操作时间', default=timezone.now)
    
    class Meta:
        db_table = 'user_activity'
        verbose_name = '用户活动'
        verbose_name_plural = '用户活动'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]