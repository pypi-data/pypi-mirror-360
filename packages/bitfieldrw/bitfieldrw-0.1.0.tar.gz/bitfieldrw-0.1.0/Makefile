# BitFieldRW Makefile
# 用于常用的开发和发布任务

.PHONY: help test build clean publish install-dev lint format check

# 默认目标
help:
	@echo "BitFieldRW 项目管理命令:"
	@echo ""
	@echo "开发命令:"
	@echo "  install-dev    安装开发依赖"
	@echo "  test           运行测试"
	@echo "  lint           代码检查"
	@echo "  format         格式化代码"
	@echo "  check          运行所有检查"
	@echo ""
	@echo "构建发布:"
	@echo "  build          构建包"
	@echo "  clean          清理构建文件"
	@echo "  publish        发布到PyPI"
	@echo ""

# 安装开发依赖
install-dev:
	uv sync --dev

# 运行测试
test:
	python -m unittest discover tests -v

# 代码检查
lint:
	uv run ruff check .
	uv run mypy bitfieldrw

# 格式化代码
format:
	uv run black .
	uv run ruff check --fix .

# 运行所有检查
check: lint test

# 构建包
build: clean
	uv build

# 清理构建文件
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete

# 发布包
publish: build
	python scripts/publish.py
