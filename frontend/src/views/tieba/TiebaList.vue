<template>
  <div class="tieba-list-page">
    <div class="container">
      <!-- 页面标题和搜索 -->
      <div class="page-header">
        <h1 class="page-title">贴吧列表</h1>
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索贴吧..."
            class="search-input"
            @input="handleSearch"
          />
          <button class="search-btn" @click="handleSearch">
            <span>搜索</span>
          </button>
        </div>
      </div>

      <!-- 分类筛选 -->
      <div class="category-filter">
        <div class="filter-header">
          <h3 class="filter-title">分类</h3>
          <button 
            class="filter-clear"
            @click="clearCategoryFilter"
            :disabled="!selectedCategory"
          >
            清除筛选
          </button>
        </div>
        <div class="category-list">
          <button
            v-for="category in categories"
            :key="category.id"
            class="category-btn"
            :class="{ active: selectedCategory === category.id }"
            @click="toggleCategory(category.id)"
          >
            <span class="category-name">{{ category.name }}</span>
            <span class="category-count">{{ category.tieba_count }}</span>
          </button>
        </div>
      </div>

      <!-- 贴吧列表 -->
      <div class="tieba-grid">
        <div v-for="tieba in tiebas" :key="tieba.id" class="tieba-card">
          <div class="tieba-cover">
            <img :src="tieba.banner || '/default-banner.jpg'" :alt="tieba.name" class="cover-image" />
            <div class="tieba-avatar">
              <img :src="tieba.avatar || '/default-tieba.png'" :alt="tieba.name" />
            </div>
          </div>
          
          <div class="tieba-content">
            <div class="tieba-header">
              <router-link :to="`/tieba/${tieba.id}`" class="tieba-name">
                {{ tieba.name }}
              </router-link>
              <span v-if="tieba.is_official" class="official-badge">官方</span>
            </div>
            
            <p class="tieba-desc">{{ tieba.description }}</p>
            
            <div class="tieba-meta">
              <span class="meta-item">
                <span class="meta-icon">👥</span>
                {{ tieba.member_count }} 成员
              </span>
              <span class="meta-item">
                <span class="meta-icon">📝</span>
                {{ tieba.post_count }} 帖子
              </span>
              <span class="meta-item">
                <span class="meta-icon">🔥</span>
                {{ tieba.today_post_count }} 今日
              </span>
            </div>
            
            <div class="tieba-category">
              <router-link :to="`/tieba?category=${tieba.category.id}" class="category-tag">
                {{ tieba.category.name }}
              </router-link>
            </div>
          </div>
          
          <div class="tieba-actions">
            <button 
              v-if="!tieba.is_joined" 
              class="join-btn"
              @click="handleJoinTieba(tieba)"
              :disabled="!isAuthenticated"
            >
              加入
            </button>
            <button 
              v-else 
              class="joined-btn"
              @click="handleLeaveTieba(tieba)"
            >
              已加入
            </button>
          </div>
        </div>
      </div>

      <!-- 加载更多 -->
      <div class="load-more">
        <button 
          v-if="hasMore" 
          class="load-more-btn"
          @click="loadMore"
          :disabled="loading"
        >
          <span v-if="loading" class="loading"></span>
          {{ loading ? '加载中...' : '加载更多' }}
        </button>
        <div v-else class="no-more">
          没有更多贴吧了
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && tiebas.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <h3 class="empty-title">暂无贴吧</h3>
        <p class="empty-desc">
          {{ searchQuery ? '没有找到相关的贴吧' : '还没有贴吧，快来创建第一个贴吧吧！' }}
        </p>
        <router-link v-if="isAuthenticated" to="/tieba/create" class="create-btn">
          创建贴吧
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGlobalStore } from '@/stores/global'
import { tiebaApi } from '@/api/tieba'
import type { Tieba, Category } from '@/types/tieba'

const route = useRoute()
const router = useRouter()
const globalStore = useGlobalStore()

const tiebas = ref<Tieba[]>([])
const categories = ref<Category[]>([])
const searchQuery = ref('')
const selectedCategory = ref<number | null>(null)
const loading = ref(false)
const currentPage = ref(1)
const hasMore = ref(true)

const isAuthenticated = computed(() => globalStore.isAuthenticated)

// 从路由参数获取筛选条件
watch(() => route.query, (query) => {
  searchQuery.value = (query.q as string) || ''
  selectedCategory.value = query.category ? Number(query.category) : null
  loadTiebas(true)
}, { immediate: true })

// 加载贴吧列表
const loadTiebas = async (reset = false) => {
  if (reset) {
    tiebas.value = []
    currentPage.value = 1
    hasMore.value = true
  }

  if (loading.value || !hasMore.value) return

  loading.value = true

  try {
    const params: any = {
      page: currentPage.value,
      page_size: 20
    }

    if (searchQuery.value) {
      params.q = searchQuery.value
    }

    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }

    const response = await tiebaApi.getTiebaList(params)
    const newTiebas = response.results || response

    if (reset) {
      tiebas.value = newTiebas
    } else {
      tiebas.value.push(...newTiebas)
    }

    // 检查是否还有更多数据
    hasMore.value = newTiebas.length === 20
    currentPage.value += 1
  } catch (error) {
    console.error('加载贴吧列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载分类列表
const loadCategories = async () => {
  try {
    const response = await tiebaApi.getCategories()
    categories.value = response.results || response
  } catch (error) {
    console.error('加载分类列表失败:', error)
  }
}

// 搜索处理
const handleSearch = () => {
  const query: any = {}
  if (searchQuery.value) query.q = searchQuery.value
  if (selectedCategory.value) query.category = selectedCategory.value
  
  router.push({ path: '/tieba', query })
}

// 分类筛选
const toggleCategory = (categoryId: number) => {
  selectedCategory.value = selectedCategory.value === categoryId ? null : categoryId
  const query: any = {}
  if (searchQuery.value) query.q = searchQuery.value
  if (selectedCategory.value) query.category = selectedCategory.value
  
  router.push({ path: '/tieba', query })
}

// 清除分类筛选
const clearCategoryFilter = () => {
  selectedCategory.value = null
  const query: any = {}
  if (searchQuery.value) query.q = searchQuery.value
  
  router.push({ path: '/tieba', query })
}

// 加入贴吧
const handleJoinTieba = async (tieba: Tieba) => {
  if (!isAuthenticated.value) {
    router.push('/login')
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

// 离开贴吧
const handleLeaveTieba = async (tieba: Tieba) => {
  try {
    await tiebaApi.leaveTieba(tieba.id)
    tieba.is_joined = false
    tieba.member_count -= 1
  } catch (error) {
    console.error('离开贴吧失败:', error)
  }
}

// 加载更多
const loadMore = () => {
  loadTiebas(false)
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.tieba-list-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.search-box {
  display: flex;
  gap: 8px;
  max-width: 400px;
  width: 100%;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: #40a9ff;
}

.search-btn {
  padding: 8px 16px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.search-btn:hover {
  background: #40a9ff;
}

.category-filter {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.filter-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.filter-clear {
  background: none;
  border: none;
  color: #1890ff;
  cursor: pointer;
  font-size: 14px;
}

.filter-clear:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.category-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #d9d9d9;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.category-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.category-btn.active {
  background: #e6f7ff;
  border-color: #1890ff;
  color: #1890ff;
}

.category-name {
  font-weight: 500;
}

.category-count {
  color: #999;
  font-size: 12px;
}

.tieba-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.tieba-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.tieba-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.tieba-cover {
  position: relative;
  height: 120px;
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.tieba-avatar {
  position: absolute;
  bottom: -20px;
  left: 20px;
  width: 80px;
  height: 80px;
  border-radius: 12px;
  border: 4px solid #fff;
  background: #fff;
  overflow: hidden;
}

.tieba-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.tieba-content {
  padding: 32px 20px 20px;
}

.tieba-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.tieba-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  text-decoration: none;
}

.tieba-name:hover {
  color: #1890ff;
}

.official-badge {
  background: #ff4d4f;
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.tieba-desc {
  color: #666;
  line-height: 1.5;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tieba-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #999;
  font-size: 12px;
}

.meta-icon {
  font-size: 14px;
}

.tieba-category {
  margin-bottom: 16px;
}

.category-tag {
  display: inline-block;
  padding: 4px 8px;
  background: #f0f2f5;
  color: #666;
  border-radius: 4px;
  font-size: 12px;
  text-decoration: none;
}

.category-tag:hover {
  background: #e6f7ff;
  color: #1890ff;
}

.tieba-actions {
  padding: 0 20px 20px;
}

.join-btn,
.joined-btn {
  width: 100%;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.join-btn {
  background: #1890ff;
  color: #fff;
}

.join-btn:hover:not(:disabled) {
  background: #40a9ff;
}

.join-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.joined-btn {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #d9d9d9;
}

.joined-btn:hover {
  background: #fff2f0;
  color: #ff4d4f;
  border-color: #ff4d4f;
}

.load-more {
  text-align: center;
  margin-bottom: 32px;
}

.load-more-btn {
  padding: 12px 32px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.load-more-btn:hover:not(:disabled) {
  background: #40a9ff;
}

.load-more-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.no-more {
  color: #999;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.empty-desc {
  color: #666;
  margin-bottom: 24px;
}

.create-btn {
  display: inline-block;
  padding: 12px 24px;
  background: #1890ff;
  color: #fff;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 500;
  transition: background 0.3s;
}

.create-btn:hover {
  background: #40a9ff;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .search-box {
    max-width: none;
  }
  
  .tieba-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .tieba-meta {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>