# Backsys - 银行营销数据展示系统

展示银行营销数据的动态可视化系统，基于 FastAPI 后端和 Streamlit 前端。

## 项目结构

```
backsys/
├── .github/workflows/ci.yml    # CI/CD 配置
├── src/
│   ├── backend/
│   │   ├── app.py              # FastAPI 应用
│   │   └── streamlit_app.py    # Streamlit 应用
│   ├── core/
│   │   ├── config.py           # 配置管理
│   │   └── models.py           # 数据模型
│   └── utils/                  # 工具函数
├── tests/                      # 测试代码
├── data/                       # 数据文件
│   ├── train.csv
│   └── test.csv
├── Dockerfile
├── pyproject.toml
└── README.md
```

## 快速开始

### 本地开发

1. 安装依赖：
```bash
uv sync --extra dev
```

2. 启动 FastAPI 后端：
```bash
uv run python -m uvicorn src.backend.app:app --reload --port 6100
```

3. 启动 Streamlit 前端：
```bash
uv run streamlit run src/backend/streamlit_app.py
```

### Docker 部署

```bash
docker build -t backsys .
docker run -d -p 6100:6100 backsys
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/summary` | GET | 数据摘要 |
| `/api/data` | GET | 获取数据（支持分页） |
| `/api/data/filtered` | GET | 筛选数据 |
| `/api/columns/{column}/unique` | GET | 获取列唯一值 |
| `/api/aggregated` | GET | 聚合数据 |

## 测试

```bash
uv run pytest tests/ -v --cov=src/ --cov-report=term-missing
```

## CI/CD

项目使用 GitHub Actions 进行持续集成：
- 代码格式检查 (Black)
- 代码风格检查 (Ruff)
- 类型检查 (MyPy)
- 单元测试 (pytest, 覆盖率 >= 80%)

## GitHub Secrets 配置

需要在 GitHub 仓库设置中配置以下 Secrets：

| Secret | 描述 |
|--------|------|
| `SSH_HOST` | 服务器 IP 地址 |
| `SSH_USER` | SSH 用户名 |
| `SSH_PASSWORD` | SSH 密码 |
| `SSH_PORT` | SSH 端口 |

## 技术栈

- **后端**: FastAPI, Uvicorn
- **前端**: Streamlit, Plotly
- **数据处理**: Pandas, Pydantic
- **测试**: pytest, pytest-cov
- **代码质量**: Black, Ruff, MyPy

## License

MIT
