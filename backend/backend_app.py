from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access variables
secret_key = os.getenv('SECRET_KEY')
database_url = os.getenv('DATABASE_URL')

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "A First post", "content": "F This is the first post."},
    {"id": 2, "title": "C Second post", "content": "B This is the second post."},
    {"id": 3, "title": "E Third post", "content": "C This is the third post."},
    {"id": 4, "title": "B Fourth post", "content": "E This is the Hello post."},
    {"id": 5, "title": "D Fifth post", "content": "D This is the fifth post."},
    {"id": 6, "title": "F Fifth post", "content": "A This is the Hello post."},

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

@app.route('/', methods=['GET'])
def index_html():
    text = "This is a home page without functions.\n Please go to /login to login"
    return text

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required.'}), 400

        '''
        # user = User.query.filter_by(username=username).first()

        # if not user or not check_password_hash(user.password, password):
        #     return jsonify({'error': 'Invalid username or password.'}), 401

        # access_token = create_access_token(identity=user.id)

        user_data = {
            'id': user.id,
            'username': user.username
        }
        '''

        test_user = "admin"
        test_user_password = "admin"

        if username != test_user or password != test_user_password:
            return jsonify({'error': 'Invalid username or password.'}), 401


        return jsonify({'message': 'You have logged in as user {username}'}), 200
    
        # return jsonify({'token': access_token, 'user': user_data})
    
    return jsonify({'message': 'This is the Login page, please use method POST withg username and password'}), 200

@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get('sort')
    direction = request.args.get('direction')

    # Check if sorting is even necessary, if not return POSTS unsorted
    if sort_field is None:
        return jsonify(POSTS)

    # Check for invalid input parameters
    if sort_field != "title" and sort_field != "content" and sort_field != "":
        return jsonify({"error": "Bad Request: Invalid Parameter for Sorting! "
                                 "Must be <'title'> or <'content'> or <''>."}), 400

    # verify a valid direction parameter. Could tolerate wrong ones, but this is cleaner
    if direction != "asc" and direction != "desc" and direction is not None:
        return jsonify({"error": "Bad Request: Invalid Parameter for Direction! "
                                 "Must be <'asc'> or <'desc'> or <''>."}), 400

    # copy to avoid unwanted change of original list
    sorted_posts = POSTS.copy()

    # Ensure sort_field is either 'title' or 'content', and direction is either 'asc' or 'desc'
    if sort_field in ['title', 'content']:
        # Reverse True means sorting descending/reversed order
        reverse = True if direction == 'desc' else False
        sorted_posts = sorted(sorted_posts, key=lambda x: x[sort_field], reverse=reverse)

    return jsonify(sorted_posts)


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
    return jsonify(
        {"message":
         f"Post with id {post_id} with "
         f"title {post_to_delete['title']} "
         f"has been deleted successfully."
         })


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post_to_update = find_post_by_id(post_id)

    # If the book wasn't found, return a 404 error
    if post_to_update is None:
        return jsonify({"error": "Post not found. Maybe it was deleted or you inserted a non existing id?"}), 404

    new_post_data = request.get_json()
    is_valid, error_message = validate_post_data(new_post_data)
    if not new_post_data or not is_valid:
        return jsonify({"error": "Invalid book data. 'title', 'author' or both are required."}), 400

    post_to_update.update(new_post_data)

    return jsonify(post_to_update), 200


@app.route('/api/posts/search', methods=['GET'])
def search_post():
    title = request.args.get('title')
    content = request.args.get('content')

    search_results = []

    for post in POSTS:
        if title and content:
            if (title.lower() in post["title"].lower()
                    and content.lower() in post["content"].lower()
                    and post not in search_results):
                search_results.append(post)

        if title and not content:
            if title.lower() in post["title"].lower() and post not in search_results:
                search_results.append(post)

        if content and not title:
            if content.lower() in post["content"].lower() and post not in search_results:
                search_results.append(post)

    if search_results:
        return jsonify(search_results), 200
    else:
        # Returns an empty list
        return jsonify(search_results), 200
        # return jsonify({"Message": "No posts were found for the title or content search parameters."}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
