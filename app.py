from flask import Flask, request, render_template, jsonify
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size

@app.route('/api/get-api-key')
def get_api_key():
    # Serve the API key securely
    api_key = os.getenv('OPEN_API_KEY')
    return jsonify({'api_key': api_key})

@app.route('/')
def upload_form():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        product_image = request.files.get('product_image')
        shelf_image = request.files.get('shelf_image')

        if not product_image or not shelf_image:
            return jsonify({"error": "Both product and shelf images are required"}), 400

        if not allowed_file(product_image.filename) or not allowed_file(shelf_image.filename):
            return jsonify({"error": "Invalid file type"}), 400

        # Secure filenames and save files
        product_filename = secure_filename(product_image.filename)
        product_path = os.path.join(app.config['UPLOAD_FOLDER'], product_filename)
        product_image.save(product_path)

        shelf_filename = secure_filename(shelf_image.filename)
        shelf_path = os.path.join(app.config['UPLOAD_FOLDER'], shelf_filename)
        shelf_image.save(shelf_path)

        return jsonify({
            "product_image_path": product_path,
            "shelf_image_path": shelf_path
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
