import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User } from '@/types/user'

interface AppConfig {
  siteName: string
  version: string
  apiBaseUrl: string
  uploadConfig: {
    maxSize: number
    allowedTypes: string[]
  }
}

export const useGlobalStore = defineStore('global', () => {
  // 状态
  const user = ref<User | null>(null)
  const isLoggedIn = computed(() => !!user.value)
  const loading = ref(false)
  const appConfig = ref<AppConfig>({
    siteName: '贴吧百科',
    version: '1.0.0',
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '/api',
    uploadConfig: {
      maxSize: 10 * 1024 * 1024, // 10MB
      allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
    }
  })

  // 获取用户信息
  const fetchUserInfo = async () => {
    try {
      const response = await authApi.getUserInfo()
      user.value = response.data
      return user.value
    } catch (error) {
      user.value = null
      throw error
    }
  }

  // 检查认证状态
  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (token) {
        await fetchUserInfo()
      }
    } catch (error) {
      console.error('检查认证状态失败:', error)
      localStorage.removeItem('access_token')
      user.value = null
    }
  }

  // 登录
  const login = async (credentials: { username: string; password: string }) => {
    try {
      loading.value = true
      const response = await authApi.login(credentials)
      
      const { access_token, user: userInfo } = response.data
      localStorage.setItem('access_token', access_token)
      user.value = userInfo
      
      return userInfo
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (userData: {
    username: string
    email: string
    password: string
    nickname?: string
  }) => {
    try {
      loading.value = true
      const response = await authApi.register(userData)
      return response.data
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      localStorage.removeItem('access_token')
      user.value = null
    }
  }

  // 加载应用配置
  const loadAppConfig = async () => {
    // 这里可以从服务器获取配置，暂时使用默认配置
    return appConfig.value
  }

  return {
    // 状态
    user,
    isLoggedIn,
    loading,
    appConfig,
    
    // 操作
    fetchUserInfo,
    checkAuthStatus,
    login,
    register,
    logout,
    loadAppConfig
  }
})