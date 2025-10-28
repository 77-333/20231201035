import api from './index'
import type { User } from '@/types/user'

// 认证相关API
export const authApi = {
  // 用户登录
  login: (credentials: { username: string; password: string }) => {
    return api.post('/auth/login/', credentials)
  },

  // 用户注册
  register: (userData: {
    username: string
    email: string
    password: string
    nickname?: string
  }) => {
    return api.post('/auth/register/', userData)
  },

  // 用户登出
  logout: () => {
    return api.post('/auth/logout/')
  },

  // 获取用户信息
  getUserInfo: () => {
    return api.get('/auth/user/')
  },

  // 更新用户资料
  updateProfile: (profileData: Partial<User>) => {
    return api.put('/auth/profile/', profileData)
  },

  // 修改密码
  changePassword: (passwordData: {
    old_password: string
    new_password: string
  }) => {
    return api.post('/auth/password/change/', passwordData)
  },

  // 重置密码
  resetPassword: (email: string) => {
    return api.post('/auth/password/reset/', { email })
  }
}

// 用户相关API
export const userApi = {
  // 获取用户详情
  getUserDetail: (userId: number) => {
    return api.get(`/users/${userId}/`)
  },

  // 搜索用户
  searchUsers: (query: string) => {
    return api.get('/users/search/', { params: { q: query } })
  },

  // 关注用户
  followUser: (userId: number) => {
    return api.post(`/users/${userId}/follow/`)
  },

  // 取消关注
  unfollowUser: (userId: number) => {
    return api.post(`/users/${userId}/unfollow/`)
  },

  // 获取粉丝列表
  getFollowers: (userId: number) => {
    return api.get(`/users/${userId}/followers/`)
  },

  // 获取关注列表
  getFollowing: (userId: number) => {
    return api.get(`/users/${userId}/following/`)
  }
}