# Vancy — AI 职业咨询顾问与智能体技能套件

> **语言版本**: [English](README.md) | [中文](README.zh-CN.md)  
> **用户操作指南**: [GUIDE.zh-CN.md](GUIDE.zh-CN.md) | [GUIDE.md](GUIDE.md)  
> **AI 工作流规范**: [WORKFLOW.zh-CN.md](WORKFLOW.zh-CN.md) | [WORKFLOW.md](WORKFLOW.md)

**Vancy** 是一套开源、全流程的职业咨询顾问 AI 智能体与技能套件，专为广大求职者、软件工程师、产品经理及职场管理者打造。它全面覆盖求职全生命周期：招聘启事深度拆解、定制化简历与求职信撰写、领英主页优化、项目案例包装、背调推荐人管理、通用行为面试与产品经理案例实战、薪酬评估与谈判，以及本地私密投递漏斗追踪。

与市面上盲目脑补技能、堆砌假大空套话的通用 AI 工具截然不同，Vancy 严格贯彻 **“调研先行、真实至上、零臆造”** 的核心原则：在动笔撰写或定制任何材料之前，它会深入访谈你的真实底层系统架构、数据指标与个人核心贡献，打造出经得起硬核面试官深度推敲的高通过率求职材料。

在你的求职工作目录中直接运行，无需克隆仓库：

```bash
npx career-consultant-skills init
```

---

## 1. 十二项开箱即用的求职技能

每项技能均严格遵循 [Agent Skills 开放规范](https://agentskills.io)，独立完备（包含 `SKILL.md` + `references/` 参考文献 + `scripts/` 工具脚本 + `assets/` 样式资源）：

| 求职阶段 | 技能名称 | 核心功能 | 交付格式 |
|---|---|---|---|
| **目标分析** | [`job-ad-analyzer`](.agents/skills/job-ad-analyzer) | 深度拆解招聘启事生成一页纸岗位简报：剖析岗位本质诉求、分级硬性门槛、梳理关键词图谱、识别幽灵职位与招聘陷阱，并给出坦诚投递建议。 | Markdown |
| **文书定制** | [`cv-builder`](.agents/skills/cv-builder) | 结合背景笔记、现有履历或领英导出文件，生成高度契合招聘方需求且通过 ATS 筛选的专业简历。使用强动词量化战绩。 | Markdown + Word (.docx) |
| | [`cv-reviewer`](.agents/skills/cv-reviewer) | 从 8 个维度（针对性、通读感、量化指标、措辞、结构、ATS 兼容性、一致性、偏见防范）对简历进行百分制诊断打分，并提供修改前后对比范式。 | Markdown + Word (.docx) |
| | [`cover-letter-builder`](.agents/skills/cover-letter-builder) | 紧扣企业业务痛点撰写一页高匹配度求职信，并提供邮件正文与网申系统适配变体。排版样式与简历严格对齐。 | Markdown + Word (.docx) |
| | [`cover-letter-reviewer`](.agents/skills/cover-letter-reviewer) | 审查求职信质量，揪出所有“换一家公司名字也能照发”的空洞套话，以硬核事实重写润色。 | Markdown + Word (.docx) |
| **品牌形象** | [`linkedin-profile-builder`](.agents/skills/linkedin-profile-builder) | 打造符合猎头与 HR 检索算法的领英个人主页：包括标语（Headline）、关于（About）、经历要点及私信拓展模版，自带字符限制合规检测。 | Markdown + Word (.docx) |
| | [`portfolio-case-study-builder`](.agents/skills/portfolio-case-study-builder) | 将复杂项目转化为结构化作品集案例（业务背景、挑战约束、架构权衡、落地指标），自带脱敏合规校验。 | Markdown + Word (.docx) |
| | [`reference-sheet-builder`](.agents/skills/reference-sheet-builder) | 规范准备背景调查推荐人清单与联络沟通模板。在每位推荐人的知情同意确认被录入前，自动拒绝导出最终文档。 | Markdown + Word (.docx) |
| **面试实战** | [`interview-prep`](.agents/skills/interview-prep) | 基于真实经历提炼 STAR 结构故事库，开展全真模拟面试与加权评分，并拟定面试后的致谢与跟进邮件。 | Markdown + Word (.docx) |
| | [`pm-interview-prep`](.agents/skills/pm-interview-prep) | 产品经理专项案例面试辅导（涵盖传统 PM 与 AI PM）：产品感设计、产品战略、指标与 A/B 测试、优先级决策、技术理解力、费米估算及 AI 产品设计演练。 | Markdown + Word (.docx) |
| **录用谈判** | [`salary-negotiation`](.agents/skills/salary-negotiation) | 全面拆解 Total Comp 综合薪酬包（底薪、绩效、期权/RSU 归属期、签字费），结合市场分位线制定谈判策略，起草得体有力的 Counter-Offer 沟通稿。 | Markdown + 测算脚本 |
| **漏斗追踪** | [`application-tracker`](.agents/skills/application-tracker) | 本地私有 CSV 求职看板：设置定期跟进提醒、每周总结复盘，并实时统计投递转化率与漏斗漏损。 | 本地 CSV + 终端命令行 |

---

## 2. 职业顾问智能体 ("Clara")

主智能体统筹调度上述十二项技能，实现全流程闭环协同：

```
[候选人原始输入资料]
       │
       ▼
 [初步录入与背景建立]  ──► artifacts/output/Candidate_Profile.md (候选人全局档案)
       │
       ▼
  [招聘启事深度拆解]    ──► artifacts/output/公司_职位/Job_Brief.md (岗位简报)
       │
       ▼
[深度经历与差距挖掘访谈]──► 核实真实业务范畴、运作规模、个人贡献与量化指标
       │
       ▼
  [简历与求职信定制]    ──► artifacts/output/公司_职位/姓名_CV.docx (排版级交付物)
       │
       ▼
 [跨文档严谨一致性审查]──► 彻底排查：联系方式、任职起止、量化数字、0 占位符残留
       │
       ▼
 [面试通关与录用谈判]  ──► STAR 面试库、PM 模拟演练、背景调查、薪资谈判信
       │
       ▼
 [求职进度与看板追踪]  ──► artifacts/output/job-applications.csv
```

---

## 3. 安装与命令行工具

无需克隆仓库，直接通过 `npx` 运行安装向导：

```bash
# 启动交互式安装向导（适配器、链接方式、语言与纸张尺寸）
npx career-consultant-skills init

# 或在当前目录下免交互静默安装所有适配器
npx career-consultant-skills init --target . --harness all --yes

# ……并同时指定文档语言与纸张尺寸
npx career-consultant-skills init --target . --harness all --yes --lang en-GB --page a4

# 安装至指定的目标项目路径
npx career-consultant-skills init --target /path/to/my-project --harness claude,opencode,github,kiro --yes

# 随时重新配置适配器（添加或移除 Claude Code、OpenCode、Copilot、Kiro 支持）
npx career-consultant-skills reconfigure --target .

# 检查并将核心提示词、技能库及脚本升级至最新版
npx career-consultant-skills update --target . --yes

# 对本地安装文件进行基于数字签名的完整性校验
npx career-consultant-skills verify --target .

# 设置生成文档时默认使用的语言与纸张尺寸
npx career-consultant-skills config --lang en-US --page a4

# 安全卸载（清理核心与适配文件，但 100% 完整保留你的 artifacts/ 求职成果）
npx career-consultant-skills uninstall --target .
```

全局安装后可改用更简短的 `vancy` 命令：

```bash
npm install -g career-consultant-skills
vancy init
```

若在本地克隆的仓库中运行，请将上述命令中的 `npx career-consultant-skills` 替换为 `node bin/cli.mjs`。

### 语言与纸张尺寸

文档会按照保存在 `.vancy/config.json` 中的全局设置进行渲染：

```bash
node bin/cli.mjs config                      # 查看当前设置
node bin/cli.mjs config --lang en-GB         # 英式英语
node bin/cli.mjs config --lang en-US --page letter
```

所有渲染器按以下优先级解析：命令行 `--lang`/`--page` → 文档自身的 front matter → `.vancy/config.json` → 默认回退值（`en-US`、`a4`）。安装向导提供按 A–Z 排序的 22 种语言，包含 English (UK) 与 English (US)；列表中没有的语言可选择 “Other” 手动输入。任何 BCP 47 标签均可使用（`en-GB`、`fr-FR`、`de-DE`、`pt-PT`、`zh-TW`）。技能库中的地区惯例表仍会为目标市场决定文档结构、篇幅与落款方式，因此使用美式英语的候选人申请英国职位时，该份文档仍会采用英式求职信惯例。

### 支持的 AI 开发环境与适配层 (Harnesses)
- **Claude Code**：自动生成 `.claude -> .agents` 软链接与 `CLAUDE.md` 知识库。
- **OpenCode**：自动生成 `.opencode -> .agents` 软链接。
- **GitHub Copilot**：自动生成 `.github/copilot-instructions.md` 与 `.github/skills`。
- **Kiro**：自动配置 `.kiro/steering/`、`.kiro/skills/` 与 `.kiro/agents/career-consultant`。
- **任意 AI 智能体开发环境**：原生 `.agents/` 目录结构，天然无缝兼容 Cursor、Codex、Gemini CLI、Windsurf 等各类工具。

---

## 4. 关键架构设计特性

- **调研先行与零臆造 (Zero Hallucination)**：Vancy 坚决不盲目猜测你的系统吞吐、数据库量级或架构技术选型。必须先对你进行技术提问，挖掘出真实细节后方可落笔。
- **100% 本地隐私保护**：所有个人数据与成果严格锁定在 `artifacts/`（包含 `artifacts/input/` 与 `artifacts/output/`）。通过自动化 `.gitignore`，杜绝任何个人隐私泄露至 Git 仓库。
- **ATS 友好且排版优雅的 Word (.docx) 引擎**：内置 5 套精美单栏版式（`classic` 经典、`modern` 现代、`minimal` 极简、`executive` 高管、`compact` 紧凑），完全基于 Word 原生样式排版，无浮动文本框或复杂嵌套表格，确保 ATS 筛选系统 100% 顺畅解析。
- **Python 纯零第三方依赖**：所有内置自动化脚本完全依赖 Python 3.8+ 标准库运行，免除复杂的 `pip install` 环境困扰。
- **不受信数据隔离防护**：将外部招聘启事与猎头沟通信息严格作为隔离文本数据输入，抵御 Prompt 注入与隐形字符篡改风险。

---

## 5. 内置脚本终端速查

以下路径以默认的 `.agents/` 安装为例；若安装在 `.claude/skills/`、`.kiro/skills/` 或 `~/.agents/skills/`，请相应替换路径前缀。

你可以直接在终端中随时调用各类独立脚本：

```bash
# 列出系统内置的 Word 排版模板
python3 .agents/skills/cv-builder/scripts/render_docx.py --list-templates

# 将定制好的 Markdown 简历渲染为交付级 Word 文档
# （仅在需要为单份文件覆盖 .vancy/config.json 时，才添加 --lang/--page）
python3 .agents/skills/cv-builder/scripts/render_docx.py artifacts/output/Acme_资深研发/张三_CV.md \
  -o artifacts/output/Acme_资深研发/张三_CV.docx \
  --template modern --final

# 静态合规检测：检查 ATS 兼容性、隐藏字符与占位符残留
python3 .agents/skills/cv-reviewer/scripts/doc_lint.py artifacts/output/Acme_资深研发/张三_CV.docx \
  --type cv --job artifacts/input/job_ad.txt

# 查看未来 7 天内到期需跟进联系的岗位清单
python3 .agents/skills/application-tracker/scripts/tracker.py --file artifacts/output/job-applications.csv due --days 7

# 对产品经理面试模拟回答进行加权评分计算
python3 .agents/skills/pm-interview-prep/scripts/score_sheet.py --category product_sense --scores structure=4,insight=4,creativity=3

# 横向对比多份录用 Offer 的综合实际收益
python3 .agents/skills/salary-negotiation/scripts/offer_calc.py compare offers.json
```

---

## 6. 开发与代码质量验证

运行自动化检测流水线，校验 Frontmatter 规范、Python AST 语法、打包内容与软链接完整性、版本号一致性：

```bash
npm run check
```

版本号只保存在 `package.json` 一处。若任一副本出现偏差，`npm run check` 会直接失败；执行 `npm version <patch|minor|major>` 时，新版本号会自动写入各技能 frontmatter 与 `.agents/manifest.json` 并暂存，同时打上发布标签。CLI、安装向导横幅与 `.agents/.vancy-version` 均在运行时读取同一个值。

---

## 7. 核心文档导航

- [**中文用户指南 (GUIDE.zh-CN.md)**](GUIDE.zh-CN.md) | [**English User Guide (GUIDE.md)**](GUIDE.md)：手把手实操教程、高频提示词模板及面试通关指南。
- [**AI 工作流规范 (WORKFLOW.zh-CN.md)**](WORKFLOW.zh-CN.md) | [**AI Workflow Specification (WORKFLOW.md)**](WORKFLOW.md)：AI 智能体遵循的标准执行协议、禁忌准则与行为树。

---

## 开源协议

本项目采用 [MIT](LICENSE) 开源协议 © Vancy 贡献者

