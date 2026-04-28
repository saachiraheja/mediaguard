# 🛡️ MediaGuard: Forensic Asset Protection Suite

**An AI-powered digital forensic platform for IP violation detection and admissible evidence generation.**

### 📌 Project Overview
MediaGuard is designed for sports broadcasters and media rights holders to protect high-stakes digital assets. It identifies unauthorized reproduction of media and detects AI-driven manipulation using advanced image forensics, bridging the gap between technical detection and legal admissibility under **BSA 2023 (Section 63)** and the **IT Act 2000**.

### 🔹 Why This Project?
* **Admissible Evidence:** Automatically generates forensic reports formatted for Indian legal standards.
* **Multi-Layer Detection:** Moves beyond simple metadata by using perceptual and structural hashing.
* **Security First:** Implements 2FA (TOTP) and bcrypt hashing for enterprise-grade organisation portals.
* **DFIR Focused:** Designed with Digital Forensics and Incident Response principles for real-world piracy tracking.

### ⚙️ Features Implemented

| Feature | Forensic/Legal Concept |
| :--- | :--- |
| **4-Layer Hashing Engine** | pHash, aHash, dHash, & SSIM for modification-resistant detection |
| **AI Manipulation Detection** | Error Level Analysis (ELA) to find digital tampering/AI edits |
| **Forensic Evidence Report** | Automated PDF generation compliant with **BSA 2023 §63** |
| **Secure Org Vault** | Firebase-backed encrypted storage for official assets |
| **Multi-Factor Auth (2FA)** | Google Authenticator (TOTP) for organisation logins |
| **Role-Based Access** | SuperAdmin, Approved Organisation, and Public Scanner roles |

### 📂 Directory Structure
```text
📦 MediaGuard
 |-- 📂 app.py (Main Streamlit Entry)
 |-- 📂 engine.py (Forensic Hashing & ELA Engine)
 |-- 📂 database_manager.py (Firebase CRUD & Auth Logic)
 |-- 📂 styles.py (Enterprise UI/UX Definitions)
 |-- 📂 firebase_config.py (Secure Firestore Connection)
 |-- 📜 requirements.txt (Deployment Dependencies)
 |-- 📜 README.md (Project Documentation)
 ```

 ### 🚀 Forensic Concepts & Implementation

**1️⃣ The Problem: Digital Chain of Custody & IP Fragmentation**
* **Forensic Problem Statement:** In the high-velocity sports media landscape, official assets lack a persistent "Digital Fingerprint." Metadata is easily stripped, and traditional watermarking is bypassed by simple transformations. This creates a visibility gap where organizations cannot prove the **Integrity** or **Provenance** of their media once it leaves their environment.

**2️⃣ Multi-Layer Perceptual Hashing (DNA of Media)**
* **Implementation:** Instead of relying on metadata, MediaGuard generates a **Robust Perceptual Hash (pHash)** using Discrete Cosine Transform (DCT). 
* **Impact:** This identifies unauthorized copies even if they have been resized or color-corrected, maintaining a high **Structural Similarity Index (SSIM)** match against the official vault.

**3️⃣ Anomaly Detection via Error Level Analysis (ELA)**
* **Concept:** Digital misappropriation often involves re-branding or re-editing official media.
* **Implementation:** MediaGuard uses **ELA** to detect non-uniform compression levels. By analyzing the resave-error rate, the system flags anomalies in content, identifying specifically which parts of an image were tampered with.

**4️⃣ Authentication & Legal Admissibility (BSA 2023 §63)**
* **Solution:** Under Section 63 of the Bharatiya Sakshya Adhiniyam, electronic records require specific technical validation. MediaGuard automates the generation of a **Forensic Artifact Report** logging the Cryptographic Hash, Similarity scores, and Timestamps for legal submission.

### 🛠️ Setup & Installation

**🔹 Prerequisites**
* Python 3.10+
* Firebase Project (Firestore enabled)
* Streamlit Cloud Account

**🔹 Installation Steps**
1. **Clone the Repo:**
   ```bash
   git clone [https://github.com/saachiraheja/mediaguard.git](https://github.com/saachiraheja/mediaguard.git)
   cd mediaguard 
   ```
1. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Run Locally:**
    ```bash
    streamlit run app.py
    ```
### 📞 Contact
* **GitLab:** [https://github.com/saachiraheja](https://github.com/saachiraheja)
* **Email:** [raheja.saachi04114@gmail.com](mailto:raheja.saachi04114@gmail.com)
* **LinkedIn:** [https://www.linkedin.com/in/saachi-raheja-8768572bb/](https://www.linkedin.com/in/saachi-raheja-8768572bb/)

### ✅ Final Thoughts
MediaGuard demonstrates a scalable approach to IP protection by combining **OpenCV-based forensics** with **Firebase-driven cloud architecture**. It is built specifically to address the evolving challenges of digital piracy in the Indian media landscape.
