<template>
  <div class="user-profile-page">
    <div class="container">
      <!-- 用户信息头部 -->
      <div class="profile-header">
        <div class="header-content">
          <div class="user-avatar">
            <img :src="user.avatar || '/default-avatar.png'" :alt="user.username" />
            <button v-if="isOwnProfile" class="edit-avatar-btn" @click="editAvatar">
              更换头像
            </button>
          </div>
          
          <div class="user-info">
            <div class="basic-info">
              <h1 class="username">{{ user.username }}</h1>
              <p class="bio" v-if="user.bio">{{ user.bio }}</p>
              <p class="join-time">加入时间：{{ formatTime(user.createdAt) }}</p>
            </div>
            
            <div class="user-stats">
              <div class="stat-item" @click="showFollowers = true">
                <span class="stat-number">{{ user.followerCount || 0 }}</span>
                <span class="stat-label">粉丝</span>
              </div>
              <div class="stat-item" @click="showFollowing = true">
                <span class="stat-number">{{ user.followingCount || 0 }}</span>
                <span class="stat-label">关注</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ user.postCount || 0 }}</span>
                <span class="stat-label">帖子</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ user.commentCount || 0 }}</span>
                <span class="stat-label">评论</span>
              </div>
            </div>
            
            <div class="user-actions">
              <button 
                v-if="!isOwnProfile && globalStore.isAuthenticated"
                class="btn" 
                :class="user.isFollowing ? 'btn-outline' : 'btn-primary'"
                @click="toggleFollow"
                :disabled="following"
              >
                {{ following ? '操作中...' : user.isFollowing ? '已关注' : '关注' }}
              </button>
              
              <button 
                v-if="isOwnProfile"
                class="btn btn-primary" 
                @click="editProfile"
              >
                编辑资料
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 内容标签页 -->
      <div class="profile-tabs">
        <div class="tabs-header">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            class="tab-btn" 
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            {{ tab.name }}
          </button>
        </div>
        
        <div class="tab-content">
          <!-- 帖子列表 -->
          <div v-if="activeTab === 'posts'" class="posts-tab">
            <div class="posts-list">
              <div 
                v-for="post in userPosts" 
                :key="post.id" 
                class="post-item"
                @click="viewPost(post.id)"
              >
                <div class="post-header">
                  <span class="tieba-name">{{ post.tiebaName }}</span>
                  <span class="post-time">{{ formatTime(post.createdAt) }}</span>
                </div>
                <h3 class="post-title">{{ post.title }}</h3>
                <p class="post-content">{{ post.content }}</p>
                <div class="post-stats">
                  <span class="stat">
                    <i class="icon-like">👍</i> {{ post.likeCount || 0 }}
                  </span>
                  <span class="stat">
                    <i class="icon-comment">💬</i> {{ post.commentCount || 0 }}
                  </span>
                  <span class="stat">
                    <i class="icon-view">👁️</i> {{ post.viewCount || 0 }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="pagination" v-if="postsTotalPages > 1">
              <button 
                :disabled="postsCurrentPage === 1" 
                @click="changePostsPage(postsCurrentPage - 1)"
                class="page-btn"
              >
                上一页
              </button>
              <span class="page-info">第 {{ postsCurrentPage }} 页 / 共 {{ postsTotalPages }} 页</span>
              <button 
                :disabled="postsCurrentPage === postsTotalPages" 
                @click="changePostsPage(postsCurrentPage + 1)"
                class="page-btn"
              >
                下一页
              </button>
            </div>
          </div>
          
          <!-- 评论列表 -->
          <div v-else-if="activeTab === 'comments'" class="comments-tab">
            <div class="comments-list">
              <div 
                v-for="comment in userComments" 
                :key="comment.id" 
                class="comment-item"
                @click="viewPost(comment.postId)"
              >
                <div class="comment-header">
                  <span class="post-title">{{ comment.postTitle }}</span>
                  <span class="comment-time">{{ formatTime(comment.createdAt) }}</span>
                </div>
                <p class="comment-content">{{ comment.content }}</p>
                <div class="comment-stats">
                  <span class="stat">
                    <i class="icon-like">👍</i> {{ comment.likeCount || 0 }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="pagination" v-if="commentsTotalPages > 1">
              <button 
                :disabled="commentsCurrentPage === 1" 
                @click="changeCommentsPage(commentsCurrentPage - 1)"
                class="page-btn"
              >
                上一页
              </button>
              <span class="page-info">第 {{ commentsCurrentPage }} 页 / 共 {{ commentsTotalPages }} 页</span>
              <button 
                :disabled="commentsCurrentPage === commentsTotalPages" 
                @click="changeCommentsPage(commentsCurrentPage + 1)"
                class="page-btn"
              >
                下一页
              </button>
            </div>
          </div>
          
          <!-- 收藏列表 -->
          <div v-else-if="activeTab === 'collections'" class="collections-tab">
            <div class="collections-list">
              <div 
                v-for="post in collectedPosts" 
                :key="post.id" 
                class="post-item"
                @click="viewPost(post.id)"
              >
                <div class="post-header">
                  <span class="tieba-name">{{ post.tiebaName }}</span>
                  <span class="post-time">{{ formatTime(post.createdAt) }}</span>
                </div>
                <h3 class="post-title">{{ post.title }}</h3>
                <p class="post-content">{{ post.content }}</p>
                <div class="post-stats">
                  <span class="stat">
                    <i class="icon-like">👍</i> {{ post.likeCount || 0 }}
                  </span>
                  <span class="stat">
                    <i class="icon-comment">💬</i> {{ post.commentCount || 0 }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="pagination" v-if="collectionsTotalPages > 1">
              <button 
                :disabled="collectionsCurrentPage === 1" 
                @click="changeCollectionsPage(collectionsCurrentPage - 1)"
                class="page-btn"
              >
                上一页
              </button>
              <span class="page-info">第 {{ collectionsCurrentPage }} 页 / 共 {{ collectionsTotalPages }} 页</span>
              <button 
                :disabled="collectionsCurrentPage === collectionsTotalPages" 
                @click="changeCollectionsPage(collectionsCurrentPage + 1)"
                class="page-btn"
              >
                下一页
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 关注/粉丝模态框 -->
      <div v-if="showFollowers || showFollowing" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>{{ showFollowers ? '粉丝列表' : '关注列表' }}</h3>
            <button class="close-btn" @click="closeModal">×</button>
          </div>
          <div class="modal-body">
            <div class="user-list">
              <div 
                v-for="userItem in modalUsers" 
                :key="userItem.id" 
                class="user-list-item"
              >
                <img :src="userItem.avatar || '/default-avatar.png'" :alt="userItem.username" />
                <div class="user-details">
                  <span class="username">{{ userItem.username }}</span>
                  <span class="bio" v-if="userItem.bio">{{ userItem.bio }}</span>
                </div>
                <button 
                  v-if="!isOwnProfile && globalStore.isAuthenticated"
                  class="btn btn-small"
                  :class="userItem.isFollowing ? 'btn-outline' : 'btn-primary'"
                  @click="toggleUserFollow(userItem)"
                >
                  {{ userItem.isFollowing ? '已关注' : '关注' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 编辑资料模态框 -->
      <div v-if="showEditProfile" class="modal-overlay" @click="showEditProfile = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>编辑资料</h3>
            <button class="close-btn" @click="showEditProfile = false">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveProfile">
              <div class="form-group">
                <label>用户名</label>
                <input v-model="editForm.username" type="text" required />
              </div>
              <div class="form-group">
                <label>个人简介</label>
                <textarea v-model="editForm.bio" rows="3" placeholder="介绍一下自己..."></textarea>
              </div>
              <div class="form-actions">
                <button type="button" @click="showEditProfile = false" class="btn btn-outline">
                  取消
                </button>
                <button type="submit" class="btn btn-primary" :disabled="savingProfile">
                  {{ savingProfile ? '保存中...' : '保存' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGlobalStore } from '@/stores/global'
import { userApi, postApi } from '@/api/auth'
import type { User, Post, Comment } from '@/types/user'

const route = useRoute()
const router = useRouter()
const globalStore = useGlobalStore()

const userId = route.params.id as string

// 用户信息
const user = ref<User>({
  id: '',
  username: '',
  avatar: '',
  bio: '',
  createdAt: '',
  followerCount: 0,
  followingCount: 0,
  postCount: 0,
  commentCount: 0,
  isFollowing: false
})

// 标签页
const tabs = [
  { id: 'posts', name: '帖子' },
  { id: 'comments', name: '评论' },
  { id: 'collections', name: '收藏' }
]
const activeTab = ref('posts')

// 帖子列表
const userPosts = ref<Post[]>([])
const postsCurrentPage = ref(1)
const postsPageSize = ref(10)
const postsTotalPages = ref(1)

// 评论列表
const userComments = ref<Comment[]>([])
const commentsCurrentPage = ref(1)
const commentsPageSize = ref(10)
const commentsTotalPages = ref(1)

// 收藏列表
const collectedPosts = ref<Post[]>([])
const collectionsCurrentPage = ref(1)
const collectionsPageSize = ref(10)
const collectionsTotalPages = ref(1)

// 模态框相关
const showFollowers = ref(false)
const showFollowing = ref(false)
const showEditProfile = ref(false)
const modalUsers = ref<User[]>([])

// 编辑资料
const editForm = ref({
  username: '',
  bio: ''
})
const savingProfile = ref(false)

// 关注操作
const following = ref(false)

// 计算属性
const isOwnProfile = computed(() => {
  return globalStore.user?.id === userId
})

// 加载用户信息
const loadUserProfile = async () => {
  try {
    const response = await userApi.getUserProfile(userId)
    user.value = response.data
    editForm.value = {
      username: user.value.username,
      bio: user.value.bio || ''
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

// 加载用户帖子
const loadUserPosts = async () => {
  try {
    const response = await postApi.getUserPosts(userId, {
      page: postsCurrentPage.value,
      size: postsPageSize.value
    })
    userPosts.value = response.data.posts
    postsTotalPages.value = Math.ceil(response.data.total / postsPageSize.value)
  } catch (error) {
    console.error('加载用户帖子失败:', error)
  }
}

// 加载用户评论
const loadUserComments = async () => {
  try {
    const response = await userApi.getUserComments(userId, {
      page: commentsCurrentPage.value,
      size: commentsPageSize.value
    })
    userComments.value = response.data.comments
    commentsTotalPages.value = Math.ceil(response.data.total / commentsPageSize.value)
  } catch (error) {
    console.error('加载用户评论失败:', error)
  }
}

// 加载用户收藏
const loadUserCollections = async () => {
  try {
    const response = await userApi.getUserCollections(userId, {
      page: collectionsCurrentPage.value,
      size: collectionsPageSize.value
    })
    collectedPosts.value = response.data.posts
    collectionsTotalPages.value = Math.ceil(response.data.total / collectionsPageSize.value)
  } catch (error) {
    console.error('加载用户收藏失败:', error)
  }
}

// 关注/取消关注用户
const toggleFollow = async () => {
  if (!globalStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  following.value = true
  try {
    if (user.value.isFollowing) {
      await userApi.unfollowUser(userId)
      user.value.followerCount = Math.max(0, (user.value.followerCount || 0) - 1)
    } else {
      await userApi.followUser(userId)
      user.value.followerCount = (user.value.followerCount || 0) + 1
    }
    user.value.isFollowing = !user.value.isFollowing
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    following.value = false
  }
}

// 查看帖子
const viewPost = (postId: string) => {
  router.push(`/post/${postId}`)
}

// 打开关注/粉丝模态框
const openModal = async (type: 'followers' | 'following') => {
  try {
    const response = await userApi.getUserRelations(userId, type)
    modalUsers.value = response.data.users
    
    if (type === 'followers') {
      showFollowers.value = true
    } else {
      showFollowing.value = true
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

// 关闭模态框
const closeModal = () => {
  showFollowers.value = false
  showFollowing.value = false
  modalUsers.value = []
}

// 关注模态框中的用户
const toggleUserFollow = async (userItem: User) => {
  try {
    if (userItem.isFollowing) {
      await userApi.unfollowUser(userItem.id)
    } else {
      await userApi.followUser(userItem.id)
    }
    userItem.isFollowing = !userItem.isFollowing
  } catch (error) {
    console.error('操作失败:', error)
  }
}

// 编辑资料
const editProfile = () => {
  showEditProfile.value = true
}

// 保存资料
const saveProfile = async () => {
  savingProfile.value = true
  try {
    await userApi.updateProfile(editForm.value)
    user.value.username = editForm.value.username
    user.value.bio = editForm.value.bio
    showEditProfile.value = false
  } catch (error) {
    console.error('保存资料失败:', error)
  } finally {
    savingProfile.value = false
  }
}

// 更换头像
const editAvatar = () => {
  // 这里可以实现头像上传功能
  alert('头像上传功能待实现')
}

// 分页操作
const changePostsPage = (page: number) => {
  postsCurrentPage.value = page
  loadUserPosts()
}

const changeCommentsPage = (page: number) => {
  commentsCurrentPage.value = page
  loadUserComments()
}

const changeCollectionsPage = (page: number) => {
  collectionsCurrentPage.value = page
  loadUserCollections()
}

// 格式化时间
const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

// 监听标签页变化
watch(activeTab, (newTab) => {
  if (newTab === 'posts') {
    loadUserPosts()
  } else if (newTab === 'comments') {
    loadUserComments()
  } else if (newTab === 'collections') {
    loadUserCollections()
  }
})

// 监听模态框显示
watch([showFollowers, showFollowing], ([showFollower, showFollowing]) => {
  if (showFollower) {
    openModal('followers')
  } else if (showFollowing) {
    openModal('following')
  }
})

onMounted(() => {
  loadUserProfile()
  loadUserPosts()
})
</script>

<style scoped>
.user-profile-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px 0;
}

.profile-header {
  background: white;
  border-radius: 8px;
  padding: 40px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

.user-avatar {
  position: relative;
  flex-shrink: 0;
}

.user-avatar img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid #f0f0f0;
}

.edit-avatar-btn {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}

.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.basic-info {
  margin-bottom: 16px;
}

.username {
  font-size: 32px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.bio {
  font-size: 16px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 8px;
}

.join-time {
  font-size: 14px;
  color: #999;
}

.user-stats {
  display: flex;
  gap: 40px;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #1890ff;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.user-actions {
  display: flex;
  gap: 12px;
}

.profile-tabs {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.tabs-header {
  display: flex;
  border-bottom: 1px solid #eee;
}

.tab-btn {
  padding: 16px 24px;
  background: none;
  border: none;
  font-size: 16px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
  border-bottom: 2px solid transparent;
}

.tab-btn.active {
  color: #1890ff;
  border-bottom-color: #1890ff;
}

.tab-btn:hover {
  color: #1890ff;
}

.tab-content {
  padding: 24px;
}

.posts-list,
.comments-list,
.collections-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.post-item,
.comment-item {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.post-item:hover,
.comment-item:hover {
  background: #e9ecef;
  transform: translateY(-1px);
}

.post-header,
.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.tieba-name {
  color: #1890ff;
  font-size: 14px;
  font-weight: 500;
}

.post-time,
.comment-time {
  font-size: 12px;
  color: #999;
}

.post-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.4;
}

.post-content,
.comment-content {
  color: #666;
  line-height: 1.6;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-stats,
.comment-stats {
  display: flex;
  gap: 16px;
}

.stat {
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  border-color: #1890ff;
  color: #1890ff;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  transition: background 0.3s;
}

.user-list-item:hover {
  background: #f5f5f5;
}

.user-list-item img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.user-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-details .username {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.user-details .bio {
  font-size: 12px;
  color: #999;
}

.btn-small {
  padding: 6px 12px;
  font-size: 12px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .user-stats {
    justify-content: space-around;
    gap: 20px;
  }
  
  .user-actions {
    justify-content: center;
  }
  
  .tabs-header {
    flex-wrap: wrap;
  }
  
  .tab-btn {
    flex: 1;
    min-width: 100px;
    padding: 12px 16px;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
}
</style>