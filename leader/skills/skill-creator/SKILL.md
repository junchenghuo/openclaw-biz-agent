# Skill: Internal Skill Creator

## 使用场景
- 任何机器人提出“缺少技能”或需要新的自动化能力时，由 Team Leader 使用此技能确定需求并生成对应的 skill 脚手架。

## 流程
1. 在 `/Users/imac/midCreate/openclaw-workspaces/ai-team/log/skilsLog` 中记录申请（时间、申请人、场景、状态=pending）。
2. 审核通过后，在目标工作区的 `skills/<skill-name>/` 目录创建 `SKILL.md` 与脚本，或引用官方模板。
3. 更新日志状态为 `approved`，并附上安装路径。
4. 通知申请人使用 `/skill load <skill-name>` 或在 `skills-lock.json` 中声明。

## 参考命令
```bash
# 复制现有模板
cp -R /Users/imac/openclaw/openclaw-main/extensions/example-skill \
      /Users/imac/midCreate/openclaw-workspaces/ai-team/<role>/skills/<skill-name>

# 安装依赖
cd /Users/imac/midCreate/openclaw-workspaces/ai-team/<role>/skills/<skill-name>
```

## 输出要求
- `SKILL.md`：描述触发条件、使用方式、示例。
- 若含脚本，提供 `scripts/` 与 README。
- 在申请日志中将状态记为 `installed` 并附安装 commit/路径。
