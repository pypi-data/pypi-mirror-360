"""
Universal Prompt Builder 기본 테스트

모듈의 기본 임포트와 구조를 테스트합니다.
"""

import pytest


def test_models_import():
    """모델 임포트 테스트"""
    from raas_prompt_builder.models import (
        PromptType, PromptTemplate, PromptVariable,
        PromptRequest, PromptResponse, BuiltPrompt
    )
    
    # 열거형 값 확인
    assert PromptType.COMMIT_SUMMARY == "commit_summary"
    assert PromptType.CODE_REVIEW == "code_review"
    assert PromptType.BUG_ANALYSIS == "bug_analysis"


def test_exceptions_import():
    """예외 클래스 임포트 테스트"""
    from raas_prompt_builder.exceptions import (
        PromptBuilderException,
        TemplateNotFoundException,
        VariableValidationException
    )
    
    # 예외 클래스 확인
    assert issubclass(TemplateNotFoundException, PromptBuilderException)
    assert issubclass(VariableValidationException, PromptBuilderException)


def test_prompt_variable_creation():
    """PromptVariable 생성 테스트"""
    from raas_prompt_builder.models import PromptVariable
    
    variable = PromptVariable(
        name="commit_message",
        value="Fix authentication bug",
        required=True
    )
    
    assert variable.name == "commit_message"
    assert variable.value == "Fix authentication bug"
    assert variable.required is True


def test_prompt_template_creation():
    """PromptTemplate 생성 테스트"""
    from raas_prompt_builder.models import PromptTemplate, PromptType
    
    template = PromptTemplate(
        name="commit_summary_template",
        content="Summarize this commit: {commit_message}",  # template -> content로 변경
        # prompt_type 제거 (PromptTemplate에 없음)
        # description 제거 (PromptTemplate에 없음)
    )
    
    assert template.name == "commit_summary_template"
    assert template.content == "Summarize this commit: {commit_message}"


def test_prompt_request_creation():
    """PromptRequest 생성 테스트"""
    from raas_prompt_builder.models import PromptRequest, PromptType
    
    request = PromptRequest(
        template_id="commit_summary_template",  # template_name -> template_id로 변경
        prompt_type=PromptType.COMMIT_SUMMARY,
        variables={"commit_message": "Fix bug in login"}
    )
    
    assert request.template_id == "commit_summary_template"
    assert request.prompt_type == PromptType.COMMIT_SUMMARY
    assert request.variables["commit_message"] == "Fix bug in login"


def test_built_prompt_creation():
    """BuiltPrompt 생성 테스트"""
    from raas_prompt_builder.models import BuiltPrompt, PromptType
    
    built = BuiltPrompt(
        prompt_type=PromptType.COMMIT_SUMMARY,
        content="Summarize this commit: Fix bug in login",
        template_name="commit_summary_template",
        variables_used={"commit_message": "Fix bug in login"}
    )
    
    assert built.prompt_type == PromptType.COMMIT_SUMMARY
    assert built.content == "Summarize this commit: Fix bug in login"
    assert built.template_name == "commit_summary_template"
    assert built.variables_used["commit_message"] == "Fix bug in login"


def test_exception_creation():
    """예외 생성 테스트"""
    from raas_prompt_builder.exceptions import TemplateNotFoundException
    
    exception = TemplateNotFoundException("missing_template")
    
    assert "missing_template" in str(exception)
    assert exception.details["template_name"] == "missing_template" 