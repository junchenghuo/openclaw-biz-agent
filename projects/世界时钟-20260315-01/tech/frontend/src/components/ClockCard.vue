<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import type { ClockItem } from '../types'

const props = defineProps<{
  clock: ClockItem
}>()

// 解析时间字符串并计算当前时间
const currentTime = ref('')
const currentDate = ref('')
const utcOffset = ref('')

let timer: number | null = null

const updateTime = () => {
  try {
    const date = new Date(props.clock.time)
    const now = new Date()
    
    // 计算时区差异
    const targetDate = new Date(now.toLocaleString('en-US', { timeZone: props.clock.timezone }))
    const utcDate = new Date(now.toLocaleString('en-US', { timeZone: 'UTC' }))
    const diffMinutes = (targetDate.getTime() - utcDate.getTime()) / 60000
    
    const hours = Math.floor(Math.abs(diffMinutes) / 60)
    const minutes = Math.abs(diffMinutes) % 60
    const sign = diffMinutes >= 0 ? '+' : '-'
    utcOffset.value = `UTC${sign}${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
    
    // 格式化时间 HH:mm:ss
    currentTime.value = targetDate.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })
    
    // 格式化日期
    currentDate.value = targetDate.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    })
  } catch (e) {
    console.error('Time parse error:', e)
  }
}

onMounted(() => {
  updateTime()
  timer = window.setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<template>
  <div class="clock-card">
    <div class="clock-city">{{ clock.name }}</div>
    <div class="clock-time">{{ currentTime }}</div>
    <div class="clock-date">{{ currentDate }}</div>
    <div class="clock-timezone">{{ utcOffset }} · {{ clock.timezone }}</div>
  </div>
</template>

<style scoped>
.clock-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.clock-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.clock-city {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.clock-time {
  font-size: 2.5rem;
  font-weight: 700;
  color: #16213e;
  margin-bottom: 8px;
  font-variant-numeric: tabular-nums;
}

.clock-date {
  font-size: 0.875rem;
  color: #666;
  margin-bottom: 8px;
}

.clock-timezone {
  font-size: 0.75rem;
  color: #999;
}
</style>
