<template>
  <div class="search-page">
    <div class="container">
      <!-- 搜索框 -->
      <div class="search-header">
        <div class="search-box">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索帖子、贴吧、用户..."
            @keyup.enter="performSearch"
            class="search-input"
          />
          <button @click="performSearch" class="search-btn">
            <i class="icon">🔍</i>
          </button>
        </div>
        
        <!-- 搜索筛选 -->
        <div class="search-filters">
          <div class="filter-group">
            <label>搜索类型：</label>
            <select v-model="searchType" @change="performSearch">
              <option value="all">全部</option>
              <option value="posts">帖子</option>
              <option value="tieba">贴吧</option>
              <option value="users">用户</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label>排序：</label>
            <select v-model="sortBy" @change="performSearch">
              <option value="relevance">相关度</option>
              <option value="latest">最新</option>
              <option value="hot">最热</option>
            </select>
          </div>
        </div>
      </div>
      
      <!-- 搜索结果 -->
      <div class="search-results">
        <!-- 搜索结果统计 -->
        <div class="results-info">
          <p v-if="searching">搜索中...</p>
          <p v-else-if="hasResults">
            找到 {{ totalResults }} 个结果
          </p>
          <p v-else-if="searchQuery">
            没有找到相关结果
          </p>
          <p v-else>
            请输入搜索关键词
          </p>
        </div>
        
        <!-- 搜索结果标签页 -->
        <div class="results-tabs" v-if="hasResults">
          <div class="tabs-header">
            <button 
              v-for="tab in resultTabs" 
              :key="tab.id"
              class="tab-btn" 
              :class="{ active: activeResultTab === tab.id }"
              @click="activeResultTab = tab.id"
            >
              {{ tab.name }} ({{ tab.count }})
            </button>
          </div>
          
          <div class="tab-content">
            <!-- 帖子搜索结果 -->
            <div v-if="activeResultTab === 'posts' && postResults.length > 0" class="posts-results">
              <div class="results-list">
                <div 
                  v-for="post in postResults" 
                  :key="post.id" 
                  class="result-item post-item"
                  @click="viewPost(post.id)"
                >
                  <div class="result-header">
                    <span class="tieba-name">{{ post.tiebaName }}</span>
                    <span class="result-time">{{ formatTime(post.createdAt) }}</span>
                  </div>
                  <h3 class="result-title" v-html="highlightText(post.title)"></h3>
                  <p class="result-content" v-html="highlightText(post.content)"></p>
                  <div class="result-stats">
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
            
            <!-- 贴吧搜索结果 -->
            <div v-if="activeResultTab === 'tieba' && tiebaResults.length > 0" class="tieba-results">
              <div class="results-list">
                <div 
                  v-for="tieba in tiebaResults" 
                  :key="tieba.id" 
                  class="result-item tieba-item"
                  @click="viewTieba(tieba.id)"
                >
                  <div class="tieba-info">
                    <img :src="tieba.avatar || '/default-tieba-avatar.png'" :alt="tieba.name" />
                    <div class="tieba-details">
                      <h3 class="result-title" v-html="highlightText(tieba.name)"></h3>
                      <p class="result-desc" v-html="highlightText(tieba.description)"></p>
                      <div class="tieba-stats">
                        <span class="stat">{{ tieba.memberCount || 0 }} 成员</span>
                        <span class="stat">{{ tieba.postCount || 0 }} 帖子</span>
                        <span class="stat">{{ tieba.categoryName }}</span>
                      </div>
                    </div>
                  </div>
                  <button 
                    v-if="globalStore.isAuthenticated"
                    class="join-btn" 
                    :class="{ joined: tieba.isJoined }"
                    @click.stop="toggleJoinTieba(tieba)"
                  >
                    {{ tieba.isJoined ? '已加入' : '加入' }}
                  </button>
                </div>
              </div>
              
              <div class="pagination" v-if="tiebaTotalPages > 1">
                <button 
                  :disabled="tiebaCurrentPage === 1" 
                  @click="changeTiebaPage(tiebaCurrentPage - 1)"
                  class="page-btn"
                >
                  上一页
                </button>
                <span class="page-info">第 {{ tiebaCurrentPage }} 页 / 共 {{ tiebaTotalPages }} 页</span>
                <button 
                  :disabled="tiebaCurrentPage === tiebaTotalPages" 
                  @click="changeTiebaPage(tiebaCurrentPage + 1)"
                  class="page-btn"
                >
                  下一页
                </button>
              </div>
            </div>
            
            <!-- 用户搜索结果 -->
            <div v-if="activeResultTab === 'users' && userResults.length > 0" class="users-results">
              <div class="results-list">
                <div 
                  v-for="user in userResults" 
                  :key="user.id" 
                  class="result-item user-item"
                  @click="viewUser(user.id)"
                >
                  <div class="user-info">
                    <img :src="user.avatar || '/default-avatar.png'" :alt="user.username" />
                    <div class="user-details">
                      <h3 class="result-title" v-html="highlightText(user.username)"></h3>
                      <p class="result-bio" v-if="user.bio">{{ user.bio }}</p>
                      <div class="user-stats">
                        <span class="stat">{{ user.followerCount || 0 }} 粉丝</span>
                        <span class="stat">{{ user.postCount || 0 }} 帖子</span>
                      </div>
                    </div>
                  </div>
                  <button 
                    v-if="globalStore.isAuthenticated && user.id !== globalStore.user?.id"
                    class="follow-btn" 
                    :class="{ following: user.isFollowing }"
                    @click.stop="toggleFollowUser(user)"
                  >
                    {{ user.isFollowing ? '已关注' : '关注' }}
                  </button>
                </div>
              </div>
              
              <div class="pagination" v-if="usersTotalPages > 1">
                <button 
                  :disabled="usersCurrentPage === 1" 
                  @click="changeUsersPage(usersCurrentPage - 1)"
                  class="page-btn"
                >
                  上一页
                </button>
                <span class="page-info">第 {{ usersCurrentPage }} 页 / 共 {{ usersTotalPages }} 页</span>
                <button 
                  :disabled="usersCurrentPage === usersTotalPages" 
                  @click="changeUsersPage(usersCurrentPage + 1)"
                  class="page-btn"
                >
                  下一页
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 搜索建议 -->
        <div class="search-suggestions" v-if="!hasResults && searchQuery && !searching">
          <h3>搜索建议：</h3>
          <ul>
            <li>检查关键词拼写是否正确</li>
            <li>尝试使用更简单的关键词</li>
            <li>尝试搜索其他相关内容</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGlobalStore } from '@/stores/global'
import { searchApi } from '@/api/search'
import { tiebaApi } from '@/api/tieba'
import { userApi } from '@/api/auth'
import type { Post, Tieba, User } from '@/types'

const route = useRoute()
const router = useRouter()
const globalStore = useGlobalStore()

// 搜索参数
const searchQuery = ref(route.query.q as string || '')
const searchType = ref(route.query.type as string || 'all')
const sortBy = ref(route.query.sort as string || 'relevance')

// 搜索结果
const postResults = ref<Post[]>([])
const tiebaResults = ref<Tieba[]>([])
const userResults = ref<User[]>([])

// 分页信息
const postsCurrentPage = ref(1)
const postsPageSize = ref(10)
const postsTotalPages = ref(1)

const tiebaCurrentPage = ref(1)
const tiebaPageSize = ref(10)
const tiebaTotalPages = ref(1)

const usersCurrentPage = ref(1)
const usersPageSize = ref(10)
const usersTotalPages = ref(1)

// 搜索状态
const searching = ref(false)

// 结果标签页
const resultTabs = computed(() => {
  const tabs = []
  
  if (postResults.value.length > 0 || searchType.value === 'posts' || searchType.value === 'all') {
    tabs.push({ id: 'posts', name: '帖子', count: postResults.value.length })
  }
  
  if (tiebaResults.value.length > 0 || searchType.value === 'tieba' || searchType.value === 'all') {
    tabs.push({ id: 'tieba', name: '贴吧', count: tiebaResults.value.length })
  }
  
  if (userResults.value.length > 0 || searchType.value === 'users' || searchType.value === 'all') {
    tabs.push({ id: 'users', name: '用户', count: userResults.value.length })
  }
  
  return tabs
})

const activeResultTab = ref(resultTabs.value[0]?.id || 'posts')

// 计算属性
const hasResults = computed(() => {
  return postResults.value.length > 0 || tiebaResults.value.length > 0 || userResults.value.length > 0
})

const totalResults = computed(() => {
  return postResults.value.length + tiebaResults.value.length + userResults.value.length
})

// 执行搜索
const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    return
  }
  
  searching.value = true
  
  try {
    // 更新URL参数
    const queryParams: any = { q: searchQuery.value }
    if (searchType.value !== 'all') queryParams.type = searchType.value
    if (sortBy.value !== 'relevance') queryParams.sort = sortBy.value
    
    router.replace({ query: queryParams })
    
    // 根据搜索类型执行搜索
    if (searchType.value === 'all' || searchType.value === 'posts') {
      await searchPosts()
    }
    
    if (searchType.value === 'all' || searchType.value === 'tieba') {
      await searchTieba()
    }
    
    if (searchType.value === 'all' || searchType.value === 'users') {
      await searchUsers()
    }
    
    // 设置默认激活的标签页
    if (resultTabs.value.length > 0) {
      activeResultTab.value = resultTabs.value[0].id
    }
  } catch (error) {
    console.error('搜索失败:', error)
  } finally {
    searching.value = false
  }
}

// 搜索帖子
const searchPosts = async () => {
  try {
    const response = await searchApi.searchPosts({
      keyword: searchQuery.value,
      page: postsCurrentPage.value,
      size: postsPageSize.value,
      sort: sortBy.value
    })
    postResults.value = response.data.posts
    postsTotalPages.value = Math.ceil(response.data.total / postsPageSize.value)
  } catch (error) {
    console.error('搜索帖子失败:', error)
    postResults.value = []
  }
}

// 搜索贴吧
const searchTieba = async () => {
  try {
    const response = await searchApi.searchTieba({
      keyword: searchQuery.value,
      page: tiebaCurrentPage.value,
      size: tiebaPageSize.value
    })
    tiebaResults.value = response.data.tiebas
    tiebaTotalPages.value = Math.ceil(response.data.total / tiebaPageSize.value)
  } catch (error) {
    console.error('搜索贴吧失败:', error)
    tiebaResults.value = []
  }
}

// 搜索用户
const searchUsers = async () => {
  try {
    const response = await searchApi.searchUsers({
      keyword: searchQuery.value,
      page: usersCurrentPage.value,
      size: usersPageSize.value
    })
    userResults.value = response.data.users
    usersTotalPages.value = Math.ceil(response.data.total / usersPageSize.value)
  } catch (error) {
    console.error('搜索用户失败:', error)
    userResults.value = []
  }
}

// 高亮文本
const highlightText = (text: string) => {
  if (!searchQuery.value) return text
  
  const regex = new RegExp(`(${searchQuery.value})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

// 查看帖子
const viewPost = (postId: string) => {
  router.push(`/post/${postId}`)
}

// 查看贴吧
const viewTieba = (tiebaId: string) => {
  router.push(`/tieba/${tiebaId}`)
}

// 查看用户
const viewUser = (userId: string) => {
  router.push(`/user/${userId}`)
}

// 加入/离开贴吧
const toggleJoinTieba = async (tieba: Tieba) => {
  if (!globalStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  try {
    if (tieba.isJoined) {
      await tiebaApi.leaveTieba(tieba.id)
      tieba.memberCount = Math.max(0, (tieba.memberCount || 0) - 1)
    } else {
      await tiebaApi.joinTieba(tieba.id)
      tieba.memberCount = (tieba.memberCount || 0) + 1
    }
    tieba.isJoined = !tieba.isJoined
  } catch (error) {
    console.error('操作失败:', error)
  }
}

// 关注/取消关注用户
const toggleFollowUser = async (user: User) => {
  if (!globalStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  try {
    if (user.isFollowing) {
      await userApi.unfollowUser(user.id)
      user.followerCount = Math.max(0, (user.followerCount || 0) - 1)
    } else {
      await userApi.followUser(user.id)
      user.followerCount = (user.followerCount || 0) + 1
    }
    user.isFollowing = !user.isFollowing
  } catch (error) {
    console.error('操作失败:', error)
  }
}

// 分页操作
const changePostsPage = (page: number) => {
  postsCurrentPage.value = page
  searchPosts()
}

const changeTiebaPage = (page: number) => {
  tiebaCurrentPage.value = page
  searchTieba()
}

const changeUsersPage = (page: number) => {
  usersCurrentPage.value = page
  searchUsers()
}

// 格式化时间
const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

// 监听路由参数变化
watch(() => route.query, (newQuery) => {
  if (newQuery.q !== searchQuery.value) {
    searchQuery.value = newQuery.q as string || ''
    if (searchQuery.value) {
      performSearch()
    }
  }
})

onMounted(() => {
  if (searchQuery.value) {
    performSearch()
  }
})
</script>

<style scoped>
.search-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px 0;
}

.search-header {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.search-box {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #1890ff;
  border-radius: 24px;
  font-size: 16px;
  outline: none;
}

.search-input:focus {
  border-color: #40a9ff;
}

.search-btn {
  padding: 12px 24px;
  background: #1890ff;
  border: none;
  border-radius: 24px;
  color: white;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s;
}

.search-btn:hover {
  background: #40a9ff;
}

.search-filters {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
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

.search-results {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.results-info {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.results-info p {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.results-tabs {
  margin-top: 24px;
}

.tabs-header {
  display: flex;
  border-bottom: 1px solid #eee;
  margin-bottom: 24px;
}

.tab-btn {
  padding: 12px 24px;
  background: none;
  border: none;
  font-size: 14px;
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

.results-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-item {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.result-item:hover {
  background: #e9ecef;
  transform: translateY(-1px);
}

.result-header {
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

.result-time {
  font-size: 12px;
  color: #999;
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.4;
}

.result-title mark {
  background: #fff566;
  padding: 2px 4px;
  border-radius: 2px;
}

.result-content,
.result-desc,
.result-bio {
  color: #666;
  line-height: 1.6;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.result-content mark,
.result-desc mark,
.result-bio mark {
  background: #fff566;
  padding: 2px 4px;
  border-radius: 2px;
}

.result-stats,
.tieba-stats,
.user-stats {
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

.tieba-item,
.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tieba-info,
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.tieba-info img {
  width: 60px;
  height: 60px;
  border-radius: 50%;
}

.user-info img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
}

.tieba-details,
.user-details {
  flex: 1;
}

.join-btn,
.follow-btn {
  padding: 8px 16px;
  border: 1px solid #1890ff;
  background: white;
  color: #1890ff;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.join-btn:hover,
.follow-btn:hover {
  background: #1890ff;
  color: white;
}

.join-btn.joined,
.follow-btn.following {
  background: #52c41a;
  border-color: #52c41a;
  color: white;
}

.join-btn.joined:hover,
.follow-btn.following:hover {
  background: #73d13d;
  border-color: #73d13d;
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

.search-suggestions {
  margin-top: 24px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.search-suggestions h3 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
}

.search-suggestions ul {
  margin: 0;
  padding-left: 20px;
  color: #666;
}

.search-suggestions li {
  margin-bottom: 8px;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-box {
    flex-direction: column;
  }
  
  .search-filters {
    flex-direction: column;
    gap: 12px;
  }
  
  .filter-group {
    justify-content: space-between;
  }
  
  .tabs-header {
    flex-wrap: wrap;
  }
  
  .tab-btn {
    flex: 1;
    min-width: 100px;
    padding: 10px 16px;
    font-size: 13px;
  }
  
  .tieba-item,
  .user-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .join-btn,
  .follow-btn {
    align-self: flex-end;
  }
}
</style>