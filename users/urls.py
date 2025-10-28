from django.urls import path
from . import views

urlpatterns = [
    # 认证相关
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.UserLogoutView.as_view(), name='user-logout'),
    
    # 用户资料
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/change-password/', views.PasswordChangeView.as_view(), name='change-password'),
    
    # 用户详情
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # 关注相关
    path('users/<int:user_id>/follow/', views.FollowUserView.as_view(), name='follow-user'),
    path('users/<int:user_id>/unfollow/', views.UnfollowUserView.as_view(), name='unfollow-user'),
    path('users/<int:user_id>/followers/', views.UserFollowersView.as_view(), name='user-followers'),
    path('users/<int:user_id>/following/', views.UserFollowingView.as_view(), name='user-following'),
    
    # 搜索
    path('search/', views.search_users, name='search-users'),
]