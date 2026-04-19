# 🌿 Food Therapy System - 部署与运行指南 (DEPLOYMENT.md)

本文件详细介绍了如何通过 Docker 快速构建并部署 **食疗养生推荐系统**。该系统是一个基于 **Vue 3** 前端和 **FastAPI** 后端的全栈中医药理项目。

---

## 1. 项目简介
**食疗养生推荐系统** 旨在利用中医传统理论与 AI 大模型，为用户提供科学的饮食调理建议。
- **前端**：Vue 3 + Vite + Vant，提供沉浸式“国风”交互体验。
- **后端**：FastAPI + Python 3.9，负责核心算法计算及 AI RAG 引证。
- **构建方式**：采用 Docker 多阶段构建，将前后端压缩至同一个轻量级镜像中。

---

## 2. 环境要求
在开始之前，请确保您的本地环境已安装以下工具：
- **Docker**: 20.10.x 或更高版本
- **Docker Compose** (可选): v2.x 或更高版本
- **网络环境**: 能够访问 `hub.docker.com` 或已配置国内加速镜像源。

---

## 3. 本地构建步骤

### 3.1 构建镜像
在项目根目录下（包含 `Dockerfile` 的位置），运行以下命令进行镜像构建：

```bash
docker build -t food-therapy-app .
```

> [!TIP]
> 如果在国内构建速度较慢，建议在构建前配置 Docker 镜像加速器（如阿里云、网易云等）。

### 3.2 运行容器
构建完成后，使用以下命令启动容器。我们将容器内的 **8000** 端口映射到本地的 **8000** 端口：

```bash
docker run -d \
  --name food-therapy-container \
  -p 8000:8000 \
  --env-file Backened/.env \
  food-therapy-app
```

启动后，您可以访问 [http://localhost:8000](http://localhost:8000) 查看完整系统。

---

## 4. 环境变量配置 (.env)

系统核心组件（AI 助手、智能引擎）依赖于大模型 API。您需要在 `Backened/.env` 文件中进行配置。

### 创建 .env 文件
在 `Backened/` 目录下创建 `.env` 文件，内容如下：

```ini
# DeepSeek API 配置 (推荐)
DEEPSEEK_API_KEY=您的_DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 其他配置 (可选)
PORT=8000
```

> [!IMPORTANT]
> - 如果没有配置 API Key，系统将自动降级为 **本地专家规则库**，核心功能依然可用，但失去 AI 个性化理由。
> - 请确保在 `docker run` 时通过 `--env-file` 参数指定该文件。

---

## 5. 云端部署建议

本项目非常适合部署在现代 PaaS 平台上：

### 5.1 Zeabur / Railway
1. **关联 GitHub**: 将您的代码（含 Dockerfile）上传至 GitHub 仓库。
2. **导入项目**: 在平台后台选择“Import from GitHub”。
3. **设置变量**: 在平台的 "Environment Variables" 选项卡中手动填入 `DEEPSEEK_API_KEY`。
4. **自动构建**: 平台会自动识别根目录下的 `Dockerfile` 并进行构建部署。

---

## 6. 常见问题排查 (Troubleshooting)

### 6.1 构建缓慢
- **现象**: `npm install` 或 `pip install` 长时间卡住。
- **解决**: 修改 Dockerfile，在构建阶段增加 `--registry=https://registry.npmmirror.com` 或 pip 镜像源。

### 6.2 网络超时 / API Key 失效
- **现象**: 智能推荐加载中或报错。
- **排查**: 
  - 检查容器是否能访问外网。
  - 确认 `DEEPSEEK_API_KEY` 是否正确且余额充足。
  - 检查后端日志：`docker logs -f food-therapy-container`。

### 6.3 页面 404
- **现象**: 访问 root 页面显示 `{"message": "..."}`。
- **排查**: 请确保在构建镜像时，`diet-health-frontend` 目录下的 `dist` 已成功生成并被拷贝至 `Backened/static`。

---

© 2026 食疗养生项目组 | 技术驱动健康
