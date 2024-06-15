from flask import Flask, request, render_template, jsonify
import os
import base64
import requests
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size

# Set up logging
logging.basicConfig(level=logging.DEBUG)

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
        # Retrieve collection image
        coll_image = request.files.get('coll_image')
        if not coll_image or not allowed_file(coll_image.filename):
            return jsonify({"error": "Collection image is required and must be a valid file type"}), 400

        # Secure filename and save collection image
        shelf_filename = secure_filename(coll_image.filename)
        shelf_path = os.path.join(app.config['UPLOAD_FOLDER'], shelf_filename)
        coll_image.save(shelf_path)

        # Convert collection image to base64
        with open(shelf_path, "rb") as image_file:
            base64_shelf_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Prepare to accumulate responses
        all_responses = []

        # Process each pill image and its corresponding name
        pill_files = request.files.getlist('pill_images')
        if len(pill_files) > 10:
            return jsonify({"error": "You can upload up to 10 pill images"}), 400

        for index, pill_image in enumerate(pill_files):
            if not allowed_file(pill_image.filename):
                continue  # Skip invalid file types

            # Get the corresponding pill name from the form
            pill_name = request.form.get(f'pill_name_{index}')
            if not pill_name:
                continue  # Skip if name is missing

            # Secure filename and save pill image
            product_filename = secure_filename(pill_image.filename)
            product_path = os.path.join(app.config['UPLOAD_FOLDER'], product_filename)
            pill_image.save(product_path)

            # Convert pill image to base64
            with open(product_path, "rb") as image_file:
                base64_product_image = base64.b64encode(image_file.read()).decode('utf-8')

            # Fetch API key from the environment
            api_key = os.getenv('OPEN_API_KEY')
            if not api_key:
                return jsonify({"error": "API key not found"}), 500

            # Prepare payload for OpenAI API
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": f"""
                        First, I will give you an image of a pill named '{pill_name}'. 
                        Describe the pill. Ignore any text.
                        Then I will give you an image of a collection of pills called a pilload. 
                        Describe the items shown in the pilload. 
                        Return a statement stating only if based on these descriptions if the pill '{pill_name}' is in the pilload, 
                        based on appearance alone - no text - and what quadrant of the picture it is in.
                        """
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Here is the pill image"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_product_image}"
                                }
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Here is the pilload image"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_shelf_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 300
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            # Make the API request to OpenAI
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

            if response.status_code == 200:
                # Convert the response to JSON
                api_result = response.json()
                
                # Extract the content from the response
                message_content = api_result['choices'][0]['message']['content']
                
                # Log the response for debugging
                app.logger.debug('OpenAI API Response: %s', message_content)
                
                # Add the response to the list of all responses
                all_responses.append(f"Pill Name: {pill_name}\nResponse: {message_content}")
            else:
                # Log the error for debugging
                app.logger.error('Error from OpenAI API: %s', response.text)
                all_responses.append(f"Pill Name: {pill_name}\nError: {response.text}")

        # Return the accumulated responses
        return jsonify({
            "api_response_content": all_responses
        })

    except Exception as e:
        # Log the exception for debugging
        app.logger.exception('Exception during file upload or API request')
        return jsonify({"error": str(e)}), 500

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    # Ensure the upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
