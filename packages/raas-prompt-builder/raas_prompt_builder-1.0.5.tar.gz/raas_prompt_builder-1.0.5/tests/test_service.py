"""
Tests for universal_prompt_builder.service
"""

import pytest
from raas_prompt_builder.service import PromptBuilderService
from raas_prompt_builder.models import (
    PromptInput,
    PromptType,
    CustomizationOptions,
    PromptResult
)
from raas_prompt_builder.exceptions import (
    PromptBuilderException,
    TemplateNotFoundException
)


class TestPromptBuilderService:
    """PromptBuilderService 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.service = PromptBuilderService()
        self.sample_aggregated_data = {
            "developer_stats": {
                "test@example.com": {
                    "developer": "Test Developer",
                    "commit_count": 5,
                    "lines_added": 100,
                    "lines_deleted": 50,
                    "files_changed": 10,
                    "languages_used": ["Python", "JavaScript"],
                    "avg_complexity": 2.5
                }
            },
            "repository_stats": {
                "test-repo": {
                    "total_commits": 5,
                    "total_files": 10
                }
            }
        }
    
    def test_service_initialization(self):
        """서비스 초기화 테스트"""
        assert self.service is not None
        assert hasattr(self.service, 'templates')
        assert len(self.service.templates) > 0
        assert "daily_summary" in self.service.templates
    
    def test_build_daily_summary_prompt_success(self):
        """일일 요약 프롬프트 생성 성공 테스트"""
        result = self.service.build_daily_summary_prompt(
            aggregated_data=self.sample_aggregated_data,
            target_developer="Test Developer"
        )
        
        assert isinstance(result, PromptResult)
        assert result.is_valid
        assert "Test Developer" in result.prompt
        assert "5개" in result.prompt  # 커밋 수
        assert result.template_used == "daily_summary"
        assert result.metadata.template_version == "1.0"
        assert result.metadata.token_count > 0
    
    def test_build_daily_summary_prompt_with_missing_developer(self):
        """존재하지 않는 개발자로 프롬프트 생성 테스트"""
        result = self.service.build_daily_summary_prompt(
            aggregated_data=self.sample_aggregated_data,
            target_developer="Nonexistent Developer"
        )
        
        assert isinstance(result, PromptResult)
        assert result.is_valid
        assert "Nonexistent Developer" in result.prompt
        assert "0개" in result.prompt  # 기본값으로 0 커밋
    
    def test_build_daily_summary_prompt_with_empty_data(self):
        """빈 데이터로 프롬프트 생성 테스트"""
        empty_data = {"developer_stats": {}}
        
        result = self.service.build_daily_summary_prompt(
            aggregated_data=empty_data,
            target_developer="Test Developer"
        )
        
        assert isinstance(result, PromptResult)
        assert result.is_valid
        assert "Test Developer" in result.prompt
    
    @pytest.mark.asyncio
    async def test_build_prompt_async_success(self):
        """비동기 프롬프트 생성 성공 테스트"""
        input_data = PromptInput(
            aggregated_data=self.sample_aggregated_data,
            prompt_type=PromptType.DAILY_SUMMARY,
            target_developer="Test Developer"
        )
        
        result = await self.service.build_prompt(input_data)
        
        assert isinstance(result, PromptResult)
        assert result.is_valid
        assert "Test Developer" in result.prompt
        assert result.template_used == "daily_summary"
    
    @pytest.mark.asyncio
    async def test_build_prompt_with_customization(self):
        """커스터마이징 옵션과 함께 프롬프트 생성 테스트"""
        customization = CustomizationOptions(
            tone="casual",
            include_emoji=False,
            language="english"
        )
        
        input_data = PromptInput(
            aggregated_data=self.sample_aggregated_data,
            prompt_type=PromptType.DAILY_SUMMARY,
            target_developer="Test Developer",
            customization=customization
        )
        
        result = await self.service.build_prompt(input_data)
        
        assert isinstance(result, PromptResult)
        assert result.is_valid
        assert result.metadata.language == "korean"  # 현재는 한국어로 고정
    
    def test_select_template_success(self):
        """템플릿 선택 성공 테스트"""
        template = self.service._select_template(PromptType.DAILY_SUMMARY)
        
        assert isinstance(template, str)
        assert len(template) > 0
        assert "{developer_name}" in template
        assert "{commit_count}" in template
    
    def test_select_template_not_found(self):
        """존재하지 않는 템플릿 선택 테스트"""
        # 임시로 존재하지 않는 프롬프트 타입 생성
        class InvalidPromptType:
            value = "nonexistent_template"
        
        invalid_type = InvalidPromptType()
        
        with pytest.raises(TemplateNotFoundException):
            self.service._select_template(invalid_type)
    
    def test_build_context_with_existing_developer(self):
        """존재하는 개발자로 컨텍스트 구성 테스트"""
        input_data = PromptInput(
            aggregated_data=self.sample_aggregated_data,
            prompt_type=PromptType.DAILY_SUMMARY,
            target_developer="Test Developer"
        )
        
        context = self.service._build_context(input_data)
        
        assert context["developer_name"] == "Test Developer"
        assert context["commit_count"] == 5
        assert context["files_changed"] == 10
        assert context["lines_added"] == 100
        assert context["lines_deleted"] == 50
        assert "Python" in context["languages_used"]
    
    def test_build_context_with_missing_developer(self):
        """존재하지 않는 개발자로 컨텍스트 구성 테스트"""
        input_data = PromptInput(
            aggregated_data=self.sample_aggregated_data,
            prompt_type=PromptType.DAILY_SUMMARY,
            target_developer="Missing Developer"
        )
        
        context = self.service._build_context(input_data)
        
        assert context["developer_name"] == "Missing Developer"
        assert context["commit_count"] == 0
        assert context["files_changed"] == 0
        assert context["lines_added"] == 0
        assert context["lines_deleted"] == 0
    
    def test_render_template_success(self):
        """템플릿 렌더링 성공 테스트"""
        template = "Hello {name}, you have {count} items"
        context = {"name": "John", "count": 5}
        
        result = self.service._render_template(template, context)
        
        assert result == "Hello John, you have 5 items"
    
    def test_render_template_missing_variable(self):
        """템플릿 변수 누락 시 예외 발생 테스트"""
        template = "Hello {name}, you have {count} items"
        context = {"name": "John"}  # count 누락
        
        with pytest.raises(PromptBuilderException):
            self.service._render_template(template, context)
    
    def test_optimize_token_usage(self):
        """토큰 사용량 최적화 테스트"""
        # 짧은 텍스트는 그대로 유지
        short_text = "Short prompt"
        optimized_short = self.service._optimize_token_usage(short_text)
        assert optimized_short == short_text
        
        # 긴 텍스트는 잘림
        long_text = "A" * 3000  # 매우 긴 텍스트
        optimized_long = self.service._optimize_token_usage(long_text)
        assert len(optimized_long) < len(long_text)
    
    def test_estimate_token_count(self):
        """토큰 수 추정 테스트"""
        text = "This is a test with multiple words"
        token_count = self.service._estimate_token_count(text)
        
        # 대략적인 토큰 수 확인 (정확한 값보다는 합리적인 범위)
        word_count = len(text.split())
        assert token_count >= word_count  # 최소한 단어 수만큼
        assert token_count <= word_count * 2  # 최대 단어 수의 2배


class TestPromptBuilderServiceErrorHandling:
    """PromptBuilderService 오류 처리 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.service = PromptBuilderService()
    
    @pytest.mark.asyncio
    async def test_build_prompt_with_invalid_data(self):
        """잘못된 데이터로 프롬프트 생성 시 예외 처리 테스트"""
        # pydantic 검증으로 인해 None 데이터는 생성 시점에 예외 발생
        with pytest.raises(Exception):  # ValidationError 또는 다른 예외
            input_data = PromptInput(
                aggregated_data=None,
                prompt_type=PromptType.DAILY_SUMMARY,
                target_developer="Test Developer"
            )
    
    def test_build_daily_summary_with_malformed_data(self):
        """잘못된 형식의 데이터로 일일 요약 생성 테스트"""
        malformed_data = {
            "developer_stats": "not_a_dict"  # 딕셔너리가 아님
        }
        
        # 예외가 발생하거나 적절히 처리되어야 함
        try:
            result = self.service.build_daily_summary_prompt(
                aggregated_data=malformed_data,
                target_developer="Test Developer"
            )
            # 예외가 발생하지 않으면 결과가 유효해야 함
            assert isinstance(result, PromptResult)
        except (PromptBuilderException, AttributeError, TypeError):
            # 예외가 발생하는 것도 정상적인 동작
            pass 