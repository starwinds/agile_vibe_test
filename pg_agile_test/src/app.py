from flask import Flask, request, jsonify
from src.db_utils import connect, insert_item, search_combined
from src.embedding import get_embedding

app = Flask(__name__)

@app.route('/item', methods=['POST'])
def add_item_endpoint():
    data = request.get_json()
    if not data or not all(k in data for k in ['item_name', 'category', 'content']):
        return jsonify({"error": "Missing required fields: item_name, category, content"}), 400

    try:
        # Get embedding for the content
        vec = get_embedding(data['content'])

        # Connect to DB and insert item
        conn = connect()
        insert_item(conn, data['item_name'], data['category'], data['content'], vec)
        conn.close()

        return jsonify({"message": "Item added successfully"}), 201
    except Exception as e:
        # A real app would have more specific error handling and logging
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['GET'])
def search_endpoint():
    query = request.args.get('query')
    category = request.args.get('category')

    if not query:
        return jsonify({"error": "Missing required 'query' parameter"}), 400

    try:
        # Get embedding for the query
        query_vec = get_embedding(query)

        # Connect to DB and search
        conn = connect()
        results = search_combined(conn, query_vec, category=category, limit=5)
        conn.close()

        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
