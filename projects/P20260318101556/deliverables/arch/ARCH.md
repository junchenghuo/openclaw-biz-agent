# 世界时钟页面 - 技术设计文档

## 1. 项目概述

- **项目ID**: P20260318101556
- **项目名称**: 世界时钟页面
- **项目类型**: 单页面 Web 应用
- **核心功能**: 展示多个国家的实时时钟，圆形钟表设计，每个钟表代表对应国家风格
- **目标用户**: 需要查看多国时间的用户

## 2. 验收标准

- 至少8国时区可用
- 实时更新时间
- 圆形钟表 UI 设计
- 每个时钟有对应国家风格元素

## 3. 技术栈选型

### 前端
- **框架**: React 18 + TypeScript
- **样式**: Tailwind CSS + 自定义 CSS 动画
- **时钟动画**: CSS Animation + Canvas
- **时区处理**: moment-timezone / date-fns-tz
- **构建工具**: Vite

### 后端
- **Runtime**: Node.js 18+
- **框架**: Express.js
- **接口**: RESTful API
- **时区数据**: moment-timezone

## 4. 架构设计

### 4.1 系统架构

```
┌─────────────────┐     ┌─────────────────┐
│   Browser       │────▶│   Express API   │
│   (React SPA)   │◀────│   (Node.js)     │
└─────────────────┘     └─────────────────┘
```

### 4.2 前端架构

```
src/
├── components/
│   ├── WorldClock/         # 主时钟组件
│   ├── ClockDial/          # 圆形钟表盘
│   ├── ClockHand/          # 时针分针秒针
│   └── CountryFlag/        # 国家标识
├── hooks/
│   └── useWorldTime.ts     # 获取世界时间
├── utils/
│   └── timezone.ts         # 时区工具
├── styles/
│   └── clock.css           # 钟表动画样式
├── App.tsx
└── main.tsx
```

### 4.3 后端架构

```
server/
├── index.js                # 入口
├── routes/
│   └── time.js             # 时间接口
├── services/
│   └── timezoneService.ts  # 时区服务
└── data/
    └── countries.js        # 国家配置
```

## 5. 接口设计

### 5.1 获取多国时间

**GET** `/api/world-time`

**响应示例**:
```json
{
  "code": 0,
  "data": [
    {
      "country": "中国",
      "countryCode": "CN",
      "timezone": "Asia/Shanghai",
      "time": "2026-03-18T10:15:57.000+08:00",
      "offset": 8,
      "flag": "🇨🇳"
    },
    {
      "country": "美国",
      "countryCode": "US",
      "timezone": "America/New_York",
      "time": "2026-03-17T21:15:57.000-04:00",
      "offset": -4,
      "flag": "🇺🇸"
    }
  ]
}
```

### 5.2 获取支持时区列表

**GET** `/api/timezones`

**响应示例**:
```json
{
  "code": 0,
  "data": [
    { "value": "Asia/Shanghai", "label": "中国 (北京)", "flag": "🇨🇳" },
    { "value": "America/New_York", "label": "美国 (纽约)", "flag": "🇺🇸" },
    { "value": "Asia/Tokyo", "label": "日本 (东京)", "flag": "🇯🇵" },
    { "value": "Europe/London", "label": "英国 (伦敦)", "flag": "🇬🇧" },
    { "value": "Europe/Paris", "label": "法国 (巴黎)", "flag": "🇫🇷" },
    { "value": "Europe/Berlin", "label": "德国 (柏林)", "flag": "🇩🇪" },
    { "value": "Australia/Sydney", "label": "澳大利亚 (悉尼)", "flag": "🇦🇺" },
    { "value": "Asia/Kolkata", "label": "印度 (孟买)", "flag": "🇮🇳" }
  ]
}
```

## 6. 时区配置

默认8国时区：

| 国家 | 时区 | UTC 偏移 |
|------|------|----------|
| 中国 | Asia/Shanghai | +8 |
| 美国 (纽约) | America/New_York | -5 (EST) |
| 日本 | Asia/Tokyo | +9 |
| 英国 | Europe/London | +0 |
| 法国 | Europe/Paris | +1 |
| 德国 | Europe/Berlin | +1 |
| 澳大利亚 (悉尼) | Australia/Sydney | +11 |
| 韩国 | Asia/Seoul | +9 |

## 7. 前端 UI 设计

### 7.1 布局

- 网格布局：4x2 或响应式适配
- 每个时钟卡片：圆形，直径约 200px
- 背景：深色主题，星空效果

### 7.2 钟表设计

- 12小时制表盘
- 指针：时针、分针、秒针（红色）
- 刻度：数字 + 刻度线
- 国家风格：
  - 中国：红色主调，龙纹元素
  - 美国：蓝红配色，星星元素
  - 日本：樱花元素，和风
  - 其他：各国配色

### 7.3 动画效果

- 秒针每秒平滑转动
- 整点报时微光效果
- 卡片 hover 放大效果

## 8. 部署方案

### 8.1 环境

- 前端：静态部署（可托管于任意静态服务器）
- 后端：Node.js 服务

### 8.2 端口

- 前端: 5173 (Vite dev)
- 后端: 3000

## 9. 开发里程碑

1. **需求原型** - 完成 UI 原型设计
2. **架构** - 本文档
3. **开发联调** - 前后端联调完成
4. **部署提测** - 部署到测试环境
5. **验收** - 满足8国时区可用标准

## 10. 风险与注意事项

- 夏令时处理：moment-timezone 自动处理
- 时区数据准确性：使用权威时区库
- 前端实时更新：每秒轮询或 WebSocket