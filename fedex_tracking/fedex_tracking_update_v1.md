# 🚀 FedEx Tracking Automation – Initial Version Update (v1.0)

This is the first working prototype of the FedEx Tracking Automation Script using Selenium with `undetected_chromedriver`.

---

## 🧩 Key Features Implemented

- ✅ Auto-opens FedEx tracking page
- ✅ Auto-fills tracking number
- ✅ Handles GDPR popup
- ✅ Clicks 'Track' and fetches delivery status
- ✅ Waits and scrapes full tracking details
- ✅ Extracts and prints **Delivery Summary**
- ✅ Extracts and prints **Detailed Travel History**

---

## ▶️ How to Run

```bash
python fedex_tracker.py
```

- 🔁 Replace the tracking number inside the script:
  ```python
  tracking_num = "881618932162"
  ```
  with **any valid FedEx tracking number**.

---

## 🧠 What Happens Behind the Scenes

1. FedEx site opens in a browser.
2. Tracking number is entered with keystroke simulation.
3. GDPR popup is handled (if appears).
4. Page navigates to the detailed tracking section.
5. Summary of delivery is shown:
   - Delivery Status (Delivered/Not Delivered)
   - Delivery Day
   - Delivery Date & Time
   - Status Details
6. Pressing `Enter` triggers the scraping of full travel history.
7. A chronological timeline of package movement is printed.
8. Press `Escape` or close the browser to exit.

---

## 🧭 Sample Output

```
📦 **FedEx Tracking Summary**
Main Delivery Status   : Delivered
Delivery Day           : Monday
Delivery Date & Time   : 6/2/25 at 12:27 PM
Delivery Status Detail : Delivered

🔍 PRESS ENTER TO KNOW MORE DETAILED DELIVERY HISTORY...

📜 **Detailed Travel History**

Monday, 6/2/25
8:49 AM — On FedEx vehicle for delivery @ STOCKTON, CA
12:27 PM — Delivered @ LATHROP, CA
...
```

---

## 🛠️ Issues Faced

- ⏳ **Element Timeout**: FedEx tracking page uses shadow DOM + delayed rendering, required dynamic waiting and custom JS execution.
- ⚠️ **GDPR Consent Dialog**: Intermittently blocks input, needed detection and dismissal.
- 🧱 **Shadow DOM Travel History**: Required advanced `execute_script` to fetch content inside shadowRoot.

---

## 🧪 Next Scope of Work

### 🔄 Build a Framework

- ✅ Wrap the logic into a **CLI or Web-based prototype UI**
- ✅ Input **multiple tracking numbers** at once
- ✅ Loop through and extract results **in bulk**

### 📁 Export Options

- Save results to `.txt`, `.csv`, or `.xlsx`
- Integrate **notification/email system** for summaries

### 🧱 Advanced Plans

- Add **headless mode** to run silently
- Build a **.exe** for Windows users (PyInstaller)
- Schedule regular checks using **cron/job scheduler**

---

## 🧠 Developer Note

> This script is a working prototype for automating logistics tracking.  
> It can be integrated into **dashboards**, **alert systems**, or **e-commerce order management** platforms for real-time insights.

---

## 🧾 Full Source Code

```python
# (code block omitted for brevity here, added in real file)
```

---