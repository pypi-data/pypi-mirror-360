"""
Universal Prompt Builder Models

프롬프트 생성을 위한 데이터 모델들을 정의합니다.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field


class PromptType(str, Enum):
    """프롬프트 유형"""
    DAILY_SUMMARY = "daily_summary"
    CODE_REVIEW = "code_review"
    WORK_PATTERN_ANALYSIS = "work_pattern_analysis"
    TEAM_REPORT = "team_report"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    COMMIT_SUMMARY = "commit_summary"
    BUG_ANALYSIS = "bug_analysis"


class CustomizationOptions(BaseModel):
    """커스터마이징 옵션"""
    tone: str = Field(default="professional", description="프롬프트 톤 (professional, casual, formal)")
    detail_level: str = Field(default="medium", description="상세도 수준 (low, medium, high)")
    language: str = Field(default="korean", description="언어 (korean, english)")
    include_emoji: bool = Field(default=True, description="이모지 포함 여부")
    include_statistics: bool = Field(default=True, description="통계 포함 여부")
    include_recommendations: bool = Field(default=False, description="권장사항 포함 여부")
    max_length: Optional[int] = Field(default=None, description="최대 길이 제한")


class TemplateConfig(BaseModel):
    """템플릿 설정"""
    template_name: str = Field(..., description="템플릿 이름")
    version: str = Field(default="1.0", description="템플릿 버전")
    token_limit: int = Field(default=4000, description="토큰 제한")
    required_fields: List[str] = Field(default_factory=list, description="필수 필드 목록")
    optional_fields: List[str] = Field(default_factory=list, description="선택적 필드 목록")


class PromptInput(BaseModel):
    """프롬프트 입력 데이터"""
    aggregated_data: Dict[str, Any] = Field(..., description="집계된 데이터")
    prompt_type: PromptType = Field(..., description="프롬프트 유형")
    target_developer: str = Field(..., description="대상 개발자")
    customization: Optional[CustomizationOptions] = Field(default=None, description="커스터마이징 옵션")
    context: Optional[str] = Field(default=None, description="추가 컨텍스트")
    
    def __init__(self, **data):
        if data.get('customization') is None:
            data['customization'] = CustomizationOptions()
        super().__init__(**data)


class PromptMetadata(BaseModel):
    """프롬프트 메타데이터"""
    template_version: str = Field(..., description="사용된 템플릿 버전")
    token_count: int = Field(..., description="토큰 수")
    generation_time: datetime = Field(default_factory=datetime.now, description="생성 시간")
    estimated_cost: float = Field(default=0.0, description="예상 비용")
    language: str = Field(default="korean", description="언어")
    customizations_applied: List[str] = Field(default_factory=list, description="적용된 커스터마이징")


class PromptResult(BaseModel):
    """프롬프트 결과 데이터"""
    prompt: str = Field(..., description="생성된 프롬프트")
    metadata: PromptMetadata = Field(..., description="메타데이터")
    context_data: Dict[str, Any] = Field(..., description="컨텍스트 데이터")
    template_used: str = Field(..., description="사용된 템플릿")
    
    @property
    def is_valid(self) -> bool:
        """프롬프트 유효성 확인"""
        return bool(self.prompt and self.prompt.strip())
    
    @property
    def estimated_tokens(self) -> int:
        """예상 토큰 수 (대략적 계산)"""
        return int(len(self.prompt.split()) * 1.3)  # 영어 기준 근사치


class TemplateVariable(BaseModel):
    """템플릿 변수"""
    name: str = Field(..., description="변수 이름")
    value: Any = Field(..., description="변수 값")
    is_required: bool = Field(default=True, description="필수 여부")
    default_value: Any = Field(default=None, description="기본값")


class PromptTemplate(BaseModel):
    """프롬프트 템플릿"""
    name: str = Field(..., description="템플릿 이름")
    content: str = Field(..., description="템플릿 내용")
    variables: List[TemplateVariable] = Field(default_factory=list, description="템플릿 변수들")
    config: Optional[TemplateConfig] = Field(default=None, description="템플릿 설정")
    
    def get_required_variables(self) -> List[str]:
        """필수 변수 목록 반환"""
        return [var.name for var in self.variables if var.is_required]
    
    def get_optional_variables(self) -> List[str]:
        """선택적 변수 목록 반환"""
        return [var.name for var in self.variables if not var.is_required]


class TokenUsage(BaseModel):
    """토큰 사용량 정보"""
    prompt_tokens: int = Field(..., description="프롬프트 토큰 수")
    estimated_completion_tokens: int = Field(..., description="예상 완료 토큰 수")
    total_tokens: int = Field(..., description="총 토큰 수")
    cost_estimate: float = Field(default=0.0, description="비용 추정")
    
    @property
    def is_within_limit(self) -> bool:
        """토큰 제한 내 여부"""
        return self.total_tokens <= 4000  # 기본 제한값


class PromptVariable(BaseModel):
    """프롬프트 변수"""
    name: str = Field(..., description="변수 이름")
    value: str = Field(..., description="변수 값")
    variable_type: str = Field(default="string", description="변수 타입")
    required: bool = Field(default=True, description="필수 여부")
    
    
class PromptRequest(BaseModel):
    """프롬프트 요청"""
    prompt_type: PromptType = Field(..., description="프롬프트 타입")
    template_id: str = Field(..., description="템플릿 ID")
    variables: Dict[str, Any] = Field(default_factory=dict, description="템플릿 변수들")
    options: Optional[CustomizationOptions] = Field(default=None, description="커스터마이징 옵션")


class PromptResponse(BaseModel):
    """프롬프트 응답"""
    prompt: str = Field(..., description="생성된 프롬프트")
    success: bool = Field(..., description="성공 여부")
    error_message: Optional[str] = Field(None, description="에러 메시지")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="메타데이터")


class BuiltPrompt(BaseModel):
    """빌드된 프롬프트"""
    prompt_type: PromptType = Field(..., description="프롬프트 타입")
    content: str = Field(..., description="프롬프트 내용")
    template_name: str = Field(..., description="템플릿 이름")
    variables_used: Dict[str, Any] = Field(default_factory=dict, description="사용된 변수들")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="메타데이터")
    token_count: int = Field(default=0, description="토큰 수")


class ContextData(BaseModel):
    """컨텍스트 데이터"""
    developer_stats: Dict[str, Any] = Field(..., description="개발자 통계")
    repository_stats: Dict[str, Any] = Field(..., description="저장소 통계")
    time_analysis: Dict[str, Any] = Field(..., description="시간 분석")
    complexity_metrics: Dict[str, Any] = Field(..., description="복잡도 메트릭")
    relevant_commits: List[Dict[str, Any]] = Field(default_factory=list, description="관련 커밋들")
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """요약 통계 반환"""
        return {
            "total_commits": len(self.relevant_commits),
            "developer_count": len(self.developer_stats),
            "repository_count": len(self.repository_stats),
            "has_complexity_data": bool(self.complexity_metrics)
        } 