<template>
  <div class="notifications-page">
    <div class="container">
      <!-- 页面头部 -->
      <div class="page-header">
        <h1>消息通知</h1>
        <div class="header-actions">
          <button 
            @click="markAllAsRead" 
            class="btn-mark-all"
            :disabled="unreadCount === 0"
          >
            {{ markingAll ? '标记中...' : '全部标记已读' }}
          </button>
          <button 
            @click="clearAll" 
            class="btn-clear-all"
            :disabled="notifications.length === 0"
          >
            {{ clearingAll ? '清空中...' : '清空全部' }}
          </button>
        </div>
      </div>
      
      <!-- 标签页 -->
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="['tab', { active: activeTab === tab.key }]"
        >
          {{ tab.label }}
          <span v-if="tab.count > 0" class="tab-count">{{ tab.count }}</span>
        </button>
      </div>
      
      <!-- 通知列表 -->
      <div class="notifications-list">
        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <span>加载中...</span>
        </div>
        
        <div v-else-if="filteredNotifications.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <h3>暂无通知</h3>
          <p>当您收到新的通知时，它们会显示在这里</p>
        </div>
        
        <div v-else class="notifications">
          <div 
            v-for="notification in filteredNotifications" 
            :key="notification.id"
            :class="['notification-item', { unread: !notification.read }]"
            @click="handleNotificationClick(notification)"
          >
            <!-- 通知图标 -->
            <div class="notification-icon">
              <span :class="getNotificationIcon(notification.type)">
                {{ getNotificationEmoji(notification.type) }}
              </span>
            </div>
            
            <!-- 通知内容 -->
            <div class="notification-content">
              <div class="notification-title">
                {{ notification.title }}
              </div>
              <div class="notification-message">
                {{ notification.message }}
              </div>
              <div class="notification-meta">
                <span class="time">{{ formatTime(notification.created_at) }}</span>
                <span v-if="!notification.read" class="unread-badge">未读</span>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div class="notification-actions">
              <button 
                v-if="!notification.read"
                @click.stop="markAsRead(notification)"
                class="btn-mark-read"
                title="标记为已读"
              >
                ✓
              </button>
              <button 
                @click.stop="deleteNotification(notification)"
                class="btn-delete"
                title="删除"
              >
                ×
              </button>
            </div>
          </div>
        </div>
        
        <!-- 加载更多 -->
        <div v-if="hasMore && !loading" class="load-more">
          <button @click="loadMore" class="btn-load-more">
            {{ loadingMore ? '加载中...' : '加载更多' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

interface Notification {
  id: string
  type: 'like' | 'comment' | 'follow' | 'system' | 'mention' | 'reply'
  title: string
  message: string
  read: boolean
  created_at: string
  target_id?: string
  target_type?: 'post' | 'comment' | 'user'
  sender_id?: string
  sender_name?: string
}

const router = useRouter()

// 标签页配置
const tabs = ref([
  { key: 'all', label: '全部', count: 0 },
  { key: 'unread', label: '未读', count: 0 },
  { key: 'like', label: '点赞', count: 0 },
  { key: 'comment', label: '评论', count: 0 },
  { key: 'follow', label: '关注', count: 0 },
  { key: 'system', label: '系统', count: 0 }
])

const activeTab = ref('all')

// 通知数据
const notifications = ref<Notification[]>([])
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = ref(true)
const markingAll = ref(false)
const clearingAll = ref(false)

// 计算属性
const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

const filteredNotifications = computed(() => {
  if (activeTab.value === 'all') {
    return notifications.value
  } else if (activeTab.value === 'unread') {
    return notifications.value.filter(n => !n.read)
  } else {
    return notifications.value.filter(n => n.type === activeTab.value)
  }
})

// 生命周期
onMounted(async () => {
  await loadNotifications()
  updateTabCounts()
})

// 加载通知
const loadNotifications = async () => {
  loading.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    notifications.value = [
      {
        id: '1',
        type: 'like',
        title: '有人点赞了你的帖子',
        message: '用户“小明”点赞了你的帖子“Vue3最佳实践分享”',
        read: false,
        created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        target_id: '123',
        target_type: 'post',
        sender_id: '456',
        sender_name: '小明'
      },
      {
        id: '2',
        type: 'comment',
        title: '有人评论了你的帖子',
        message: '用户“小红”评论了你的帖子：写得真不错！',
        read: false,
        created_at: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        target_id: '123',
        target_type: 'post',
        sender_id: '789',
        sender_name: '小红'
      },
      {
        id: '3',
        type: 'follow',
        title: '有人关注了你',
        message: '用户“小刚”关注了你',
        read: true,
        created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        target_id: '456',
        target_type: 'user',
        sender_id: '101',
        sender_name: '小刚'
      },
      {
        id: '4',
        type: 'system',
        title: '系统通知',
        message: '您的帖子“Vue3最佳实践分享”已被设为精华帖',
        read: true,
        created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: '5',
        type: 'reply',
        title: '有人回复了你的评论',
        message: '用户“小李”回复了你的评论：谢谢分享！',
        read: true,
        created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        target_id: '456',
        target_type: 'comment',
        sender_id: '202',
        sender_name: '小李'
      }
    ]
    
  } catch (error) {
    console.error('加载通知失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载更多
const loadMore = async () => {
  if (loadingMore.value || !hasMore.value) return
  
  loadingMore.value = true
  
  try {
    // 模拟加载更多数据
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 这里应该调用API加载更多数据
    // 模拟添加更多数据
    const newNotifications: Notification[] = [
      {
        id: '6',
        type: 'like',
        title: '有人点赞了你的评论',
        message: '用户“小王”点赞了你的评论',
        read: true,
        created_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: '7',
        type: 'mention',
        title: '有人提到了你',
        message: '用户“小张”在帖子中提到了你',
        read: true,
        created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString()
      }
    ]
    
    notifications.value.push(...newNotifications)
    
    // 模拟没有更多数据
    hasMore.value = false
    
  } catch (error) {
    console.error('加载更多通知失败:', error)
  } finally {
    loadingMore.value = false
  }
}

// 更新标签页计数
const updateTabCounts = () => {
  tabs.value.forEach(tab => {
    if (tab.key === 'all') {
      tab.count = notifications.value.length
    } else if (tab.key === 'unread') {
      tab.count = unreadCount.value
    } else {
      tab.count = notifications.value.filter(n => n.type === tab.key).length
    }
  })
}

// 标记为已读
const markAsRead = async (notification: Notification) => {
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 300))
    
    notification.read = true
    updateTabCounts()
    
  } catch (error) {
    console.error('标记已读失败:', error)
  }
}

// 标记全部为已读
const markAllAsRead = async () => {
  if (unreadCount.value === 0) return
  
  markingAll.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    notifications.value.forEach(n => {
      n.read = true
    })
    
    updateTabCounts()
    
  } catch (error) {
    console.error('标记全部已读失败:', error)
  } finally {
    markingAll.value = false
  }
}

// 删除通知
const deleteNotification = async (notification: Notification) => {
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 300))
    
    const index = notifications.value.findIndex(n => n.id === notification.id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
      updateTabCounts()
    }
    
  } catch (error) {
    console.error('删除通知失败:', error)
  }
}

// 清空全部
const clearAll = async () => {
  if (notifications.value.length === 0) return
  
  clearingAll.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    notifications.value = []
    updateTabCounts()
    
  } catch (error) {
    console.error('清空全部失败:', error)
  } finally {
    clearingAll.value = false
  }
}

// 处理通知点击
const handleNotificationClick = (notification: Notification) => {
  // 标记为已读
  if (!notification.read) {
    markAsRead(notification)
  }
  
  // 根据通知类型跳转到相应页面
  if (notification.target_id && notification.target_type) {
    switch (notification.target_type) {
      case 'post':
        router.push(`/post/${notification.target_id}`)
        break
      case 'comment':
        // 跳转到帖子详情页并滚动到评论位置
        router.push(`/post/${notification.target_id}#comment-${notification.target_id}`)
        break
      case 'user':
        router.push(`/user/${notification.target_id}`)
        break
    }
  }
}

// 获取通知图标
const getNotificationIcon = (type: string) => {
  const icons = {
    like: 'icon-like',
    comment: 'icon-comment',
    follow: 'icon-follow',
    system: 'icon-system',
    mention: 'icon-mention',
    reply: 'icon-reply'
  }
  return icons[type as keyof typeof icons] || 'icon-system'
}

// 获取通知表情符号
const getNotificationEmoji = (type: string) => {
  const emojis = {
    like: '👍',
    comment: '💬',
    follow: '👤',
    system: '🔔',
    mention: '@',
    reply: '↩️'
  }
  return emojis[type as keyof typeof emojis] || '🔔'
}

// 格式化时间
const formatTime = (timeString: string) => {
  const time = new Date(timeString)
  const now = new Date()
  const diff = now.getTime() - time.getTime()
  
  if (diff < 60000) { // 1分钟内
    return '刚刚'
  } else if (diff < 3600000) { // 1小时内
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) { // 1天内
    return `${Math.floor(diff / 3600000)}小时前`
  } else if (diff < 604800000) { // 1周内
    return `${Math.floor(diff / 86400000)}天前`
  } else {
    return time.toLocaleDateString('zh-CN')
  }
}
</script>

<style scoped>
.notifications-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px 0;
}

.container {
  max-width: 800px;
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

.btn-mark-all,
.btn-clear-all {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  background: white;
  color: #666;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-mark-all:hover:not(:disabled),
.btn-clear-all:hover:not(:disabled) {
  border-color: #1890ff;
  color: #1890ff;
}

.btn-mark-all:disabled,
.btn-clear-all:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.tab {
  position: relative;
  padding: 16px 24px;
  border: none;
  background: none;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
}

.tab:hover {
  color: #1890ff;
}

.tab.active {
  color: #1890ff;
  border-bottom-color: #1890ff;
  font-weight: 500;
}

.tab-count {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #ff4d4f;
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 12px;
  min-width: 18px;
  text-align: center;
}

.notifications-list {
  min-height: 400px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #666;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f0f0f0;
  border-top: 3px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  color: #999;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #666;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.notifications {
  padding: 0;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background: #fafafa;
}

.notification-item.unread {
  background: #f0f8ff;
}

.notification-item.unread:hover {
  background: #e6f7ff;
}

.notification-icon {
  margin-right: 16px;
  margin-top: 2px;
}

.notification-icon span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f0f0f0;
  font-size: 18px;
}

.notification-item.unread .notification-icon span {
  background: #e6f7ff;
  color: #1890ff;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
  font-size: 14px;
}

.notification-message {
  color: #666;
  font-size: 14px;
  line-height: 1.4;
  margin-bottom: 8px;
  word-wrap: break-word;
}

.notification-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #999;
}

.unread-badge {
  background: #ff4d4f;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
}

.notification-actions {
  display: flex;
  gap: 8px;
  margin-left: 16px;
}

.btn-mark-read,
.btn-delete {
  width: 32px;
  height: 32px;
  border: 1px solid #d9d9d9;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-mark-read:hover {
  border-color: #52c41a;
  color: #52c41a;
}

.btn-delete:hover {
  border-color: #ff4d4f;
  color: #ff4d4f;
}

.load-more {
  padding: 24px;
  text-align: center;
  border-top: 1px solid #f0f0f0;
}

.btn-load-more {
  padding: 8px 24px;
  border: 1px solid #d9d9d9;
  background: white;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-load-more:hover:not(:disabled) {
  border-color: #1890ff;
  color: #1890ff;
}

.btn-load-more:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  
  .tabs {
    overflow-x: auto;
    white-space: nowrap;
  }
  
  .tab {
    padding: 12px 16px;
    font-size: 13px;
  }
  
  .notification-item {
    padding: 12px 16px;
  }
  
  .notification-icon {
    margin-right: 12px;
  }
  
  .notification-icon span {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }
  
  .notification-actions {
    flex-direction: column;
    gap: 4px;
  }
  
  .btn-mark-read,
  .btn-delete {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }
}
</style>