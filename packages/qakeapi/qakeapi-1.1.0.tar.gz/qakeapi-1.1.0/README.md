# QakeAPI 🚀

A modern, lightweight, and fast ASGI web framework for building APIs in Python, focusing on developer experience and performance.

[![Tests](https://github.com/Craxti/qakeapi/actions/workflows/tests.yml/badge.svg)](https://github.com/Craxti/qakeapi/actions/workflows/tests.yml)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PyPI version](https://badge.fury.io/py/qakeapi.svg)](https://badge.fury.io/py/qakeapi)
[![Downloads](https://pepy.tech/badge/qakeapi)](https://pepy.tech/project/qakeapi)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<p align="center">
  <img src="logo.png" alt="QakeAPI Logo" width="200"/>
</p>

## ✨ Why QakeAPI?

- 🚀 **High Performance**: Built on ASGI for maximum speed and scalability
- 💡 **Intuitive API**: Clean, Pythonic interface that feels natural
- 📝 **Auto Documentation**: OpenAPI/Swagger docs generated automatically
- 🔒 **Security First**: Built-in authentication, CORS, and rate limiting
- 🎯 **Type Safety**: Full type hints support for better IDE integration
- 📦 **Modular**: Easy to extend with middleware and plugins

## 🎯 Perfect For

- RESTful APIs
- Microservices
- Real-time applications
- API Gateways
- Backend for SPAs
- Serverless Functions

## 🚀 Quick Start

### Option 1: Using CLI (Recommended)

```bash
# Install QakeAPI
pip install qakeapi

# Create a new project with CLI
python3 qakeapi_cli.py create my-api --template=api

# Navigate to project and run
cd my-api
python app/main.py
```

### Option 2: Manual Setup

```bash
pip install qakeapi
```

Create a simple API in seconds:

```python
from qakeapi import Application, Response
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

app = Application()

@app.get("/")
async def hello():
    return {"message": "Hello, World!"}

@app.post("/items")
async def create_item(item: Item):
    return Response.json(item.dict(), status_code=201)

if __name__ == "__main__":
    app.run()
```

## 🛠️ CLI Tool

QakeAPI comes with a powerful CLI tool for rapid project scaffolding:

```bash
# List available templates and features
python3 qakeapi_cli.py list

# Create projects with different templates
python3 qakeapi_cli.py create my-api --template=api
python3 qakeapi_cli.py create my-web --template=web --features=auth,templates
python3 qakeapi_cli.py create my-microservice --template=microservice

# Interactive mode
python3 qakeapi_cli.py create my-app
```

**Available Templates:**
- **Basic API** - Simple CRUD operations
- **Full API** - Complete API with auth, database, cache
- **Web Application** - Templates, static files, frontend
- **Microservice** - Lightweight service with minimal dependencies

**Available Features:**
- Authentication (JWT)
- Database integration (SQLAlchemy)
- Caching (Redis)
- Rate limiting
- Templates (Jinja2)
- WebSockets
- Testing (pytest)
- Docker support
- Live reload for development

## 🌟 Key Features

### Authentication & Security
```python
from qakeapi.security import requires_auth, BasicAuthBackend

auth = BasicAuthBackend()

@app.get("/protected")
@requires_auth(auth)
async def protected():
    return {"message": "Secret data"}
```

### Rate Limiting
```python
from qakeapi.security import RateLimiter

limiter = RateLimiter(requests_per_minute=60)
app.add_middleware(limiter)
```

### CORS Support
```python
from qakeapi.middleware import CORSMiddleware

cors = CORSMiddleware(allow_origins=["http://localhost:3000"])
app.add_middleware(cors)
```

## 📚 Documentation

- [Quick Start Guide](https://github.com/Craxti/qakeapi/wiki/Quick-Start)
- [API Reference](https://github.com/Craxti/qakeapi/wiki/API-Reference)
- [Middleware Guide](https://github.com/Craxti/qakeapi/wiki/Middleware)
- [Security Best Practices](https://github.com/Craxti/qakeapi/wiki/Security)
- [Deployment Guide](https://github.com/Craxti/qakeapi/wiki/Deployment)

## 🔥 Real-World Examples

Check out our [examples](examples/) directory for production-ready examples:

- [Authentication API](examples/auth_app.py)
- [Rate Limited API](examples/rate_limit_app.py)
- [CORS-enabled API](examples/cors_app.py)
- [WebSocket Chat](examples/websocket_app.py)
- [Background Tasks](examples/background_tasks_app.py)

## 🤝 Contributing

We love your input! We want to make contributing to QakeAPI as easy and transparent as possible. Check out our [Contributing Guide](CONTRIBUTING.md) to get started.

### Development Setup

```bash
git clone https://github.com/Craxti/qakeapi.git
cd qakeapi
pip install -e ".[dev]"
pytest
```

## 🌟 Show Your Support

Give a ⭐️ if this project helped you! Every star helps increase the visibility of the project.

## 📝 License

[MIT License](LICENSE) - feel free to use this project for your applications.

## 🙏 Acknowledgments

- Inspired by modern web frameworks like FastAPI and Starlette
- Built with love for the Python community
- Thanks to all our contributors!

## 📬 Get in Touch

- Report bugs by [creating an issue](https://github.com/Craxti/qakeapi/issues)
- Follow [@qakeapi](https://twitter.com/qakeapi) for updates
- Join our [Discord community](https://discord.gg/qakeapi)

---

<p align="center">Made with ❤️ by the QakeAPI Team</p> 