import api from './index'

// 上传相关API
export const uploadApi = {
  // 上传单张图片
  uploadImage: (file: File, onProgress?: (progressEvent: ProgressEvent) => void) => {
    const formData = new FormData()
    formData.append('image', file)
    
    return api.post('/upload/image/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
    })
  },

  // 批量上传图片
  uploadImages: (files: File[], onProgress?: (progressEvent: ProgressEvent) => void) => {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('images', file)
    })
    
    return api.post('/upload/images/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
    })
  },

  // 上传头像
  uploadAvatar: (file: File) => {
    const formData = new FormData()
    formData.append('avatar', file)
    
    return api.post('/upload/avatar/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 上传贴吧头像
  uploadTiebaAvatar: (file: File, tiebaId: number) => {
    const formData = new FormData()
    formData.append('avatar', file)
    formData.append('tieba_id', tiebaId.toString())
    
    return api.post('/upload/tieba/avatar/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 上传贴吧横幅
  uploadTiebaBanner: (file: File, tiebaId: number) => {
    const formData = new FormData()
    formData.append('banner', file)
    formData.append('tieba_id', tiebaId.toString())
    
    return api.post('/upload/tieba/banner/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 上传附件
  uploadAttachment: (file: File) => {
    const formData = new FormData()
    formData.append('attachment', file)
    
    return api.post('/upload/attachment/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 删除上传的文件
  deleteFile: (fileUrl: string) => {
    return api.delete('/upload/file/', { 
      data: { url: fileUrl } 
    })
  },

  // 获取上传配置
  getUploadConfig: () => {
    return api.get('/upload/config/')
  }
}

export default uploadApi