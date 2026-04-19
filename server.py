from flask import Flask, request, jsonify
from flask_cors import CORS
from bookDAO import bookDAO

app = Flask(__name__, static_url_path="", static_folder="staticpages")
CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/books", methods=["GET"])
def get_all():
    books = bookDAO.getAll()
    return jsonify(books), 200


@app.route("/books/<int:id>", methods=["GET"])
def find_by_id(id):
    book = bookDAO.findByID(id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book), 200


@app.route("/books", methods=["POST"])
def create():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    title = data.get("title")
    author = data.get("author")
    price = data.get("price")

    if title is None or str(title).strip() == "":
        return jsonify({"error": "title is required"}), 400
    if author is None or str(author).strip() == "":
        return jsonify({"error": "author is required"}), 400
    if price is None:
        return jsonify({"error": "price is required"}), 400

    book = {
        "title": str(title).strip(),
        "author": str(author).strip(),
        "price": price
    }

    created = bookDAO.create(book)
    return jsonify(created), 201


@app.route("/books/<int:id>", methods=["PUT"])
def update(id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    book = {}

    if "title" in data:
        title = str(data["title"]).strip()
        if title == "":
            return jsonify({"error": "title cannot be empty"}), 400
        book["title"] = title

    if "author" in data:
        author = str(data["author"]).strip()
        if author == "":
            return jsonify({"error": "author cannot be empty"}), 400
        book["author"] = author

    if "price" in data:
        book["price"] = data["price"]

    if not book:
        return jsonify({"error": "No fields provided to update"}), 400

    updated = bookDAO.update(id, book)
    if not updated:
        return jsonify({"error": "Book not found"}), 404

    return jsonify(updated), 200


@app.route("/books/<int:id>", methods=["DELETE"])
def delete(id):
    deleted = bookDAO.delete(id)
    if not deleted:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"success": True}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)