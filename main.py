import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Beginner Coder API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Snippet(BaseModel):
    title: str
    language: str
    code: str
    explanation: str


class Language(BaseModel):
    id: str
    name: str
    description: str
    difficulty: str
    topics: List[str]
    hello_world: Snippet
    tips: List[str]
    resources: List[dict]


# Static beginner-friendly content (no DB required for this simple catalog)
LANGUAGES: List[Language] = [
    Language(
        id="python",
        name="Python",
        description="Friendly, readable, and great for beginners. Used for web, data, AI, scripts, and more.",
        difficulty="Easy",
        topics=["Variables", "Loops", "Functions", "Lists", "Dictionaries"],
        hello_world=Snippet(
            title="Hello, World!",
            language="python",
            code="""# hello.py\nprint('Hello, World!')""",
            explanation="Run with: python hello.py"
        ),
        tips=[
            "Use meaningful names: total_price, user_age",
            "Prefer f-strings for formatting",
            "Read errors from bottom-up: the final line often explains it",
        ],
        resources=[
            {"label": "Official Docs", "url": "https://docs.python.org/3/"},
            {"label": "W3Schools", "url": "https://www.w3schools.com/python/"},
        ],
    ),
    Language(
        id="c",
        name="C",
        description="Low-level power and speed. Great for understanding how computers work.",
        difficulty="Medium",
        topics=["Compilation", "Pointers", "Arrays", "Structs", "Headers"],
        hello_world=Snippet(
            title="Hello, World!",
            language="c",
            code='''// hello.c\n#include <stdio.h>\n\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}''',
            explanation="Compile with: gcc hello.c -o hello\nRun: ./hello"
        ),
        tips=[
            "Always initialize your variables",
            "Check return values of functions like malloc and fopen",
            "Use -Wall -Wextra flags with gcc to catch bugs early",
        ],
        resources=[
            {"label": "C Reference", "url": "https://en.cppreference.com/w/c"},
            {"label": "Learn C", "url": "https://www.learn-c.org/"},
        ],
    ),
    Language(
        id="cpp",
        name="C++",
        description="C with high-level features: OOP, templates, and the STL.",
        difficulty="Medium",
        topics=["Classes", "Vectors", "References", "STL", "Templates"],
        hello_world=Snippet(
            title="Hello, World!",
            language="cpp",
            code='''// hello.cpp\n#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, World!" << endl;\n    return 0;\n}''',
            explanation="Compile with: g++ hello.cpp -o hello\nRun: ./hello"
        ),
        tips=[
            "Prefer std::vector over raw arrays",
            "Use references (T&) to avoid unnecessary copies",
            "Learn RAII to manage resources safely",
        ],
        resources=[
            {"label": "cppreference", "url": "https://en.cppreference.com/w/"},
            {"label": "Learn C++", "url": "https://www.learncpp.com/"},
        ],
    ),
    Language(
        id="html",
        name="HTML & CSS",
        description="The building blocks of the web: structure (HTML) and style (CSS).",
        difficulty="Easy",
        topics=["Tags", "Attributes", "Semantic HTML", "Selectors", "Flexbox", "Grid"],
        hello_world=Snippet(
            title="A simple page",
            language="html",
            code='''<!-- index.html -->\n<!doctype html>\n<html lang="en">\n  <head>\n    <meta charset="UTF-8" />\n    <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n    <title>Hello</title>\n  </head>\n  <body>\n    <h1>Hello, World!</h1>\n    <p>Welcome to the web!</p>\n  </body>\n</html>''',
            explanation="Open the file in your browser. Use VS Code Live Server for quick reloads."
        ),
        tips=[
            "Use semantic tags: header, nav, main, section, footer",
            "Mobile-first: start with small screens, then add @media rules",
            "Use CSS Flexbox/Grid for layout instead of floats",
        ],
        resources=[
            {"label": "MDN Web Docs", "url": "https://developer.mozilla.org/en-US/"},
            {"label": "Flexbox Froggy", "url": "https://flexboxfroggy.com/"},
        ],
    ),
]


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/api/languages", response_model=List[Language])
def list_languages(q: Optional[str] = None):
    if not q:
        return LANGUAGES
    query = q.lower().strip()
    return [lang for lang in LANGUAGES if query in lang.name.lower() or any(query in t.lower() for t in lang.topics)]


@app.get("/api/languages/{lang_id}", response_model=Language)
def get_language(lang_id: str):
    for lang in LANGUAGES:
        if lang.id == lang_id:
            return lang
    raise HTTPException(status_code=404, detail="Language not found")


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
