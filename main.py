from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import cv2
import os
import base64
import numpy as np

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, operation):
    print(f"the operation is {operation} and filename is {filename}")

    img = cv2.imread(f"uploads/{filename}")

    match operation:
        case "cgray":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        case "invert":
            imgProcessed = cv2.bitwise_not(img)
        case "blur":
            imgProcessed = cv2.GaussianBlur(img, (15, 15), 0)
        case "sepia":
            sepia_filter = np.array([[0.272, 0.534, 0.131],
                                     [0.349, 0.686, 0.168],
                                     [0.393, 0.769, 0.189]])
            imgProcessed = cv2.transform(img, sepia_filter)
        case "resize":
            new_size = (800, 600) 
            imgProcessed = cv2.resize(img, new_size)
        case "edges":
            imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            imgProcessed = cv2.Canny(imgGray, 100, 200)
        case "threshold":
            imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, imgProcessed = cv2.threshold(imgGray, 128, 255, cv2.THRESH_BINARY)
        case _:
            raise ValueError("Unsupported operation")

    # Save processed image
    newFilename = f"{operation}_{filename}"
    newFilePath = os.path.join('static', newFilename)
    cv2.imwrite(newFilePath, imgProcessed)
    
    # Convert processed image to base64 for display
    _, buffer = cv2.imencode('.png', imgProcessed)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return img_base64


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    img_data = None
    if request.method == "POST":
        operation = request.form.get("operation")
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('home'))
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('home'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_data = processImage(filename, operation)
            if img_data:
                return render_template("edit.html", img_data=img_data)
            else:
                flash('Error processing image')
                return redirect(url_for('home'))
    
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True, port=5001)
