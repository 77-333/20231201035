// 贴吧相关类型定义
export interface Category {
  id: number
  name: string
  description: string
  icon?: string
  tieba_count: number
  created_at: string
}

export interface Tieba {
  id: number
  name: string
  description: string
  avatar?: string
  banner?: string
  category: Category
  creator: User
  member_count: number
  post_count: number
  today_post_count: number
  is_official: boolean
  is_private: boolean
  is_joined: boolean
  created_at: string
  updated_at: string
}

export interface TiebaMember {
  id: number
  user: User
  tieba: Tieba
  role: 'member' | 'moderator' | 'admin'
  joined_at: string
  post_count: number
  comment_count: number
}

export interface TiebaAnnouncement {
  id: number
  title: string
  content: string
  author: User
  tieba: Tieba
  is_pinned: boolean
  created_at: string
  updated_at: string
}

export interface TiebaSearchResult {
  tiebas: Tieba[]
  total_count: number
  page: number
  page_size: number
}

// 帖子相关类型定义
export interface Post {
  id: number
  title: string
  content: string
  author: User
  tieba: Tieba
  is_anonymous: boolean
  is_essence: boolean
  is_pinned: boolean
  is_locked: boolean
  view_count: number
  like_count: number
  comment_count: number
  collect_count: number
  is_liked: boolean
  is_collected: boolean
  images?: string[]
  attachments?: string[]
  created_at: string
  updated_at: string
}

export interface PostCreateData {
  title: string
  content: string
  tieba: number
  is_anonymous?: boolean
  images?: File[]
  attachments?: File[]
}

export interface PostUpdateData {
  title?: string
  content?: string
  is_anonymous?: boolean
}

export interface PostSearchResult {
  posts: Post[]
  total_count: number
  page: number
  page_size: number
}

// 评论相关类型定义
export interface Comment {
  id: number
  content: string
  author: User
  post: Post
  parent?: Comment
  is_anonymous: boolean
  like_count: number
  reply_count: number
  is_liked: boolean
  images?: string[]
  created_at: string
  updated_at: string
}

export interface CommentCreateData {
  content: string
  post: number
  parent_id?: number
  is_anonymous?: boolean
  images?: File[]
}

export interface CommentUpdateData {
  content?: string
  is_anonymous?: boolean
}

export interface CommentSearchResult {
  comments: Comment[]
  total_count: number
  page: number
  page_size: number
}

// 互动相关类型定义
export interface Like {
  id: number
  user: User
  content_type: 'post' | 'comment'
  object_id: number
  created_at: string
}

export interface Collection {
  id: number
  user: User
  post: Post
  created_at: string
}

export interface Report {
  id: number
  reporter: User
  content_type: 'post' | 'comment'
  object_id: number
  reason: string
  description?: string
  status: 'pending' | 'processing' | 'resolved' | 'rejected'
  created_at: string
  updated_at: string
}

// 分页相关类型定义
export interface PaginationParams {
  page?: number
  page_size?: number
}

export interface PaginatedResponse<T> {
  results: T[]
  count: number
  next: string | null
  previous: string | null
}