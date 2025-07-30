"""
Universal Prompt Builder 예외 클래스

프롬프트 빌더와 관련된 예외들을 정의합니다.
"""

from typing import Dict, Any, Optional


class PromptBuilderException(Exception):
    """프롬프트 빌더 관련 기본 예외 클래스"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class TemplateNotFoundException(PromptBuilderException):
    """템플릿을 찾을 수 없는 예외"""
    
    def __init__(self, template_name: str):
        message = f"Template not found: {template_name}"
        details = {
            "template_name": template_name
        }
        super().__init__(message, details)


class VariableValidationException(PromptBuilderException):
    """변수 검증 예외"""
    
    def __init__(self, variable_name: str, reason: str):
        message = f"Variable validation failed for '{variable_name}': {reason}"
        details = {
            "variable_name": variable_name,
            "reason": reason
        }
        super().__init__(message, details)


class TemplateRenderException(PromptBuilderException):
    """템플릿 렌더링 예외"""
    
    def __init__(self, template_id: str, reason: str):
        message = f"Template rendering failed for '{template_id}': {reason}"
        details = {
            "template_id": template_id,
            "reason": reason
        }
        super().__init__(message, details)


class TemplateRenderingException(PromptBuilderException):
    """템플릿 렌더링 예외"""
    
    def __init__(self, template_name: str, original_error: Exception):
        message = f"Template rendering failed for '{template_name}'"
        details = {
            "template_name": template_name,
            "error_type": type(original_error).__name__,
            "error_message": str(original_error)
        }
        super().__init__(message, details)


class InvalidPromptTypeException(PromptBuilderException):
    """잘못된 프롬프트 타입 예외"""
    
    def __init__(self, prompt_type: str, valid_types: list):
        message = f"Invalid prompt type '{prompt_type}'. Valid types: {valid_types}"
        details = {
            "prompt_type": prompt_type,
            "valid_types": valid_types
        }
        super().__init__(message, details)


class TemplateCompilationException(PromptBuilderException):
    """템플릿 컴파일 예외"""
    
    def __init__(self, template_content: str, original_error: Exception):
        message = f"Template compilation failed"
        details = {
            "template_content": template_content[:100] + "..." if len(template_content) > 100 else template_content,
            "error_type": type(original_error).__name__,
            "error_message": str(original_error)
        }
        super().__init__(message, details)


class TokenLimitExceededException(PromptBuilderException):
    """토큰 제한을 초과한 경우"""
    def __init__(self, current_tokens: int, limit: int):
        message = f"Token limit exceeded: {current_tokens} > {limit}"
        super().__init__(message, {
            "current_tokens": current_tokens,
            "limit": limit,
            "excess": current_tokens - limit
        })


class MissingVariableException(PromptBuilderException):
    """필수 템플릿 변수가 누락된 경우"""
    def __init__(self, variable_name: str, template_name: str):
        message = f"Required variable '{variable_name}' missing for template '{template_name}'"
        super().__init__(message, {
            "variable_name": variable_name,
            "template_name": template_name
        })


class InvalidCustomizationException(PromptBuilderException):
    """잘못된 커스터마이징 옵션인 경우"""
    def __init__(self, option: str, value: str, valid_values: list):
        message = f"Invalid customization option '{option}': {value}"
        super().__init__(message, {
            "option": option,
            "value": value,
            "valid_values": valid_values
        }) 