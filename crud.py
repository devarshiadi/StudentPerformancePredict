import database, hashlib, json
from auth import get_password_hash, verify_password
import models

# Users

def get_user_by_id(user_id):
    with database.get_conn() as c:
        r = c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return r and models.User(id=r['id'], email=r['email'], name=r['name'])

def create_user(email, name, password):
    hashed = get_password_hash(password)
    with database.get_conn() as c:
        c.execute("INSERT INTO users (email,name,hashed_password) VALUES (?,?,?)",
                  (email,name,hashed))

def get_user_by_email(email):
    with database.get_conn() as c:
        r = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    return r and models.User(id=r['id'], email=r['email'], name=r['name'])

def get_user_by_id(user_id):
    with database.get_conn() as c:
        r = c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return r and models.User(id=r['id'], email=r['email'], name=r['name'])

def authenticate_user(email, password):
    user = get_user_by_email(email)
    if not user: return None
    with database.get_conn() as c:
        r = c.execute("SELECT hashed_password FROM users WHERE email=?", (email,)).fetchone()
    if not verify_password(password, r['hashed_password']): return None
    return user

def list_users():
    with database.get_conn() as c:
        rows = c.execute("SELECT * FROM users").fetchall()
    return [models.User(id=r['id'], email=r['email'], name=r['name']) for r in rows]

def update_user(user_id, name, email):
    with database.get_conn() as c:
        c.execute("UPDATE users SET name=?,email=? WHERE id=?", (name,email,user_id))

def delete_user(user_id):
    with database.get_conn() as c:
        c.execute("DELETE FROM users WHERE id=?", (user_id,))

# Predictions

def save_prediction(user_id, pred, acc, algo, input_dict):
    j = json.dumps(input_dict)
    with database.get_conn() as c:
        cur = c.execute(
          "INSERT INTO predictions (user_id,predicted,accuracy,algorithm,input_json) VALUES (?,?,?,?,?)",
          (user_id,pred,acc,algo,j)
        )
    return cur.lastrowid

def get_predictions(user_id):
    with database.get_conn() as c:
        rows = c.execute("SELECT * FROM predictions WHERE user_id=? ORDER BY id", (user_id,)).fetchall()
    return [models.Prediction(id=r['id'], predicted=r['predicted'], accuracy=r['accuracy'], algorithm=r['algorithm'], input_json=json.loads(r['input_json']), timestamp=r['timestamp']) for r in rows]

def delete_prediction(pred_id, user_id):
    with database.get_conn() as c:
        c.execute("DELETE FROM predictions WHERE id=? AND user_id=?", (pred_id,user_id))




