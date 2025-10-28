<template>
  <div class="not-found-page">
    <div class="container">
      <div class="not-found-content">
        <div class="error-code">404</div>
        <h1 class="error-title">页面未找到</h1>
        <p class="error-desc">
          抱歉，您访问的页面不存在或已被移动。
        </p>
        <div class="error-actions">
          <router-link to="/" class="btn btn-primary">
            返回首页
          </router-link>
          <button class="btn btn-outline" @click="goBack">
            返回上页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}
</script>

<style scoped>
.not-found-page {
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.not-found-content {
  text-align: center;
  max-width: 500px;
  margin: 0 auto;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: #1890ff;
  line-height: 1;
  margin-bottom: 16px;
}

.error-title {
  font-size: 32px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.error-desc {
  font-size: 16px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 32px;
}

.error-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn {
  padding: 12px 24px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid;
}

.btn-primary {
  background: #1890ff;
  border-color: #1890ff;
  color: #fff;
}

.btn-primary:hover {
  background: #40a9ff;
  border-color: #40a9ff;
}

.btn-outline {
  background: transparent;
  border-color: #d9d9d9;
  color: #666;
}

.btn-outline:hover {
  border-color: #1890ff;
  color: #1890ff;
}

@media (max-width: 768px) {
  .error-code {
    font-size: 80px;
  }
  
  .error-title {
    font-size: 24px;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 100%;
    max-width: 200px;
  }
}
</style>