.PHONY: help install test test-unit test-integration test-all lint format type-check security-scan clean build publish-test publish

help: ## 도움말 표시
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 개발 의존성 설치
	uv sync --dev

test-unit: ## 단위 테스트 실행
	uv run pytest tests/ -m "unit" -v --cov=pycobaltix --cov-report=term-missing

test-integration: ## 통합 테스트 실행 (API 키 필요)
	uv run pytest tests/ -m "integration" -v --cov=pycobaltix --cov-append --cov-report=term-missing

test-all: ## 모든 테스트 실행
	uv run pytest tests/ -v --cov=pycobaltix --cov-report=html --cov-report=term-missing

test-fast: ## 빠른 테스트만 실행 (slow 테스트 제외)
	uv run pytest tests/ -m "not slow" -v

test-watch: ## 파일 변경 감지하여 테스트 자동 실행
	uv run pytest-watch tests/ -m "unit" --runner "pytest -v"

lint: ## 코드 린팅 (ruff)
	uv run ruff check .

lint-fix: ## 코드 린팅 및 자동 수정
	uv run ruff check . --fix

format: ## 코드 포매팅
	uv run ruff format .

format-check: ## 코드 포매팅 확인
	uv run ruff format --check .

type-check: ## 타입 체크 (mypy)
	uv run mypy pycobaltix --ignore-missing-imports

security-scan: ## 보안 스캔
	uv add --dev bandit safety
	uv run bandit -r pycobaltix/
	uv run safety check

quality-check: lint format-check type-check ## 코드 품질 종합 체크

clean: ## 캐시 및 빌드 파일 정리
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

build: clean ## 패키지 빌드
	uv build

publish-test: build ## 테스트 PyPI에 배포
	uv add --dev twine
	uv run twine upload --repository testpypi dist/*

publish: build ## PyPI에 배포
	uv add --dev twine
	uv run twine upload dist/*

pre-commit: quality-check test-unit ## 커밋 전 체크
	@echo "✅ 커밋 전 체크 완료!"

pre-push: quality-check test-all security-scan ## 푸시 전 체크
	@echo "✅ 푸시 전 체크 완료!"

dev-setup: install ## 개발 환경 초기 설정
	@echo "📦 의존성 설치 완료"
	@echo "🧪 테스트 실행: make test-unit"
	@echo "🔍 코드 품질 체크: make quality-check"
	@echo "📚 더 많은 명령어: make help"

ci-test: ## CI에서 실행되는 테스트
	uv run pytest tests/ -m "unit" --cov=pycobaltix --cov-report=xml --cov-report=term-missing
	@if [ -n "$$NAVER_API_KEY_ID" ] && [ -n "$$NAVER_API_KEY" ]; then \
		uv run pytest tests/ -m "integration" --cov=pycobaltix --cov-append --cov-report=xml --cov-report=term-missing; \
	fi

bump-patch: ## 패치 버전 업데이트
	@echo "현재 버전에서 패치 버전을 업데이트합니다..."
	@# 여기에 버전 업데이트 로직 추가 가능

bump-minor: ## 마이너 버전 업데이트
	@echo "현재 버전에서 마이너 버전을 업데이트합니다..."
	@# 여기에 버전 업데이트 로직 추가 가능

bump-major: ## 메이저 버전 업데이트
	@echo "현재 버전에서 메이저 버전을 업데이트합니다..."
	@# 여기에 버전 업데이트 로직 추가 가능