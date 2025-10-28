import api from './index'

// 搜索相关API
export const searchApi = {
  // 综合搜索
  searchAll: (params: {
    keyword: string
    page?: number
    size?: number
    sort?: 'relevance' | 'latest' | 'hot'
  }) => {
    return api.get('/search/all/', { params })
  },

  // 搜索帖子
  searchPosts: (params: {
    keyword: string
    page?: number
    size?: number
    sort?: 'relevance' | 'latest' | 'hot'
    tieba?: number
    author?: number
  }) => {
    return api.get('/search/posts/', { params })
  },

  // 搜索贴吧
  searchTieba: (params: {
    keyword: string
    page?: number
    size?: number
    category?: number
  }) => {
    return api.get('/search/tieba/', { params })
  },

  // 搜索用户
  searchUsers: (params: {
    keyword: string
    page?: number
    size?: number
  }) => {
    return api.get('/search/users/', { params })
  },

  // 获取搜索建议
  getSuggestions: (keyword: string) => {
    return api.get('/search/suggestions/', { 
      params: { q: keyword } 
    })
  },

  // 获取热门搜索
  getHotSearches: () => {
    return api.get('/search/hot/')
  },

  // 获取搜索历史
  getSearchHistory: () => {
    return api.get('/search/history/')
  },

  // 清空搜索历史
  clearSearchHistory: () => {
    return api.delete('/search/history/')
  },

  // 获取相关搜索
  getRelatedSearches: (keyword: string) => {
    return api.get('/search/related/', { 
      params: { q: keyword } 
    })
  }
}

export default searchApi