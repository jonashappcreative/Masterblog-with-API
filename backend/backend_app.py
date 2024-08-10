from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def validate_post_data(data):
    # Ensure data is a dictionary and has required keys
    # is not valid = False
    if not isinstance(data, dict):
        return "not_a_dict", "Input is not a dict."

    if "title" not in data and "content" not in data:
        return "something_is_missing", "Title and content are required in data."
    elif "title" not in data and "content" in data:
        return "something_is_missing", "Title is required in data."
    elif "content" not in data:
        return "something_is_missing", "Content is required in data."

    # is valid = True
    return "nothing_is_missing", "good"


def find_post_by_id(post_id):
    for post in POSTS:
        if post["id"] == post_id:
            return post

    # If post_id is not Found in POSTS
    return None


@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def add_post():
    if request.method == 'POST':
        # This is the data from the body of the Post Request
        new_post = request.get_json()

        # Check if JSON was parsed successfully and contains required fields

        # not yet implemented feedback on what's missing in the request:
        is_valid, error_message = validate_post_data(new_post)

        if is_valid == "something_is_missing":
            is_valid = False
        elif is_valid == "not_a_dict":
            is_valid = False
        else:
            is_valid = True

        if not new_post or not is_valid:
            return jsonify({"error": f"Invalid post data. {error_message}"}), 400

        # Generate a new ID for the book
        # checks if there are posts already (if POSTS), otherwise gives value 1
        # checks for the current maximum post id value and adds one as new max equals new id
        new_id = max(post['id'] for post in POSTS) + 1 if POSTS else 1

        # gives the new post dict the ID field
        new_post['id'] = new_id

        # Add the new book to our list
        POSTS.append(new_post)

        # Return the new book data to the client
        # 201 is status code for a created object
        return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post_to_delete = find_post_by_id(post_id)

    # If the book wasn't found, return a 404 error
    if post_to_delete is None:
        return jsonify({"error": "Post not found. It was already deleted or never existed."}), 404

    # Remove the book from the list
    POSTS.remove(post_to_delete)

    # Return the deleted book
    return jsonify({"message": f"Post with id {post_id} with title '{post_to_delete["title"]}' "
                               f"has been deleted successfully."})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
