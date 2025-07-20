import google.generativeai as genai
from PIL import Image

def preprocess_code(code):
    if code.startswith("```python") and code.endswith("```"):
        return code[9:-3]
    if code.startswith("```") and code.endswith("```"):
        return code[3:-3]
    return code

def get_gemini_code_for_images(image1_path, image2_path, api_key, model_name="gemini-2.5-flash-preview-05-20"):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    image1 = Image.open(image1_path).resize((800, 600))
    image2 = Image.open(image2_path).resize((800, 600))
    prompt = """The given two images are graphs from a flight simulation and actual flight data. Image1 is the real flight data graph which acts as the baseline, \n"""
    prompt += "and Image2 is the simulated flight data graph. The graph is a flight simulation data output of a flight vehicle. I want the numerical data points used to plot the XY graph in the images.\n"
    prompt += "First generate the numerical data points used to plot the XY graph in the first image, then generate the numerical data points used to plot the XY graph in the second image.\n"
    prompt += "Then write the python code to make 2 different dataframes with the numerical data points used to plot the XY graph in the images, one for each respectively. Use the name 'df_real_flight' \n"
    prompt += "for the first dataframe and 'df_simulated_flight' for the second dataframe.\n"
    prompt += "Don't output any other information except the python code. Don't use asterisk in the code output. Maintain appropriate indentation in the code output."
    response = model.generate_content([image1, image2, prompt])
    code = preprocess_code(response.text)
    return code 