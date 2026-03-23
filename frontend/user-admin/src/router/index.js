import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login/index.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/components/Layout/index.vue'),
    redirect: '/apps',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard/index.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'apps',
        name: 'Apps',
        component: () => import('@/views/Apps/index.vue'),
        meta: { title: '应用中心' }
      },
      {
        path: 'users',
        name: 'UserList',
        component: () => import('@/views/User/index.vue'),
        meta: { title: '用户管理', permission: 'user:read' }
      },
      {
        path: 'roles',
        name: 'RoleList',
        component: () => import('@/views/Role/index.vue'),
        meta: { title: '角色管理', permission: 'role:read' }
      },
      {
        path: 'departments',
        name: 'DeptList',
        component: () => import('@/views/Dept/index.vue'),
        meta: { title: '部门管理', permission: 'dept:read' }
      },
      {
        path: 'permissions',
        name: 'PermissionList',
        component: () => import('@/views/Permission/index.vue'),
        meta: { title: '权限管理', permission: 'permissions:read' }
      },
      {
        path: 'logs',
        name: 'LogsList',
        component: () => import('@/views/Logs/index.vue'),
        meta: { title: '操作日志', permission: 'system:logs' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile/index.vue'),
        meta: { title: '个人中心' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.path === '/login') {
    next()
  } else if (!token) {
    next('/login')
  } else {
    next()
  }
})

export default router
