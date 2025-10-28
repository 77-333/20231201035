from django.urls import path, include
from . import views

urlpatterns = [
    # 分类相关
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    
    # 贴吧相关
    path('tiebas/', views.TiebaListView.as_view(), name='tieba-list'),
    path('tiebas/create/', views.TiebaCreateView.as_view(), name='tieba-create'),
    path('tiebas/<int:tieba_id>/', views.TiebaDetailView.as_view(), name='tieba-detail'),
    path('tiebas/<int:tieba_id>/join/', views.JoinTiebaView.as_view(), name='join-tieba'),
    path('tiebas/<int:tieba_id>/leave/', views.LeaveTiebaView.as_view(), name='leave-tieba'),
    path('tiebas/<int:tieba_id>/members/', views.TiebaMembersView.as_view(), name='tieba-members'),
    path('tiebas/<int:tieba_id>/announcements/', views.TiebaAnnouncementsView.as_view(), name='tieba-announcements'),
    
    # 推荐和搜索
    path('recommended/', views.recommended_tiebas, name='recommended-tiebas'),
    path('hot/', views.hot_tiebas, name='hot-tiebas'),
    path('search/', views.search_tiebas, name='search-tiebas'),
]