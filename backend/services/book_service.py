"""Book Service - CSV 파일 로딩 및 도서 데이터 관리"""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BookService:
    """도서 데이터 관리 서비스"""
    
    def __init__(self, csv_path: str = "docs/100권 노션 원본.csv"):
        self.csv_path = Path(csv_path)
        self.books: List[Dict] = []
        
    def load_books(self) -> int:
        """
        CSV 파일에서 도서 데이터 로드
        
        Returns:
            로드된 도서 개수
        """
        if not self.csv_path.exists():
            logger.error(f"[FAIL] CSV file not found: {self.csv_path}")
            return 0
        
        try:
            df = pd.read_csv(self.csv_path)
            
            # 딕셔너리 리스트로 변환
            self.books = df.to_dict('records')
            
            logger.info(f"[OK] {len(self.books)} books loaded from CSV")
            return len(self.books)
        
        except Exception as e:
            logger.error(f"[FAIL] CSV loading error: {e}")
            return 0
    
    def get_book_by_id(self, book_id: int) -> Optional[Dict]:
        """
        일련번호로 도서 조회
        
        Args:
            book_id: 일련번호
        
        Returns:
            도서 딕셔너리 또는 None
        """
        for book in self.books:
            if book.get('일련번호') == book_id:
                return book
        return None
    
    def get_books_by_ids(self, book_ids: List[int]) -> List[Dict]:
        """
        여러 일련번호로 도서 조회
        
        Args:
            book_ids: 일련번호 리스트
        
        Returns:
            도서 딕셔너리 리스트
        """
        result = []
        for book_id in book_ids:
            book = self.get_book_by_id(book_id)
            if book:
                result.append(book)
        return result
    
    def get_books_by_domain(self, domain: str) -> List[Dict]:
        """
        도메인으로 필터링
        
        Args:
            domain: 구분 (경제/경영, 과학/기술, 역사/사회, 인문/자기계발)
        
        Returns:
            해당 도메인의 도서 리스트
        """
        return [book for book in self.books if book.get('구분') == domain]
    
    def search_books(self, keyword: str, field: str = 'Title') -> List[Dict]:
        """
        키워드로 도서 검색
        
        Args:
            keyword: 검색 키워드
            field: 검색할 필드 (Title, 저자, Topic 등)
        
        Returns:
            검색 결과 리스트
        """
        results = []
        for book in self.books:
            if keyword.lower() in str(book.get(field, '')).lower():
                results.append(book)
        return results
    
    def get_book_summary(self, book_id: int, use_short: bool = True) -> str:
        """
        도서 요약 가져오기
        
        Args:
            book_id: 일련번호
            use_short: True면 짧은 요약, False면 긴 Summary
        
        Returns:
            요약 텍스트
        """
        book = self.get_book_by_id(book_id)
        if not book:
            return f"Book {book_id} not found"
        
        field = '요약' if use_short else 'Summary'
        return book.get(field, "No summary available")
    
    def get_books_summary_combined(self, book_ids: List[int], use_short: bool = True) -> str:
        """
        여러 도서의 요약을 하나로 합치기
        
        Args:
            book_ids: 일련번호 리스트
            use_short: True면 짧은 요약 사용
        
        Returns:
            통합 요약 텍스트
        """
        summaries = []
        for book_id in book_ids:
            book = self.get_book_by_id(book_id)
            if book:
                title = book.get('Title', f'Book {book_id}')
                summary = book.get('요약' if use_short else 'Summary', '')
                summaries.append(f"[{title}]\n{summary}")
        
        return "\n\n".join(summaries)
    
    def get_stats(self) -> Dict:
        """도서 통계"""
        if not self.books:
            return {}
        
        # 도메인별 카운트
        domain_counts = {}
        for book in self.books:
            domain = book.get('구분', 'Unknown')
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        return {
            "total_books": len(self.books),
            "by_domain": domain_counts,
            "year_range": (
                min(b.get('연도', 9999) for b in self.books),
                max(b.get('연도', 0) for b in self.books)
            )
        }


# Global book service instance
book_service = BookService()

