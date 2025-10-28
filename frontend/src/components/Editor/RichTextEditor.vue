<template>
  <div class="rich-text-editor">
    <!-- 工具栏 -->
    <div class="toolbar">
      <!-- 文本格式 -->
      <div class="tool-group">
        <button 
          type="button" 
          class="tool-btn" 
          :class="{ active: activeFormat.bold }"
          @click="toggleFormat('bold')"
          title="粗体"
        >
          <i class="icon">B</i>
        </button>
        <button 
          type="button" 
          class="tool-btn" 
          :class="{ active: activeFormat.italic }"
          @click="toggleFormat('italic')"
          title="斜体"
        >
          <i class="icon">I</i>
        </button>
        <button 
          type="button" 
          class="tool-btn" 
          :class="{ active: activeFormat.underline }"
          @click="toggleFormat('underline')"
          title="下划线"
        >
          <i class="icon">U</i>
        </button>
        <button 
          type="button" 
          class="tool-btn" 
          :class="{ active: activeFormat.strikethrough }"
          @click="toggleFormat('strikethrough')"
          title="删除线"
        >
          <i class="icon">S</i>
        </button>
      </div>
      
      <!-- 段落格式 -->
      <div class="tool-group">
        <select v-model="currentBlock" @change="applyBlockFormat" class="format-select">
          <option value="paragraph">段落</option>
          <option value="h1">标题1</option>
          <option value="h2">标题2</option>
          <option value="h3">标题3</option>
          <option value="blockquote">引用</option>
        </select>
      </div>
      
      <!-- 列表 -->
      <div class="tool-group">
        <button 
          type="button" 
          class="tool-btn" 
          @click="insertList('ordered')"
          title="有序列表"
        >
          <i class="icon">1.</i>
        </button>
        <button 
          type="button" 
          class="tool-btn" 
          @click="insertList('unordered')"
          title="无序列表"
        >
          <i class="icon">•</i>
        </button>
      </div>
      
      <!-- 链接和图片 -->
      <div class="tool-group">
        <button 
          type="button" 
          class="tool-btn" 
          @click="insertLink"
          title="插入链接"
        >
          <i class="icon">🔗</i>
        </button>
        <button 
          type="button" 
          class="tool-btn" 
          @click="insertImage"
          title="插入图片"
        >
          <i class="icon">🖼️</i>
        </button>
      </div>
      
      <!-- 代码 -->
      <div class="tool-group">
        <button 
          type="button" 
          class="tool-btn" 
          @click="insertCode"
          title="插入代码"
        >
          <i class="icon">{}</i>
        </button>
      </div>
      
      <!-- 表情 -->
      <div class="tool-group">
        <button 
          type="button" 
          class="tool-btn" 
          @click="toggleEmojiPicker"
          title="表情"
        >
          <i class="icon">😊</i>
        </button>
      </div>
      
      <!-- 字数统计 -->
      <div class="tool-group word-count">
        <span>{{ wordCount }} 字</span>
      </div>
    </div>
    
    <!-- 编辑器内容 -->
    <div 
      ref="editor" 
      class="editor-content" 
      contenteditable="true"
      @input="onInput"
      @focus="onFocus"
      @blur="onBlur"
      @keydown="onKeydown"
      @paste="onPaste"
      :placeholder="placeholder"
    ></div>
    
    <!-- 链接插入模态框 -->
    <div v-if="showLinkModal" class="modal-overlay">
      <div class="modal">
        <h3>插入链接</h3>
        <div class="modal-body">
          <input 
            v-model="linkUrl" 
            type="text" 
            placeholder="请输入链接地址"
            class="modal-input"
          />
          <input 
            v-model="linkText" 
            type="text" 
            placeholder="链接文本（可选）"
            class="modal-input"
          />
        </div>
        <div class="modal-footer">
          <button @click="confirmLink" class="btn-primary">确定</button>
          <button @click="cancelLink" class="btn-secondary">取消</button>
        </div>
      </div>
    </div>
    
    <!-- 图片上传模态框 -->
    <div v-if="showImageModal" class="modal-overlay">
      <div class="modal">
        <h3>插入图片</h3>
        <div class="modal-body">
          <div class="upload-area" @click="triggerFileInput">
            <input 
              ref="fileInput" 
              type="file" 
              accept="image/*" 
              multiple 
              @change="handleFileSelect"
              style="display: none"
            />
            <div v-if="!uploadedImages.length" class="upload-placeholder">
              <i class="upload-icon">📁</i>
              <p>点击选择图片或拖拽图片到这里</p>
            </div>
            <div v-else class="image-preview">
              <div 
                v-for="(image, index) in uploadedImages" 
                :key="index" 
                class="preview-item"
              >
                <img :src="image.preview" :alt="image.name" />
                <button @click="removeImage(index)" class="remove-btn">×</button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="confirmImages" class="btn-primary">插入</button>
          <button @click="cancelImages" class="btn-secondary">取消</button>
        </div>
      </div>
    </div>
    
    <!-- 表情选择器 -->
    <div v-if="showEmojiPicker" class="emoji-picker">
      <div class="emoji-categories">
        <button 
          v-for="category in emojiCategories" 
          :key="category"
          :class="{ active: activeEmojiCategory === category }"
          @click="activeEmojiCategory = category"
          class="category-btn"
        >
          {{ category }}
        </button>
      </div>
      <div class="emoji-list">
        <button 
          v-for="emoji in filteredEmojis" 
          :key="emoji"
          @click="insertEmoji(emoji)"
          class="emoji-btn"
        >
          {{ emoji }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'

interface Props {
  modelValue?: string
  placeholder?: string
  height?: string
  maxLength?: number
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
  (e: 'focus'): void
  (e: 'blur'): void
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请输入内容...',
  height: '300px',
  maxLength: 5000
})

const emit = defineEmits<Emits>()

// 编辑器引用
const editor = ref<HTMLElement>()

// 编辑器状态
const isFocused = ref(false)
const activeFormat = ref({
  bold: false,
  italic: false,
  underline: false,
  strikethrough: false
})

const currentBlock = ref('paragraph')

// 模态框状态
const showLinkModal = ref(false)
const showImageModal = ref(false)
const showEmojiPicker = ref(false)

// 链接数据
const linkUrl = ref('')
const linkText = ref('')

// 图片上传
const fileInput = ref<HTMLInputElement>()
const uploadedImages = ref<Array<{file: File, preview: string}>>([])

// 表情选择器
const activeEmojiCategory = ref('表情')
const emojiCategories = ['表情', '动物', '食物', '活动', '旅行', '物品', '符号']
const emojis = {
  '表情': ['😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇'],
  '动物': ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯'],
  '食物': ['🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🍈', '🍒'],
  '活动': ['⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🎱', '🏓', '🏸'],
  '旅行': ['🚗', '🚕', '🚙', '🚌', '🚎', '🏎️', '🚓', '🚑', '🚒', '🚐'],
  '物品': ['⌚', '📱', '📲', '💻', '⌨️', '🖥️', '🖨️', '🖱️', '🖲️', '🕹️'],
  '符号': ['❤️', '💛', '💚', '💙', '💜', '🖤', '💔', '❣️', '💕', '💞']
}

// 计算属性
const wordCount = computed(() => {
  if (!editor.value) return 0
  const text = editor.value.innerText || ''
  return text.replace(/\s+/g, ' ').trim().split(' ').filter(word => word.length > 0).length
})

const filteredEmojis = computed(() => {
  return emojis[activeEmojiCategory.value as keyof typeof emojis] || []
})

// 监听模型值变化
watch(() => props.modelValue, (newValue) => {
  if (editor.value && newValue !== editor.value.innerHTML) {
    editor.value.innerHTML = newValue || ''
  }
})

// 生命周期
onMounted(() => {
  if (editor.value && props.modelValue) {
    editor.value.innerHTML = props.modelValue
  }
  
  // 设置编辑器高度
  if (editor.value) {
    editor.value.style.minHeight = props.height
  }
})

// 事件处理
const onInput = () => {
  if (!editor.value) return
  
  const content = editor.value.innerHTML
  emit('update:modelValue', content)
  emit('change', content)
  
  // 更新格式状态
  updateFormatState()
}

const onFocus = () => {
  isFocused.value = true
  emit('focus')
}

const onBlur = () => {
  isFocused.value = false
  emit('blur')
}

const onKeydown = (event: KeyboardEvent) => {
  // 处理Tab键
  if (event.key === 'Tab') {
    event.preventDefault()
    document.execCommand('insertHTML', false, '&nbsp;&nbsp;&nbsp;&nbsp;')
  }
  
  // 处理Ctrl+B/I/U等快捷键
  if (event.ctrlKey || event.metaKey) {
    switch (event.key.toLowerCase()) {
      case 'b':
        event.preventDefault()
        toggleFormat('bold')
        break
      case 'i':
        event.preventDefault()
        toggleFormat('italic')
        break
      case 'u':
        event.preventDefault()
        toggleFormat('underline')
        break
    }
  }
}

const onPaste = (event: ClipboardEvent) => {
  const clipboardData = event.clipboardData
  if (!clipboardData) return
  
  // 处理纯文本粘贴
  const text = clipboardData.getData('text/plain')
  if (text) {
    event.preventDefault()
    document.execCommand('insertText', false, text)
  }
}

// 格式操作
const toggleFormat = (format: keyof typeof activeFormat.value) => {
  document.execCommand(format)
  updateFormatState()
}

const applyBlockFormat = () => {
  const format = currentBlock.value
  if (format === 'paragraph') {
    document.execCommand('formatBlock', false, '<p>')
  } else {
    document.execCommand('formatBlock', false, `<${format}>`)
  }
}

const insertList = (type: 'ordered' | 'unordered') => {
  document.execCommand(type === 'ordered' ? 'insertOrderedList' : 'insertUnorderedList')
}

// 链接操作
const insertLink = () => {
  const selection = window.getSelection()
  if (selection && selection.toString().trim()) {
    linkText.value = selection.toString()
  }
  showLinkModal.value = true
}

const confirmLink = () => {
  if (linkUrl.value.trim()) {
    const linkHtml = linkText.value.trim() 
      ? `<a href="${linkUrl.value}" target="_blank">${linkText.value}</a>`
      : `<a href="${linkUrl.value}" target="_blank">${linkUrl.value}</a>`
    
    document.execCommand('insertHTML', false, linkHtml)
  }
  cancelLink()
}

const cancelLink = () => {
  showLinkModal.value = false
  linkUrl.value = ''
  linkText.value = ''
}

// 图片操作
const insertImage = () => {
  showImageModal.value = true
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files) return
  
  Array.from(target.files).forEach(file => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        uploadedImages.value.push({
          file,
          preview: e.target?.result as string
        })
      }
      reader.readAsDataURL(file)
    }
  })
  
  // 清空文件输入
  target.value = ''
}

const removeImage = (index: number) => {
  uploadedImages.value.splice(index, 1)
}

const confirmImages = async () => {
  for (const image of uploadedImages.value) {
    // 在实际应用中，这里应该上传图片到服务器
    const imgHtml = `<img src="${image.preview}" alt="${image.file.name}" style="max-width: 100%; height: auto;" />`
    document.execCommand('insertHTML', false, imgHtml)
  }
  cancelImages()
}

const cancelImages = () => {
  showImageModal.value = false
  uploadedImages.value = []
}

// 表情操作
const toggleEmojiPicker = () => {
  showEmojiPicker.value = !showEmojiPicker.value
}

const insertEmoji = (emoji: string) => {
  document.execCommand('insertText', false, emoji)
  showEmojiPicker.value = false
}

// 代码操作
const insertCode = () => {
  const codeHtml = '<code>代码内容</code>'
  document.execCommand('insertHTML', false, codeHtml)
}

// 工具函数
const updateFormatState = () => {
  if (!editor.value) return
  
  activeFormat.value = {
    bold: document.queryCommandState('bold'),
    italic: document.queryCommandState('italic'),
    underline: document.queryCommandState('underline'),
    strikethrough: document.queryCommandState('strikethrough')
  }
}

// 公共方法
defineExpose({
  focus: () => editor.value?.focus(),
  blur: () => editor.value?.blur(),
  clear: () => {
    if (editor.value) {
      editor.value.innerHTML = ''
      emit('update:modelValue', '')
    }
  },
  getContent: () => editor.value?.innerHTML || '',
  getText: () => editor.value?.innerText || ''
})
</script>

<style scoped>
.rich-text-editor {
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  background: white;
  position: relative;
}

.toolbar {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
  flex-wrap: wrap;
  gap: 8px;
}

.tool-group {
  display: flex;
  align-items: center;
  gap: 4px;
  padding-right: 12px;
  border-right: 1px solid #e8e8e8;
}

.tool-group:last-child {
  border-right: none;
  padding-right: 0;
}

.tool-btn {
  padding: 6px 8px;
  border: 1px solid transparent;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
}

.tool-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.tool-btn.active {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

.format-select {
  padding: 4px 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: white;
  font-size: 14px;
}

.word-count {
  color: #666;
  font-size: 12px;
  margin-left: auto;
}

.editor-content {
  padding: 12px;
  min-height: 200px;
  max-height: 500px;
  overflow-y: auto;
  outline: none;
  line-height: 1.6;
  font-size: 14px;
}

.editor-content:empty:before {
  content: attr(placeholder);
  color: #bfbfbf;
}

.editor-content:focus {
  outline: none;
}

.editor-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.editor-content :deep(a) {
  color: #1890ff;
  text-decoration: none;
}

.editor-content :deep(a:hover) {
  text-decoration: underline;
}

.editor-content :deep(code) {
  background: #f5f5f5;
  padding: 2px 4px;
  border-radius: 2px;
  font-family: 'Courier New', monospace;
}

.editor-content :deep(blockquote) {
  border-left: 4px solid #1890ff;
  padding-left: 12px;
  margin-left: 0;
  color: #666;
  font-style: italic;
}

/* 模态框样式 */
.modal-overlay {
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

.modal {
  background: white;
  border-radius: 8px;
  padding: 24px;
  min-width: 400px;
  max-width: 500px;
}

.modal h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
}

.modal-body {
  margin-bottom: 20px;
}

.modal-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 14px;
}

.modal-input:focus {
  outline: none;
  border-color: #1890ff;
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s;
}

.upload-area:hover {
  border-color: #1890ff;
}

.upload-placeholder {
  color: #666;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 12px;
  display: block;
}

.image-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.preview-item {
  position: relative;
  width: 80px;
  height: 80px;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  border: none;
  background: #ff4d4f;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-primary {
  padding: 8px 16px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary {
  padding: 8px 16px;
  background: #f5f5f5;
  color: #666;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

/* 表情选择器 */
.emoji-picker {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  width: 300px;
}

.emoji-categories {
  display: flex;
  border-bottom: 1px solid #f0f0f0;
  padding: 8px;
}

.category-btn {
  flex: 1;
  padding: 6px 8px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 12px;
  border-radius: 4px;
}

.category-btn.active {
  background: #1890ff;
  color: white;
}

.emoji-list {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 4px;
  padding: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.emoji-btn {
  padding: 8px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 18px;
  border-radius: 4px;
  transition: background 0.2s;
}

.emoji-btn:hover {
  background: #f0f0f0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .toolbar {
    padding: 6px 8px;
  }
  
  .tool-group {
    padding-right: 8px;
  }
  
  .tool-btn {
    min-width: 28px;
    height: 28px;
    font-size: 12px;
  }
  
  .modal {
    min-width: 300px;
    margin: 20px;
  }
  
  .emoji-picker {
    width: 280px;
  }
}
</style>