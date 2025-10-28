<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-card">
        <div class="register-header">
          <h1 class="register-title">注册贴吧</h1>
          <p class="register-subtitle">创建您的贴吧账户，开始精彩旅程</p>
        </div>

        <form @submit.prevent="handleRegister" class="register-form">
          <div class="form-row">
            <div class="form-group">
              <label for="username" class="form-label">用户名</label>
              <input
                id="username"
                v-model="form.username"
                type="text"
                class="form-control"
                placeholder="请输入用户名"
                required
                @blur="checkUsername"
              />
              <div v-if="usernameError" class="error-text">{{ usernameError }}</div>
            </div>

            <div class="form-group">
              <label for="nickname" class="form-label">昵称</label>
              <input
                id="nickname"
                v-model="form.nickname"
                type="text"
                class="form-control"
                placeholder="请输入昵称"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="email" class="form-label">邮箱地址</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              class="form-control"
              placeholder="请输入邮箱地址"
              required
              @blur="checkEmail"
            />
            <div v-if="emailError" class="error-text">{{ emailError }}</div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="password" class="form-label">密码</label>
              <input
                id="password"
                v-model="form.password"
                type="password"
                class="form-control"
                placeholder="请输入密码"
                required
                @input="validatePassword"
              />
            </div>

            <div class="form-group">
              <label for="confirmPassword" class="form-label">确认密码</label>
              <input
                id="confirmPassword"
                v-model="form.confirmPassword"
                type="password"
                class="form-control"
                placeholder="请再次输入密码"
                required
                @input="validatePassword"
              />
            </div>
          </div>

          <div v-if="passwordError" class="error-text">{{ passwordError }}</div>

          <div class="form-group">
            <label class="checkbox">
              <input type="checkbox" v-model="agreed" required />
              <span>我已阅读并同意</span>
            </label>
            <a href="#" class="terms-link">《用户协议》</a>
            <span>和</span>
            <a href="#" class="terms-link">《隐私政策》</a>
          </div>

          <button type="submit" class="register-btn" :disabled="loading || !agreed">
            <span v-if="loading" class="loading"></span>
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </form>

        <div class="register-footer">
          <p>已有账户？
            <router-link to="/login" class="login-link">立即登录</router-link>
          </p>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/auth'

const router = useRouter()

const form = reactive({
  username: '',
  nickname: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const agreed = ref(false)
const loading = ref(false)
const error = ref('')
const usernameError = ref('')
const emailError = ref('')
const passwordError = ref('')

// 检查用户名
const checkUsername = async () => {
  if (!form.username) {
    usernameError.value = '用户名不能为空'
    return
  }

  if (form.username.length < 3) {
    usernameError.value = '用户名至少需要3个字符'
    return
  }

  if (!/^[a-zA-Z0-9_]+$/.test(form.username)) {
    usernameError.value = '用户名只能包含字母、数字和下划线'
    return
  }

  usernameError.value = ''
}

// 检查邮箱
const checkEmail = () => {
  if (!form.email) {
    emailError.value = '邮箱不能为空'
    return
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.email)) {
    emailError.value = '请输入有效的邮箱地址'
    return
  }

  emailError.value = ''
}

// 验证密码
const validatePassword = () => {
  if (!form.password) {
    passwordError.value = '密码不能为空'
    return
  }

  if (form.password.length < 6) {
    passwordError.value = '密码至少需要6个字符'
    return
  }

  if (form.password !== form.confirmPassword) {
    passwordError.value = '两次输入的密码不一致'
    return
  }

  passwordError.value = ''
}

const handleRegister = async () => {
  // 验证表单
  checkUsername()
  checkEmail()
  validatePassword()

  if (usernameError.value || emailError.value || passwordError.value) {
    return
  }

  if (!agreed.value) {
    error.value = '请同意用户协议和隐私政策'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await authApi.register({
      username: form.username,
      email: form.email,
      password: form.password,
      nickname: form.nickname || form.username
    })

    // 注册成功，跳转到登录页
    router.push('/login?registered=true')
  } catch (err: any) {
    error.value = err.response?.data?.message || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.register-container {
  width: 100%;
  max-width: 500px;
}

.register-card {
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-title {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.register-subtitle {
  color: #666;
  font-size: 14px;
}

.register-form {
  margin-bottom: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.error-text {
  color: #ff4d4f;
  font-size: 12px;
  margin-top: 4px;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.checkbox input {
  width: 16px;
  height: 16px;
}

.terms-link {
  color: #667eea;
  text-decoration: none;
  margin: 0 4px;
}

.terms-link:hover {
  text-decoration: underline;
}

.register-btn {
  width: 100%;
  padding: 12px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
}

.register-btn:hover:not(:disabled) {
  background: #5a6fd8;
}

.register-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.loading {
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.register-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.register-footer p {
  color: #666;
  font-size: 14px;
}

.login-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.login-link:hover {
  text-decoration: underline;
}

.error-message {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #ff4d4f;
  padding: 12px;
  border-radius: 6px;
  margin-top: 16px;
  font-size: 14px;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
  
  .register-card {
    padding: 24px;
  }
}
</style>