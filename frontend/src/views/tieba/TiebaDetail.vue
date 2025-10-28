<template>
  <div class="tieba-detail-page">
    <!-- 贴吧头部信息 -->
    <div class="tieba-header">
      <div class="container">
        <div class="header-content">
          <div class="tieba-info">
            <div class="avatar">
              <img :src="tieba.avatar || '/default-tieba-avatar.png'" :alt="tieba.name" />
            </div>
            <div class="info">
              <h1 class="tieba-name">{{ tieba.name }}</h1>
              <p class="tieba-desc">{{ tieba.description }}</p>
              <div class="stats">
                <span class="stat-item">
                  <strong>{{ tieba.memberCount || 0 }}</strong> 成员
                </span>
                <span class="stat-item">
                  <strong>{{ tieba.postCount || 0 }}</strong> 帖子
                </span>
                <span class="stat-item">
                  <strong>{{ tieba.categoryName }}</strong> 分类
                </span>
              </div>
            </div>
          </div>
          <div class="actions">
            <button 
              v-if="!isJoined" 
              class="btn btn-primary" 
              @click="joinTieba"
              :disabled="joining"
            >
              {{ joining ? '加入中...' : '加入贴吧' }}
            </button>
            <button 
              v-else 
              class="btn btn-outline" 
              @click="leaveTieba"
              :disabled="leaving"
            >
              {{ leaving ? '离开中...' : '已加入' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 帖子列表 -->
    <div class="container">
      <div class="posts-section">
        <div class="section-header">
          <h2>帖子列表</h2>
          <button 
            v-if="isJoined" 
            class="btn btn-primary" 
            @click="showCreatePost = true"
          >
            发帖
          </button>
        </div>

        <!-- 帖子筛选 -->
        <div class="filters">
          <div class="filter-group">
            <label>排序：</label>
            <select v-model="sortBy" @change="loadPosts">
              <option value="latest">最新</option>
              <option value="hot">最热</option>
              <option value="recommend">推荐</option>
            </select>
          </div>
        </div>

        <!-- 帖子列表 -->
        <div class="posts-list">
          <div 
            v-for="post in posts" 
            :key="post.id" 
            class="post-item"
            @click="viewPost(post.id)"
          >
            <div class="post-header">
              <div class="author-info">
                <img :src="post.authorAvatar || '/default-avatar.png'" :alt="post.authorName" />
                <span class="author-name">{{ post.authorName }}</span>
              </div>
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

        <!-- 分页 -->
        <div class="pagination" v-if="totalPages > 1">
          <button 
            :disabled="currentPage === 1" 
            @click="changePage(currentPage - 1)"
            class="page-btn"
          >
            上一页
          </button>
          <span class="page-info">第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span>
          <button 
            :disabled="currentPage === totalPages" 
            @click="changePage(currentPage + 1)"
            class="page-btn"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 发帖模态框 -->
    <div v-if="showCreatePost" class="modal-overlay" @click="showCreatePost = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>发布新帖子</h3>
          <button class="close-btn" @click="showCreatePost = false">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createPost">
            <div class="form-group">
              <label>标题</label>
              <input v-model="newPost.title" type="text" required />
            </div>
            <div class="form-group">
              <label>内容</label>
              <textarea v-model="newPost.content" rows="6" required></textarea>
            </div>
            <div class="form-actions">
              <button type="button" @click="showCreatePost = false" class="btn btn-outline">
                取消
              </button>
              <button type="submit" class="btn btn-primary" :disabled="creatingPost">
                {{ creatingPost ? '发布中...' : '发布' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGlobalStore } from '@/stores/global'
import { tiebaApi, postApi } from '@/api/tieba'
import type { Tieba, Post } from '@/types/tieba'

const route = useRoute()
const router = useRouter()
const globalStore = useGlobalStore()

const tiebaId = route.params.id as string

// 贴吧信息
const tieba = ref<Tieba>({
  id: '',
  name: '',
  description: '',
  avatar: '',
  categoryName: '',
  memberCount: 0,
  postCount: 0
})

// 帖子列表
const posts = ref<Post[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalPages = ref(1)
const sortBy = ref('latest')

// 加入状态
const isJoined = ref(false)
const joining = ref(false)
const leaving = ref(false)

// 发帖相关
const showCreatePost = ref(false)
const creatingPost = ref(false)
const newPost = ref({
  title: '',
  content: ''
})

// 加载贴吧详情
const loadTiebaDetail = async () => {
  try {
    const response = await tiebaApi.getTiebaDetail(tiebaId)
    tieba.value = response.data
    
    // 检查用户是否已加入
    if (globalStore.isAuthenticated) {
      const joinStatus = await tiebaApi.checkJoinStatus(tiebaId)
      isJoined.value = joinStatus.data.isJoined
    }
  } catch (error) {
    console.error('加载贴吧详情失败:', error)
  }
}

// 加载帖子列表
const loadPosts = async () => {
  try {
    const response = await postApi.getPostsByTieba(tiebaId, {
      page: currentPage.value,
      size: pageSize.value,
      sort: sortBy.value
    })
    posts.value = response.data.posts
    totalPages.value = Math.ceil(response.data.total / pageSize.value)
  } catch (error) {
    console.error('加载帖子列表失败:', error)
  }
}

// 加入贴吧
const joinTieba = async () => {
  if (!globalStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  joining.value = true
  try {
    await tiebaApi.joinTieba(tiebaId)
    isJoined.value = true
    tieba.value.memberCount = (tieba.value.memberCount || 0) + 1
  } catch (error) {
    console.error('加入贴吧失败:', error)
  } finally {
    joining.value = false
  }
}

// 离开贴吧
const leaveTieba = async () => {
  leaving.value = true
  try {
    await tiebaApi.leaveTieba(tiebaId)
    isJoined.value = false
    tieba.value.memberCount = Math.max(0, (tieba.value.memberCount || 0) - 1)
  } catch (error) {
    console.error('离开贴吧失败:', error)
  } finally {
    leaving.value = false
  }
}

// 创建帖子
const createPost = async () => {
  if (!globalStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  creatingPost.value = true
  try {
    await postApi.createPost({
      tiebaId: tiebaId,
      title: newPost.value.title,
      content: newPost.value.content
    })
    
    showCreatePost.value = false
    newPost.value = { title: '', content: '' }
    await loadPosts() // 重新加载帖子列表
    tieba.value.postCount = (tieba.value.postCount || 0) + 1
  } catch (error) {
    console.error('创建帖子失败:', error)
  } finally {
    creatingPost.value = false
  }
}

// 查看帖子详情
const viewPost = (postId: string) => {
  router.push(`/post/${postId}`)
}

// 分页
const changePage = (page: number) => {
  currentPage.value = page
  loadPosts()
}

// 格式化时间
const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(() => {
  loadTiebaDetail()
  loadPosts()
})
</script>

<style scoped>
.tieba-detail-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.tieba-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.tieba-info {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.avatar img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.tieba-name {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 8px;
}

.tieba-desc {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 16px;
}

.stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  font-size: 14px;
}

.stat-item strong {
  font-size: 18px;
}

.actions {
  flex-shrink: 0;
}

.posts-section {
  padding: 40px 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h2 {
  font-size: 24px;
  color: #333;
}

.filters {
  margin-bottom: 20px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group label {
  font-weight: 500;
  color: #666;
}

.filter-group select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.post-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s;
}

.post-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-info img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.author-name {
  font-weight: 500;
  color: #1890ff;
}

.post-time {
  font-size: 12px;
  color: #999;
}

.post-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.4;
}

.post-content {
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-stats {
  display: flex;
  gap: 20px;
}

.stat {
  font-size: 14px;
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
  max-height: 90vh;
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
  min-height: 120px;
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
  }
  
  .tieba-info {
    flex-direction: column;
    text-align: center;
  }
  
  .stats {
    justify-content: center;
  }
  
  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .post-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
}
</style>