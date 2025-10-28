import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { applyReactInVue } from 'veaury'
import App from './App.vue'
import router from './router'
import './styles/index.scss'

// 创建Vue应用
const app = createApp(App)

// 使用状态管理
const pinia = createPinia()
app.use(pinia)

// 使用路由
app.use(router)

// 挂载应用
app.mount('#app')

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue Error:', err)
  console.error('Component:', instance)
  console.error('Info:', info)
}

// 全局属性
app.config.globalProperties.$filters = {
  formatDate(date: string) {
    return new Date(date).toLocaleString('zh-CN')
  },
  truncate(text: string, length: number = 100) {
    if (text.length <= length) return text
    return text.substring(0, length) + '...'
  }
}