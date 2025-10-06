from flask import Flask, render_template, request, redirect, url_for
import cv2
import numpy as np
from keras.models import load_model
import pytesseract
from fuzzywuzzy import fuzz

# Set the path to the Tesseract executable (change this path based on your Tesseract installation)
#Sets the system path for the Tesseract executable so pytesseract can run OCR.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from flask import Flask, request, redirect, session, render_template, jsonify, send_file, send_from_directory
import cv2
import torch
import secrets
import os
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
import cv2
import numpy as np
import fitz
from collections import Counter
from PIL import Image

# Creating the flask app
app = Flask(__name__, static_folder='static', template_folder="templates")

secret_key = secrets.token_hex(16)
app.secret_key = secret_key

logging.basicConfig(level=logging.INFO)

# Folder to store the uploaded images
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif', 'tiff','pdf','PDF'}

# Global variables for filenames
filename1 = ""
filename2 = ""

# Load the model outside the route definition
model = load_model("Classiff_3.h5")

# def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
#     """Return a sharpened version of the image, using an unsharp mask."""
#     blurred = cv2.GaussianBlur(image, kernel_size, sigma)
#     sharpened = float(amount + 1) * image - float(amount) * blurred
#     sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
#     sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
#     sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
#     if threshold > 0:
#         low_contrast_mask = np.absolute(image - blurred) < threshold
#         np.copyto(sharpened, image, where=low_contrast_mask)
#     return sharpened
def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=3.0, threshold=0):
    """Apply unsharp mask to sharpen the input image."""
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = (amount + 1) * image - amount * blurred
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)

    # Optional thresholding
    if threshold > 0:
        low_contrast_mask = np.abs(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)

    return sharpened

# Function to preprocess an image for prediction
def adjust_brightness_contrast(image):
    print('ENTERED adjust_brightness_contrast')
    # Convert the image to grayscale
    height, width, channels = image.shape
    print(f"Image Size: Height = {height}, Width = {width}, Channels = {channels}")
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate the histogram of the image
    hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])

    # Calculate the cumulative distribution function (CDF) of the histogram
    cdf = hist.cumsum()

    # Normalize the CDF
    cdf_normalized = cdf / cdf.max()

    # Find the minimum and maximum pixel values to adjust contrast
    min_pixel_value = int(cdf_normalized.argmax() / 256 * 255)
    max_pixel_value = int(cdf_normalized.argmin() / 256 * 255)

    # Adjust contrast and brightness
    alpha = 255 / (max_pixel_value - min_pixel_value)
    beta = -min_pixel_value * alpha
    adjusted_image = cv2.convertScaleAbs(gray_image, alpha=alpha, beta=beta)
    cv2.imwrite('4th.png', image)
    adjusted_image = unsharp_mask(adjusted_image)
    cv2.imwrite('5th.png', adjusted_image)
    print('RETURNED ADJUSTED IMAGE')
    return adjusted_image


def rotate_image(numpy_array, angle):
    try:
        # Convert the NumPy array to a PIL Image
        original_image = Image.fromarray(numpy_array)

        # Rotate the image
        rotated_image = original_image.rotate(angle, expand=True)

        return rotated_image

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def extract_text(image_path):
    print('ENTERED extract_text')
    # Read the image using OpenCV
    image = cv2.imread(image_path)
    print('step1')

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print('step2')

    # Use edge detection to find lines in the image
    edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)
    print('step3')
    lines = cv2.HoughLines(edges, 1, 3.14 / 180, 100)
    print('step4')

    # Find the angle of the detected lines
    angles = [line[0][1] for line in lines]
    print('step5')

    # Calculate the median angle
    median_angle = np.median(angles)
    print('step6')

    # Rotate the image to correct orientation
    rotated_image = Image.fromarray(image)
    print('step7')
    rotated_image = rotated_image.rotate(-median_angle, resample=Image.BICUBIC)
    print('step8')

    # Convert the rotated image back to OpenCV format
    rotated_image_cv2 = np.array(rotated_image)
    print('step9')
    # image = cv2.imread(rotated_image_cv2)
    # print('step10')
    image = cv2.resize(rotated_image_cv2, (800, 600))
    print('step11')

    # Adjust brightness and contrast
    adjusted_image = adjust_brightness_contrast(image)
    print('step12')
    cv2.imwrite('hua.jpg', adjusted_image)
    print('step13')

    # Use pytesseract to extract text from the adjusted image
    # rotated_right_image = rotate_image(adjusted_image, 90)
    text = pytesseract.image_to_string(adjusted_image)
    text2 = pytesseract.image_to_string(adjusted_image, lang= 'hin')
    # print('hindi text',text2)
    
    # print(text.strip().lower())
    # print(len(text))
    text3 = (text.strip().lower()) + (text2.strip().lower())
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@THIS IS TEXT#',text3)
    return text3.strip().lower()

def process_text_and_classification(extracted_text, class_keywords, class_labels, predictions, keyword1):
    # Check for variations of keywords in each category using fuzzy matching
    print('ENTERED PROCESS TEXT CLASSIFICATION')
    if not extracted_text:
        print("No Information Found. This may not be a document.")
        return "No Information Found"
    
    for key_word in keyword1:
        print('KEYWORD  FOUND')
        if key_word.lower() in extracted_text:
            print('new logic successful')
            return ""

    for category, keywords in class_keywords.items():
        print('ENTERED IF KEYWORD IS FOUND IN CLASSKEYWORD ITEM')
        if any(fuzz.partial_ratio(keyword, extracted_text.lower()) >= 90 for keyword in keywords):
            print(f"{category} Information Found:")
            return f"{category} Information"

    # Display the predicted class probabilities
    print("Class Probabilities:")
    for i in range(len(class_labels)):
        class_index = np.argsort(predictions)[0][i]
        class_label = class_labels[class_index]
        probability = predictions[0][class_index]
        print(f"{class_label}: {probability:.2%}")

    # Display the class with the highest probability
    highest_probability_index = np.argmax(predictions)
    highest_probability_label = class_labels[highest_probability_index]
    highest_probability = predictions[0][highest_probability_index]
    print(highest_probability_label)
    if highest_probability > 0.80:
        if highest_probability_label == ('Passport' or 'PASSPORT'):
            return "@@"
        else:

        # print(f"\nClass with Highest Probability:")
        # print(f"{highest_probability_label}: {highest_probability:.2%}")
            print('CAME FROM MODEL',highest_probability_label)
            return highest_probability_label
        
    else:
        print('keep_as_it_is')
        return ""

# Define class keywords associated with each category
class_keywords = {
    'PASSPORT': ['republic'],
    'Aadhar Card': ['aadhar', 'uidai', 'help@uidai', 'unique', 'identificationauthorify', 'uildal','vid','आधार','मेरा आधार', 'मेरी पहचान'],
    'PAN Card': ['permanent', 'account', 'pan', 'income tax department'],
    'Voter ID': ['voterid', 'election', 'commission', 'electoral', 'assembly', 'constituency', 'elector', 'ectoral'],
    'Driving License': ['issuing','driving', 'lmv', 'license', 'lmv-t', 'mcwg', 'mcwog', 'drive', 'driving', 'vehicals', 'vehical', 'validity', 'transport']
    # Add more categories and their associated keywords as needed
}



# Home page
@app.route('/')
def index():
    app.logger.error("index")
    print("index html")
    return render_template('Classification.html')



# Result page
@app.route('/classifier', methods=['POST','GET'])
def classifier_route():
    keyword1 = ['indresh','bhai']
    
    try:
        result=""
        print("classification start")
        image1_path = request.form.get(r'imageInput1')
        print(image1_path)

        image1_path=image1_path.replace('D:','\\\\172.17.134.229').replace('/','\\').replace('\\\\','\\')
        image1_path = '\\' + image1_path
        #image1_path = image1_path.replace('\\\\','////').replace('\\','//')
        print(image1_path)
        #with open(image1_path, 'rb') as f:
        #    contents = f.read()
        #    binary_file = open("uploaded_image.jpg", "wb")
        #    binary_file.write(contents)  

        def most_frequent(List):
            occurence_count = Counter(List)
            return occurence_count.most_common(1)[0][0]

        resultList=[]

        # Preprocess the image
        # Use the global variable if needed
        global model

        print("after model line")
        # Function to preprocess an image for prediction
        def adjust_brightness_contrast(image):
            # Convert the image to grayscale
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])

            cdf = hist.cumsum()

            # Normalize the CDF
            cdf_normalized = cdf / cdf.max()

            # Find the minimum and maximum pixel values to adjust contrast
            min_pixel_value = int(cdf_normalized.argmax() / 256 * 255)
            max_pixel_value = int(cdf_normalized.argmin() / 256 * 255)

            # Adjust contrast and brightness
            alpha = 255 / (max_pixel_value - min_pixel_value)
            beta = -min_pixel_value * alpha
            adjusted_image = cv2.convertScaleAbs(gray_image, alpha=alpha, beta=beta)
            cv2.imwrite('3rd.png', image)
            return adjusted_image
        
        if "pdf" in image1_path:
            print('INSIDE PDF')
            #Open the PDF file
            pdf_document = fitz.open(image1_path)
            print("after pdf file read")
            print(image1_path)

            
            #Iterate through pages and convert to images
            for page_number in range(len(pdf_document)):
                page = pdf_document[int(page_number)-1]
                img = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                img.save('img.png', 'png')
                image = cv2.imread('img.png')
                
                unknown1_image = 'img.png'


                print("Image path")
                

                # Extract text from the image
                extracted_text = extract_text(unknown1_image)
                print(len(extracted_text))
                print(extracted_text)

                print('TEXT EXTRACTION')

                # Read and preprocess the image for classification
                img = cv2.imread(unknown1_image)
                img = cv2.resize(img, (255, 255))
                img = np.expand_dims(img, axis=0)
                img = img / 255.0

                # Predict the class probabilities
                print('Now Predicting through Model')
                predictions = model.predict(img)
                

                # Define class labels
                class_labels = ['AADHAR', 'AADHAR', 'AADHAR', 'AADHAR', 'DRIVING_LICENCE', 'PAN', 'PAN','Passport', 'VOTERID', 'VOTERID']
                # Process the extracted text and image classification results
                print('GOING FOR PROCESS TEXT CLASSIFICATION')
                result = process_text_and_classification(extracted_text, class_keywords, class_labels, predictions, keyword1)

                # If the result is not an early response, print it
                if "Information" in result:
                    print('INFORMATION WORD FOUND')
                    print("The image is categorized as: {result}")

                resultList.append(result)
                
                print(result)

            res=most_frequent(resultList)
            
            print(res)
            return jsonify({'result' : res})
        
        else:
                #Extract text from the image
                print('ENTERED FOR JPG AND PNG')
                print(image1_path)
                unknown2_image = image1_path
                print('unknown1_image',unknown2_image)
                extracted_text = extract_text(unknown2_image)
                print(len(extracted_text))
                print(extracted_text)

                # Read and preprocess the image for classification
                img = cv2.imread(unknown2_image)
                img = cv2.resize(img, (255, 255))
                img = np.expand_dims(img, axis=0)
                img = img / 255.0

                print("before model prediction")
                # Predict the class probabilities
                predictions = model.predict(img)

                # Define class labels
                class_labels = ['AADHAR', 'AADHAR', 'AADHAR', 'AADHAR', 'DRIVING_LICENCE', 'PAN', 'PAN', 'Passport', 'VOTERID', 'VOTERID']
                result = process_text_and_classification(extracted_text, class_keywords, class_labels, predictions,keyword1)


                print(result)
                # If the result is not an early response, print it
                if "Information" in result:
                    print("The image is categorized as: {result}")

                return jsonify({'result': result})
    
    except Exception as e:
        print("Error occurred: %s", str(e))
        jsonify({'result':'Not working ' })

# Define the route to serve the loading icon
@app.route('/loading.gif')
def serve_loading_icon():
    return send_from_directory('static', 'loading.gif')

if __name__ == "__main__":
    app.run(port='84', debug=False)