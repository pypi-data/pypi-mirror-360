![logo](logo.png)

[![codecov](https://codecov.io/gh/Hcha-byte/Flask-Back/branch/main/graph/badge.svg?token=TY4UGA63NQ)](https://codecov.io/gh/Hcha-byte/Flask-Back)
[![Run Tests](https://github.com/Hcha-byte/Flask-Back/actions/workflows/test.yml/badge.svg)](https://github.com/Hcha-byte/Flask-Back/actions/workflows/test.yml)
![Python Versions](https://img.shields.io/pypi/pyversions/flask-back)
[![PyPI](https://img.shields.io/pypi/v/flask-back?label=PyPI&color=brightgreen&cacheSeconds=3600)](https://pypi.org/project/flask-back/)
![License](https://img.shields.io/github/license/hcha-byte/flask-back?color=brightgreen)

**Flask-Back** is a lightweight Flask extension for managing "back" URLs to help users return to their previous page in a clean and configurable way.

---

## 🚀 Features

* Automatically or manually save back URLs
* Use `{{ back_url }}` in templates
* Fallback to the referrer if no back URL is saved
* Exclude specific endpoints from tracking
* Session-based and lightweight

---

## 📦 Installation

```bash
pip install flask-back
```

---

## 🧪 Quick Example

```python
from flask import Flask, redirect
from flask_back import Back

app = Flask(__name__)
app.secret_key = "supersecret"

back = Back(app, default_url="/", use_referrer=True)

@app.route("/save")
@back.save_url
def save_page():
    return "This page is now saved as the back URL."

@app.route("/go-back")
def go_back():
    return redirect(back.get_url())

@app.route("/excluded")
@back.exclude
def excluded_page():
    return "This page won't be tracked as a back URL."
```

In templates:

```jinja2
<a href="{{ back_url }}">Go Back</a>
```

---

## ⚙️ Configuration

You can pass these options when initializing:

```python
Back(app,
     default_url="/fallback",     # Where to go if nothing is saved
     use_referrer=True,           # Use Referer header as fallback
     excluded_endpoints=["static"]  # List of endpoints to skip
)
```

---

## 🧼 API Summary

* `Back(app=None, **settings)` – Create the extension
* `save_url(func)` – Decorator to manually mark routes as back URLs
* `get_url(default=None)` – Retrieve saved URL or fallback
* `clear()` – Clear current back URL from session
* `exclude(func)` – Decorator to ignore tracking for a route

---

## ✅ Testing

```bash
pytest
pytest --cov=src --cov-report=term-missing
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, testing, and PR tips.

---

## 🔐 Security

Found a vulnerability? Please report it via [GitHub Issues](https://github.com/Hcha-byte/Flask-Back/issues) or email [Hcha.Byte@gmail.com](mailto:Hcha.Byte@gmail.com).

---

## 📦 License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

---

## 💡 Inspiration

Flask-Back was built to solve a common pattern in web apps: helping users return to the right place—without relying solely on browser behavior. Now you can manage that flow clearly and securely.

---

> ⭐ Star the repo if you find it helpful!

[![GitHub stars](https://img.shields.io/github/stars/Hcha-byte/Flask-Back?style=social)](https://github.com/Hcha-byte/Flask-Back)