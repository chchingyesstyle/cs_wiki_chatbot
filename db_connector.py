import pymysql
from typing import List, Dict, Optional
from config import Config

class WikiDBConnector:
    """Connector for MediaWiki MariaDB database"""
    
    def __init__(self):
        self.config = Config()
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = pymysql.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                database=self.config.DB_NAME,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print(f"Connected to database: {self.config.DB_NAME}")
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def search_pages(self, query: str, limit: int = 5) -> List[Dict]:
        """Search wiki pages by title or content, prioritizing current pages"""
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                # MediaWiki 1.43+ uses slots + content table
                # Prioritize: 1) Current pages, 2) Title matches over content matches
                sql = """
                    SELECT 
                        p.page_id,
                        p.page_title,
                        p.page_namespace,
                        t.old_text as content,
                        CASE 
                            WHEN p.page_title NOT LIKE %s
                                AND p.page_title NOT LIKE %s
                                AND p.page_title NOT LIKE %s THEN 3
                            ELSE 1
                        END +
                        CASE 
                            WHEN p.page_title LIKE %s THEN 2
                            ELSE 0
                        END as relevance
                    FROM page p
                    JOIN revision r ON p.page_latest = r.rev_id
                    JOIN slots s ON r.rev_id = s.slot_revision_id
                    JOIN content c ON s.slot_content_id = c.content_id
                    LEFT JOIN text t ON CAST(SUBSTRING(c.content_address, 4) AS UNSIGNED) = t.old_id
                    WHERE p.page_namespace = 0
                    AND (
                        p.page_title LIKE %s 
                        OR t.old_text LIKE %s
                    )
                    ORDER BY relevance DESC
                    LIMIT %s
                """
                search_term = f"%{query}%"
                cursor.execute(sql, ('%OUTDATED%', '%EXPIRED%', '%MOVED%', search_term, search_term, search_term, limit))
                results = cursor.fetchall()
                return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_page_by_title(self, title: str) -> Optional[Dict]:
        """Get a specific page by title"""
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                # MediaWiki 1.43+ schema
                sql = """
                    SELECT 
                        p.page_id,
                        p.page_title,
                        p.page_namespace,
                        t.old_text as content
                    FROM page p
                    JOIN revision r ON p.page_latest = r.rev_id
                    JOIN slots s ON r.rev_id = s.slot_revision_id
                    JOIN content c ON s.slot_content_id = c.content_id
                    LEFT JOIN text t ON CAST(SUBSTRING(c.content_address, 4) AS UNSIGNED) = t.old_id
                    WHERE p.page_title = %s
                    AND p.page_namespace = 0
                    LIMIT 1
                """
                cursor.execute(sql, (title.replace(' ', '_'),))
                result = cursor.fetchone()
                return result
        except Exception as e:
            print(f"Get page error: {e}")
            return None
    
    def get_all_pages(self, limit: int = 100) -> List[Dict]:
        """Get all wiki pages (for context building)"""
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                # MediaWiki 1.43+ schema
                sql = """
                    SELECT 
                        p.page_id,
                        p.page_title,
                        LEFT(t.old_text, 200) as content
                    FROM page p
                    JOIN revision r ON p.page_latest = r.rev_id
                    JOIN slots s ON r.rev_id = s.slot_revision_id
                    JOIN content c ON s.slot_content_id = c.content_id
                    LEFT JOIN text t ON CAST(SUBSTRING(c.content_address, 4) AS UNSIGNED) = t.old_id
                    WHERE p.page_namespace = 0
                    LIMIT %s
                """
                cursor.execute(sql, (limit,))
                results = cursor.fetchall()
                return results
        except Exception as e:
            print(f"Get all pages error: {e}")
            return []
