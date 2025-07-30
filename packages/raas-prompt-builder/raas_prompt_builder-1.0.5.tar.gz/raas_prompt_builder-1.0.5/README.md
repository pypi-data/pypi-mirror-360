# Universal Prompt Builder

동적 프롬프트 생성을 위한 범용 프롬프트 빌더 모듈입니다.

## 특징

- 🔧 **템플릿 기반**: Jinja2를 사용한 유연한 템플릿 시스템
- 📝 **동적 생성**: 컨텍스트에 따른 동적 프롬프트 생성
- 🎯 **타입 안전**: Pydantic을 통한 강력한 타입 검증
- 🔄 **재사용 가능**: 모듈화된 프롬프트 컴포넌트

## 설치

```bash
pip install yeonjae-universal-prompt-builder
```

## 사용법

```python
from yeonjae_universal_prompt_builder import PromptBuilder, PromptTemplate

# 기본 사용법
builder = PromptBuilder()
template = PromptTemplate(
    name="greeting",
    template="Hello, {{ name }}! Welcome to {{ place }}.",
    variables=["name", "place"]
)

prompt = builder.build(template, {"name": "Alice", "place": "PyPI"})
print(prompt)  # "Hello, Alice! Welcome to PyPI."
```

## 라이센스

MIT License

## 버전 히스토리

- 1.0.2: 초기 배포 버전
- 1.0.1: 개발 버전
- 1.0.0: 프로토타입 