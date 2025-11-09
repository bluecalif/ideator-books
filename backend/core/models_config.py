"""LLM Models Configuration - 노드별 모델 설정"""

# 노드별 LLM 모델 설정
# 필요에 따라 각 노드마다 다른 모델 사용 가능


class ModelsConfig:
    """노드별 LLM 모델 설정"""

    # AnchorMapper: 도서→앵커 매핑 및 분석
    ANCHOR_MAPPER_MODEL = "gpt-4.1-mini"
    
    # Reviewer: 4개 도메인 리뷰 (병렬 실행)
    REVIEWER_MODEL = "gpt-4.1-mini"
    
    # Integrator: 리뷰 통합 및 긴장축 추출
    INTEGRATOR_MODEL = "gpt-4.1-mini"
    
    # Producer: 최종 1p 생성
    PRODUCER_MODEL = "gpt-4.1-mini"
    
    # Temperature 설정
    ANCHOR_MAPPER_TEMP = 0.0
    REVIEWER_TEMP = 0.3
    INTEGRATOR_TEMP = 0.5
    PRODUCER_TEMP = 0.7

    @classmethod
    def get_model(cls, node_name: str) -> str:
        """노드 이름으로 모델 가져오기"""
        mapping = {
            "anchor_mapper": cls.ANCHOR_MAPPER_MODEL,
            "reviewer": cls.REVIEWER_MODEL,
            "integrator": cls.INTEGRATOR_MODEL,
            "producer": cls.PRODUCER_MODEL,
        }
        return mapping.get(node_name.lower(), "gpt-4o-mini")

    @classmethod
    def get_temperature(cls, node_name: str) -> float:
        """노드 이름으로 temperature 가져오기"""
        mapping = {
            "anchor_mapper": cls.ANCHOR_MAPPER_TEMP,
            "reviewer": cls.REVIEWER_TEMP,
            "integrator": cls.INTEGRATOR_TEMP,
            "producer": cls.PRODUCER_TEMP,
        }
        return mapping.get(node_name.lower(), 0.5)


# Global instance
models_config = ModelsConfig()
