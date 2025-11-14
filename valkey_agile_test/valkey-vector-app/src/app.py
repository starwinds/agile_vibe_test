from flask import Flask, request, jsonify, render_template_string
from .embedding import get_embedding
from .db_utils import connect, search_similar, insert_doc, create_index
import numpy as np
import uuid

app = Flask(__name__)

@app.route('/')
def hello_world():
    html_content = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>QA Service</title>
    <style>
        body { font-family: sans-serif; margin: 2em; }
        h1, h2 { color: #333; }
        form { margin-bottom: 2em; }
        label { display: block; margin-bottom: 0.5em; }
        input[type="text"], textarea { width: 100%; padding: 0.5em; margin-bottom: 1em; }
        #answer { background-color: #f0f0f0; padding: 1em; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>QA Service</h1>

    <h2>Ask a Question</h2>
    <form action="/qa" method="get" id="qa-form">
        <label>Question:</label>
        <input type="text" name="question">
        <button type="submit">Ask</button>
    </form>
    <div id="answer"></div>

    <h2>Add a Document</h2>
    <form action="/add_document" method="post" id="add-doc-form">
        <label>Document Content:</label>
        <textarea name="document" rows="5"></textarea>
        <button type="submit">Add Document</button>
    </form>
    <div id="add-doc-status"></div>
    <script>
        document.getElementById('qa-form').addEventListener('submit', async function(event) {
            event.preventDefault();
            const question = document.querySelector('#qa-form input[name="question"]').value;
            const responseDiv = document.getElementById('answer');
            responseDiv.innerHTML = 'Loading...';

            try {
                const response = await fetch(`/qa?question=${encodeURIComponent(question)}`);
                const data = await response.json();
                if (response.ok) {
                    responseDiv.innerHTML = `<strong>Answer:</strong> ${data.answer}`;
                } else {
                    responseDiv.innerHTML = `<strong>Error:</strong> ${data.error || 'Unknown error'}`;
                }
            } catch (error) {
                responseDiv.innerHTML = `<strong>Error:</strong> ${error.message}`;
            }
        });

        document.getElementById('add-doc-form').addEventListener('submit', async function(event) {
            event.preventDefault();
            const documentContent = document.querySelector('#add-doc-form textarea[name="document"]').value;
            const statusDiv = document.getElementById('add-doc-status');
            statusDiv.innerHTML = 'Adding document...';

            try {
                const response = await fetch('/add_document', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ document: documentContent })
                });
                const data = await response.json();
                if (response.ok) {
                    statusDiv.innerHTML = `<strong>Success:</strong> ${data.message} (ID: ${data.doc_id})`;
                    document.querySelector('#add-doc-form textarea[name="document"]').value = ''; // Clear textarea
                } else {
                    statusDiv.innerHTML = `<strong>Error:</strong> ${data.error || 'Unknown error'}`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<strong>Error:</strong> ${error.message}`;
            }
        });
    </script>
</body>
</html>
"""
    return render_template_string(html_content)

@app.route('/qa', methods=['GET'])
def qa():
    question = request.args.get('question')
    if not question:
        return jsonify({"error": "Question parameter is required"}), 400

    query_embedding = get_embedding(question)
    # The vector from get_embedding is bytes, but search_similar expects a list/numpy array of floats.
    # Let's convert it back.
    query_vector = np.frombuffer(query_embedding, dtype=np.float32)

    conn = connect()
    results = search_similar(conn, query_vector, limit=1)

    if not results:
        return jsonify({"answer": "No similar documents found."})

    return jsonify({"answer": results[0]['content']})

@app.route('/add_document', methods=['POST'])
def add_document():
    data = request.get_json()
    document_content = data.get('document')

    if not document_content:
        return jsonify({"error": "Document content is required"}), 400

    doc_id = str(uuid.uuid4())
    embedding = get_embedding(document_content)

    conn = connect()
    insert_doc(conn, doc_id, document_content, embedding)

    return jsonify({"message": "Document added successfully", "doc_id": doc_id}), 201


if __name__ == '__main__':
    conn = connect()
    create_index(conn)
    app.run(debug=True)
