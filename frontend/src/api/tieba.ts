import api from './index'

// 贴吧相关API
export const tiebaApi = {
  // 获取分类列表
  getCategories: () => {
    return api.get('/tieba/categories/')
  },

  // 获取贴吧列表
  getTiebaList: (params?: {
    q?: string
    category?: number
    page?: number
    page_size?: number
  }) => {
    return api.get('/tieba/tiebas/', { params })
  },

  // 获取贴吧详情
  getTiebaDetail: (tiebaId: number) => {
    return api.get(`/tieba/tiebas/${tiebaId}/`)
  },

  // 创建贴吧
  createTieba: (tiebaData: {
    name: string
    description: string
    category: number
    avatar?: File
    banner?: File
  }) => {
    const formData = new FormData()
    Object.entries(tiebaData).forEach(([key, value]) => {
      if (value !== undefined) {
        formData.append(key, value)
      }
    })
    return api.post('/tieba/tiebas/create/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 加入贴吧
  joinTieba: (tiebaId: number) => {
    return api.post(`/tieba/tiebas/${tiebaId}/join/`)
  },

  // 离开贴吧
  leaveTieba: (tiebaId: number) => {
    return api.post(`/tieba/tiebas/${tiebaId}/leave/`)
  },

  // 获取贴吧成员列表
  getTiebaMembers: (tiebaId: number, params?: { page?: number; page_size?: number }) => {
    return api.get(`/tieba/tiebas/${tiebaId}/members/`, { params })
  },

  // 获取贴吧公告
  getTiebaAnnouncements: (tiebaId: number) => {
    return api.get(`/tieba/tiebas/${tiebaId}/announcements/`)
  },

  // 获取推荐贴吧
  getRecommendedTiebas: () => {
    return api.get('/tieba/recommended/')
  },

  // 获取热门贴吧
  getHotTiebas: () => {
    return api.get('/tieba/hot/')
  },

  // 搜索贴吧
  searchTiebas: (query: string) => {
    return api.get('/tieba/search/', { params: { q: query } })
  }
}

// 帖子相关API
export const postApi = {
  // 获取帖子列表
  getPostList: (params?: {
    tieba?: number
    author?: number
    q?: string
    sort?: 'latest' | 'hot' | 'essence'
    page?: number
    page_size?: number
  }) => {
    return api.get('/posts/posts/', { params })
  },

  // 获取帖子详情
  getPostDetail: (postId: number) => {
    return api.get(`/posts/posts/${postId}/`)
  },

  // 创建帖子
  createPost: (postData: {
    title: string
    content: string
    tieba: number
    is_anonymous?: boolean
    images?: File[]
    attachments?: File[]
  }) => {
    const formData = new FormData()
    Object.entries(postData).forEach(([key, value]) => {
      if (value !== undefined) {
        if (Array.isArray(value)) {
          value.forEach(file => formData.append(key, file))
        } else {
          formData.append(key, value)
        }
      }
    })
    return api.post('/posts/posts/create/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 更新帖子
  updatePost: (postId: number, postData: {
    title?: string
    content?: string
    is_anonymous?: boolean
  }) => {
    return api.put(`/posts/posts/${postId}/update/`, postData)
  },

  // 删除帖子
  deletePost: (postId: number) => {
    return api.delete(`/posts/posts/${postId}/delete/`)
  },

  // 点赞帖子
  likePost: (postId: number) => {
    return api.post(`/posts/posts/${postId}/like/`)
  },

  // 收藏帖子
  collectPost: (postId: number) => {
    return api.post(`/posts/posts/${postId}/collect/`)
  },

  // 举报帖子
  reportPost: (postId: number, reportData: {
    reason: string
    description?: string
  }) => {
    return api.post(`/posts/posts/${postId}/report/`, reportData)
  },

  // 获取热门帖子
  getHotPosts: () => {
    return api.get('/posts/hot/')
  },

  // 获取推荐帖子
  getRecommendedPosts: () => {
    return api.get('/posts/recommended/')
  },

  // 获取用户浏览历史
  getUserPostHistory: (params?: { page?: number; page_size?: number }) => {
    return api.get('/posts/user/history/', { params })
  }
}

// 评论相关API
export const commentApi = {
  // 获取评论列表
  getCommentList: (postId: number, params?: { page?: number; page_size?: number }) => {
    return api.get(`/comments/posts/${postId}/comments/`, { params })
  },

  // 创建评论
  createComment: (commentData: {
    content: string
    post: number
    parent_id?: number
    is_anonymous?: boolean
    images?: File[]
  }) => {
    const formData = new FormData()
    Object.entries(commentData).forEach(([key, value]) => {
      if (value !== undefined) {
        if (Array.isArray(value)) {
          value.forEach(file => formData.append(key, file))
        } else {
          formData.append(key, value)
        }
      }
    })
    return api.post('/comments/comments/create/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 获取评论详情
  getCommentDetail: (commentId: number) => {
    return api.get(`/comments/comments/${commentId}/`)
  },

  // 更新评论
  updateComment: (commentId: number, commentData: {
    content?: string
    is_anonymous?: boolean
  }) => {
    return api.put(`/comments/comments/${commentId}/update/`, commentData)
  },

  // 删除评论
  deleteComment: (commentId: number) => {
    return api.delete(`/comments/comments/${commentId}/delete/`)
  },

  // 点赞评论
  likeComment: (commentId: number) => {
    return api.post(`/comments/comments/${commentId}/like/`)
  },

  // 举报评论
  reportComment: (commentId: number, reportData: {
    reason: string
    description?: string
  }) => {
    return api.post(`/comments/comments/${commentId}/report/`, reportData)
  },

  // 获取评论回复
  getCommentReplies: (commentId: number, params?: { page?: number; page_size?: number }) => {
    return api.get(`/comments/comments/${commentId}/replies/`, { params })
  },

  // 获取用户评论
  getUserComments: (params?: { page?: number; page_size?: number }) => {
    return api.get('/comments/user/comments/', { params })
  },

  // 搜索评论
  searchComments: (query: string) => {
    return api.get('/comments/comments/search/', { params: { q: query } })
  }
}