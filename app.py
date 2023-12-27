from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Initialize SQLite database
DATABASE = 'tasks.db'

def create_table():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            done BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

# Create the tasks table if it doesn't exist
create_table()

# CRUD operations

# Read all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    tasks = [{'id': row[0], 'title': row[1], 'description': row[2], 'done': row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify({'tasks': tasks})

# Read a specific task by ID
@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = c.fetchone()
    conn.close()

    if task is None:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify({'task': {'id': task[0], 'title': task[1], 'description': task[2], 'done': task[3]}})

# Create a new task
@app.route('/tasks', methods=['POST'])
def create_task():
    if not request.json or 'title' not in request.json:
        return jsonify({'error': 'Title is required'}), 400

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO tasks (title, description, done) VALUES (?, ?, ?)',
              (request.json['title'], request.json.get('description', ""), False))
    conn.commit()
    task_id = c.lastrowid
    conn.close()

    return jsonify({'task': {'id': task_id, 'title': request.json['title'], 'description': request.json.get('description', ""), 'done': False}}), 201

# Update a task by ID
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = c.fetchone()

    if task is None:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    update_data = {}
    if 'title' in request.json:
        update_data['title'] = request.json['title']
    if 'description' in request.json:
        update_data['description'] = request.json['description']
    if 'done' in request.json:
        update_data['done'] = request.json['done']

    c.execute('UPDATE tasks SET title=?, description=?, done=? WHERE id=?',
              (update_data.get('title', task[1]),
               update_data.get('description', task[2]),
               update_data.get('done', task[3]),
               task_id))
    conn.commit()
    conn.close()

    return jsonify({'task': {'id': task_id, 'title': update_data.get('title', task[1]), 'description': update_data.get('description', task[2]), 'done': update_data.get('done', task[3])}})

# Delete a task by ID
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

    return jsonify({'result': True})

if __name__ == '__main__':
    app.run(debug=True)
