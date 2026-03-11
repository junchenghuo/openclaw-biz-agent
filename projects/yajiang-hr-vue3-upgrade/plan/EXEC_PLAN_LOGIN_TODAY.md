# Login 项目今日执行排期（跨角色）

日期：2026-03-05
负责人：PM（统一调度）

## 目标
今日完成从需求澄清到技术方案冻结，并启动前后端开发与测试准备，确保联调路径打通。

## 排期

### 10:20 - 11:00｜PM（进行中）
- 完成 PRD 与验收标准定稿
- 产物：`projects/yajiang-hr-vue3-upgrade/product/PRD_LOGIN.md`

### 11:00 - 12:00｜架构（arch）
- 产出登录架构说明、接口契约、错误码规范
- 产物：`projects/yajiang-hr-vue3-upgrade/architecture/ARCH_LOGIN.md`、`projects/yajiang-hr-vue3-upgrade/tech/backend/OPENAPI.yaml`

### 13:30 - 16:30｜前端（fe）+ 后端（be）并行
- FE：登录页实现（校验、状态反馈、错误处理）
- BE：登录接口实现（按 OpenAPI）
- 产物：`projects/yajiang-hr-vue3-upgrade/tech/frontend/UI_NOTES.md`、`projects/yajiang-hr-vue3-upgrade/tech/backend/IMPLEMENTATION_NOTES.md`

### 16:30 - 18:00｜测试（qa）
- 基于 FE+BE 结果完成测试计划与联调验证
- 产物：`projects/yajiang-hr-vue3-upgrade/qa/TEST_PLAN_LOGIN.md`

### 18:00 - 18:30｜运维（ops）
- 输出部署说明、环境变量与监控告警最小集
- 产物：`projects/yajiang-hr-vue3-upgrade/ops/DEPLOY_LOGIN.md`

## 验收口径（今日）
1. 契约冻结：OpenAPI 可用于联调
2. 前后端主流程可跑通（至少 dev 环境）
3. 测试计划可执行，覆盖正常/异常路径
4. 运维交付部署与监控文档
