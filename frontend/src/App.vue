<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <Header />
    
    <!-- 主要内容区域 -->
    <main class="main-content">
      <router-view />
    </main>
    
    <!-- 底部信息 -->
    <Footer />
    
    <!-- 全局加载状态 -->
    <LoadingOverlay v-if="globalLoading" />
    
    <!-- 全局消息提示 -->
    <MessageContainer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGlobalStore } from '@/stores/global'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import LoadingOverlay from '@/components/common/LoadingOverlay.vue'
import MessageContainer from '@/components/common/MessageContainer.vue'

const router = useRouter()
const globalStore = useGlobalStore()
const globalLoading = ref(false)

// 应用初始化
onMounted(async () => {
  try {
    globalLoading.value = true
    
    // 检查用户登录状态
    await globalStore.checkAuthStatus()
    
    // 加载应用配置
    await globalStore.loadAppConfig()
    
  } catch (error) {
    console.error('应用初始化失败:', error)
  } finally {
    globalLoading.value = false
  }
})

// 监听路由变化
router.beforeEach((to, from, next) => {
  // 页面访问权限检查
  if (to.meta.requiresAuth && !globalStore.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding-top: 64px; /* 导航栏高度 */
  min-height: calc(100vh - 120px); /* 减去导航栏和底部高度 */
}
</style>