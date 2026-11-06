# 安装（只做一步）

把 `design-judgment` 这个文件夹复制到下面其中一个位置：

- Qoder：`~/.qoder/skills/design-judgment/`
- Claude Code：`~/.claude/skills/design-judgment/`

复制完，在 Qoder 或 Claude Code 里新开一个会话，skill 就生效了。

也可以用一条命令装（需要先把这个 skill 传到 GitHub）：

```bash
npx skills add <这个 skill 所在的 GitHub 仓库地址> --skill design-judgment -a qoder
```

## 验证装上了

在对话框里输入 `/design-judgment`，或者直接说一句「按设计规范生成一个订单详情页 demo」，如果 agent 开始先读规范再画，就说明装上了。

## 要求

- 电脑上有 Python 3（记录和上传脚本用的就是它，不用另外装东西）。
- 上传功能默认是关的，同意了才会往外传（见 SKILL.md 里的「上传要先同意」）。
