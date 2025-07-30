"""
Tests for universal_prompt_builder.models
"""

import pytest
from datetime import datetime
from raas_prompt_builder.models import (
    PromptType,
    CustomizationOptions,
    TemplateConfig,
    PromptInput,
    PromptMetadata,
    PromptResult,
    TemplateVariable,
    PromptTemplate,
    TokenUsage,
    ContextData
)


class TestPromptType:
    """PromptType 열거형 테스트"""
    
    def test_prompt_types(self):
        """프롬프트 타입들이 올바르게 정의되어 있는지 확인"""
        assert PromptType.DAILY_SUMMARY == "daily_summary"
        assert PromptType.CODE_REVIEW == "code_review"
        assert PromptType.WORK_PATTERN_ANALYSIS == "work_pattern_analysis"
        assert PromptType.TEAM_REPORT == "team_report"
        assert PromptType.PERFORMANCE_ANALYSIS == "performance_analysis"


class TestCustomizationOptions:
    """CustomizationOptions 모델 테스트"""
    
    def test_default_values(self):
        """기본값들이 올바르게 설정되는지 확인"""
        options = CustomizationOptions()
        
        assert options.tone == "professional"
        assert options.detail_level == "medium"
        assert options.language == "korean"
        assert options.include_emoji is True
        assert options.include_statistics is True
        assert options.include_recommendations is False
        assert options.max_length is None
    
    def test_custom_values(self):
        """커스텀 값들이 올바르게 설정되는지 확인"""
        options = CustomizationOptions(
            tone="casual",
            detail_level="high",
            language="english",
            include_emoji=False,
            max_length=1000
        )
        
        assert options.tone == "casual"
        assert options.detail_level == "high"
        assert options.language == "english"
        assert options.include_emoji is False
        assert options.max_length == 1000


class TestPromptInput:
    """PromptInput 모델 테스트"""
    
    def test_basic_creation(self):
        """기본 PromptInput 생성 테스트"""
        input_data = PromptInput(
            aggregated_data={"test": "data"},
            prompt_type=PromptType.DAILY_SUMMARY,
            target_developer="test@example.com"
        )
        
        assert input_data.aggregated_data == {"test": "data"}
        assert input_data.prompt_type == PromptType.DAILY_SUMMARY
        assert input_data.target_developer == "test@example.com"
        assert isinstance(input_data.customization, CustomizationOptions)
    
    def test_with_customization(self):
        """커스터마이징 옵션과 함께 생성 테스트"""
        custom_options = CustomizationOptions(tone="formal")
        input_data = PromptInput(
            aggregated_data={"test": "data"},
            prompt_type=PromptType.CODE_REVIEW,
            target_developer="dev@example.com",
            customization=custom_options,
            context="Additional context"
        )
        
        assert input_data.customization.tone == "formal"
        assert input_data.context == "Additional context"


class TestPromptResult:
    """PromptResult 모델 테스트"""
    
    def test_basic_creation(self):
        """기본 PromptResult 생성 테스트"""
        metadata = PromptMetadata(
            template_version="1.0",
            token_count=100
        )
        
        result = PromptResult(
            prompt="Test prompt content",
            metadata=metadata,
            context_data={"test": "context"},
            template_used="daily_summary"
        )
        
        assert result.prompt == "Test prompt content"
        assert result.metadata.template_version == "1.0"
        assert result.context_data == {"test": "context"}
        assert result.template_used == "daily_summary"
    
    def test_is_valid_property(self):
        """is_valid 속성 테스트"""
        metadata = PromptMetadata(template_version="1.0", token_count=100)
        
        # 유효한 프롬프트
        valid_result = PromptResult(
            prompt="Valid prompt",
            metadata=metadata,
            context_data={},
            template_used="test"
        )
        assert valid_result.is_valid is True
        
        # 빈 프롬프트
        invalid_result = PromptResult(
            prompt="",
            metadata=metadata,
            context_data={},
            template_used="test"
        )
        assert invalid_result.is_valid is False
        
        # 공백만 있는 프롬프트
        whitespace_result = PromptResult(
            prompt="   ",
            metadata=metadata,
            context_data={},
            template_used="test"
        )
        assert whitespace_result.is_valid is False
    
    def test_estimated_tokens_property(self):
        """estimated_tokens 속성 테스트"""
        metadata = PromptMetadata(template_version="1.0", token_count=100)
        
        result = PromptResult(
            prompt="This is a test prompt with multiple words",
            metadata=metadata,
            context_data={},
            template_used="test"
        )
        
        # 8개 단어 * 1.3 = 10.4 -> 10 (int)
        word_count = len(result.prompt.split())
        expected_tokens = int(word_count * 1.3)
        assert result.estimated_tokens == expected_tokens


class TestPromptTemplate:
    """PromptTemplate 모델 테스트"""
    
    def test_basic_creation(self):
        """기본 PromptTemplate 생성 테스트"""
        template = PromptTemplate(
            name="test_template",
            content="Hello {name}, your score is {score}"
        )
        
        assert template.name == "test_template"
        assert template.content == "Hello {name}, your score is {score}"
        assert len(template.variables) == 0
    
    def test_with_variables(self):
        """변수와 함께 생성 테스트"""
        variables = [
            TemplateVariable(name="name", value="John", is_required=True),
            TemplateVariable(name="score", value=95, is_required=False, default_value=0)
        ]
        
        template = PromptTemplate(
            name="test_template",
            content="Hello {name}, your score is {score}",
            variables=variables
        )
        
        required_vars = template.get_required_variables()
        optional_vars = template.get_optional_variables()
        
        assert "name" in required_vars
        assert "score" in optional_vars
        assert len(required_vars) == 1
        assert len(optional_vars) == 1


class TestTokenUsage:
    """TokenUsage 모델 테스트"""
    
    def test_basic_creation(self):
        """기본 TokenUsage 생성 테스트"""
        usage = TokenUsage(
            prompt_tokens=100,
            estimated_completion_tokens=200,
            total_tokens=300
        )
        
        assert usage.prompt_tokens == 100
        assert usage.estimated_completion_tokens == 200
        assert usage.total_tokens == 300
        assert usage.cost_estimate == 0.0
    
    def test_is_within_limit_property(self):
        """is_within_limit 속성 테스트"""
        # 제한 내
        within_limit = TokenUsage(
            prompt_tokens=100,
            estimated_completion_tokens=200,
            total_tokens=300
        )
        assert within_limit.is_within_limit is True
        
        # 제한 초과
        over_limit = TokenUsage(
            prompt_tokens=2000,
            estimated_completion_tokens=3000,
            total_tokens=5000
        )
        assert over_limit.is_within_limit is False


class TestContextData:
    """ContextData 모델 테스트"""
    
    def test_basic_creation(self):
        """기본 ContextData 생성 테스트"""
        context = ContextData(
            developer_stats={"dev1": {"commits": 5}},
            repository_stats={"repo1": {"files": 10}},
            time_analysis={"peak_hour": 14},
            complexity_metrics={"avg_complexity": 2.5}
        )
        
        assert context.developer_stats == {"dev1": {"commits": 5}}
        assert context.repository_stats == {"repo1": {"files": 10}}
        assert context.time_analysis == {"peak_hour": 14}
        assert context.complexity_metrics == {"avg_complexity": 2.5}
        assert len(context.relevant_commits) == 0
    
    def test_get_summary_stats(self):
        """get_summary_stats 메서드 테스트"""
        commits = [{"id": 1}, {"id": 2}, {"id": 3}]
        
        context = ContextData(
            developer_stats={"dev1": {}, "dev2": {}},
            repository_stats={"repo1": {}, "repo2": {}, "repo3": {}},
            time_analysis={},
            complexity_metrics={"avg": 2.0},
            relevant_commits=commits
        )
        
        summary = context.get_summary_stats()
        
        assert summary["total_commits"] == 3
        assert summary["developer_count"] == 2
        assert summary["repository_count"] == 3
        assert summary["has_complexity_data"] is True 