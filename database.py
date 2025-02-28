import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('warehouse.db')
        self.cur = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL
            )
        ''')
        self.conn.commit()
     
    def add_item(self, name, quantity, price):
        self.cur.execute('INSERT INTO items (name, quantity, price) VALUES (?, ?, ?)',
                        (name, quantity, price))
        self.conn.commit()
    
    def get_all_items(self):
        self.cur.execute('SELECT * FROM items')
        return self.cur.fetchall()
    
    def update_item(self, id, name, quantity, price):
        self.cur.execute('UPDATE items SET name=?, quantity=?, price=? WHERE id=?',
                        (name, quantity, price, id))
        self.conn.commit()
    
    def delete_item(self, id):
        self.cur.execute('DELETE FROM items WHERE id=?', (id,))
        self.conn.commit()
    
    def search_items(self, name='', min_quantity=None, max_price=None):
        query = 'SELECT * FROM items WHERE 1=1'
        params = []
        
        if name:
            query += ' AND name LIKE ?'
            params.append(f'%{name}%')
        
        if min_quantity is not None:
            query += ' AND quantity >= ?'
            params.append(min_quantity)
        
        if max_price is not None:
            query += ' AND price <= ?'
            params.append(max_price)
        
        self.cur.execute(query, params)
        return self.cur.fetchall() 