# **Calhoun Course Downloader**

A Python-based CLI tool to **download course videos** from [Jon Calhoun's courses](https://courses.calhoun.io). It logs in, scrapes lessons, and downloads `.mp4` videos directly from the site.

---

## **📌 Features**
- Supports [Test With Go](https://testwithgo.com/) and [Web Development with Go](https://www.usegolang.com/)
- Names videos using lesson titles
- Organizes videos into section-based folders

---

## **🛠️ Installation**
### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/Nilesh2000/joncalhoun-dl.git
cd joncalhoun-dl
```

### **2️⃣ Set Up a Virtual Environment (Optional but Recommended)**
```sh
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
```

### **3️⃣ Install Dependencies**
```sh
pip install -r requirements.txt
```

---

## **🚀 Usage**
### **1️⃣ Run the Script**
```sh
python main.py --email="your_email@example.com" --password="your_password" --course="testwithgo"
```

### **2️⃣ Available Flags**
| Flag         | Description |
|------------- |-------------|
| `--email`    | Your login email (required) |
| `--password` | Your login password (required) |
| `--course`   | Course to download (`testwithgo`, `webdevwithgo`) (required) |
| `--dest`     | (Optional) Custom download directory |

### **3️⃣ Example: Download a Course to a Custom Folder**
```sh
python main.py --email="your_email@example.com" --password="your_password" --course="webdevwithgo" --dest="/path/to/save"
```

---

## **📂 Project Structure**
```sh
calhoun-dl/
│── main.py                # Entry point script
│── auth.py                # Handles authentication
│── scraper.py             # Scrapes lessons & extracts MP4 URLs
│── downloader.py          # Downloads videos from MP4 links
│── utils.py               # Utility functions (argument parsing)
│── config.py              # Stores configuration data (like COURSES)
│── requirements.txt       # Dependencies
│── .gitignore             # Ignore unnecessary files
│── LICENSE                # License file
│── README.md              # Documentation
```

---

## **👥 Contributors**
- [Nilesh D](https://github.com/Nilesh2000/)

---

## **📜 License**

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
