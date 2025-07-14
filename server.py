#server which handless todos and http routing
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import hashlib

users_map= {}
todo_map = {}
next_id = 1

def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()

class ToDoHandler(BaseHTTPRequestHandler): #new custom class ToDoHandler  used to handle HTTP requests,
    # It inherits from BaseHTTPRequestHandler

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def send_json_response(self,data,status_code=200):
        self.send_response(status_code)
        self.send_header("Content-type","application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path == "/todos":
            self.send_json_response({
                "status": "ok",
                "todos": todo_map
            })
        else:
            self.send_json_response({
                "status": "error",
                "message": "Invalid Get route"
            },status_code=404)

    def do_POST(self):
        global next_id
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_json_response({
                "status": "error",
                "message": "No data received"
            }, status_code=400)
            return

        post_data = self.rfile.read(content_length)

        try:
            postData = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_json_response({
                "status": "error",
                "message": "invalid JSON"
            }, status_code=400)
            return

        if self.path == "/add":
            if 'todo' not in postData or not postData['todo'].strip():
                self.send_json_response({
                    "status": "error",
                    "message": "Todo cannot be empty"
                }, status_code=400)
                return

            new_todo = postData['todo'].strip()

            # replaces new_todo if already exits
            existing_id = None
            for todo_id, todo in todo_map.items():
                if todo['todo'].lower() == new_todo.lower():
                    existing_id = todo_id
                    break

            if existing_id is not None:
                todo_map[existing_id]['todo'] = new_todo
                self.send_json_response({
                    "status": "Updated",
                    "todo": {existing_id: todo_map[existing_id]}
                })
                return

            todo_map[next_id] = {
                "todo": new_todo,
                "status": "active"
            }
            self.send_json_response({
                "status": "ok",
                "message": "Todo added",
                "todo": {next_id: todo_map[next_id]}
            })
            next_id += 1

        elif self.path == "/register":
            username = postData.get("username")
            password = postData.get("password")

            if not username or not password:
                self.send_json_response({
                    "status": "error",
                    "message": "Username and password required"
                }, 400)
                return

            if username in users_map:
                self.send_json_response({
                    "status": "error",
                    "message": "Username already exists"
                }, 400)
                return

            users_map[username] = hash_password(password)
            self.send_json_response({
                "status": "ok",
                "message": "User registered successfully"
            })

        elif self.path == "/login":
            username = postData.get("username")
            password = postData.get("password")

            if username not in users_map or users_map[username] != hash_password(password):
                self.send_json_response({
                    "status": "error",
                    "message": "Invalid username or password"
                }, 401)
                return

            self.send_json_response({
                "status": "ok",
                "message": f"Welcome, {username}!"
            })

        elif self.path == "/delete":
            todo_id = postData.get("id")
            if not isinstance(todo_id, int):
                self.send_json_response({
                    "status": "error",
                    "message": "Todo id must be an integer"
                }, status_code=400)
                return

            if todo_id in todo_map:
                deleted = todo_map.pop(todo_id)
                self.send_json_response({
                    "status": "ok",
                    "message": f"Todo ID {todo_id} deleted",
                    "deleted": {todo_id: deleted}
                })


        else:
            self.send_json_response({
                "status": "error",
                "message": "Invalid Post Route"
            }, status_code=404)

    def do_PUT(self):
        if self.path.startswith("/update/"):
            try:
                todo_id = int(self.path.split("/")[-1])
            except ValueError:
                self.send_json_response({
                    "status": "error",
                    "message": "Invalid todo ID in URL"
                }, status_code=400)
                return

            content_length = int(self.headers.get("Content-Length",0))
            if content_length == 0:
                self.send_json_response({
                    "status": "error",
                    "message": "provide id to update"
                }, status_code=400)
                return

            update_data = self.rfile.read(content_length)


            try:
                updated_Data = json.loads(update_data)
            except json.JSONDecodeError:
                self.send_json_response({
                    "status": "error",
                    "message": "Invalid json"
                }, status_code=400)
                return

            updated_todo = updated_Data.get("todo")
            updated_status = updated_Data.get("status")

            if todo_id in todo_map:
                if updated_todo:
                    todo_map[todo_id]['todo'] = updated_todo
                if updated_status in ['active', "inactive"]:
                    todo_map[todo_id]['status'] = updated_status
                self.send_json_response({
                    "status": "Updated",
                    "message": f"Todo with id {todo_id} updated",
                    "todo": {todo_id: todo_map[todo_id]}
                })
            else:
                self.send_json_response({
                    "status": "error",
                    "message": f"No todo found with id {todo_id}"
                }, status_code=400)

        else:
            self.send_json_response({
                "status": "error",
                "message": "Invalid update Route"
            }, status_code=404)


    def do_DELETE(self):
        global next_id
        if self.path == "/clear":
            todo_map.clear()
            next_id = 1
            self.send_json_response({
                "status": "ok",
                "message": "all todos deleted",
                "todos": {}
            })
        else:
            self.send_json_response({
                "status": "error",
                "message": "Invalid Delete Route"
            }, status_code=404)



def run(server_class=HTTPServer, handler_class=ToDoHandler, port=8000): #function run() with default parameters, server_class- create the HTTP server,
    # handler_class-handles HTTP requests, port-server listens on
    server_address = ('localhost', port) #server will bind to (host + port
    httpd = server_class(server_address, handler_class) #creates the server, server_class-Creates an instance of the server
    #Every time a request comes in, it creates an object of ToDoHandler to process it
    print(f"Starting httpd on port {port}...")
    httpd.serve_forever() # infinite loop that keeps the server running

if __name__ == "__main__":
    run()