<template>
  <div class="post-detail-page">
    <div class="container">
      <!-- 帖子内容 -->
      <div class="post-content">
        <div class="post-header">
          <div class="breadcrumb">
            <router-link :to="`/tieba/${post.tiebaId}`" class="breadcrumb-item">
              {{ post.tiebaName }}
            </router-link>
            <span class="breadcrumb-separator">/</span>
            <span class="breadcrumb-current">{{ post.title }}</span>
          </div>
          
          <h1 class="post-title">{{ post.title }}</h1>
          
          <div class="post-meta">
            <div class="author-info">
              <img :src="post.authorAvatar || '/default-avatar.png'" :alt="post.authorName" />
              <div class="author-details">
                <span class="author-name">{{ post.authorName }}</span>
                <span class="post-time">{{ formatTime(post.createdAt) }}</span>
              </div>
            </div>
            
            <div class="post-stats">
              <span class="stat">
                <i class="icon-view">👁️</i> {{ post.viewCount || 0 }} 浏览
              </span>
              <span class="stat">
                <i class="icon-like">👍</i> {{ post.likeCount || 0 }} 点赞
              </span>
              <span class="stat">
                <i class="icon-comment">💬</i> {{ post.commentCount || 0 }} 评论
              </span>
            </div>
          </div>
        </div>
        
        <div class="post-body">
          <div class="content" v-html="post.content"></div>
          
          <div class="post-actions">
            <button 
              class="action-btn" 
              :class="{ active: post.isLiked }"
              @click="toggleLike"
              :disabled="liking"
            >
              <i class="icon">👍</i>
              {{ post.isLiked ? '已点赞' : '点赞' }}
              <span class="count">{{ post.likeCount || 0 }}</span>
            </button>
            
            <button class="action-btn" @click="focusCommentInput">
              <i class="icon">💬</i>
              评论
              <span class="count">{{ post.commentCount || 0 }}</span>
            </button>
            
            <button class="action-btn" :class="{ active: post.isCollected }" @click="toggleCollect">
              <i class="icon">⭐</i>
              {{ post.isCollected ? '已收藏' : '收藏' }}
            </button>
            
            <button class="action-btn" @click="sharePost">
              <i class="icon">📤</i>
              分享
            </button>
          </div>
        </div>
      </div>
      
      <!-- 评论区域 -->
      <div class="comments-section">
        <div class="section-header">
          <h2>评论 ({{ comments.length }})</h2>
        </div>
        
        <!-- 发表评论 -->
        <div class="comment-form" v-if="globalStore.isAuthenticated">
          <div class="form-header">
            <img :src="globalStore.user?.avatar || '/default-avatar.png'" :alt="globalStore.user?.username" />
            <span>发表评论</span>
          </div>
          <div class="form-body">
            <textarea 
              v-model="newComment" 
              placeholder="写下你的评论..."
              rows="3"
              ref="commentInput"
            ></textarea>
            <div class="form-actions">
              <button 
                class="btn btn-primary" 
                @click="submitComment"
                :disabled="!newComment.trim() || submittingComment"
              >
                {{ submittingComment ? '发布中...' : '发布评论' }}
              </button>
            </div>
          </div>
        </div>
        <div v-else class="login-prompt">
          <p>请<a href="/login">登录</a>后发表评论</p>
        </div>
        
        <!-- 评论列表 -->
        <div class="comments-list">
          <div 
            v-for="comment in comments" 
            :key="comment.id" 
            class="comment-item"
          >
            <div class="comment-header">
              <div class="comment-author">
                <img :src="comment.authorAvatar || '/default-avatar.png'" :alt="comment.authorName" />
                <div class="author-info">
                  <span class="author-name">{{ comment.authorName }}</span>
                  <span class="comment-time">{{ formatTime(comment.createdAt) }}</span>
                </div>
              </div>
              <div class="comment-actions">
                <button 
                  class="action-btn small" 
                  :class="{ active: comment.isLiked }"
                  @click="toggleCommentLike(comment)"
                >
                  <i class="icon">👍</i> {{ comment.likeCount || 0 }}
                </button>
                <button 
                  v-if="comment.authorId === globalStore.user?.id"
                  class="action-btn small danger"
                  @click="deleteComment(comment.id)"
                >
                  删除
                </button>
              </div>
            </div>
            
            <div class="comment-content">
              {{ comment.content }}
            </div>
            
            <!-- 回复区域 -->
            <div class="replies" v-if="comment.replies && comment.replies.length > 0">
              <div 
                v-for="reply in comment.replies" 
                :key="reply.id" 
                class="reply-item"
              >
                <div class="reply-header">
                  <span class="reply-author">{{ reply.authorName }}</span>
                  <span class="reply-time">{{ formatTime(reply.createdAt) }}</span>
                </div>
                <div class="reply-content">
                  {{ reply.content }}
                </div>
              </div>
            </div>
            
            <!-- 回复表单 -->
            <div class="reply-form" v-if="showReplyForm === comment.id">
              <textarea 
                v-model="replyContent" 
                placeholder="写下你的回复..."
                rows="2"
              ></textarea>
              <div class="form-actions">
                <button class="btn btn-outline" @click="cancelReply">取消</button>
                <button 
                  class="btn btn-primary" 
                  @click="submitReply(comment.id)"
                  :disabled="!replyContent.trim()"
                >
                  回复
                </button>
              </div>
            </div>
            
            <button 
              v-if="globalStore.isAuthenticated && showReplyForm !== comment.id"
              class="reply-btn"
              @click="showReply(comment.id)"
            >
              回复
            </button>
          </div>
        </div>
        
        <!-- 分页 -->
        <div class="pagination" v-if="commentTotalPages > 1">
          <button 
            :disabled="commentCurrentPage === 1" 
            @click="changeCommentPage(commentCurrentPage - 1)"
            class="page-btn"
          >
            上一页
          </button>
          <span class="page-info">第 {{ commentCurrentPage }} 页 / 共 {{ commentTotalPages }} 页</span>
          <button 
            :disabled="commentCurrentPage === commentTotalPages" 
            @click="changeCommentPage(commentCurrentPage + 1)"
            class="page-btn"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGlobalStore } from '@/stores/global'
import { postApi, commentApi } from '@/api/tieba'
import type { Post, Comment } from '@/types/tieba'

const route = useRoute()
const router = useRouter()
const globalStore = useGlobalStore()

const postId = route.params.id as string

// 帖子信息
const post = ref<Post>({
  id: '',
  title: '',
  content: '',
  authorId: '',
  authorName: '',
  authorAvatar: '',
  tiebaId: '',
  tiebaName: '',
  createdAt: '',
  viewCount: 0,
  likeCount: 0,
  commentCount: 0,
  isLiked: false,
  isCollected: false
})

// 评论相关
const comments = ref<Comment[]>([])
const newComment = ref('')
const submittingComment = ref(false)
const commentCurrentPage = ref(1)
const commentPageSize = ref(20)
const commentTotalPages = ref(1)

// 回复相关
const showReplyForm = ref<string | null>(null)
const replyContent = ref('')

// 点赞状态
const liking = ref(false)

// 输入框引用
const commentInput = ref<HTMLTextAreaElement | null>(null)

// 加载帖子详情
const loadPostDetail = async () => {
  try {
    const response = await postApi.getPostDetail(postId)
    post.value = response.data
  } catch (error) {
    console.error('加载帖子详情失败:', error)
  }
}

// 加载评论列表
const loadComments = async () => {
  try {
    const response = await commentApi.getCommentsByPost(postId, {
      page: commentCurrentPage.value,
      size: commentPageSize.value
    })
    comments.value = response.data.comments
    commentTotalPages.value = Math.ceil(response.data.total / commentPageSize.value)
  } catch (error) {
    console.error('加载评论失败:', error)
  }
}

// 点赞/取消点赞帖子
const toggleLike = async () => {
  if (!globalStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  liking.value = true
  try {
    if (post.value.isLiked) {
      await postApi.unlikePost(postId)
      post.value.likeCount = Math.max(0, (post.value.likeCount || 0) - 1)
    } else {
      await postApi.likePost(postId)
      post.value.likeCount = (post.value.likeCount || 0) + 1
    }
    post.value.isLiked = !post.value.isLiked
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    liking.value = false
  }
}

// 收藏/取消收藏帖子
const toggleCollect = async () => {
  if (!globalStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  try {
    if (post.value.isCollected) {
      await postApi.uncollectPost(postId)
    } else {
      await postApi.collectPost(postId)
    }
    post.value.isCollected = !post.value.isCollected
  } catch (error) {
    console.error('操作失败:', error)
  }
}

// 分享帖子
const sharePost = () => {
  if (navigator.share) {
    navigator.share({
      title: post.value.title,
      text: post.value.content,
      url: window.location.href
    })
  } else {
    // 复制链接到剪贴板
    navigator.clipboard.writeText(window.location.href)
    alert('链接已复制到剪贴板')
  }
}

// 提交评论
const submitComment = async () => {
  if (!globalStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  submittingComment.value = true
  try {
    await commentApi.createComment({
      postId: postId,
      content: newComment.value.trim()
    })
    
    newComment.value = ''
    await loadComments()
    post.value.commentCount = (post.value.commentCount || 0) + 1
  } catch (error) {
    console.error('发表评论失败:', error)
  } finally {
    submittingComment.value = false
  }
}

// 点赞/取消点赞评论
const toggleCommentLike = async (comment: Comment) => {
  if (!globalStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  try {
    if (comment.isLiked) {
      await commentApi.unlikeComment(comment.id)
      comment.likeCount = Math.max(0, (comment.likeCount || 0) - 1)
    } else {
      await commentApi.likeComment(comment.id)
      comment.likeCount = (comment.likeCount || 0) + 1
    }
    comment.isLiked = !comment.isLiked
  } catch (error) {
    console.error('操作失败:', error)
  }
}

// 删除评论
const deleteComment = async (commentId: string) => {
  if (!confirm('确定要删除这条评论吗？')) {
    return
  }
  
  try {
    await commentApi.deleteComment(commentId)
    await loadComments()
    post.value.commentCount = Math.max(0, (post.value.commentCount || 0) - 1)
  } catch (error) {
    console.error('删除评论失败:', error)
  }
}

// 显示回复表单
const showReply = (commentId: string) => {
  showReplyForm.value = commentId
  replyContent.value = ''
}

// 取消回复
const cancelReply = () => {
  showReplyForm.value = null
  replyContent.value = ''
}

// 提交回复
const submitReply = async (commentId: string) => {
  if (!globalStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  try {
    await commentApi.createReply({
      commentId: commentId,
      content: replyContent.value.trim()
    })
    
    showReplyForm.value = null
    replyContent.value = ''
    await loadComments() // 重新加载评论列表
  } catch (error) {
    console.error('回复失败:', error)
  }
}

// 聚焦评论输入框
const focusCommentInput = () => {
  if (commentInput.value) {
    commentInput.value.focus()
  }
}

// 分页
const changeCommentPage = (page: number) => {
  commentCurrentPage.value = page
  loadComments()
}

// 格式化时间
const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(() => {
  loadPostDetail()
  loadComments()
})
</script>

<style scoped>
.post-detail-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px 0;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 14px;
}

.breadcrumb-item {
  color: #1890ff;
  text-decoration: none;
}

.breadcrumb-item:hover {
  text-decoration: underline;
}

.breadcrumb-separator {
  color: #999;
}

.breadcrumb-current {
  color: #666;
}

.post-content {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.post-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  line-height: 1.4;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-info img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.author-details {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 500;
  color: #1890ff;
}

.post-time {
  font-size: 12px;
  color: #999;
}

.post-stats {
  display: flex;
  gap: 20px;
}

.stat {
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 4px;
}

.post-body {
  margin-top: 24px;
}

.content {
  line-height: 1.8;
  color: #333;
  margin-bottom: 24px;
}

.post-actions {
  display: flex;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.action-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.action-btn.active {
  background: #1890ff;
  border-color: #1890ff;
  color: white;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.small {
  padding: 4px 8px;
  font-size: 12px;
}

.action-btn.danger {
  color: #ff4d4f;
}

.action-btn.danger:hover {
  border-color: #ff4d4f;
}

.comments-section {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  margin-bottom: 24px;
}

.section-header h2 {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.comment-form {
  margin-bottom: 32px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.form-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.form-header img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.form-header span {
  font-weight: 500;
  color: #333;
}

.form-body textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;
  box-sizing: border-box;
}

.form-actions {
  margin-top: 12px;
  text-align: right;
}

.login-prompt {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 32px;
}

.login-prompt a {
  color: #1890ff;
  text-decoration: none;
}

.login-prompt a:hover {
  text-decoration: underline;
}

.comments-list {
  margin-bottom: 24px;
}

.comment-item {
  padding: 16px 0;
  border-bottom: 1px solid #eee;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.comment-author img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 500;
  color: #1890ff;
  font-size: 14px;
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.comment-actions {
  display: flex;
  gap: 8px;
}

.comment-content {
  color: #333;
  line-height: 1.6;
  margin-bottom: 12px;
}

.replies {
  margin-top: 12px;
  margin-left: 40px;
  border-left: 2px solid #eee;
  padding-left: 12px;
}

.reply-item {
  padding: 8px 0;
}

.reply-header {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
}

.reply-author {
  font-weight: 500;
  color: #1890ff;
  font-size: 13px;
}

.reply-time {
  font-size: 11px;
  color: #999;
}

.reply-content {
  color: #666;
  font-size: 13px;
  line-height: 1.5;
}

.reply-form {
  margin-top: 8px;
  margin-left: 40px;
}

.reply-form textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  resize: vertical;
  min-height: 60px;
  box-sizing: border-box;
}

.reply-btn {
  background: none;
  border: none;
  color: #1890ff;
  font-size: 13px;
  cursor: pointer;
  padding: 0;
}

.reply-btn:hover {
  text-decoration: underline;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  border-color: #1890ff;
  color: #1890ff;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .post-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .post-stats {
    width: 100%;
    justify-content: space-around;
  }
  
  .post-actions {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .action-btn {
    flex: 1;
    min-width: 120px;
    justify-content: center;
  }
  
  .comment-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .comment-actions {
    align-self: flex-end;
  }
  
  .replies {
    margin-left: 20px;
  }
  
  .reply-form {
    margin-left: 20px;
  }
}
</style>