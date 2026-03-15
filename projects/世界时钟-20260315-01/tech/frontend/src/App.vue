<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ClockCard from './components/ClockCard.vue'
import { getClockList, searchTimezones } from './api/clock'
import type { ClockItem } from './types'

const clocks = ref<ClockItem[]>([])
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')
const searchResults = ref<ClockItem[]>([])
const showSearch = ref(false)

// 默认8个时区
const defaultClocks: ClockItem[] = [
  { id: 1, name: '北京', timezone: 'Asia/Shanghai', time: '' },
  { id: 2, name: '东京', timezone: 'Asia/Tokyo', time: '' },
  { id: 3, name: '伦敦', timezone: 'Europe/London', time: '' },
  { id: 4, name: '纽约', timezone: 'America/New_York', time: '' },
  { id: 5, name: '巴黎', timezone: 'Europe/Paris', time: '' },
  { id: 6, name: '悉尼', timezone: 'Australia/Sydney', time: '' },
  { id: 7, name: '迪拜', timezone: 'Asia/Dubai', time: '' },
  { id: 8, name: '洛杉矶', timezone: 'America/Los_Angeles', time: '' }
]

const fetchClocks = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await getClockList()
    if (data && data.length > 0) {
      clocks.value = data
    } else {
      // API无数据时使用默认
      clocks.value = defaultClocks.map(c => ({
        ...c,
        time: new Date().toISOString()
      }))
    }
  } catch (e) {
    console.warn('API unavailable, using default clocks')
    // API不可用时使用默认
    clocks.value = defaultClocks.map(c => ({
      ...c,
      time: new Date().toISOString()
    }))
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }
  try {
    searchResults.value = await searchTimezones(searchQuery.value)
  } catch (e) {
    // 搜索失败时忽略
    searchResults.value = []
  }
}

const addClock = (clock: ClockItem) => {
  if (!clocks.value.find(c => c.timezone === clock.timezone)) {
    clocks.value.push({ ...clock, id: Date.now(), time: new Date().toISOString() })
  }
  searchQuery.value = ''
  searchResults.value = []
  showSearch.value = false
}

onMounted(() => {
  fetchClocks()
})
</script>

<template>
  <div class="app">
    <header class="header">
      <h1 class="title">🌍 世界时钟</h1>
      <button class="search-btn" @click="showSearch = !showSearch">
        🔍 添加城市
      </button>
    </header>

    <!-- 搜索面板 -->
    <div v-if="showSearch" class="search-panel">
      <input 
        v-model="searchQuery"
        @input="handleSearch"
        type="text" 
        placeholder="搜索城市或时区..."
        class="search-input"
      />
      <div v-if="searchResults.length > 0" class="search-results">
        <div 
          v-for="item in searchResults" 
          :key="item.timezone"
          class="search-item"
          @click="addClock(item)"
        >
          {{ item.name }} ({{ item.timezone }})
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      加载中...
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <!-- 时钟网格 -->
    <div v-else class="clock-grid">
      <ClockCard 
        v-for="clock in clocks" 
        :key="clock.id" 
        :clock="clock"
      />
    </div>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #fff;
}

.search-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: #fff;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
}

.search-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.search-panel {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
}

.search-results {
  margin-top: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.search-item {
  padding: 12px;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.2s;
}

.search-item:hover {
  background: #f5f5f5;
}

.loading, .error {
  text-align: center;
  color: #fff;
  font-size: 1.1rem;
  padding: 40px;
}

.error {
  color: #ff6b6b;
}

/* 桌面端 4x2 网格 */
.clock-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

/* 平板端 2x4 */
@media (max-width: 1024px) {
  .clock-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 移动端 单列 */
@media (max-width: 640px) {
  .app {
    padding: 16px;
  }
  
  .header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .clock-grid {
    grid-template-columns: 1fr;
  }
  
  .title {
    font-size: 1.5rem;
  }
}
</style>
