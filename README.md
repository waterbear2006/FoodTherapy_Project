# 🍏 食疗养生推荐系统 (FoodTherapy AI)

> **智慧中医，食疗先行**。本项目是一个集“君臣佐使”药理等级图谱、AI 温润古风助手、以及 RAG 增强医学知识库于一体的高端中医食疗专家系统。

---

## 🌟 核心特性

### 1. “君臣佐使”等级知识图谱 (Medicinal Hierarchy Graph)
- **几何权威映射**：通过节点尺寸（70px/45px/25px）与视觉光环，直观展示方剂中的核心（君）、支撑（臣）与辅助（佐/使）身份。
- **互动物理体验**：基于 Apple 极简美学设计的 ECharts 力导向布局，具备 iOS 级滚动阻尼感与丝滑的动态平衡。
- **全量语义标签**：悬浮节点即可弹出高亮 iOS 气泡名牌，连线显式标注药理角色。

### 2. “颐宝”智能古风助手 (Yi Bao Persona)
- **温润人格**：摆脱生涩的文言文，采用“温润如玉”的现代古风对话风格。
- **生活化医理**：将复杂的术语（如脾主运化）转化为生活比喻（如身体的运输小队）。
- **古籍背书**：回答自动关联《本草》、《伤寒》等古籍，并以白话文形式进行专业考证。

### 3. RAG 增强医学智库
- **向量数据库**：集成 ChromaDB，通过 BGE 深度嵌入模型实现对海量中医知识的精准检索。
- **安全性保障**：所有 AI 建议均基于本地医学知识库进行检索增强（RAG），提升专业深度。

---

## 📂 项目结构

```bash
root/
├── Backened/                # 后端 (FastAPI + Python 3.13)
│   ├── api/                 # 业务路由 (Assistant, Graph, Search, etc.)
│   ├── core/                # 核心引擎 (Graph Engine, RAG Service)
│   ├── data/                # 结构化数据 (CSV, Shicai Images)
│   ├── scripts/             # 初始化脚本 (Vector DB build)
│   ├── tcm_chroma_db/       # 本地向量数据库 (Git Ignite)
│   ├── main.py              # 服务入口
│   └── .env                 # 环境变量配置 (DASHSCOPE_API_KEY)
├── diet-health-frontend/    # 前端 (Vue 3 + Vite + Vant + ECharts)
│   ├── src/
│   │   ├── components/      # 核心组件 (RelationGraph.vue 等)
│   │   ├── pages/           # 业务页面 (SmartRecommend.vue 等)
│   │   └── assets/          # 静态资源
│   └── package.json
└── task.md                  # 项目进度管理自选
```

---

## 🛠️ 环境配置

### 1. 后端准备 (Backend Setup)
- **Python 版本**：推荐 `Python 3.13+`
- **安装依赖**：
  ```bash
  cd Backened
  pip install -r requirements.txt
  ```
- **配置环境变量**：
  在 `Backened/` 目录下创建 `.env` 文件，填入您的密钥：
  ```env
  DASHSCOPE_API_KEY=您的阿里云通义千问密钥
  AI_API_KEY=您的DeepSeek或其他API密钥
  ```

### 2. 前端准备 (Frontend Setup)
- **Node.js 版本**：推荐 `v18+`
- **安装并启动**：
  ```bash
  cd diet-health-frontend
  npm install
  npm run dev
  ```

### 3. 构建医学智库 (可选)
如果您需要开启 RAG 检索增强功能，请先运行脚本构建向量库：
```bash
cd Backened
python scripts/init_vector_db.py
```

---

## 🎨 视觉设计规范
- **风格**：Apple 极简设计语言 (Apple Minimalist)。
- **质感**：玻璃磨砂 (Glassmorphism)、高留白、iOS 强调色 (#007AFF)。
- **字体**：系统字体栈 (`-apple-system`, `SF Pro`, `Inter`)。

---

## ⚖️ 声明
本项目提供的食疗建议仅供学习与参考。如有身体不适，请务必咨询专业医师。

---
*愿君清润安康。*
