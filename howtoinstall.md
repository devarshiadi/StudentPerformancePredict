
## 🚀 Getting Started

### 1. **Clone the Repository**
```bash
git clone https://github.com/devarshiadi/StudentPerformancePredict
cd StudentPerformancePredict
````

### 2. **Create a Virtual Environment**

```bash
python -m venv venv
```

### 3. **Activate the Virtual Environment**

* **Windows**:

```bash
venv\Scripts\activate
```

* **macOS/Linux**:

```bash
source venv/bin/activate
```

### 4. **Install Required Dependencies**

```bash
pip install -r requirements.txt
```

### 5. **Run the FastAPI Server**

```bash
uvicorn app.main:app --reload
```

---

## 🧪 Testing the API

Once the server is running, open your browser and navigate to:

* Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 📌 Notes

* Make sure you have **Python 3.7+** installed.
* If you're using an IDE like VSCode, ensure the interpreter is set to use the `venv`.

---

## 🙌 License

This project is licensed under the MIT License.
