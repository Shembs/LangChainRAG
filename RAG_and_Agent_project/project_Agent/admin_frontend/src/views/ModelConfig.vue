<template>
  <div>
    <el-alert
      title="模型名称、温度、嵌入模型等参数在服务启动时已用于构建模型实例，保存后需重启服务方可生效；检索条数 k 在每次检索时读取，保存后即时生效。"
      type="warning"
      :closable="false"
      show-icon
      class="mb"
    />

    <el-card shadow="never">
      <template #header>
        <span>AI 模型与检索参数</span>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="140px"
        v-loading="loading"
      >
        <el-divider content-position="left">模型配置</el-divider>
        <el-form-item label="对话模型名称" prop="chat_model_name">
          <el-input v-model="form.chat_model_name" placeholder="如 deepseek-v4-pro" />
        </el-form-item>
        <el-form-item label="嵌入模型名称" prop="embedding_model_name">
          <el-input v-model="form.embedding_model_name" placeholder="如 text-embedding-v4" />
        </el-form-item>
        <el-form-item label="温度 (temperature)" prop="temperature">
          <el-input-number v-model="form.temperature" :min="0" :max="2" :step="0.1" />
        </el-form-item>

        <el-divider content-position="left">检索与分片参数</el-divider>
        <el-form-item label="检索条数 (k)" prop="k">
          <el-input-number v-model="form.k" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="分片大小" prop="chunk_size">
          <el-input-number v-model="form.chunk_size" :min="50" :max="2000" :step="50" />
        </el-form-item>
        <el-form-item label="分片重叠" prop="chunk_overlap">
          <el-input-number v-model="form.chunk_overlap" :min="0" :max="1999" :step="10" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">保存配置</el-button>
          <el-button @click="loadConfig">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const formRef = ref()
const loading = ref(false)
const saving = ref(false)

const form = reactive({
  chat_model_name: '',
  embedding_model_name: '',
  temperature: 0.7,
  k: 3,
  chunk_size: 200,
  chunk_overlap: 100,
})

const rules = {
  chat_model_name: [{ required: true, message: '请输入对话模型名称', trigger: 'blur' }],
  embedding_model_name: [{ required: true, message: '请输入嵌入模型名称', trigger: 'blur' }],
}

async function loadConfig() {
  loading.value = true
  try {
    const data = await api.get('/model')
    Object.assign(form, data)
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  await formRef.value.validate()
  saving.value = true
  try {
    await api.put('/model', { ...form })
    ElMessage.success('配置已保存（模型参数重启后生效）')
  } catch (e) {
    // 拦截器已提示
  } finally {
    saving.value = false
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.mb {
  margin-bottom: 16px;
}
</style>
