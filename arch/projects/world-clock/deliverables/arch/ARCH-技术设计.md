# 世界时钟页面 - 技术设计说明书

## 1. 技术选型

### 1.1 前端框架
- **推荐方案**：Vue 3 + Composition API
- **备选方案**：React 18 + Hooks
- **选择理由**：
  - Vue 3 轻量级，响应式简洁
  - Composition API 适合复杂状态管理
  - 社区生态成熟，组件库丰富

### 1.2 关键依赖

| 依赖 | 版本 | 用途 |
|-----|------|-----|
| vue | ^3.4 | 核心框架 |
| dayjs | ^1.11 | 日期时间处理（轻量级） |
| dayjs/plugin/utc | - | UTC 时区支持 |
| dayjs/plugin/timezone | - | 时区转换 |
| dayjs/plugin/localeData | - | 本地化数据 |

### 1.3 构建工具
- **Vite 5** - 快速开发启动与构建

## 2. 项目结构

```
world-clock/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/
│   │   └── styles/
│   │       └── main.css          # 全局样式
│   ├── components/
│   │   ├── AppHeader.vue         # 页面头部
│   │   ├── TimeZoneCard.vue      # 时区卡片
│   │   ├── TimeZoneGrid.vue      # 时区卡片网格
│   │   ├── AddTimeZoneModal.vue  # 添加时区弹窗
│   │   └── SettingsPanel.vue     # 设置面板
│   ├── composables/
│   │   ├── useTimeZones.js       # 时区状态管理
│   │   ├── useSettings.js        # 设置状态管理
│   │   └── useLocalStorage.js    # 本地存储封装
│   ├── utils/
│   │   └── timeUtils.js          # 时间处理工具函数
│   ├── constants/
│   │   └── index.js              # 常量定义（默认时区等）
│   ├── App.vue
│   └── main.js
├── index.html
├── package.json
└── vite.config.js
```

## 3. 组件设计

### 3.1 AppHeader
```
 Props: 无
 Emits: openSettings, openAddModal
```
- 展示标题和操作按钮
- 响应主题切换

### 3.2 TimeZoneCard
```
 Props: 
   - timezone: Object { city, zoneName, utcOffset }
   - showSeconds: Boolean
   - timeFormat: '12h' | '24h'
   - theme: 'light' | 'dark'
 Emits: remove
```
- 显示单个时区的时间信息
- 悬停动画效果
- 删除交互

### 3.3 TimeZoneGrid
```
 Props:
   - timezones: Array<TimeZone>
   - showSeconds: Boolean
   - timeFormat: '12h' | '24h'
   - theme: 'light' | 'dark'
```
- 响应式网格布局（4/3/1-2列）
- 调度 TimeZoneCard 渲染

### 3.4 AddTimeZoneModal
```
 Props: 
   - visible: Boolean
   - usedZones: Array<String> 已使用的时区
 Emits: close, add(timezone)
```
- 搜索过滤时区列表
- 显示未添加的时区选项

### 3.5 SettingsPanel
```
 Props:
   - visible: Boolean
   - timeFormat: '12h' | '24h'
   - showSeconds: Boolean
   - theme: 'light' | 'dark' | 'system'
 Emits: close, update(key, value)
```
- 右侧滑出设置面板

## 4. 数据结构

### 4.1 时区对象
```typescript
interface TimeZone {
  id: string;           // 唯一标识 (zoneName)
  city: string;         // 城市中文名
  zoneName: string;     // IANA 时区名 (Asia/Shanghai)
  utcOffset: string;    // UTC 偏移量 (UTC+8)
}
```

### 4.2 设置对象
```typescript
interface Settings {
  timeFormat: '12h' | '24h';
  showSeconds: boolean;
  theme: 'light' | 'dark' | 'system';
}
```

### 4.3 存储结构 (LocalStorage)
```json
{
  "worldClock_timezones": [
    { "city": "北京", "zoneName": "Asia/Shanghai", "utcOffset": "UTC+8" },
    { "city": "东京", "zoneName": "Asia/Tokyo", "utcOffset": "UTC+9" }
  ],
  "worldClock_settings": {
    "timeFormat": "24h",
    "showSeconds": true,
    "theme": "light"
  }
}
```

## 5. 状态管理

### 5.1 时区状态 (useTimeZones)
- `timezones: Ref<TimeZone[]>` - 当前时区列表
- `addTimeZone(zone)` - 添加时区
- `removeTimeZone(id)` - 删除时区
- `reorderTimeZones(fromIndex, toIndex)` - 拖拽排序

### 5.2 设置状态 (useSettings)
- `settings: Reactive<Settings>` - 设置对象
- `updateSetting(key, value)` - 更新单个设置
- `toggleTheme()` - 切换主题

## 6. 核心逻辑

### 6.1 时间更新
```javascript
// 每秒更新
setInterval(() => {
  currentTime.value = dayjs();
}, 1000);
```

### 6.2 时区时间计算
```javascript
const getZoneTime = (zoneName) => {
  return dayjs().tz(zoneName);
};
```

### 6.3 12/24小时制转换
```javascript
// 24小时制
dayjs().format('HH:mm:ss')

// 12小时制  
dayjs().format('hh:mm:ss A')
```

## 7. 响应式断点

| 屏幕宽度 | 列数 | 备注 |
|---------|------|-----|
| ≥1024px | 4列 | 桌面端 |
| 768-1023px | 3列 | 平板端 |
| <768px | 1-2列 | 移动端 |

## 8. 主题实现

### 8.1 CSS 变量
```css
:root {
  --bg-primary: #f5f7fa;
  --bg-card: #ffffff;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --accent: #3b82f6;
  --danger: #ef4444;
}

[data-theme="dark"] {
  --bg-primary: #0f172a;
  --bg-card: #1e293b;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --accent: #60a5fa;
  --danger: #f87171;
}
```

### 8.2 主题切换逻辑
```javascript
const applyTheme = (theme) => {
  const effectiveTheme = theme === 'system' 
    ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
    : theme;
  document.documentElement.setAttribute('data-theme', effectiveTheme);
};
```

## 9. 默认配置

### 9.1 默认时区列表
```javascript
const DEFAULT_TIMEZONES = [
  { city: '北京', zoneName: 'Asia/Shanghai', utcOffset: 'UTC+8' },
  { city: '东京', zoneName: 'Asia/Tokyo', utcOffset: 'UTC+9' },
  { city: '纽约', zoneName: 'America/New_York', utcOffset: 'UTC-5' },
  { city: '伦敦', zoneName: 'Europe/London', utcOffset: 'UTC+0' },
  { city: '悉尼', zoneName: 'Australia/Sydney', utcOffset: 'UTC+11' },
];
```

### 9.2 默认设置
```javascript
const DEFAULT_SETTINGS = {
  timeFormat: '24h',
  showSeconds: true,
  theme: 'light'
};
```

## 10. 验收标准对照

| 验收项 | 实现方式 |
|--------|---------|
| 默认5个时区 | DEFAULT_TIMEZONES 常量 |
| 每秒更新 | setInterval 1000ms |
| 添加时区 | AddTimeZoneModal + useTimeZones |
| 删除时区 | TimeZoneCard 删除按钮 |
| 本地存储 | useLocalStorage composable |
| 12/24小时制 | SettingsPanel + timeUtils |
| 响应式 | CSS Grid + @media 断点 |
| 明暗主题 | CSS 变量 + applyTheme |

## 11. 开发计划

1. **Phase 1**：项目初始化 + 基础布局
2. **Phase 2**：时区卡片 + 时间更新
3. **Phase 3**：添加/删除时区功能
4. **Phase 4**：设置面板 + 主题切换
5. **Phase 5**：响应式 + 动画优化
6. **Phase 6**：测试与调优