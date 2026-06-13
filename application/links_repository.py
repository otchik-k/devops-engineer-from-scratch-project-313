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
            return short_url
        except Exception as e:
            self.conn.rollback()
            print(f"Транзакция отменена из‑за ошибки: {e}")


    def select_all_links(self):
        try:
            sql_select = 'SELECT id, original_url, short_name, short_url FROM links'
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql_select)
                return cur.fetchall()
        except Exception as e:
            self.conn.rollback()
            print(f"Транзакция отменена из‑за ошибки: {e}")
    
    
    def select_link_for_id(self, id_value):
        try:
            query_select = """
                SELECT id, original_url, short_name, short_url
                FROM links
                WHERE id = %s
            """
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query_select, (id_value,))
                return cur.fetchall()
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