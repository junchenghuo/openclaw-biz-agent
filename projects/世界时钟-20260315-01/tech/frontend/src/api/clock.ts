import axios from 'axios'
import type { ApiResponse, ClockItem, ConvertRequest, ConvertResponse } from './types'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 获取时钟列表
export async function getClockList(): Promise<ClockItem[]> {
  const response = await api.get<ApiResponse<ClockItem[]>>('/clocks')
  if (response.data.code === 0) {
    return response.data.data
  }
  throw new Error(response.data.message || '获取时钟列表失败')
}

// 获取指定时区时间
export async function getClockByTimezone(timezone: string): Promise<ClockItem> {
  const response = await api.get<ApiResponse<ClockItem>>(`/clocks/${encodeURIComponent(timezone)}`)
  if (response.data.code === 0) {
    return response.data.data
  }
  throw new Error(response.data.message || '获取时区时间失败')
}

// 时区搜索
export async function searchTimezones(keyword: string): Promise<ClockItem[]> {
  const response = await api.get<ApiResponse<ClockItem[]>>('/clocks/search', {
    params: { q: keyword }
  })
  if (response.data.code === 0) {
    return response.data.data
  }
  throw new Error(response.data.message || '搜索时区失败')
}

// 时间换算
export async function convertTime(data: ConvertRequest): Promise<ConvertResponse> {
  const response = await api.post<ApiResponse<ConvertResponse>>('/convert', data)
  if (response.data.code === 0) {
    return response.data.data
  }
  throw new Error(response.data.message || '时间换算失败')
}

export default api
