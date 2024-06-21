# Import the necessary libraries.
import os
from flask import (
    Flask,
    render_template,
    request,
    redirect
)
import google.generativeai as genai
import io
from PIL import Image
from dotenv import load_dotenv


# Initialize the Flask app.
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # limit upload size to 16 MB


load_dotenv()

KEY= os.environ["API_KEY"]
genai.configure(api_key=KEY)

generation_config = {
    "temperature": 0.8, 
    "top_p" : 1, 
    "top_k" : 1, 
    "max_output_tokens":2048

}

# Define a function to generate response from a wireframe and a prompt.
def generate(wireframe, model, prompt):
    """
    Generates a response from a wireframe and a prompt.
    Args:
        wireframe: The wireframe image.
        model: The generative model to use.
        prompt: The prompt to use.
        Returns:The generated response.
    """
    # Create a GenerativeModel object.


    model = genai.GenerativeModel(model, generation_config=generation_config)

    # Create a list of contents to pass to the model.
    contents = [
        wireframe,
        prompt
    ]
   
    # Generate the response.
    responses = model.generate_content(
        contents=contents,
        stream=True,
    )

    # Concatenate the response text.
    response = ""
    for res in responses:
        response += res.text.strip()
   
    # Return the generated response.
    return response

# Define the home page route.
@app.route('/', methods=['GET'])
def index():
    """
    Renders the home page.
    Returns:
        The rendered template.
    """
    return render_template('index.html')

# Define the response route.
@app.route('/response', methods=['GET', 'POST'])
def response():
    """
    Handles the user's input and send it over to the model.
    Returns:
        The response from the model.
    """
    # If the request is a POST request, process the form data.
    if request.method == 'POST':
        # Get the uploaded image from the request.
        uploaded_image = request.files['image-upload']
       
        # Convert the uploaded image to Image format from Vertex AI library
        # wireframe = Image.from_bytes(uploaded_image.read())
        # wireframe = Image.frombytes(uploaded_image.read())
        wireframe = Image.open(io.BytesIO(uploaded_image.read()))

        # Get the model and prompt from the request.
        model = request.form['model']
        prompt = request.form['prompt']
       
        # Generate the response and render the response.
        try:
            response = generate(wireframe, model, prompt)
            response = response.replace("```html", "").replace("```", "").strip()

            print(response)
            return response
        except ValueError as e:
            raise e
   
    # If the request is a GET request, redirect to the home page.
    else:
        return redirect('/')

# Run the app.
if __name__ == "__main__":
    # Get the server port from the environment variables.
    server_port = os.environ.get('PORT', '8080')

    # Run the app.
    app.run(debug=False, port=server_port, host='0.0.0.0')