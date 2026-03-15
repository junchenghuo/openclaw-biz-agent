export interface ClockItem {
  id: number
  name: string
  timezone: string
  time: string
}

export interface ApiResponse<T = any> {
  code: number
  data: T
  message?: string
}

export interface ConvertRequest {
  time: string
  from: string
  to: string
}

export interface ConvertResponse {
  time: string
}
