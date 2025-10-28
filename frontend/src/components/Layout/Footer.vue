<template>
  <footer class="footer">
    <div class="container">
      <div class="footer-content">
        <!-- 网站信息 -->
        <div class="footer-section">
          <h3 class="footer-title">贴吧应用</h3>
          <p class="footer-desc">
            一个基于Vue + React + Django的现代化贴吧社区平台
          </p>
          <div class="social-links">
            <a href="#" class="social-link">GitHub</a>
            <a href="#" class="social-link">文档</a>
            <a href="#" class="social-link">反馈</a>
          </div>
        </div>

        <!-- 快速链接 -->
        <div class="footer-section">
          <h4 class="footer-subtitle">快速链接</h4>
          <ul class="footer-links">
            <li><router-link to="/" class="footer-link">首页</router-link></li>
            <li><router-link to="/tieba" class="footer-link">贴吧</router-link></li>
            <li><router-link to="/hot" class="footer-link">热门</router-link></li>
            <li><router-link to="/search" class="footer-link">搜索</router-link></li>
          </ul>
        </div>

        <!-- 帮助中心 -->
        <div class="footer-section">
          <h4 class="footer-subtitle">帮助中心</h4>
          <ul class="footer-links">
            <li><a href="#" class="footer-link">使用指南</a></li>
            <li><a href="#" class="footer-link">常见问题</a></li>
            <li><a href="#" class="footer-link">社区规范</a></li>
            <li><a href="#" class="footer-link">联系我们</a></li>
          </ul>
        </div>

        <!-- 关于我们 -->
        <div class="footer-section">
          <h4 class="footer-subtitle">关于我们</h4>
          <ul class="footer-links">
            <li><a href="#" class="footer-link">团队介绍</a></li>
            <li><a href="#" class="footer-link">更新日志</a></li>
            <li><a href="#" class="footer-link">隐私政策</a></li>
            <li><a href="#" class="footer-link">服务条款</a></li>
          </ul>
        </div>
      </div>

      <!-- 版权信息 -->
      <div class="footer-bottom">
        <div class="copyright">
          © 2024 贴吧应用. 保留所有权利.
        </div>
        <div class="footer-stats">
          <span>在线用户: {{ onlineUsers }}</span>
          <span>总帖子数: {{ totalPosts }}</span>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const onlineUsers = ref(0)
const totalPosts = ref(0)

// 模拟获取统计数据
onMounted(() => {
  // 这里可以调用API获取实时数据
  onlineUsers.value = Math.floor(Math.random() * 1000) + 100
  totalPosts.value = Math.floor(Math.random() * 10000) + 1000
})
</script>

<style scoped>
.footer {
  background: #001529;
  color: #fff;
  margin-top: auto;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
  padding: 40px 0;
}

.footer-section {
  display: flex;
  flex-direction: column;
}

.footer-title {
  font-size: 20px;
  font-weight: bold;
  color: #1890ff;
  margin-bottom: 16px;
}

.footer-subtitle {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #fff;
}

.footer-desc {
  color: #8c8c8c;
  line-height: 1.6;
  margin-bottom: 20px;
}

.social-links {
  display: flex;
  gap: 12px;
}

.social-link {
  color: #8c8c8c;
  text-decoration: none;
  transition: color 0.3s;
}

.social-link:hover {
  color: #1890ff;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 8px;
}

.footer-link {
  color: #8c8c8c;
  text-decoration: none;
  transition: color 0.3s;
  font-size: 14px;
}

.footer-link:hover {
  color: #1890ff;
}

.footer-bottom {
  border-top: 1px solid #434343;
  padding: 20px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #8c8c8c;
  font-size: 14px;
}

.footer-stats {
  display: flex;
  gap: 20px;
}

@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    gap: 30px;
    padding: 30px 0;
  }
  
  .footer-bottom {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  
  .footer-stats {
    flex-direction: column;
    gap: 8px;
  }
}
</style>