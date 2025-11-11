"""Constants - Single Source of Truth for domain names"""

# 도메인 정의 (DB/CSV 표준: 슬래시 포함)
DOMAINS = [
    "경제/경영",
    "과학/기술",
    "역사/사회",
    "인문/자기계발"
]

# 도메인 매핑 (KB 파일명용: 슬래시 없음)
DOMAIN_TO_KB = {
    "경제/경영": "경제경영",
    "과학/기술": "과학기술",
    "역사/사회": "역사사회",
    "인문/자기계발": "인문자기계발"
}

# 역매핑 (KB → DB)
KB_TO_DOMAIN = {v: k for k, v in DOMAIN_TO_KB.items()}

# LangGraph 노드 이름
LANGGRAPH_NODES = [
    "anchor_mapper",
    "review_domain",
    "integrator",
    "producer",
    "assemble",
    "validator"
]

# 노드별 진행률
NODE_PROGRESS = {
    "anchor_mapper": 11.1,
    "review_domain": 33.3,
    "integrator": 55.6,
    "producer": 77.8,
    "assemble": 100.0,
    "validator": 88.9
}

