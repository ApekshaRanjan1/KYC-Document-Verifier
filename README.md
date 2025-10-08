# KYC Document Verifier

A deep learning-based system for automated verification of KYC documents such as Aadhaar and PAN cards.  
Developed during my internship at **SBI Life Insurance** as a **Technical Intern**.

---

## About
The **KYC Document Verifier** automates the process of identifying and validating customer identity documents using computer vision and OCR.  
It detects the document type, extracts text information, and verifies authenticity based on predefined validation rules.

---

## Features
- Automatic document type detection (Aadhaar, PAN, etc.)
- OCR-based information extraction
- Format and field validation
- Detection of forged or tampered images
- Simple and modular design for easy extension

---

## Getting Started
Clone the repository  
```bash
git clone https://github.com/ApekshaRanjan1/KYC-Document-Verifier.git  
cd KYC-Document-Verifier  
```

Install the required dependencies  
```bash
pip install -r requirements.txt  
```

(Optional) Set up [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) if not already installed on your system.  

---

## Usage
Run the main script with the input image path  
```bash
python main.py --input path/to/document.jpg --output result.json
```  

You can also integrate the verifier as a module  
```python
from verifier import Verifier  
ver = Verifier("config.yaml")  
result = ver.verify("input_document.jpg")  
print(result)
```

---

## Dataset
1. **Aadhar Dataset:** [Kaggle Link](https://www.kaggle.com/datasets/nagendra048/aadhar-dataset)   
2. **PAN Card Dataset:** [Kaggle Link](https://www.kaggle.com/datasets/nagendra048/pan-card-dataset)

---

## Contributing
Contributions, issues, and feature requests are welcome!  
Fork the repository, make your changes, and open a pull request with proper commit messages.

---

## License
This project is licensed under the **MIT License**. See the LICENSE file for more details.

---

## Contact / Author
**Apeksha Ranjan**  
GitHub: [ApekshaRanjan1](https://github.com/ApekshaRanjan1)  
LinkedIn: [linkedin.com/in/apeksha-ranjan](https://linkedin.com/in/apeksha-ranjan)

---

*Developed during internship at SBI Life Insurance as a Technical Intern.*
