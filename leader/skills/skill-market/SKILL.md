# Skill: Skill Market Fetcher

## 使用场景
- 需要检索远程技能仓库（GitHub、内部 skill market 等）并快速下载到指定角色工作区。

## 使用步骤
1. 记录申请：在 `/Users/imac/midCreate/openclaw-workspaces/ai-team/log/skilsLog` 中写入新行，状态 `pending`，注明“技能检索”。
2. 搜索：
   - GitHub：`gh search repos <keyword> --topic opencode-skill`。
   - 内部列表：参考 `/Users/imac/openclaw/openclaw-main/extensions` 目录。
3. 下载：
   ```bash
   cd /Users/imac/midCreate/openclaw-workspaces/ai-team/<role>/skills
   git clone <repo_url> <skill-name>
   # 或者
   curl -L <zip_url> -o /tmp/skill.zip && unzip /tmp/skill.zip -d <skill-name>
   ```
4. 审核并启用：检查 `SKILL.md`，根据需要更新配置（如 `skills-lock.json`）。
5. 更新日志状态为 `installed`，附带来源和 commit。

## 额外注意
- 所有下载的第三方技能需在日志备注：来源、版本、license。
- 若技能包含执行脚本，先在 sandbox 测试，确认无恶意行为再分发。
