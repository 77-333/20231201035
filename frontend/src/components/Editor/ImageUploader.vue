<template>
  <div class="image-uploader">
    <!-- 上传区域 -->
    <div 
      class="upload-area"
      :class="{ 
        'drag-over': isDragOver, 
        'has-images': uploadedImages.length > 0 
      }"
      @click="triggerFileInput"
      @drop="handleDrop"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
    >
      <input 
        ref="fileInput" 
        type="file" 
        accept="image/*" 
        multiple 
        @change="handleFileSelect"
        style="display: none"
      />
      
      <div v-if="uploadedImages.length === 0" class="upload-placeholder">
        <i class="upload-icon">📁</i>
        <p class="upload-text">点击选择图片或拖拽图片到这里</p>
        <p class="upload-hint">支持 JPG、PNG、GIF 格式，单张图片最大 5MB</p>
      </div>
      
      <div v-else class="images-preview">
        <div 
          v-for="(image, index) in uploadedImages" 
          :key="image.id" 
          class="preview-item"
        >
          <img :src="image.preview" :alt="image.file.name" />
          <div class="preview-overlay">
            <button @click.stop="removeImage(index)" class="remove-btn">
              <i class="icon">×</i>
            </button>
            <button @click.stop="viewImage(image.preview)" class="view-btn">
              <i class="icon">👁️</i>
            </button>
          </div>
          <div class="upload-progress" v-if="image.uploading">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: image.progress + '%' }"
              ></div>
            </div>
            <span class="progress-text">{{ image.progress }}%</span>
          </div>
          <div v-else-if="image.error" class="upload-error">
            <span class="error-text">上传失败</span>
            <button @click.stop="retryUpload(index)" class="retry-btn">重试</button>
          </div>
        </div>
        
        <!-- 添加更多图片按钮 -->
        <div class="add-more" @click.stop="triggerFileInput">
          <i class="add-icon">+</i>
          <span>添加图片</span>
        </div>
      </div>
    </div>
    
    <!-- 图片预览模态框 -->
    <div v-if="showPreviewModal" class="preview-modal">
      <div class="modal-overlay" @click="closePreview">
        <div class="modal-content" @click.stop>
          <button @click="closePreview" class="close-btn">×</button>
          <img :src="previewImageUrl" class="preview-image" />
        </div>
      </div>
    </div>
    
    <!-- 上传控制 -->
    <div v-if="uploadedImages.length > 0" class="upload-controls">
      <div class="controls-left">
        <span class="images-count">已选择 {{ uploadedImages.length }} 张图片</span>
        <span class="upload-status" v-if="uploadingCount > 0">
          上传中: {{ uploadingCount }}/{{ uploadedImages.length }}
        </span>
        <span class="upload-status success" v-else-if="uploadedCount > 0">
          上传完成: {{ uploadedCount }}/{{ uploadedImages.length }}
        </span>
      </div>
      
      <div class="controls-right">
        <button 
          @click="clearAll" 
          class="btn-clear"
          :disabled="uploadingCount > 0"
        >
          清空
        </button>
        <button 
          @click="startUpload" 
          class="btn-upload"
          :disabled="uploadingCount > 0 || uploadedImages.length === 0"
        >
          {{ uploadingCount > 0 ? '上传中...' : '开始上传' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { uploadApi } from '@/api/upload'

interface ImageInfo {
  id: string
  file: File
  preview: string
  uploading: boolean
  progress: number
  error: boolean
  url?: string
}

interface Props {
  maxFiles?: number
  maxSize?: number // MB
  autoUpload?: boolean
}

interface Emits {
  (e: 'upload-complete', urls: string[]): void
  (e: 'upload-progress', progress: number): void
  (e: 'upload-error', error: Error): void
}

const props = withDefaults(defineProps<Props>(), {
  maxFiles: 10,
  maxSize: 5,
  autoUpload: false
})

const emit = defineEmits<Emits>()

// DOM 引用
const fileInput = ref<HTMLInputElement>()

// 状态
const uploadedImages = ref<ImageInfo[]>([])
const isDragOver = ref(false)
const showPreviewModal = ref(false)
const previewImageUrl = ref('')

// 计算属性
const uploadingCount = computed(() => {
  return uploadedImages.value.filter(img => img.uploading).length
})

const uploadedCount = computed(() => {
  return uploadedImages.value.filter(img => img.url && !img.uploading && !img.error).length
})

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value?.click()
}

// 处理文件选择
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files) return
  
  const files = Array.from(target.files)
  processFiles(files)
  
  // 清空文件输入，允许重复选择相同文件
  target.value = ''
}

// 处理拖拽
const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (event: DragEvent) => {
  event.preventDefault()
  isDragOver.value = false
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  isDragOver.value = false
  
  const files = Array.from(event.dataTransfer?.files || [])
  processFiles(files)
}

// 处理文件
const processFiles = (files: File[]) => {
  const validFiles: File[] = []
  
  for (const file of files) {
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      alert(`文件 "${file.name}" 不是图片格式`)
      continue
    }
    
    // 检查文件大小
    const maxSizeBytes = props.maxSize * 1024 * 1024
    if (file.size > maxSizeBytes) {
      alert(`文件 "${file.name}" 超过 ${props.maxSize}MB 限制`)
      continue
    }
    
    // 检查文件数量限制
    if (uploadedImages.value.length + validFiles.length >= props.maxFiles) {
      alert(`最多只能上传 ${props.maxFiles} 张图片`)
      break
    }
    
    validFiles.push(file)
  }
  
  // 处理有效的文件
  validFiles.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const imageInfo: ImageInfo = {
        id: generateId(),
        file,
        preview: e.target?.result as string,
        uploading: false,
        progress: 0,
        error: false
      }
      
      uploadedImages.value.push(imageInfo)
      
      // 如果启用自动上传，立即开始上传
      if (props.autoUpload) {
        uploadImage(imageInfo)
      }
    }
    reader.readAsDataURL(file)
  })
}

// 移除图片
const removeImage = (index: number) => {
  uploadedImages.value.splice(index, 1)
}

// 查看图片
const viewImage = (url: string) => {
  previewImageUrl.value = url
  showPreviewModal.value = true
}

// 关闭预览
const closePreview = () => {
  showPreviewModal.value = false
  previewImageUrl.value = ''
}

// 重试上传
const retryUpload = (index: number) => {
  const image = uploadedImages.value[index]
  image.error = false
  image.progress = 0
  uploadImage(image)
}

// 开始上传
const startUpload = async () => {
  for (const image of uploadedImages.value) {
    if (!image.url && !image.uploading && !image.error) {
      await uploadImage(image)
    }
  }
  
  // 检查是否所有图片都上传完成
  const allUploaded = uploadedImages.value.every(img => img.url || img.error)
  if (allUploaded) {
    const urls = uploadedImages.value
      .filter(img => img.url)
      .map(img => img.url!) 
    
    emit('upload-complete', urls)
  }
}

// 上传单个图片
const uploadImage = async (image: ImageInfo) => {
  image.uploading = true
  image.progress = 0
  
  try {
    // 模拟上传进度（实际应用中应该使用真实的进度事件）
    const progressInterval = setInterval(() => {
      if (image.progress < 90) {
        image.progress += 10
      }
    }, 200)
    
    // 调用上传API
    const response = await uploadApi.uploadImage(image.file, (progressEvent) => {
      if (progressEvent.lengthComputable) {
        const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100)
        image.progress = progress
      }
    })
    
    clearInterval(progressInterval)
    image.progress = 100
    image.url = response.data.url
    
    // 更新总进度
    updateOverallProgress()
    
  } catch (error) {
    console.error('图片上传失败:', error)
    image.error = true
    image.uploading = false
    emit('upload-error', error as Error)
  } finally {
    image.uploading = false
  }
}

// 更新总进度
const updateOverallProgress = () => {
  const totalImages = uploadedImages.value.length
  const uploadedImagesCount = uploadedImages.value.filter(img => img.url).length
  const progress = Math.round((uploadedImagesCount / totalImages) * 100)
  
  emit('upload-progress', progress)
}

// 清空所有图片
const clearAll = () => {
  uploadedImages.value = []
}

// 工具函数
const generateId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

// 公共方法
defineExpose({
  getUploadedUrls: () => {
    return uploadedImages.value
      .filter(img => img.url)
      .map(img => img.url!)
  },
  clearAll: () => {
    uploadedImages.value = []
  },
  addFiles: (files: File[]) => {
    processFiles(files)
  }
})
</script>

<style scoped>
.image-uploader {
  width: 100%;
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: #1890ff;
  background: #f0f8ff;
}

.upload-area.drag-over {
  border-color: #1890ff;
  background: #e6f7ff;
  transform: scale(1.02);
}

.upload-area.has-images {
  padding: 16px;
  min-height: auto;
  justify-content: flex-start;
}

.upload-placeholder {
  color: #666;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 12px;
  display: block;
}

.upload-text {
  font-size: 16px;
  margin: 0 0 8px 0;
  font-weight: 500;
}

.upload-hint {
  font-size: 14px;
  margin: 0;
  color: #999;
}

.images-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  width: 100%;
}

.preview-item {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #f0f0f0;
  background: white;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.preview-item:hover .preview-overlay {
  opacity: 1;
}

.remove-btn,
.view-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 4px;
  font-size: 16px;
  transition: all 0.2s;
}

.remove-btn:hover {
  background: #ff4d4f;
  color: white;
}

.view-btn:hover {
  background: #1890ff;
  color: white;
}

.upload-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  font-size: 12px;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 2px;
}

.progress-fill {
  height: 100%;
  background: #52c41a;
  transition: width 0.3s;
}

.progress-text {
  font-size: 10px;
}

.upload-error {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 77, 79, 0.9);
  color: white;
  padding: 4px 8px;
  font-size: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.retry-btn {
  background: white;
  color: #ff4d4f;
  border: none;
  border-radius: 2px;
  padding: 2px 6px;
  font-size: 10px;
  cursor: pointer;
}

.add-more {
  width: 100px;
  height: 100px;
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
}

.add-more:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.add-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

/* 预览模态框 */
.preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
}

.modal-overlay {
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.close-btn {
  position: absolute;
  top: -40px;
  right: -40px;
  width: 32px;
  height: 32px;
  border: none;
  background: white;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

/* 上传控制 */
.upload-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding: 12px 16px;
  background: #f5f5f5;
  border-radius: 6px;
}

.controls-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.images-count {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.upload-status {
  font-size: 12px;
  color: #666;
}

.upload-status.success {
  color: #52c41a;
}

.controls-right {
  display: flex;
  gap: 8px;
}

.btn-clear,
.btn-upload {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-clear {
  background: white;
  color: #666;
}

.btn-clear:hover:not(:disabled) {
  border-color: #ff4d4f;
  color: #ff4d4f;
}

.btn-upload {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

.btn-upload:hover:not(:disabled) {
  background: #40a9ff;
  border-color: #40a9ff;
}

.btn-clear:disabled,
.btn-upload:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .upload-area {
    padding: 16px;
  }
  
  .preview-item {
    width: 80px;
    height: 80px;
  }
  
  .add-more {
    width: 80px;
    height: 80px;
  }
  
  .upload-controls {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .controls-right {
    justify-content: space-between;
  }
  
  .close-btn {
    top: -30px;
    right: -30px;
  }
}
</style>