# Business Contact Web Crawler

A Python-based web crawler that extracts publicly available business contact information from the internet based on a given **industry/sector** or **specific company name**.

This project was developed as part of an internship task to demonstrate web crawling, data extraction, and ethical scraping practices.

---

## 📌 Features

- Accepts **industry/sector** input (e.g., `IT Services`, `Healthcare`)
- Supports **company-specific search** (e.g., `Microsoft`)
- Crawls multiple public data sources:
  - Google Search
  - Company websites
  - IndiaMART
  - JustDial
- Extracts business contact details
- Outputs **clean, deduplicated CSV files**
- Handles missing data gracefully
- Includes basic logging and error handling
- Ethical scraping (only publicly available data)

---

## 📊 Extracted Data Fields

The crawler attempts to extract the following fields for each company:

| Field | Description |
|------|------------|
| Company Name | Name of the business |
| Website | Official website or listing URL |
| Founder(s)/CEO | Founder or CEO name (if publicly available) |
| Manager(s)/Directors | Key management details (if available) |
| HR Contact | HR email/contact (if available) |
| Employee Contact(s) | Decision-maker contacts (if available) |
| Email Address(es) | Valid work email addresses |
| Phone Number(s) | Business phone/mobile numbers |

> If any data is not publicly available, it is marked as **`Not Publicly Available`**.

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Libraries:**
  - requests
  - BeautifulSoup (bs4)
  - csv
  - re
  - logging
- **Output Format:** CSV

---

## 📁 Project Structure

business_crawler/
├── crawler.py
├── requirements.txt
├── .gitignore