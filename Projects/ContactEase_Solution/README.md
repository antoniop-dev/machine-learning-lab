# 📒 ContactEase Solution

ContactEase Solution is a **Python console application** that makes it easy to manage a personal contact book.  
It was designed as an educational project and is fully compatible with **Google Colab** using `%%writefile` cells.

---

## ✨ Features
- ➕ **Add new contacts**
- 📋 **View contacts** sorted by name and surname
- 🔍 **Search contacts** by:
  - Name  
  - Surname  
  - Name and surname  
  - Phone number  
- ✏️ **Edit contacts**
- ❌ **Delete contacts**
- 💾 **Save and load** contacts automatically from a JSON file

---

## 🛠️ Project Structure
Each file has a specific responsibility:
```text
ContactEase_Solution/
│── Contact.py        # Contact class (single contact)
│── ContactBook.py    # ContactBook class (manages contacts collection)
│── ui.py             # Command-line interface
│── main.py           # Application entry point
│── utilities.py      # Validation and normalization functions
└── contacts.json     # JSON file with saved contacts
```
## Project in Google Colab
In Google Colab each file is created using:
```python
%%writefile filename.extesion
# file content
```
# ▶️ Run the program
To run the program in Google Colab:
- make sure every file was correctly created by running each code cell;
- open Google Colab terminal;
- make sure to be in the same directory of main.py;
- Run using the following command: 
```bash
  python main.py