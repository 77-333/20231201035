from django.urls import path, include
from . import views

urlpatterns = [
    # 评论列表和创建
    path('posts/<int:post_id>/comments/', views.CommentListView.as_view(), name='comment-list'),
    path('comments/create/', views.CommentCreateView.as_view(), name='comment-create'),
    
    # 评论详情、更新、删除
    path('comments/<int:comment_id>/', views.CommentDetailView.as_view(), name='comment-detail'),
    path('comments/<int:comment_id>/update/', views.CommentUpdateView.as_view(), name='comment-update'),
    path('comments/<int:comment_id>/delete/', views.CommentDeleteView.as_view(), name='comment-delete'),
    
    # 评论互动
    path('comments/<int:comment_id>/like/', views.CommentLikeView.as_view(), name='comment-like'),
    path('comments/<int:comment_id>/report/', views.CommentReportView.as_view(), name='comment-report'),
    path('comments/<int:comment_id>/likes/', views.comment_likes, name='comment-likes'),
    
    # 回复相关
    path('comments/<int:comment_id>/replies/', views.CommentRepliesView.as_view(), name='comment-replies'),
    
    # 用户相关
    path('user/comments/', views.UserCommentsView.as_view(), name='user-comments'),
    
    # 搜索
    path('comments/search/', views.search_comments, name='search-comments'),
]