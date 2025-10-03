from flask import Flask, jsonify, request, abort
try:
    # When running as a package (e.g., `python -m backend.api`)
    from .db import count_posts, list_posts, get_post
except ImportError:
    # When running directly (e.g., `python backend/api.py`)
    from db import count_posts, list_posts, get_post


app = Flask(__name__)


@app.get("/api/posts")
def api_posts():
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))
    except ValueError:
        return jsonify({"error": "invalid pagination"}), 400

    page = max(1, page)
    page_size = min(100, max(1, page_size))

    total = count_posts()
    total_pages = max(1, -(-total // page_size))  # ceil div
    if page > total_pages:
        page = total_pages

    offset = (page - 1) * page_size
    posts = list_posts(page_size, offset)
    return jsonify({
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "posts": posts,
    })


@app.get("/api/posts/<post_id>")
def api_post_detail(post_id: str):
    post = get_post(post_id)
    if not post:
        abort(404)
    return jsonify(post)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)


