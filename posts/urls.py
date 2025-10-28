from django.urls import path, include
from . import views

urlpatterns = [
    # 帖子列表和创建
    path('posts/', views.PostListView.as_view(), name='post-list'),
    path('posts/create/', views.PostCreateView.as_view(), name='post-create'),
    
    # 帖子详情、更新、删除
    path('posts/<int:post_id>/', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('posts/<int:post_id>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    
    # 帖子互动
    path('posts/<int:post_id>/like/', views.PostLikeView.as_view(), name='post-like'),
    path('posts/<int:post_id>/collect/', views.PostCollectView.as_view(), name='post-collect'),
    path('posts/<int:post_id>/report/', views.PostReportView.as_view(), name='post-report'),
    
    # 用户相关
    path('user/history/', views.UserPostHistoryView.as_view(), name='user-post-history'),
    
    # 推荐和热门
    path('hot/', views.hot_posts, name='hot-posts'),
    path('recommended/', views.recommended_posts, name='recommended-posts'),
]