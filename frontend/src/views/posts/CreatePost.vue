<template>
  <div class="create-post-page">
    <div class="container">
      <!-- 页面头部 -->
      <div class="page-header">
        <h1>创建新帖子</h1>
        <div class="header-actions">
          <button @click="goBack" class="btn-back">
            <i class="icon">←</i> 返回
          </button>
          <button 
            @click="saveDraft" 
            class="btn-draft"
            :disabled="saving"
          >
            {{ saving ? '保存中...' : '保存草稿' }}
          </button>
          <button 
            @click="publishPost" 
            class="btn-publish"
            :disabled="!canPublish || publishing"
          >
            {{ publishing ? '发布中...' : '发布帖子' }}
          </button>
        </div>
      </div>
      
      <!-- 主要内容区域 -->
      <div class="post-content">
        <!-- 贴吧选择 -->
        <div class="form-section">
          <label class="form-label">选择贴吧 *</label>
          <div class="tieba-selector">
            <select v-model="selectedTieba" @change="onTiebaChange" class="tieba-select">
              <option value="">请选择贴吧</option>
              <option 
                v-for="tieba in joinedTiebas" 
                :key="tieba.id" 
                :value="tieba.id"
              >
                {{ tieba.name }}
              </option>
            </select>
            <div v-if="selectedTiebaInfo" class="tieba-info">
              <img :src="selectedTiebaInfo.avatar" :alt="selectedTiebaInfo.name" />
              <span>{{ selectedTiebaInfo.name }}</span>
            </div>
          </div>
        </div>
        
        <!-- 帖子标题 -->
        <div class="form-section">
          <label class="form-label">帖子标题 *</label>
          <input 
            v-model="postTitle" 
            type="text" 
            placeholder="请输入帖子标题"
            maxlength="100"
            class="title-input"
          />
          <div class="char-count">{{ postTitle.length }}/100</div>
        </div>
        
        <!-- 帖子内容 -->
        <div class="form-section">
          <label class="form-label">帖子内容 *</label>
          <RichTextEditor
            v-model="postContent"
            :placeholder="'请输入帖子内容...'"
            :height="'400px'"
            :max-length="5000"
            @change="onContentChange"
            class="content-editor"
          />
          <div class="char-count">{{ contentTextLength }}/5000</div>
        </div>
        
        <!-- 图片上传 -->
        <div class="form-section">
          <label class="form-label">添加图片</label>
          <ImageUploader
            ref="imageUploader"
            :max-files="10"
            :max-size="5"
            @upload-complete="onImagesUploaded"
            @upload-error="onUploadError"
            class="image-uploader"
          />
        </div>
        
        <!-- 帖子设置 -->
        <div class="form-section">
          <label class="form-label">帖子设置</label>
          <div class="post-settings">
            <label class="setting-item">
              <input 
                v-model="isAnonymous" 
                type="checkbox" 
                class="setting-checkbox"
              />
              <span class="setting-label">匿名发帖</span>
            </label>
            
            <label class="setting-item">
              <input 
                v-model="enableComments" 
                type="checkbox" 
                class="setting-checkbox"
                checked
              />
              <span class="setting-label">允许评论</span>
            </label>
            
            <label class="setting-item">
              <input 
                v-model="isTop" 
                type="checkbox" 
                class="setting-checkbox"
              />
              <span class="setting-label">置顶帖子</span>
            </label>
          </div>
        </div>
        
        <!-- 标签 -->
        <div class="form-section">
          <label class="form-label">添加标签</label>
          <div class="tags-input">
            <input 
              v-model="tagInput" 
              type="text" 
              placeholder="输入标签后按回车添加"
              @keydown.enter="addTag"
              class="tag-input"
            />
            <div class="tags-list">
              <span 
                v-for="(tag, index) in tags" 
                :key="index" 
                class="tag"
              >
                {{ tag }}
                <button @click="removeTag(index)" class="tag-remove">×</button>
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 预览区域 -->
      <div v-if="showPreview" class="preview-section">
        <h3>预览</h3>
        <div class="preview-content">
          <div class="preview-header">
            <h2>{{ postTitle || '无标题' }}</h2>
            <div class="preview-meta">
              <span>发布于 {{ formatTime(new Date()) }}</span>
              <span v-if="selectedTiebaInfo">在 {{ selectedTiebaInfo.name }}</span>
            </div>
          </div>
          <div 
            class="preview-body" 
            v-html="postContent || '<p>无内容</p>'"
          ></div>
          <div v-if="uploadedImages.length > 0" class="preview-images">
            <h4>图片预览</h4>
            <div class="images-grid">
              <img 
                v-for="(image, index) in uploadedImages" 
                :key="index" 
                :src="image" 
                :alt="'图片' + (index + 1)"
                class="preview-image"
              />
            </div>
          </div>
        </div>
      </div>
      
      <!-- 底部操作栏 -->
      <div class="footer-actions">
        <button 
          @click="togglePreview" 
          class="btn-preview"
        >
          {{ showPreview ? '隐藏预览' : '显示预览' }}
        </button>
        <div class="action-buttons">
          <button @click="resetForm" class="btn-reset">重置</button>
          <button @click="saveDraft" class="btn-draft">保存草稿</button>
          <button 
            @click="publishPost" 
            class="btn-publish"
            :disabled="!canPublish || publishing"
          >
            {{ publishing ? '发布中...' : '发布帖子' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 发布成功提示 -->
    <div v-if="showSuccess" class="success-modal">
      <div class="modal-content">
        <div class="success-icon">✅</div>
        <h3>发布成功！</h3>
        <p>您的帖子已成功发布到贴吧</p>
        <div class="modal-actions">
          <button @click="viewPost" class="btn-view">查看帖子</button>
          <button @click="createNew" class="btn-new">继续发帖</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGlobalStore } from '@/stores/global'
import { tiebaApi, postApi } from '@/api/tieba'
import { uploadApi } from '@/api/upload'
import RichTextEditor from '@/components/Editor/RichTextEditor.vue'
import ImageUploader from '@/components/Editor/ImageUploader.vue'
import type { Tieba } from '@/types'

const route = useRoute()
const router = useRouter()
const globalStore = useGlobalStore()

// 表单数据
const selectedTieba = ref('')
const postTitle = ref('')
const postContent = ref('')
const tags = ref<string[]>([])
const tagInput = ref('')
const uploadedImages = ref<string[]>([])

// 设置选项
const isAnonymous = ref(false)
const enableComments = ref(true)
const isTop = ref(false)

// 状态
const joinedTiebas = ref<Tieba[]>([])
const selectedTiebaInfo = ref<Tieba | null>(null)
const showPreview = ref(false)
const showSuccess = ref(false)
const saving = ref(false)
const publishing = ref(false)

// 计算属性
const contentTextLength = computed(() => {
  // 简单的文本长度计算（去除HTML标签）
  return postContent.value.replace(/<[^>]*>/g, '').length
})

const canPublish = computed(() => {
  return selectedTieba.value && 
         postTitle.value.trim().length > 0 && 
         postContent.value.trim().length > 0 &&
         contentTextLength.value <= 5000
})

// 生命周期
onMounted(async () => {
  await loadJoinedTiebas()
  
  // 如果有贴吧ID参数，预选贴吧
  if (route.query.tieba) {
    selectedTieba.value = route.query.tieba as string
    onTiebaChange()
  }
})

// 加载已加入的贴吧
const loadJoinedTiebas = async () => {
  try {
    const response = await tiebaApi.getTiebaList({ 
      page: 1, 
      page_size: 100 
    })
    joinedTiebas.value = response.data.results || []
  } catch (error) {
    console.error('加载贴吧列表失败:', error)
  }
}

// 贴吧选择变化
const onTiebaChange = () => {
  if (selectedTieba.value) {
    selectedTiebaInfo.value = joinedTiebas.value.find(
      tieba => tieba.id.toString() === selectedTieba.value
    ) || null
  } else {
    selectedTiebaInfo.value = null
  }
}

// 内容变化
const onContentChange = (content: string) => {
  postContent.value = content
}

// 图片上传完成
const onImagesUploaded = (urls: string[]) => {
  uploadedImages.value = urls
}

// 上传错误处理
const onUploadError = (error: Error) => {
  console.error('图片上传失败:', error)
  // 可以添加错误提示
}

// 添加标签
const addTag = () => {
  const tag = tagInput.value.trim()
  if (tag && !tags.value.includes(tag)) {
    tags.value.push(tag)
    tagInput.value = ''
  }
}

// 移除标签
const removeTag = (index: number) => {
  tags.value.splice(index, 1)
}

// 切换预览
const togglePreview = () => {
  showPreview.value = !showPreview.value
}

// 保存草稿
const saveDraft = async () => {
  if (!canPublish.value) {
    alert('请填写完整的帖子信息')
    return
  }
  
  saving.value = true
  
  try {
    // 这里可以调用保存草稿的API
    const draftData = {
      tieba: parseInt(selectedTieba.value),
      title: postTitle.value,
      content: postContent.value,
      tags: tags.value,
      images: uploadedImages.value,
      is_anonymous: isAnonymous.value,
      enable_comments: enableComments.value,
      is_top: isTop.value
    }
    
    // 模拟保存草稿
    console.log('保存草稿:', draftData)
    alert('草稿保存成功！')
    
  } catch (error) {
    console.error('保存草稿失败:', error)
    alert('保存草稿失败，请重试')
  } finally {
    saving.value = false
  }
}

// 发布帖子
const publishPost = async () => {
  if (!canPublish.value) {
    alert('请填写完整的帖子信息')
    return
  }
  
  publishing.value = true
  
  try {
    const postData = {
      tieba: parseInt(selectedTieba.value),
      title: postTitle.value,
      content: postContent.value,
      tags: tags.value,
      images: uploadedImages.value,
      is_anonymous: isAnonymous.value,
      enable_comments: enableComments.value,
      is_top: isTop.value
    }
    
    // 调用发布API
    const response = await postApi.createPost(postData)
    
    // 显示成功提示
    showSuccess.value = true
    
  } catch (error) {
    console.error('发布帖子失败:', error)
    alert('发布帖子失败，请重试')
  } finally {
    publishing.value = false
  }
}

// 查看发布的帖子
const viewPost = () => {
  // 这里应该跳转到发布的帖子页面
  router.push('/tieba')
}

// 创建新帖子
const createNew = () => {
  resetForm()
  showSuccess.value = false
}

// 重置表单
const resetForm = () => {
  selectedTieba.value = ''
  postTitle.value = ''
  postContent.value = ''
  tags.value = []
  tagInput.value = ''
  uploadedImages.value = []
  isAnonymous.value = false
  enableComments.value = true
  isTop.value = false
  showPreview.value = false
}

// 返回
const goBack = () => {
  router.go(-1)
}

// 格式化时间
const formatTime = (date: Date) => {
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.create-post-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px 0;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-back,
.btn-draft,
.btn-publish {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back {
  background: white;
  color: #666;
}

.btn-back:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.btn-draft {
  background: #f5f5f5;
  color: #666;
}

.btn-draft:hover:not(:disabled) {
  background: #e6f7ff;
  border-color: #1890ff;
  color: #1890ff;
}

.btn-publish {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

.btn-publish:hover:not(:disabled) {
  background: #40a9ff;
  border-color: #40a9ff;
}

.btn-publish:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.post-content {
  padding: 24px;
}

.form-section {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.tieba-selector {
  display: flex;
  gap: 12px;
  align-items: center;
}

.tieba-select {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.tieba-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.tieba-info img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.title-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 16px;
  outline: none;
}

.title-input:focus {
  border-color: #1890ff;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.content-editor {
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}

.image-uploader {
  margin-top: 8px;
}

.post-settings {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.setting-checkbox {
  width: 16px;
  height: 16px;
}

.setting-label {
  font-size: 14px;
  color: #666;
}

.tags-input {
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  padding: 8px;
}

.tag-input {
  width: 100%;
  border: none;
  outline: none;
  font-size: 14px;
  padding: 4px 0;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.tag {
  display: inline-flex;
  align-items: center;
  background: #e6f7ff;
  color: #1890ff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.tag-remove {
  margin-left: 4px;
  border: none;
  background: none;
  color: #1890ff;
  cursor: pointer;
  font-size: 14px;
}

.preview-section {
  padding: 24px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.preview-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
}

.preview-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.preview-header {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.preview-header h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #333;
}

.preview-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #999;
}

.preview-body {
  line-height: 1.6;
  color: #333;
}

.preview-images {
  margin-top: 20px;
}

.preview-images h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #333;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
}

.preview-image {
  width: 100%;
  height: 100px;
  object-fit: cover;
  border-radius: 4px;
}

.footer-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn-preview,
.btn-reset {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  background: white;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-preview:hover,
.btn-reset:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.success-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 32px;
  text-align: center;
  min-width: 300px;
}

.success-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.modal-content h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #333;
}

.modal-content p {
  margin: 0 0 24px 0;
  color: #666;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn-view,
.btn-new {
  padding: 8px 16px;
  border: 1px solid #1890ff;
  background: white;
  color: #1890ff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-view {
  background: #1890ff;
  color: white;
}

.btn-view:hover {
  background: #40a9ff;
  border-color: #40a9ff;
}

.btn-new:hover {
  background: #e6f7ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    margin: 0 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .footer-actions {
    flex-direction: column;
    gap: 16px;
  }
  
  .action-buttons {
    width: 100%;
    justify-content: space-between;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .btn-view,
  .btn-new {
    width: 100%;
  }
}
</style>