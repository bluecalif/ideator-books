"""Knowledge Base Service - KB 파일 파싱 및 검색"""
import re
from pathlib import Path
from typing import List, Optional, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

from backend.models.schemas import KBItem, KBSearchResult, KBStats

logger = logging.getLogger(__name__)


class KBService:
    """KB 파일 파싱 및 검색 서비스"""
    
    # KB 파일명용 도메인 (슬래시 없음)
    KB_DOMAINS = ["경제경영", "과학기술", "역사사회", "인문자기계발"]
    
    # DB/CSV 표준 도메인 (슬래시 있음)
    DB_DOMAINS = ["경제/경영", "과학/기술", "역사/사회", "인문/자기계발"]
    
    # 매핑
    DOMAIN_MAPPING = {
        "경제/경영": "경제경영",
        "과학/기술": "과학기술",
        "역사/사회": "역사사회",
        "인문/자기계발": "인문자기계발"
    }
    
    # 역매핑
    KB_TO_DB = {v: k for k, v in DOMAIN_MAPPING.items()}
    
    def __init__(self, kb_dir: str = None):
        # 프로젝트 루트의 docs/ 디렉토리 찾기
        if kb_dir is None:
            # backend/services/kb_service.py → backend/ → project_root/
            project_root = Path(__file__).parent.parent.parent
            kb_dir = project_root / "docs"
        self.kb_dir = Path(kb_dir)
        self.kb_items: Dict[str, List[KBItem]] = {}
        self.all_items: List[KBItem] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        
    def load_all_domains(self) -> Dict[str, int]:
        """모든 도메인 KB 파일 로드"""
        result = {}
        for domain in self.KB_DOMAINS:
            count = self.load_domain(domain)
            result[domain] = count
            logger.info(f"[OK] {domain}: {count} items loaded")
        
        # 전체 아이템 리스트 생성
        self.all_items = []
        for items in self.kb_items.values():
            self.all_items.extend(items)
        
        # TF-IDF 벡터라이저 준비
        self._prepare_vectorizer()
        
        logger.info(f"[OK] Total {len(self.all_items)} KB items loaded")
        return result
    
    def load_domain(self, domain: str) -> int:
        """특정 도메인 KB 파일 로드"""
        file_path = self.kb_dir / f"지식베이스생성_{domain}_구글스튜디오.md"
        
        if not file_path.exists():
            logger.error(f"[FAIL] KB file not found: {file_path}")
            return 0
        
        items = self._parse_kb_file(file_path, domain)
        self.kb_items[domain] = items
        return len(items)
    
    def _parse_kb_file(self, file_path: Path, domain: str) -> List[KBItem]:
        """KB 파일 파싱 (개별 인사이트 + 통합지식)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        items = []
        current_subcategory = None
        kb_index = 1
        
        # 소분류 섹션별로 분할
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # 소분류 헤더 감지: ### **소분류: XXX**
            subcategory_match = re.match(r'###\s+\*\*소분류:\s*(.+?)\*\*', line)
            if subcategory_match:
                current_subcategory = subcategory_match.group(1).strip()
                i += 1
                continue
            
            # 테이블 행 파싱: | 인사이트 내용 | 참고 도서 |
            if current_subcategory and line.strip().startswith('|') and not line.strip().startswith('| :'):
                parts = [p.strip() for p in line.split('|')]
                
                # 유효한 테이블 행인지 확인 (최소 4개 파트: '', 인사이트, 도서, '')
                if len(parts) >= 4 and parts[1] and parts[2]:
                    insight_text = parts[1]
                    books_text = parts[2]
                    
                    # 헤더 행 건너뛰기
                    if '핵심 인사이트' in insight_text or '참고 도서' in books_text:
                        i += 1
                        continue
                    
                    # 융합형 플래그 감지
                    is_fusion = '**(융합형)**' in insight_text
                    if is_fusion:
                        insight_text = insight_text.replace('**(융합형)**', '').strip()
                    
                    # 참고 도서 파싱 (쉼표로 구분)
                    reference_books = [b.strip() for b in books_text.split(',')]
                    
                    # anchor_id 생성
                    anchor_id = f"{domain}_{current_subcategory.replace('/', '_')}_{kb_index:03d}"
                    
                    # KBItem 생성
                    item = KBItem(
                        kb_id=f"kb_{domain}_{kb_index:04d}",
                        domain=domain,
                        subcategory=current_subcategory,
                        anchor_id=anchor_id,
                        content=insight_text,
                        is_fusion=is_fusion,
                        is_integrated_knowledge=False,
                        reference_books=reference_books
                    )
                    items.append(item)
                    kb_index += 1
            
            # 통합지식 섹션 감지: **통합 지식** 또는 **통합지식**
            elif current_subcategory and re.match(r'\*\*통합\s*지식\*\*', line):
                # 다음 줄부터 통합지식 내용 수집
                integrated_content_lines = []
                i += 1
                
                while i < len(lines):
                    next_line = lines[i]
                    # 다음 소분류 섹션이 시작되면 중단
                    if re.match(r'###\s+\*\*소분류:', next_line):
                        break
                    # 내용 수집 (빈 줄 제외)
                    if next_line.strip():
                        integrated_content_lines.append(next_line.strip())
                    i += 1
                
                # 통합지식 내용이 있으면 KBItem 생성
                if integrated_content_lines:
                    integrated_content = ' '.join(integrated_content_lines)
                    
                    # 통합지식 anchor_id: {domain}·{subcategory} 통합지식
                    anchor_id = f"{domain}·{current_subcategory} 통합지식"
                    
                    item = KBItem(
                        kb_id=f"kb_{domain}_integrated_{current_subcategory}",
                        domain=domain,
                        subcategory=current_subcategory,
                        anchor_id=anchor_id,
                        content=integrated_content,
                        is_fusion=False,
                        is_integrated_knowledge=True,
                        reference_books=[]  # 통합지식은 참고 도서 없음
                    )
                    items.append(item)
                    logger.info(f"[OK] Parsed integrated knowledge: {anchor_id}")
                
                continue
            
            i += 1
        
        return items
    
    def _prepare_vectorizer(self):
        """TF-IDF 벡터라이저 준비"""
        if not self.all_items:
            logger.warning("[WARN] No KB items to vectorize")
            return
        
        corpus = [item.content for item in self.all_items]
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        logger.info(f"[OK] TF-IDF vectorizer prepared with {len(corpus)} documents")
    
    def search(
        self,
        query: str,
        domain: Optional[str] = None,
        top_k: int = 5,
        min_score: float = 0.0,
        prioritize_integrated: bool = True
    ) -> List[KBSearchResult]:
        """
        KB 검색 (TF-IDF 유사도 기반)
        
        Args:
            query: 검색 쿼리
            domain: 도메인 필터 (선택)
            top_k: 반환할 결과 개수
            min_score: 최소 유사도 점수
            prioritize_integrated: 통합지식 우선 반환 여부
        
        Returns:
            검색 결과 리스트 (통합지식 우선)
        """
        # 도메인 필터링
        candidates = self.all_items
        if domain and domain in self.kb_items:
            candidates = self.kb_items[domain]
        
        if not candidates or not self.vectorizer:
            logger.warning("[WARN] No candidates or vectorizer not initialized")
            return []
        
        # 쿼리 벡터화
        try:
            query_vector = self.vectorizer.transform([query])
        except Exception as e:
            logger.error(f"[FAIL] Vectorization error: {e}")
            return []
        
        # 후보군에 대한 TF-IDF 매트릭스 생성
        candidate_indices = [self.all_items.index(item) for item in candidates if item in self.all_items]
        if not candidate_indices:
            return []
        
        candidate_matrix = self.tfidf_matrix[candidate_indices]
        
        # 유사도 계산
        similarities = cosine_similarity(query_vector, candidate_matrix)[0]
        
        # 통합지식 우선 정렬
        if prioritize_integrated:
            # (is_integrated_knowledge, similarity) 튜플로 정렬
            scored_candidates = []
            for idx, score in enumerate(similarities):
                item = candidates[idx]
                # 통합지식이면 점수에 0.05 가중치 추가 (우선순위 향상)
                adjusted_score = score + (0.05 if item.is_integrated_knowledge else 0.0)
                scored_candidates.append((idx, adjusted_score, score))  # (idx, adjusted, original)
            
            # adjusted_score 기준으로 정렬
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            top_candidates = scored_candidates[:top_k]
            
            results = []
            for idx, adjusted_score, original_score in top_candidates:
                if original_score >= min_score:
                    results.append(KBSearchResult(
                        item=candidates[idx],
                        similarity_score=original_score  # 원래 점수 반환
                    ))
        else:
            # 기존 로직 (유사도만으로 정렬)
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                if score >= min_score:
                    results.append(KBSearchResult(
                        item=candidates[idx],
                        similarity_score=score
                    ))
        
        return results
    
    def get_stats(self) -> KBStats:
        """KB 통계"""
        fusion_count = sum(1 for item in self.all_items if item.is_fusion)
        
        items_by_domain = {}
        for domain, items in self.kb_items.items():
            items_by_domain[domain] = len(items)
        
        items_by_subcategory = {}
        for item in self.all_items:
            key = f"{item.domain}_{item.subcategory}"
            items_by_subcategory[key] = items_by_subcategory.get(key, 0) + 1
        
        return KBStats(
            total_items=len(self.all_items),
            fusion_items=fusion_count,
            items_by_domain=items_by_domain,
            items_by_subcategory=items_by_subcategory
        )
    
    def get_item_by_anchor(self, anchor_id: str) -> Optional[KBItem]:
        """Anchor ID로 아이템 조회"""
        for item in self.all_items:
            if item.anchor_id == anchor_id:
                return item
        return None
    
    def validate_uniqueness(self) -> Dict[str, any]:
        """KB 아이템 고유성 검증"""
        anchor_ids = [item.anchor_id for item in self.all_items]
        kb_ids = [item.kb_id for item in self.all_items]
        
        duplicate_anchors = [aid for aid in anchor_ids if anchor_ids.count(aid) > 1]
        duplicate_kb_ids = [kid for kid in kb_ids if kb_ids.count(kid) > 1]
        
        return {
            "unique_anchors": len(set(anchor_ids)) == len(anchor_ids),
            "unique_kb_ids": len(set(kb_ids)) == len(kb_ids),
            "duplicate_anchors": list(set(duplicate_anchors)),
            "duplicate_kb_ids": list(set(duplicate_kb_ids)),
            "total_items": len(self.all_items)
        }


# Global KB service instance
kb_service = KBService()

# Auto-load KB on module import
logger.info("[KB-SERVICE] Auto-loading KB on module import...")
try:
    _load_stats = kb_service.load_all_domains()
    logger.info(f"[KB-SERVICE] KB auto-loaded successfully: {_load_stats}")
except Exception as e:
    logger.error(f"[KB-SERVICE] KB auto-load failed: {e}")

