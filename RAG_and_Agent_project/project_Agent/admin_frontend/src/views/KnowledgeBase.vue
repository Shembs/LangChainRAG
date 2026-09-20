<template>
  <div>
    <el-card shadow="never" class="mb">
      <template #header>
        <span>上传知识文档</span>
      </template>
      <el-upload
        drag
        multiple
        :show-file-list="false"
        :http-request="handleUpload"
        accept=".txt,.pdf,.docx"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 .txt / .pdf / .docx，上传后自动重建向量库索引</div>
        </template>
      </el-upload>
    </el-card>

    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>已上传文件（{{ files.length }}）</span>
          <div>
            <el-button size="small" :loading="refreshing" @click="handleRefresh">
              <el-icon><Refresh /></el-icon> 重建索引
            </el-button>
            <el-button size="small" :loading="loading" @click="loadFiles">
              <el-icon><RefreshRight /></el-icon> 刷新列表
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="files" v-loading="loading" empty-text="暂无已上传文件">
        <el-table-column label="文件名" prop="name" min-width="240">
          <template #default="{ row }">
            <span>{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="大小" prop="size_kb" width="120">
          <template #default="{ row }">{{ row.size_kb }} KB</template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button size="small" type="danger" text @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Refresh, RefreshRight } from '@element-plus/icons-vue'
import api from '../api'

const files = ref([])
const loading = ref(false)
const refreshing = ref(false)

async function loadFiles() {
  loading.value = true
  try {
    files.value = await api.get('/kb/files')
  } finally {
    loading.value = false
  }
}

async function handleUpload({ file }) {
  const formData = new FormData()
  formData.append('files', file)
  try {
    const res = await api.post('/kb/upload', formData)
    const saved = res.saved?.length || 0
    const failed = res.failed?.length || 0
    if (res.refresh?.success) {
      ElMessage.success(`已上传 ${saved} 个文件，知识库索引已更新`)
    } else if (saved) {
      ElMessage.warning(`文件已保存 ${saved} 个，但索引更新失败`)
    }
    if (failed) {
      ElMessage.error(`${failed} 个文件上传失败（仅支持 .txt/.pdf/.docx）`)
    }
    await loadFiles()
  } catch (e) {
    // 拦截器已提示
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除文件「${row.name}」吗？`, '提示', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
  const res = await api.delete(`/kb/files/${encodeURIComponent(row.name)}`)
  if (res.success) {
    ElMessage.success(res.message)
    await loadFiles()
  } else {
    ElMessage.error(res.message)
  }
}

async function handleRefresh() {
  refreshing.value = true
  try {
    const res = await api.post('/kb/refresh')
    if (res.success) {
      ElMessage.success('索引重建成功')
    } else {
      ElMessage.error(res.message)
    }
  } finally {
    refreshing.value = false
  }
}

onMounted(loadFiles)
</script>

<style scoped>
.mb {
  margin-bottom: 16px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
