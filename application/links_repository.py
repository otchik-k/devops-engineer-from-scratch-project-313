from psycopg2.extras import RealDictCursor

from config import DOMEN_FOR_SHORT_URL


class LinksRepository:
    def __init__(self, conn):
        self.conn = conn


    def insert_data(self, original_url, short_name):
        try:
            query_insert = """
                INSERT INTO links (original_url, short_name) 
                VALUES (%s, %s) 
                RETURNING id;
            """
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query_insert, (original_url, short_name))
                id_value = cur.fetchone()['id']
                short_url = f"{DOMEN_FOR_SHORT_URL}/{short_name}/{id_value}"
                query_update = """
                        UPDATE links 
                        SET short_url = %s 
                        WHERE id = %s;
                    """
                cur.execute(query_update, (short_url, id_value))
                self.conn.commit()
            return {'original_url': original_url, 'short_name': short_name}
        except Exception as e:
            self.conn.rollback()
            print(f"Транзакция отменена из‑за ошибки: {e}")
    

    def get_total_links_count(self):
        try:
            query_select = 'SELECT COUNT(*) FROM links;'
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query_select)
                result = cur.fetchone()
                print(result)
                return result['count'] if result else 0
        except Exception as e:
            self.conn.rollback()
            print(f"Транзакция отменена из‑за ошибки: {e}")
            return 0
            

    def select_all_links(self):
        try:
            query_select = 'SELECT id, original_url, short_name, short_url FROM links'
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query_select)
                return cur.fetchall()
        except Exception as e:
            self.conn.rollback()
            print(f"Транзакция отменена из‑за ошибки: {e}")


    def select_links_from_range(self, range):
        offset = range[0]
        limit = range[1] - range[0] + 1
        try:
            query_select = 'SELECT id, original_url, short_name, short_url FROM links ORDER BY id LIMIT %s OFFSET %s;'
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query_select, (limit, offset))
                return cur.fetchall()
        except Exception as e:
            self.conn.rollback()
            print(f"Транзакция отменена из‑за ошибки: {e}")
            return 0
    
    
    def select_link_for_id(self, id_value):
        try:
            query_select = """
                SELECT id, original_url, short_name, short_url
                FROM links
                WHERE id = %s
            """
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query_select, (id_value,))
                return cur.fetchone()
        except Exception as e:
            self.conn.rollback()
            print(f"Транзакция отменена из‑за ошибки: {e}")
    
    
    def update_link_for_id(self, id_value, original_url, short_name):
        try:
            short_url = f"{DOMEN_FOR_SHORT_URL}/{short_name}/{id_value}"
            query_update = """
                    UPDATE links
                    SET original_url = %s, short_name = %s, short_url = %s
                    WHERE id = %s
                """
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query_update, (original_url, short_name, short_url, id_value))
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"Транзакция отменена из‑за ошибки: {e}")
    
    
    def delete_link_for_id(self, id_value):
        try:
            query_delete = """
                DELETE FROM links
                WHERE id = %s
            """
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query_delete, (id_value,))
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"Транзакция отменена из‑за ошибки: {e}")