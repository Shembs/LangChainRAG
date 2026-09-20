<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="brand">
        <span class="brand-logo">🤖</span>
        <span class="brand-name">后台管理</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="menu"
        router
        background-color="#1e2a45"
        text-color="#e8edf5"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/kb">
          <el-icon><FolderOpened /></el-icon>
          <span>知识库管理</span>
        </el-menu-item>
        <el-menu-item index="/model">
          <el-icon><Setting /></el-icon>
          <span>模型调整</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-title">{{ route.meta.title }}</div>
        <div class="header-right">
          <span class="username">{{ username }}</span>
          <el-button size="small" text @click="handleLogout">
            <el-icon><SwitchButton /></el-icon> 退出登录
          </el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { FolderOpened, Setting, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)
const username = localStorage.getItem('admin_username') || 'admin'

async function handleLogout() {
  await ElMessageBox.confirm('确认退出登录吗？', '提示', {
    confirmButtonText: '退出',
    cancelButtonText: '取消',
    type: 'warning',
  })
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_username')
  router.push({ name: 'login' })
}
</script>

<style scoped>
.layout {
  height: 100%;
}
.aside {
  background-color: #1e2a45;
}
.brand {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  font-weight: 600;
}
.brand-logo {
  font-size: 1.4rem;
}
.menu {
  border-right: none;
}
.header {
  background: #fff;
  border-bottom: 1px solid #e6e8eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.username {
  color: #7f8c8d;
  font-size: 0.9rem;
}
.main {
  background: #f5f6fa;
}
</style>
