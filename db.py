import  sqlite3 as sql

con = sql.connect('db.sqlite')

def init_db():
    db = con.cursor()
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        images TEXT
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        products TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    db.close()

def login(username, password):
    db = con.cursor()
    db.execute(f'SELECT * FROM users WHERE name = "{username}" AND password = "{password}"')
    user = db.fetchone()
    db.close()
    if user:
        return {'id': user[0], 'name': user[1], 'email': user[2]}
    else:
        return None

def get_user(user_id):
    db = con.cursor()
    db.execute(f'SELECT * FROM users WHERE id = "{user_id}"')
    user = db.fetchone()
    db.close()
    if user:
        return {'id': user[0], 'name': user[1], 'email': user[2]}
    else:
        return None
    
def get_users():
    db = con.cursor()
    db.execute('SELECT * FROM users')
    users = db.fetchall()
    db.close()
    return [{'id': user[0], 'name': user[1], 'email': user[2]} for user in users]

def get_products():
    db = con.cursor()
    db.execute('SELECT * FROM products')
    products = db.fetchall()
    db.close()
    return [{'id': product[0], 'name': product[1], 'price': product[2], 'images': product[3]} for product in products if product[1] != "Hidden Flag"]

def get_product(product_id):
    db = con.cursor()
    db.execute(f'SELECT * FROM products WHERE id = "{product_id}"')
    product = db.fetchone()
    db.close()
    if product:
        return {
            'id': product[0],
            'name': product[1],
            'price': product[2],
            'images': product[3]
        }
    else:
        return None
    
def getComments(product_id):
    db = con.cursor()
    db.execute(f'SELECT * FROM comments WHERE product_id = "{product_id}"')
    comments = db.fetchall()
    db.close()
    data = [{'id': comment[0], 'product_id': comment[1], 'user': get_user(comment[2]), 'text': comment[3], 'created_at': comment[4]} for comment in comments]
    return data

def addTransaction(user_id, products):
    db = con.cursor()
    db.execute('INSERT INTO transactions (user_id, products) VALUES (?, ?)', (user_id, str(products)))
    con.commit()
    transaction_id = db.lastrowid
    db.close()
    return transaction_id