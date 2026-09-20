import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { public: true, title: '登录' },
  },
  {
    path: '/',
    component: () => import('../views/AdminLayout.vue'),
    redirect: '/kb',
    children: [
      {
        path: 'kb',
        name: 'kb',
        component: () => import('../views/KnowledgeBase.vue'),
        meta: { title: '知识库管理' },
      },
      {
        path: 'model',
        name: 'model',
        component: () => import('../views/ModelConfig.vue'),
        meta: { title: '模型调整' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 登录守卫
router.beforeEach((to) => {
  const token = localStorage.getItem('admin_token')
  if (!to.meta.public && !token) {
    return { name: 'login' }
  }
  if (to.name === 'login' && token) {
    return { name: 'kb' }
  }
  document.title = to.meta.title ? `${to.meta.title} · 后台管理` : '智能客服 · 后台管理'
  return true
})

export default router
