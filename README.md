# AI Plagiarism Checker

An **AI-powered plagiarism detection system** that determines whether a piece of text is plagiarized from another using **machine learning techniques**.

The system converts text into numerical vectors using **TF-IDF Vectorization** and classifies plagiarism using a **LightGBM model**.
The application includes a **Flask backend with an HTML interface**.

---

# Live Demo

Try the deployed application:

https://ai-plagarism-checker-3jzr.onrender.com/

---

# Screenshots

### File Input Interface

![Homepage](screenshots/1.png)

### Text Input Interface

![Input Interface](screenshots/2.png)

### Prediction Result

![Prediction Result](screenshots/3.png)

### Model Prediction Example

![Model Output](screenshots/output_example.png)

*(Add or remove screenshots as needed)*

---

# Features

* Machine learning based plagiarism detection
* TF-IDF feature extraction
* LightGBM classification model
* Flask web interface
* Real-time plagiarism prediction

---

# Tech Stack

### Backend

* Python
* Flask

### Machine Learning

* LightGBM
* Scikit-learn
* TF-IDF Vectorizer
* Pandas
* NumPy

### Frontend

* HTML
* CSS

### Deployment

* Render

---

# Project Structure

```
AI_plagarism_Checker
│
├── app.py
├── train_model.py
├── model.pkl
├── vectorizer.pkl
│
├── templates
│   └── index.html
│
├── screenshots
│   ├── homepage.png
│   ├── input_page.png
│   ├── result.png
│   └── output_example.png
│
├── requirements.txt
└── README.md
```

---

# Installation

## Clone the repository

```
git clone https://github.com/no-usefun/AI_plagarism_Checker.git
```

## Move into the project directory

```
cd AI_plagarism_Checker
```

## Install dependencies

```
pip install -r requirements.txt
```

---

# Run the Application

```
python app.py
```

Then open:

```
http://127.0.0.1:5000
```

---

# How It Works

1. User inputs two pieces of text.
2. Text is preprocessed and cleaned.
3. TF-IDF converts the text into numerical vectors.
4. The vectors are passed to the LightGBM classifier.
5. The model predicts whether plagiarism exists.

---

# Model Pipeline

```
Text Input
   ↓
Text Preprocessing
   ↓
TF-IDF Vectorization
   ↓
LightGBM Model
   ↓
Prediction
```

---

# Future Improvements

* Sentence level plagiarism highlighting
* File upload support (PDF/DOCX)
* Similarity percentage score
* API support
* Larger training dataset

---

# Deployment

Hosted on **Render**

Live URL
https://ai-plagarism-checker-3jzr.onrender.com/

---

# License

MIT License
