import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '../utils/auth'
import MainLayout from '../layouts/MainLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  // 所有需登录的页面包裹在统一布局中
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/home',
      },
      {
        path: 'home',
        name: 'Home',
        component: () => import('../views/Nav.vue'),
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('../views/Chat.vue'),
      },
      {
        path: 'rag',
        name: 'Rag',
        component: () => import('../views/Rag.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  if (to.matched.some(r => r.meta.requiresAuth)) {
    if (!getToken()) {
      next({ name: 'Login' })
      return
    }
  }

  if (to.name === 'Login' && getToken()) {
    next({ name: 'Home' })
    return
  }

  next()
})

export default router
