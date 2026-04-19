# 🌿 Food Therapy System (食疗养生推荐系统)

这是一个基于中医理论与现代AI辅助结合的食疗健康推荐系统。项目分为 **前端 (Vue 3 + Vite)** 和 **后端 (Python + FastAPI)** 两部分，旨在为用户提供从体质自测、健康档案管理到专属中医食谱推荐的闭环体验。

---

## 🛠 技术栈

* **前端**：Vue 3, Vite, 原生 CSS
* **后端**：Python 3.x, FastAPI, Uvicorn, OpenAI-compatible API
* **数据存储**：轻量级本地文件 (CSV) 与内存级检索树 (Trie & Hash) 以及基础 SQLite

---

## ✨ 核心特性

- **体质自测与档案管理**：基于传统中医体质分类，量化分析用户的身体指标。
- **智能食谱推荐 (全天候天气感知)**：由 AI 大模型驱动。并在最新版本中深度结合了 **实时周边气象要素** (和风天气)。不仅参考体质，还会自动捕获用户当地的温度、湿度，进行“因时、因地”的动态中医食疗精准干预。
- **动态选址与直观看板**：采用自动读取与修改定位解耦机制，用户可一键修改所处城市。智能推荐面板将实时反馈气象数据介入状况，推荐理由更加“通透可见”。
- **名医知识库本地兜底**：在无网络或未配置大模型 API Key 情况下，能自动退化至经典的本地本地知识库进行推荐，永不宕机。

---

## 📁 目录结构

```text
📦 FoodTherapy_Project
 ┣ 📂 Backened/                 # 后端目录
 ┃ ┣ 📂 api/                    # 路由拦截点 (quiz, recommend, recipes 等)
 ┃ ┣ 📂 core/                   # 核心算法、数据预加载器、AI推荐引擎
 ┃ ┣ 📂 data/                   # 本地数据库 (包含食材数据集、菜谱数据与海量食材图片)
 ┃ ┣ 📂 models/                 # Pydantic 数据规范模型
 ┃ ┣ 📜 main.py                 # FastAPI 入口文件
 ┃ ┗ 📜 requirements.txt        # 后端依赖包列表
 ┣ 📂 diet-health-frontend/     # 前端目录
 ┃ ┣ 📂 src/                    # 页面与组件源码
 ┃ ┣ 📜 package.json            # 前端依赖包列表
 ┃ ┗ 📜 vite.config.js          # Vite 构建配置
 ┗ 📜 .gitignore                # 规范化忽略文件
```

---

## 🚀 快速上手：同伴部署指南

克隆本项目到本地后，请打开**两个命令行终端**，分别运行前后端。

### 一、 后端运行指南 (终端 A)

**1. 创建并激活虚拟环境（推荐使用 Conda）：**
```bash
cd Backened

# 创建一个干净的 python 3.9 环境
conda create -n food_therapy_env python=3.9 
conda activate food_therapy_env
```
*(如果不用 Conda，也可使用内置的 `python -m venv venv` 然后激活它)*

**2. 安装运行依赖：**
```bash
pip install -r requirements.txt
```

**3. 配置环境变量：**
后端中的智能推荐模块依赖 AI 大模型。请在 `Backened/` 根目录下手动新建一个文件并命名为 `.env`，填入以下内容（如果没有接口密钥也没关系，项目内部含有完备的经典中医**“基础兜底逻辑”**，可以照常运转）：
```ini
AI_API_KEY=修改成你的API_KEY
AI_BASE_URL=https://api.deepseek.com/v1 # 这里依据你的供应商进行更改
```

**4. 启动 FastAPI 本地服务器：**
```bash
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```
看到命令行打印出 `Application startup complete.` 字样说明启动成功，接口运行在 `http://127.0.0.1:8001`。

---

### 二、 前端运行指南 (终端 B)

**1. 进入前端目录并安装依赖：**
你需要确保电脑上安装了 Node.js (推荐 v18+ 稳定版)。
```bash
cd diet-health-frontend
npm install
```

**2. 启动 Vite 热更新开发服务器：**
```bash
npm run dev
```

成功后控制台会显示类似如下的信息：
```text
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```
按住 `Ctrl` 点击该链接即可在浏览器中愉快地体验完整的食疗推荐系统。

---

## 💡 开发协作留意事项

1. **依赖管控**：严禁将本机的 `food_therapy_env` 或 `node_modules` 文件夹上传到分支。
2. **秘钥隔离**：`.env` 文件已被完全纳入 `.gitignore` 忽略清单中。严禁将你在 `.env` 文件里写入的私人 API_KEY 代码推送到公网仓库中，以防被黑客盗刷。
3. **数据读取**：启动加载时，后端的预加载器会主动吸附 `data/shicai .csv`。目前已修复全量读取结尾 `\r` 触发的破图 Bug，添加新食材只需要更新 CSV 且把原图放到 `data/Shicaiimages/` 下即可。
