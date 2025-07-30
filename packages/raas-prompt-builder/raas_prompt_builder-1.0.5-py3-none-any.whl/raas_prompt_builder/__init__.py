"""
Universal Prompt Builder

다양한 목적의 LLM 프롬프트를 동적으로 생성하는 범용 모듈입니다.
개발자별 코드 분석 요약, 코드 품질 평가, 작업 패턴 분석용 프롬프트를 최적화합니다.

Features:
- 동적 템플릿 생성 및 관리
- 토큰 사용량 최적화
- 다양한 프롬프트 유형 지원
- 커스터마이징 옵션
- 다국어 지원
"""

__version__ = "1.0.0"

from .service import PromptBuilderService
from .models import (
    PromptInput,
    PromptResult,
    PromptType,
    PromptMetadata,
    CustomizationOptions,
    TemplateConfig,
    PromptTemplate,
    TokenUsage,
    ContextData
)
from .exceptions import (
    PromptBuilderException,
    InvalidPromptTypeException,
    TemplateNotFoundException,
    TokenLimitExceededException,
    TemplateRenderException,
    MissingVariableException,
    InvalidCustomizationException
)

__all__ = [
    'PromptBuilderService',
    'PromptInput',
    'PromptResult',
    'PromptType',
    'PromptMetadata',
    'CustomizationOptions',
    'TemplateConfig',
    'PromptTemplate',
    'TokenUsage',
    'ContextData',
    'PromptBuilderException',
    'InvalidPromptTypeException',
    'TemplateNotFoundException',
    'TokenLimitExceededException',
    'TemplateRenderException',
    'MissingVariableException',
    'InvalidCustomizationException'
] 