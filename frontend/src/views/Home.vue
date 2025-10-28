<template>
  <div class="home">
    <!-- 顶部横幅 -->
    <section class="banner">
      <div class="container">
        <div class="banner-content">
          <h1 class="banner-title">欢迎来到贴吧社区</h1>
          <p class="banner-desc">发现有趣的贴吧，参与热门讨论，结交志同道合的朋友</p>
          <div class="banner-actions">
            <router-link to="/tieba" class="btn btn-primary btn-lg">
              浏览贴吧
            </router-link>
            <router-link v-if="!isAuthenticated" to="/register" class="btn btn-outline btn-lg">
              立即加入
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- 主要内容区 -->
    <div class="container">
      <div class="home-content">
        <!-- 左侧：热门帖子 -->
        <div class="main-content">
          <section class="section">
            <div class="section-header">
              <h2 class="section-title">热门帖子</h2>
              <router-link to="/hot" class="section-more">查看更多</router-link>
            </div>
            
            <div class="post-list">
              <div v-for="post in hotPosts" :key="post.id" class="post-card">
                <div class="post-header">
                  <div class="post-author">
                    <img :src="post.author.avatar || '/default-avatar.png'" :alt="post.author.nickname" class="author-avatar" />
                    <div class="author-info">
                      <span class="author-name">{{ post.author.nickname }}</span>
                      <span class="post-time">{{ formatTime(post.created_at) }}</span>
                    </div>
                  </div>
                  <div class="post-tieba">
                    <router-link :to="`/tieba/${post.tieba.id}`" class="tieba-link">
                      {{ post.tieba.name }}
                    </router-link>
                  </div>
                </div>
                
                <router-link :to="`/post/${post.id}`" class="post-body">
                  <h3 class="post-title">{{ post.title }}</h3>
                  <p class="post-content">{{ post.content }}</p>
                  
                  <div v-if="post.images && post.images.length > 0" class="post-images">
                    <img :src="post.images[0]" :alt="post.title" class="post-image" />
                  </div>
                </router-link>
                
                <div class="post-footer">
                  <div class="post-stats">
                    <span class="stat-item">
                      <span>👁️</span>
                      {{ post.view_count }}
                    </span>
                    <span class="stat-item">
                      <span>❤️</span>
                      {{ post.like_count }}
                    </span>
                    <span class="stat-item">
                      <span>💬</span>
                      {{ post.comment_count }}
                    </span>
                  </div>
                  <div class="post-actions">
                    <button class="action-btn" @click="handleLike(post)">
                      {{ post.is_liked ? '取消点赞' : '点赞' }}
                    </button>
                    <button class="action-btn" @click="handleCollect(post)">
                      {{ post.is_collected ? '取消收藏' : '收藏' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- 右侧：推荐贴吧 -->
        <div class="sidebar">
          <section class="section">
            <div class="section-header">
              <h2 class="section-title">推荐贴吧</h2>
            </div>
            
            <div class="tieba-list">
              <div v-for="tieba in recommendedTiebas" :key="tieba.id" class="tieba-card">
                <div class="tieba-header">
                  <img :src="tieba.avatar || '/default-tieba.png'" :alt="tieba.name" class="tieba-avatar" />
                  <div class="tieba-info">
                    <router-link :to="`/tieba/${tieba.id}`" class="tieba-name">
                      {{ tieba.name }}
                    </router-link>
                    <p class="tieba-desc">{{ tieba.description }}</p>
                  </div>
                </div>
                
                <div class="tieba-stats">
                  <span class="stat">{{ tieba.member_count }} 成员</span>
                  <span class="stat">{{ tieba.post_count }} 帖子</span>
                </div>
                
                <button 
                  v-if="!tieba.is_joined" 
                  class="btn btn-primary btn-sm"
                  @click="handleJoinTieba(tieba)"
                >
                  加入
                </button>
                <button 
                  v-else 
                  class="btn btn-outline btn-sm"
                  @click="handleLeaveTieba(tieba)"
                >
                  已加入
                </button>
              </div>
            </div>
          </section>

          <!-- 热门分类 -->
          <section class="section">
            <div class="section-header">
              <h2 class="section-title">热门分类</h2>
            </div>
            
            <div class="category-list">
              <router-link 
                v-for="category in hotCategories" 
                :key="category.id" 
                :to="`/tieba?category=${category.id}`"
                class="category-item"
              >
                <span class="category-name">{{ category.name }}</span>
                <span class="category-count">{{ category.tieba_count }}</span>
              </router-link>
            </div>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useGlobalStore } from '@/stores/global'
import { postApi, tiebaApi } from '@/api/tieba'
import type { Post, Tieba, Category } from '@/types/tieba'

const globalStore = useGlobalStore()

const hotPosts = ref<Post[]>([])
const recommendedTiebas = ref<Tieba[]>([])
const hotCategories = ref<Category[]>([])

const isAuthenticated = computed(() => globalStore.isAuthenticated)

// 加载数据
const loadData = async () => {
  try {
    // 获取热门帖子
    const postsResponse = await postApi.getHotPosts()
    hotPosts.value = postsResponse.results || postsResponse
    
    // 获取推荐贴吧
    const tiebasResponse = await tiebaApi.getRecommendedTiebas()
    recommendedTiebas.value = tiebasResponse.results || tiebasResponse
    
    // 获取分类列表
    const categoriesResponse = await tiebaApi.getCategories()
    hotCategories.value = categoriesResponse.results || categoriesResponse
    
  } catch (error) {
    console.error('加载首页数据失败:', error)
  }
}

// 格式化时间
const formatTime = (timeStr: string) => {
  const time = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - time.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 2592000000) return `${Math.floor(diff / 86400000)}天前`
  
  return time.toLocaleDateString()
}

// 处理点赞
const handleLike = async (post: Post) => {
  if (!isAuthenticated.value) {
    // 提示登录
    return
  }
  
  try {
    await postApi.likePost(post.id)
    post.is_liked = !post.is_liked
    post.like_count += post.is_liked ? 1 : -1
  } catch (error) {
    console.error('点赞失败:', error)
  }
}

// 处理收藏
const handleCollect = async (post: Post) => {
  if (!isAuthenticated.value) {
    // 提示登录
    return
  }
  
  try {
    await postApi.collectPost(post.id)
    post.is_collected = !post.is_collected
    post.collect_count += post.is_collected ? 1 : -1
  } catch (error) {
    console.error('收藏失败:', error)
  }
}

// 处理加入贴吧
const handleJoinTieba = async (tieba: Tieba) => {
  if (!isAuthenticated.value) {
    // 提示登录
    return
  }
  
  try {
    await tiebaApi.joinTieba(tieba.id)
    tieba.is_joined = true
    tieba.member_count += 1
  } catch (error) {
    console.error('加入贴吧失败:', error)
  }
}

// 处理离开贴吧
const handleLeaveTieba = async (tieba: Tieba) => {
  try {
    await tiebaApi.leaveTieba(tieba.id)
    tieba.is_joined = false
    tieba.member_count -= 1
  } catch (error) {
    console.error('离开贴吧失败:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 80px 0;
  text-align: center;
}

.banner-content {
  max-width: 600px;
  margin: 0 auto;
}

.banner-title {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 16px;
}

.banner-desc {
  font-size: 18px;
  margin-bottom: 32px;
  opacity: 0.9;
}

.banner-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn-lg {
  padding: 12px 32px;
  font-size: 16px;
}

.btn-outline {
  background: transparent;
  border: 2px solid #fff;
  color: #fff;
}

.btn-outline:hover {
  background: #fff;
  color: #667eea;
}

.home-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 32px;
  padding: 40px 0;
}

.section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.section-more {
  color: #1890ff;
  text-decoration: none;
  font-size: 14px;
}

.section-more:hover {
  text-decoration: underline;
}

/* 帖子卡片样式 */
.post-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s;
}

.post-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 500;
  color: #333;
}

.post-time {
  font-size: 12px;
  color: #999;
}

.tieba-link {
  color: #1890ff;
  text-decoration: none;
  font-size: 14px;
}

.tieba-link:hover {
  text-decoration: underline;
}

.post-body {
  text-decoration: none;
  color: inherit;
  display: block;
  margin-bottom: 12px;
}

.post-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.post-content {
  color: #666;
  line-height: 1.6;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-images {
  margin-top: 12px;
}

.post-image {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: 4px;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.post-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #999;
  font-size: 14px;
}

.post-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: none;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

/* 贴吧卡片样式 */
.tieba-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.tieba-header {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.tieba-avatar {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  object-fit: cover;
}

.tieba-info {
  flex: 1;
}

.tieba-name {
  font-weight: 600;
  color: #333;
  text-decoration: none;
  display: block;
  margin-bottom: 4px;
}

.tieba-name:hover {
  color: #1890ff;
}

.tieba-desc {
  color: #666;
  font-size: 12px;
  line-height: 1.4;
}

.tieba-stats {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.stat {
  color: #999;
  font-size: 12px;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
}

/* 分类列表样式 */
.category-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #fff;
  border-radius: 6px;
  text-decoration: none;
  color: #333;
  transition: background 0.3s;
}

.category-item:hover {
  background: #f5f5f5;
}

.category-name {
  font-weight: 500;
}

.category-count {
  color: #999;
  font-size: 12px;
}

@media (max-width: 768px) {
  .home-content {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .banner-title {
    font-size: 32px;
  }
  
  .banner-desc {
    font-size: 16px;
  }
  
  .banner-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style>