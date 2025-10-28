<template>
  <header class="header">
    <div class="container">
      <div class="header-content">
        <!-- Logo -->
        <div class="logo">
          <router-link to="/" class="logo-link">
            <span class="logo-text">贴吧</span>
          </router-link>
        </div>

        <!-- 搜索框 -->
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索贴吧、帖子、用户..."
            class="search-input"
            @keyup.enter="handleSearch"
          />
          <button class="search-btn" @click="handleSearch">
            <span>搜索</span>
          </button>
        </div>

        <!-- 导航菜单 -->
        <nav class="nav-menu">
          <router-link to="/" class="nav-item">首页</router-link>
          <router-link to="/tieba" class="nav-item">贴吧</router-link>
          <router-link to="/hot" class="nav-item">热门</router-link>
        </nav>

        <!-- 用户操作区 -->
        <div class="user-actions">
          <template v-if="isAuthenticated">
            <!-- 消息通知 -->
            <div class="notification">
              <button class="action-btn">
                <span>🔔</span>
              </button>
            </div>

            <!-- 用户菜单 -->
            <div class="user-menu">
              <div class="user-info" @click="toggleUserMenu">
                <img :src="user.avatar || '/default-avatar.png'" :alt="user.nickname" class="user-avatar" />
                <span class="user-name">{{ user.nickname }}</span>
              </div>
              
              <div v-if="showUserMenu" class="user-dropdown">
                <router-link to="/user/profile" class="dropdown-item">个人中心</router-link>
                <router-link to="/user/posts" class="dropdown-item">我的帖子</router-link>
                <router-link to="/user/comments" class="dropdown-item">我的评论</router-link>
                <div class="dropdown-divider"></div>
                <button class="dropdown-item logout-btn" @click="handleLogout">退出登录</button>
              </div>
            </div>
          </template>
          
          <template v-else>
            <router-link to="/login" class="login-btn">登录</router-link>
            <router-link to="/register" class="register-btn">注册</router-link>
          </template>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useGlobalStore } from '@/stores/global'

const router = useRouter()
const globalStore = useGlobalStore()

const searchQuery = ref('')
const showUserMenu = ref(false)

const isAuthenticated = computed(() => globalStore.isAuthenticated)
const user = computed(() => globalStore.user)

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(searchQuery.value.trim())}`)
  }
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const handleLogout = async () => {
  try {
    await globalStore.logout()
    showUserMenu.value = false
    router.push('/')
  } catch (error) {
    console.error('退出登录失败:', error)
  }
}

// 点击外部关闭用户菜单
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.user-menu')) {
    showUserMenu.value = false
  }
}

// 添加全局点击事件监听
import { onMounted, onUnmounted } from 'vue'
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.header {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  height: 64px;
  gap: 24px;
}

.logo-link {
  font-size: 24px;
  font-weight: bold;
  color: #1890ff;
  text-decoration: none;
}

.search-box {
  flex: 1;
  max-width: 400px;
  display: flex;
  gap: 8px;
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

.nav-menu {
  display: flex;
  gap: 24px;
}

.nav-item {
  color: #666;
  text-decoration: none;
  padding: 8px 0;
  transition: color 0.3s;
}

.nav-item:hover,
.nav-item.router-link-active {
  color: #1890ff;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background 0.3s;
}

.action-btn:hover {
  background: #f5f5f5;
}

.user-menu {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.3s;
}

.user-info:hover {
  background: #f5f5f5;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.user-name {
  font-size: 14px;
  color: #333;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 160px;
  z-index: 1001;
}

.dropdown-item {
  display: block;
  padding: 12px 16px;
  color: #333;
  text-decoration: none;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.dropdown-item:hover {
  background: #f5f5f5;
}

.dropdown-divider {
  height: 1px;
  background: #f0f0f0;
  margin: 4px 0;
}

.logout-btn {
  color: #ff4d4f;
}

.logout-btn:hover {
  background: #fff2f0;
}

.login-btn,
.register-btn {
  padding: 6px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s;
}

.login-btn {
  color: #1890ff;
  border: 1px solid #1890ff;
}

.login-btn:hover {
  background: #e6f7ff;
}

.register-btn {
  background: #1890ff;
  color: #fff;
  border: 1px solid #1890ff;
}

.register-btn:hover {
  background: #40a9ff;
}

@media (max-width: 768px) {
  .header-content {
    gap: 12px;
  }
  
  .search-box {
    max-width: 200px;
  }
  
  .nav-menu {
    gap: 12px;
  }
  
  .user-name {
    display: none;
  }
}
</style>