// 用户相关类型定义
export interface User {
  id: number
  username: string
  email: string
  nickname: string
  avatar?: string
  bio?: string
  level: number
  experience: number
  is_active: boolean
  date_joined: string
  last_login?: string
  followers_count: number
  following_count: number
  posts_count: number
  comments_count: number
}

export interface UserProfile extends User {
  phone?: string
  gender?: 'male' | 'female' | 'other'
  birthday?: string
  location?: string
  website?: string
  social_links?: {
    wechat?: string
    qq?: string
    weibo?: string
    github?: string
  }
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  nickname?: string
}

export interface PasswordChangeData {
  old_password: string
  new_password: string
}

export interface UserStats {
  total_posts: number
  total_comments: number
  total_likes: number
  total_collections: number
  total_followers: number
  total_following: number
}

export interface FollowRelationship {
  id: number
  follower: User
  following: User
  created_at: string
}

export interface UserSearchResult {
  users: User[]
  total_count: number
  page: number
  page_size: number
}