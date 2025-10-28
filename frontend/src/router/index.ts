import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// 页面组件导入
const Home = () => import('@/views/Home.vue')
const Login = () => import('@/views/auth/Login.vue')
const Register = () => import('@/views/auth/Register.vue')
const TiebaList = () => import('@/views/tieba/TiebaList.vue')
const TiebaDetail = () => import('@/views/tieba/TiebaDetail.vue')
const PostDetail = () => import('@/views/posts/PostDetail.vue')
const CreatePost = () => import('@/views/posts/CreatePost.vue')
const UserProfile = () => import('@/views/user/UserProfile.vue')
const Notifications = () => import('@/views/user/Notifications.vue')
const Settings = () => import('@/views/user/Settings.vue')
const Search = () => import('@/views/Search.vue')
const NotFound = () => import('@/views/NotFound.vue')

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: '首页 - 贴吧百科',
      keepAlive: true
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      title: '登录',
      requiresGuest: true
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: {
      title: '注册',
      requiresGuest: true
    }
  },
  {
    path: '/tieba',
    name: 'TiebaList',
    component: TiebaList,
    meta: {
      title: '贴吧列表',
      keepAlive: true
    }
  },
  {
    path: '/tieba/:id',
    name: 'TiebaDetail',
    component: TiebaDetail,
    meta: {
      title: '贴吧详情',
      requiresAuth: true
    }
  },
  {
    path: '/post/:id',
    name: 'PostDetail',
    component: PostDetail,
    meta: {
      title: '帖子详情',
      keepAlive: true
    }
  },
  {
    path: '/post/create',
    name: 'CreatePost',
    component: CreatePost,
    meta: {
      title: '创建帖子',
      requiresAuth: true
    }
  },
  {
    path: '/user/:id',
    name: 'UserProfile',
    component: UserProfile,
    meta: {
      title: '用户主页',
      requiresAuth: true
    }
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: Notifications,
    meta: {
      title: '消息通知',
      requiresAuth: true
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: {
      title: '设置',
      requiresAuth: true
    }
  },
  {
    path: '/search',
    name: 'Search',
    component: Search,
    meta: {
      title: '搜索',
      keepAlive: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: {
      title: '页面不存在'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title as string
  }
  
  next()
})

export default router