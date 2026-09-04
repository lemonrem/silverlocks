# Silverlocks

[English](README.md)

Silverlocks 是一个轻量、无 Hook 的 Codex Skill。它让开发流程随任务规模变化：小而明确的修改直接完成；风险高、跨模块或可能跨会话的工作先经过 Plan Gate；测试、构建、重启、专业 Skills 和连续性记录只在确有价值时使用。

它是独立 Skill，不是 Plugin。安装后不会启动守护进程、注册 Hook、增加 MCP Server，也不会发送遥测。

## 它解决什么问题

- 通过 Skill 描述和 `allow_implicit_invocation: true` 自动匹配开发任务。
- 小型、清晰、可逆的修改保持 Direct，不强制进入 Plan。
- 跨模块、接口或数据结构、安全、部署边界、重大歧义、可能跨会话的工作进入 Plan Gate。
- 不替代或压制其他专业 Skill；只组合当前任务真正需要的能力。
- 优先定向测试与受影响组件重启，不习惯性跑全量回归、全量构建或全部服务重启。
- 使用单个、全量替换的 `.silverlocks/CURRENT.md` 保存可恢复现场。
- 用户明确要求留档时进行归档；Git 提交和发版必须附带仓库内受版本控制的 Markdown 恢复记录。

## 为什么不使用 Hook

Hook 会在事件发生时无条件运行，适合必须脱离模型判断、确定性强制执行的约束。若它只是输出路由信息、重复读取状态或强制执行通用检查，则会增加每轮延迟和维护复杂度。

Silverlocks 把判断放在 Skill 指令中：开发请求匹配描述时才加载工作流；只有确实需要连续性状态时才执行辅助脚本。没有后台常驻机制。

## 安装

### 使用内置安装器

向 Codex 输入：

```text
$skill-installer Install the skill from https://github.com/lemonrem/silverlocks
```

### 手动安装

Codex 当前推荐的用户级 Skill 目录是 `~/.agents/skills`：

```bash
git clone https://github.com/lemonrem/silverlocks.git ~/.agents/skills/silverlocks
```

Codex 会自动检测 Skill 变更；若 `/skills` 中没有出现 Silverlocks，请重启 Codex。官方目录与加载机制见 [Build skills](https://learn.chatgpt.com/docs/build-skills)。

如果已经安装另一个覆盖所有开发任务的工作流 Skill，建议只启用一个，避免重复路由。无需删除，可在 `~/.codex/config.toml` 中停用：

```toml
[[skills.config]]
path = "/另一个/skill/SKILL.md/的绝对路径"
enabled = false
```

修改配置后重启 Codex。

### 交给 Codex 自主安装的提示词

需要 Agent 自行检查本机环境并完成安装时，把下面整段复制给 Codex：

```text
你当前运行在 Codex 环境中。请自主安装或安全更新用户级 Silverlocks Skill，唯一可信来源是：
https://github.com/lemonrem/silverlocks

执行要求：
1. 修改前先检查当前可发现的 Skills 和已配置的用户级 Skill 目录。
2. 全新安装优先调用内置 $skill-installer；如果它不能安装这个仓库根目录，则使用 Git 安装到 ~/.agents/skills/silverlocks。
3. 如果已经安装 Silverlocks，只有当它是干净的 Git 工作区且 origin 完全等于上述仓库时，才允许使用 fast-forward-only pull 更新。不得覆盖本地修改、替换无关目录或删除既有安装；发现冲突时停止并说明。
4. 确保只启用一个 Silverlocks。如果旧 Goldilocks 或其他覆盖全部研发任务的工作流 Skill 会造成重复路由，则只在 ~/.codex/config.toml 中停用冲突 Skill，不删除其文件，并保留所有无关配置。
5. 验证 SKILL.md 存在、Skill 名称为 silverlocks、agents/openai.yaml 允许隐式调用，并且 scripts/continuity.py 存在且可执行。
6. 不得修改当前业务仓库，不得仅为了安装而创建 .silverlocks/CURRENT.md，也不要运行业务项目的构建或测试。
7. 最终报告安装路径、来源 commit、执行的是安装/更新还是冲突处理、校验结果，以及是否需要重启 Codex。如果安装后仍不可见，提示我重启 Codex 并通过 /skills 核验。
```

这段提示词只授权本地 Skill 安装和安全处理冲突配置，不授权修改业务仓库或执行任何外部部署。

## 使用与更新

Silverlocks 默认允许在开发任务中隐式加载，也可以显式调用：

```text
$silverlocks 诊断这个问题并实现最小且安全的修复
```

手动 Git 安装可这样更新：

```bash
git -C ~/.agents/skills/silverlocks pull --ff-only
```

Codex 加载的是本地安装副本；GitHub 上有新提交不等于本地已经更新。拉取后若未自动生效，重启 Codex。

## 与仓库无关的运行方式

Silverlocks 安装在用户级目录，与具体仓库无关。打开任意 Git 仓库即可使用同一套研发工作流，不需要把本仓库文件复制进业务项目，也不依赖特定业务仓库、技术栈、固定目录结构或预先存在的 `AGENTS.md`。

新会话第一次收到开发请求时，Codex 会通过已安装 Skill 的辅助脚本定位当前仓库。如果可恢复任务已经存在 `<当前仓库>/.silverlocks/CURRENT.md`，则只读取一次；如果较大任务可能跨会话且尚无快照，则可以通过辅助脚本创建。能在当前会话完成的小任务不会生成它。

状态始终属于当前打开的工作区：

```text
任意项目/
└── .silverlocks/
    ├── CURRENT.md
    └── archive/work/
```

Git 只用于识别仓库根目录和可选地记录 revision。非 Git 工作区也可使用，只需明确把工作区根目录传给辅助脚本。项目存在自己的 `AGENTS.md` 时，该规则仍然优先，并与 Silverlocks 组合使用，而不是 Silverlocks 的运行前提。

## 连续性与归档

每个新会话第一次处理某个工作区的开发任务时，Silverlocks 检查一次 `.silverlocks/CURRENT.md`。文件结构合格时只读取一次，并将保存的目标与当前请求对照；无关状态会被忽略。

`CURRENT.md` 不是流水账。它最多 8 KiB，只保留已验证进度、一个明确的下一步、长期有效的约束和最少证据。每次更新都会原子化地完全替换内容，不追加历史。结束、替换或明确要求留档时，旧快照才进入 `.silverlocks/archive/work/`。

本地 `.silverlocks/` 通常不提交到 Git。但用户要求 Git 提交或发版时，必须同时生成一个仓库内受版本控制的 Markdown 恢复记录：优先遵循项目现有约定，没有约定时放在 `docs/versions/`。完整规则与命令见 [continuity.md](references/continuity.md)。

## 目录结构

```text
silverlocks/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── continuity.md
│   └── planning-and-verification.md
├── scripts/continuity.py
└── tests/test_continuity.py
```

## 隐私与权限边界

- 不联网、不遥测、不检查更新、不启动后台服务、不注册 Hook。
- 辅助脚本只读写指定工作区中的 `.silverlocks` 状态。
- 连续性文件和归档明确禁止写入密钥、Token、敏感地址和原始私密日志。
- Silverlocks 不会自动取得提交、推送、部署、发送消息或修改外部系统的权限。
- 当前用户请求和仓库内规则始终优先。

## 开发与验证

要求 Python 3.10 或更高版本。Git 是可选依赖；存在 Git 时会记录当前 revision。

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py .
```

## 许可与来源

Silverlocks 使用 MIT License。它是受 [Goldilocks](https://github.com/blackstone2333/goldilocks) 启发的独立无 Hook 改造版本，详见 [NOTICE.md](NOTICE.md)。本项目与 OpenAI 无隶属关系。
