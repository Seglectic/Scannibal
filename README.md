# **Scannibal**
A simple web app for generating barcodes, QR codes (including Micro QR), and DataMatrix codes.
Built with FastAPI, Uvicorn, and python-barcode.

## **Features**
- Generate Code128, EAN, QR, Micro QR, and DataMatrix codes
- Light/Dark mode toggle
- Optional embedded text display
- Clean, minimal frontend
    
## **Requirements (Local Dev)**
- Python 3.11+  
- pip  
- Virtualenv recommended  
### Create virtual environment and install dependencies:
`python -m venv .venv`  
`source .venv/bin/activate`  
`pip install -r requirements.txt`  

### Run locally:
uvicorn app:app –reload –port 8069

### Visit in browser:
http://localhost:8069
