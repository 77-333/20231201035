<template>
  <div class="settings-page">
    <div class="container">
      <!-- 页面头部 -->
      <div class="page-header">
        <h1>设置</h1>
        <div class="header-actions">
          <button 
            @click="saveSettings" 
            class="btn-save"
            :disabled="!hasChanges || saving"
          >
            {{ saving ? '保存中...' : '保存设置' }}
          </button>
          <button 
            @click="resetSettings" 
            class="btn-reset"
            :disabled="!hasChanges"
          >
            重置
          </button>
        </div>
      </div>
      
      <!-- 设置内容 -->
      <div class="settings-content">
        <!-- 侧边栏导航 -->
        <div class="settings-sidebar">
          <nav class="settings-nav">
            <button 
              v-for="section in sections" 
              :key="section.key"
              @click="activeSection = section.key"
              :class="['nav-item', { active: activeSection === section.key }]"
            >
              <span class="nav-icon">{{ section.icon }}</span>
              <span class="nav-label">{{ section.label }}</span>
            </button>
          </nav>
        </div>
        
        <!-- 设置面板 -->
        <div class="settings-panel">
          <!-- 账户设置 -->
          <div v-if="activeSection === 'account'" class="settings-section">
            <h2>账户设置</h2>
            
            <div class="setting-group">
              <h3>基本信息</h3>
              <div class="setting-item">
                <label class="setting-label">用户名</label>
                <input 
                  v-model="settings.account.username" 
                  type="text" 
                  class="setting-input"
                  placeholder="请输入用户名"
                />
              </div>
              
              <div class="setting-item">
                <label class="setting-label">邮箱</label>
                <input 
                  v-model="settings.account.email" 
                  type="email" 
                  class="setting-input"
                  placeholder="请输入邮箱"
                />
              </div>
              
              <div class="setting-item">
                <label class="setting-label">个人简介</label>
                <textarea 
                  v-model="settings.account.bio" 
                  class="setting-textarea"
                  placeholder="请输入个人简介"
                  maxlength="200"
                  rows="4"
                ></textarea>
                <div class="char-count">{{ settings.account.bio.length }}/200</div>
              </div>
            </div>
            
            <div class="setting-group">
              <h3>隐私设置</h3>
              <div class="setting-item">
                <label class="setting-label">个人主页可见性</label>
                <select v-model="settings.account.profileVisibility" class="setting-select">
                  <option value="public">公开</option>
                  <option value="followers">仅关注者可见</option>
                  <option value="private">私密</option>
                </select>
              </div>
              
              <div class="setting-item">
                <label class="setting-label">帖子可见性</label>
                <select v-model="settings.account.postVisibility" class="setting-select">
                  <option value="public">公开</option>
                  <option value="followers">仅关注者可见</option>
                  <option value="private">私密</option>
                </select>
              </div>
              
              <div class="setting-item">
                <label class="setting-label">允许私信</label>
                <select v-model="settings.account.allowMessages" class="setting-select">
                  <option value="all">所有人</option>
                  <option value="followers">仅关注者</option>
                  <option value="none">不允许</option>
                </select>
              </div>
            </div>
          </div>
          
          <!-- 通知设置 -->
          <div v-if="activeSection === 'notifications'" class="settings-section">
            <h2>通知设置</h2>
            
            <div class="setting-group">
              <h3>推送通知</h3>
              <div class="setting-item">
                <label class="setting-label">点赞通知</label>
                <div class="setting-toggle">
                  <input 
                    v-model="settings.notifications.likes" 
                    type="checkbox" 
                    class="toggle-input"
                  />
                  <span class="toggle-slider"></span>
                </div>
              </div>
              
              <div class="setting-item">
                <label class="setting-label">评论通知</label>
                <div class="setting-toggle">
                  <input 
                    v-model="settings.notifications.comments" 
                    type="checkbox" 
                    class="toggle-input"
                  />
                  <span class="toggle-slider"></span>
                </div>
              </div>
              
              <div class="setting-item">
                <label class="setting-label">关注通知</label>
                <div class="setting-toggle">
                  <input 
                    v-model="settings.notifications.follows" 
                    type="checkbox" 
                    class="toggle-input"
                  />
                  <span class="toggle-slider"></span>
                </div>
              </div>
              
              <div class="setting-item">
                <label class="setting-label">系统通知</label>
                <div class="setting-toggle">
                  <input 
                    v-model="settings.notifications.system" 
                    type="checkbox" 
                    class="toggle-input"
                  />
                  <span class="toggle-slider"></span>
                </div>
              </div>
            </div>
            
            <div class="setting-group">
              <h3>邮件通知</h3>
              <div class="setting-item">
                <label class="setting-label">重要通知邮件</label>
                <div class="setting-toggle">
                  <input 
                    v-model="settings.notifications.emailImportant" 
                    type="checkbox" 
                    class="toggle-input"
                  />
                  <span class="toggle-slider"></span>
                </div>
              </div>
              
              <div class="setting-item">
                <label class="setting-label">每周摘要</label>
                <div class="setting-toggle">
                  <input 
                    v-model="settings.notifications.emailWeekly" 
                    type="checkbox" 
                    class="toggle-input"
                  />
                  <span class="toggle-slider"></span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 隐私设置 -->
          <div v-if="activeSection === 'privacy'" class="settings-section">
            <h2>隐私设置</h2>
            
            <div class="setting-group">
              <h3>数据隐私</h3>
              <div class="setting-item">
                <label class="setting-label">个性化推荐</label>
                <div class="setting-toggle">
                  <input 
                    v-model="settings.privacy.personalizedRecommendations" 
                    type="checkbox" 
                    class="toggle-input"
                  />
                  <span class="toggle-slider"></span>
                </div>
                <p class="setting-description">基于您的活动提供个性化内容推荐</p>
              </div>
              
              <div class="setting-item">
                <label class="setting-label">数据分析</label>
                <div class="setting-toggle">
                  <input 
                    v-model="settings.privacy.dataAnalytics" 
                    type="checkbox" 
                    class="toggle-input"
                  />
                  <span class="toggle-slider"></span>
                </div>
                <p class="setting-description">允许我们收集匿名数据以改进服务</p>
              </div>
            </div>
            
            <div class="setting-group">
              <h3>搜索可见性</h3>
              <div class="setting-item">
                <label class="setting-label">在搜索结果中显示</label>
                <div class="setting-toggle">
                  <input 
                    v-model="settings.privacy.searchable" 
                    type="checkbox" 
                    class="toggle-input"
                  />
                  <span class="toggle-slider"></span>
                </div>
                <p class="setting-description">允许其他用户通过搜索找到您</p>
              </div>
              
              <div class="setting-item">
                <label class="setting-label">显示在线状态</label>
                <div class="setting-toggle">
                  <input 
                    v-model="settings.privacy.showOnlineStatus" 
                    type="checkbox" 
                    class="toggle-input"
                  />
                  <span class="toggle-slider"></span>
                </div>
                <p class="setting-description">向其他用户显示您的在线状态</p>
              </div>
            </div>
          </div>
          
          <!-- 安全设置 -->
          <div v-if="activeSection === 'security'" class="settings-section">
            <h2>安全设置</h2>
            
            <div class="setting-group">
              <h3>账户安全</h3>
              <div class="setting-item">
                <label class="setting-label">修改密码</label>
                <div class="security-action">
                  <button @click="showChangePassword = true" class="btn-change-password">
                    修改密码
                  </button>
                </div>
              </div>
              
              <div class="setting-item">
                <label class="setting-label">两步验证</label>
                <div class="security-action">
                  <div class="two-factor-status">
                    <span :class="['status', { enabled: settings.security.twoFactorEnabled }]">
                      {{ settings.security.twoFactorEnabled ? '已启用' : '未启用' }}
                    </span>
                    <button 
                      @click="toggleTwoFactor" 
                      class="btn-toggle-two-factor"
                    >
                      {{ settings.security.twoFactorEnabled ? '禁用' : '启用' }}
                    </button>
                  </div>
                </div>
              </div>
              
              <div class="setting-item">
                <label class="setting-label">登录设备管理</label>
                <div class="security-action">
                  <button @click="showDeviceManagement = true" class="btn-device-management">
                    管理设备
                  </button>
                </div>
              </div>
            </div>
            
            <div class="setting-group">
              <h3>会话管理</h3>
              <div class="setting-item">
                <label class="setting-label">自动登出时间</label>
                <select v-model="settings.security.autoLogout" class="setting-select">
                  <option value="30">30分钟</option>
                  <option value="60">1小时</option>
                  <option value="120">2小时</option>
                  <option value="never">从不</option>
                </select>
              </div>
            </div>
          </div>
          
          <!-- 外观设置 -->
          <div v-if="activeSection === 'appearance'" class="settings-section">
            <h2>外观设置</h2>
            
            <div class="setting-group">
              <h3>主题</h3>
              <div class="setting-item">
                <label class="setting-label">主题模式</label>
                <div class="theme-options">
                  <label class="theme-option">
                    <input 
                      v-model="settings.appearance.theme" 
                      type="radio" 
                      value="light"
                      class="theme-radio"
                    />
                    <span class="theme-preview light"></span>
                    <span class="theme-label">浅色</span>
                  </label>
                  
                  <label class="theme-option">
                    <input 
                      v-model="settings.appearance.theme" 
                      type="radio" 
                      value="dark"
                      class="theme-radio"
                    />
                    <span class="theme-preview dark"></span>
                    <span class="theme-label">深色</span>
                  </label>
                  
                  <label class="theme-option">
                    <input 
                      v-model="settings.appearance.theme" 
                      type="radio" 
                      value="auto"
                      class="theme-radio"
                    />
                    <span class="theme-preview auto"></span>
                    <span class="theme-label">跟随系统</span>
                  </label>
                </div>
              </div>
              
              <div class="setting-item">
                <label class="setting-label">字体大小</label>
                <select v-model="settings.appearance.fontSize" class="setting-select">
                  <option value="small">小</option>
                  <option value="medium">中</option>
                  <option value="large">大</option>
                </select>
              </div>
            </div>
            
            <div class="setting-group">
              <h3>布局</h3>
              <div class="setting-item">
                <label class="setting-label">页面宽度</label>
                <select v-model="settings.appearance.layoutWidth" class="setting-select">
                  <option value="fluid">流式</option>
                  <option value="fixed">固定</option>
                </select>
              </div>
              
              <div class="setting-item">
                <label class="setting-label">显示密度</label>
                <select v-model="settings.appearance.density" class="setting-select">
                  <option value="comfortable">舒适</option>
                  <option value="compact">紧凑</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 修改密码模态框 -->
    <div v-if="showChangePassword" class="modal-overlay">
      <div class="modal-content">
        <h3>修改密码</h3>
        <form @submit.prevent="changePassword" class="password-form">
          <div class="form-group">
            <label>当前密码</label>
            <input 
              v-model="passwordForm.currentPassword" 
              type="password" 
              required
            />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input 
              v-model="passwordForm.newPassword" 
              type="password" 
              required
            />
          </div>
          <div class="form-group">
            <label>确认新密码</label>
            <input 
              v-model="passwordForm.confirmPassword" 
              type="password" 
              required
            />
          </div>
          <div class="modal-actions">
            <button type="button" @click="showChangePassword = false">取消</button>
            <button type="submit" :disabled="changingPassword">
              {{ changingPassword ? '修改中...' : '确认修改' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'

// 设置分类
const sections = [
  { key: 'account', label: '账户设置', icon: '👤' },
  { key: 'notifications', label: '通知设置', icon: '🔔' },
  { key: 'privacy', label: '隐私设置', icon: '🔒' },
  { key: 'security', label: '安全设置', icon: '🛡️' },
  { key: 'appearance', label: '外观设置', icon: '🎨' }
]

const activeSection = ref('account')

// 设置数据
const originalSettings = {
  account: {
    username: '当前用户',
    email: 'user@example.com',
    bio: '这个人很懒，什么都没有写...',
    profileVisibility: 'public',
    postVisibility: 'public',
    allowMessages: 'all'
  },
  notifications: {
    likes: true,
    comments: true,
    follows: true,
    system: true,
    emailImportant: true,
    emailWeekly: false
  },
  privacy: {
    personalizedRecommendations: true,
    dataAnalytics: true,
    searchable: true,
    showOnlineStatus: true
  },
  security: {
    twoFactorEnabled: false,
    autoLogout: '60'
  },
  appearance: {
    theme: 'light',
    fontSize: 'medium',
    layoutWidth: 'fluid',
    density: 'comfortable'
  }
}

const settings = reactive({ ...originalSettings })

// 状态
const saving = ref(false)
const hasChanges = ref(false)
const showChangePassword = ref(false)
const changingPassword = ref(false)
const showDeviceManagement = ref(false)

// 修改密码表单
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 监听设置变化
watch(settings, (newSettings) => {
  hasChanges.value = JSON.stringify(newSettings) !== JSON.stringify(originalSettings)
}, { deep: true })

// 保存设置
const saveSettings = async () => {
  if (!hasChanges.value) return
  
  saving.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 更新原始设置
    Object.assign(originalSettings, JSON.parse(JSON.stringify(settings)))
    hasChanges.value = false
    
    alert('设置保存成功！')
    
  } catch (error) {
    console.error('保存设置失败:', error)
    alert('保存设置失败，请重试')
  } finally {
    saving.value = false
  }
}

// 重置设置
const resetSettings = () => {
  Object.assign(settings, JSON.parse(JSON.stringify(originalSettings)))
  hasChanges.value = false
}

// 修改密码
const changePassword = async () => {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    alert('两次输入的密码不一致')
    return
  }
  
  if (passwordForm.newPassword.length < 6) {
    alert('密码长度不能少于6位')
    return
  }
  
  changingPassword.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    alert('密码修改成功！')
    showChangePassword.value = false
    
    // 清空表单
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    
  } catch (error) {
    console.error('修改密码失败:', error)
    alert('修改密码失败，请重试')
  } finally {
    changingPassword.value = false
  }
}

// 切换两步验证
const toggleTwoFactor = async () => {
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    settings.security.twoFactorEnabled = !settings.security.twoFactorEnabled
    
    alert(`两步验证${settings.security.twoFactorEnabled ? '已启用' : '已禁用'}`)
    
  } catch (error) {
    console.error('切换两步验证失败:', error)
    alert('操作失败，请重试')
  }
}
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px 0;
}

.container {
  max-width: 1200px;
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

.btn-save,
.btn-reset {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  background: white;
  color: #666;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-save:hover:not(:disabled) {
  border-color: #1890ff;
  color: #1890ff;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-reset:hover:not(:disabled) {
  border-color: #ff4d4f;
  color: #ff4d4f;
}

.settings-content {
  display: flex;
  min-height: 600px;
}

.settings-sidebar {
  width: 240px;
  border-right: 1px solid #f0f0f0;
  background: #fafafa;
}

.settings-nav {
  padding: 16px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 12px 24px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s;
  color: #666;
}

.nav-item:hover {
  background: #f0f0f0;
  color: #333;
}

.nav-item.active {
  background: #e6f7ff;
  color: #1890ff;
  border-right: 2px solid #1890ff;
}

.nav-icon {
  margin-right: 12px;
  font-size: 16px;
}

.nav-label {
  font-size: 14px;
  font-weight: 500;
}

.settings-panel {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.settings-section h2 {
  margin: 0 0 24px 0;
  font-size: 20px;
  color: #333;
}

.setting-group {
  margin-bottom: 32px;
}

.setting-group h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.setting-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
}

.setting-label {
  width: 200px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.setting-input,
.setting-textarea,
.setting-select {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
}

.setting-input:focus,
.setting-textarea:focus,
.setting-select:focus {
  border-color: #1890ff;
}

.setting-textarea {
  resize: vertical;
  min-height: 80px;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.setting-toggle {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.toggle-input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

.toggle-input:checked + .toggle-slider {
  background-color: #1890ff;
}

.toggle-input:checked + .toggle-slider:before {
  transform: translateX(20px);
}

.setting-description {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #999;
  line-height: 1.4;
}

.security-action {
  flex: 1;
}

.btn-change-password,
.btn-toggle-two-factor,
.btn-device-management {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  background: white;
  color: #666;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-change-password:hover,
.btn-toggle-two-factor:hover,
.btn-device-management:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.two-factor-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status.enabled {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.status:not(.enabled) {
  background: #fff2f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
}

.theme-options {
  display: flex;
  gap: 16px;
}

.theme-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.theme-radio {
  display: none;
}

.theme-preview {
  width: 60px;
  height: 40px;
  border: 2px solid #d9d9d9;
  border-radius: 6px;
  margin-bottom: 8px;
  transition: all 0.2s;
}

.theme-preview.light {
  background: #ffffff;
}

.theme-preview.dark {
  background: #1f1f1f;
}

.theme-preview.auto {
  background: linear-gradient(90deg, #ffffff 50%, #1f1f1f 50%);
}

.theme-radio:checked + .theme-preview {
  border-color: #1890ff;
}

.theme-label {
  font-size: 12px;
  color: #666;
}

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

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 24px;
  min-width: 400px;
}

.modal-content h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
}

.password-form .form-group {
  margin-bottom: 16px;
}

.password-form label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #333;
}

.password-form input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.modal-actions button {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  background: white;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.modal-actions button[type="submit"] {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

.modal-actions button[type="submit"]:hover:not(:disabled) {
  background: #40a9ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    margin: 0 16px;
  }
  
  .settings-content {
    flex-direction: column;
  }
  
  .settings-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .settings-nav {
    display: flex;
    overflow-x: auto;
    padding: 0;
  }
  
  .nav-item {
    flex-shrink: 0;
    padding: 12px 16px;
  }
  
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .setting-label {
    width: 100%;
  }
  
  .theme-options {
    flex-direction: column;
    gap: 12px;
  }
  
  .modal-content {
    min-width: auto;
    margin: 0 16px;
  }
}
</style>