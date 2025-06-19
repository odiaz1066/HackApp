from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
import sqlite3 as sql
from urllib.parse import parse_qs
import json
from db import con, init_db, get_product, get_products, login, getComments, addTransaction, get_user, get_users

flag = "d6486ba2a9e59434851bfc7b6e5e4a18"

def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'  
        elif "/api/users" in self.path:
            params = parse_qs(self.path)
            print(f'Received GET request for: {self.path}')
            print(params)
            user_id = params.get('/api/users?id', [None])[0]
            if user_id:
                response = get_user(user_id)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                print(response)
                self.wfile.write(bytes(json.dumps(response), 'utf-8'))
                return
            else:
                response = get_users()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(bytes(json.dumps(response), 'utf-8'))
                return        
        elif '/api/products' in self.path:
            params = parse_qs(self.path)
            print(f'Received GET request for: {self.path}')
            print(params)
            product_id = params.get('/api/products?id', [None])[0]
            if product_id:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = get_product(product_id)
                print(response)
                self.wfile.write(bytes(str(response), 'utf-8'))
                return
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = get_products()
                self.wfile.write(bytes(str(response), 'utf-8'))
                return
        elif "/api/comments" in self.path:
            params = parse_qs(self.path)
            print(f'Received GET request for: {self.path}')
            print(params)
            product_id = params.get('/api/comments?product_id', [None])[0]
            response = getComments(product_id)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
            return
        elif "/api/transactions" in self.path:
            params = parse_qs(self.path)
            print(f'Received GET request for: {self.path}')
            print(params)
            user_id = params.get('/api/transactions?user_id', [None])[0]
            if user_id:
                db = con.cursor()
                db.execute(f'SELECT * FROM transactions WHERE user_id = "{user_id}"')
                transactions = db.fetchall()
                db.close()
                #response = [{'id': t[0], 'user_id': t[1], 'products': t[2], 'created_at': t[3]} for t in transactions]
                response = transactions
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(bytes(json.dumps(response), 'utf-8'))
                return
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'User ID is required')
                return
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(f'Received POST data: {post_data.decode()}')
        data = json.loads(post_data.decode())
        print(f'Parsed POST data: {data}')
        if "/api/login" in self.path:
            username = data.get('username')
            password = data.get('password')
            print(f'Login attempt with username: {username} and password: {password}')
            user = login(username, password)
            if not user:
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b'Login failed')
                return
            #Here we make a secure token composed of [username][id padded with 0s]
            token = {"token": f'{user["name"]}{str(user["id"]).rjust(3, "0")}'}
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(token), 'utf-8'))
            return
        if "/api/register" in self.path:
            name = data.get('name')
            email = data.get('email')
            password = data.get('pass')
            print(f'Registration attempt with name: {name}, email: {email}')
            db = con.cursor()
            try:
                db.execute(f'INSERT INTO users (name, email, password) VALUES ("{name}", "{email}", "{password}")')
                con.commit()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(bytes(json.dumps('Registration successful'), "utf-8"))
            except sql.IntegrityError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write('User already exists')
            finally:
                db.close()
            return
        elif "/api/comments" in self.path:
            product_id = data.get('product_id')
            user_id = data.get('user_id')
            text = data.get('text')
            print(f'Adding comment for product {product_id} by user {user_id}: {text}')
            db = con.cursor()
            try:
                db.execute(f'INSERT INTO comments (product_id, user_id, text) VALUES ({product_id}, {user_id}, "{text}")')
                con.commit()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(bytes(json.dumps('Comment added successfully'), 'utf-8'))
            except sql.IntegrityError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Error adding comment')
            finally:
                db.close()
            return
        elif "/api/cart" in self.path:
            cart_data = data.get('cart')
            print(f'Cart data received: {cart_data}')
            cart_items = []
            for item in cart_data:
                product_id = item.get('id')
                quantity = item.get('quantity', 1)
                product = get_product(product_id)
                if product:
                    cart_items.append({
                        'product': product,
                        'quantity': quantity
                    })
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(cart_items), 'utf-8'))
            return
        elif "/api/checkout" in self.path:
            user_id = data.get('user_id')
            cart_data = data.get('cart')
            response = addTransaction(user_id, cart_data)
            if response:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(bytes(json.dumps({'transaction_id': response}), 'utf-8'))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Error processing transaction')
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'POST request received')

init_db()  # Initialize the database
run(handler_class=MyHandler)
