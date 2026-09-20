<template>
  <div class="login-page">
    <el-card class="login-card">
      <div class="login-header">
        <div class="logo">🤖</div>
        <h2>智能客服 · 后台管理</h2>
        <p>知识库上传与 AI 模型调整</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @keyup.enter="handleLogin"
      >
        <el-form-item label="管理员账号" prop="username">
          <el-input v-model="form.username" placeholder="请输入管理员账号" :prefix-icon="User" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="login-btn" :loading="loading" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入管理员账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const data = await api.post('/login', {
      username: form.username,
      password: form.password,
    })
    localStorage.setItem('admin_token', data.token)
    localStorage.setItem('admin_username', data.username)
    ElMessage.success('登录成功')
    router.push({ name: 'kb' })
  } catch (e) {
    // 错误信息已由响应拦截器统一提示
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e2a45 0%, #2a3a5c 100%);
}
.login-card {
  width: 380px;
  border-radius: 16px;
  padding: 8px 12px;
}
.login-header {
  text-align: center;
  margin-bottom: 20px;
}
.login-header .logo {
  font-size: 3rem;
}
.login-header h2 {
  margin: 8px 0 4px;
  color: #2c3e50;
}
.login-header p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.85rem;
}
.login-btn {
  width: 100%;
}
</style>
