import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import logging
from urllib.parse import urljoin

# ---------------- LOGGING ----------------
logging.basicConfig(
    filename="crawler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"(?:\+91[\s\-]?)?[6-9]\d{9}"

# ---------------- GOOGLE SEARCH ----------------
def google_search(industry):
    urls = set()
    url = f"https://www.google.com/search?q={industry}+company+India"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        for a in soup.select("a"):
            href = a.get("href")
            if href and href.startswith("/url?q="):
                clean = href.replace("/url?q=", "").split("&")[0]
                if clean.startswith("http"):
                    urls.add(clean)
    except:
        pass

    return list(urls)

# ---------------- WEBSITE EXTRACTION ----------------
def extract_from_website(site):
    emails, phones = set(), set()
    founders = managers = hr = ""

    try:
        r = requests.get(site, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        text = soup.get_text(" ")

        emails.update(re.findall(EMAIL_REGEX, text))
        phones.update(re.findall(PHONE_REGEX, text))

        for e in emails:
            if "hr@" in e or "career" in e:
                hr = e
                break

        for a in soup.find_all("a", href=True):
            h = a["href"].lower()
            if "about" in h or "team" in h or "leadership" in h:
                try:
                    pr = requests.get(urljoin(site, a["href"]), headers=HEADERS, timeout=10)
                    t = pr.text.lower()
                    if "founder" in t or "ceo" in t:
                        founders = "Available on website"
                    if "director" in t or "manager" in t:
                        managers = "Available on website"
                except:
                    pass
    except:
        pass

    return emails, phones, founders, managers, hr

# ---------------- INDIAMART ----------------
def crawl_indiamart(industry, limit=5):
    results = []
    url = f"https://dir.indiamart.com/search.mp?ss={industry}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")

        cards = soup.select(".cardlinks")[:limit]

        for c in cards:
            href = c.get("href")
            link = href if href.startswith("http") else "https://dir.indiamart.com" + href
            link = link.split("?")[0]

            cr = requests.get(link, headers=HEADERS, timeout=10)
            text = cr.text

            # company name logic
            name = ""
            if "/proddetail/" in link:
                slug = link.split("/proddetail/")[-1]
                slug = "-".join(slug.split("-")[:-1])
                name = slug.replace("-", " ").title()
            else:
                slug = link.rstrip("/").split("/")[-1]
                name = slug.replace("-", " ").title()

            emails = list(set(re.findall(EMAIL_REGEX, text)))
            phones = list(set(re.findall(PHONE_REGEX, text)))[:3]

            results.append({
                "Company Name": name,
                "Website": link,
                "Founder(s)/CEO": "Not Publicly Available",
                "Manager(s)/Directors": "Not Publicly Available",
                "HR Contact": emails[0] if emails else "Not Publicly Available",
                "Employee Contact(s)": "Not Publicly Available",
                "Email Address(es)": "; ".join(emails) if emails else "Not Publicly Available",
                "Phone Number(s)": "; ".join(phones) if phones else "Not Publicly Available"
            })

            time.sleep(2)

    except Exception as e:
        logging.error(e)

    return results

# ---------------- JUSTDIAL ----------------
def crawl_justdial(industry, city="bangalore", limit=5):
    results = []
    url = f"https://www.justdial.com/{city}/{industry}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        names = soup.select(".lng_cont_name")[:limit]

        for n in names:
            results.append({
                "Company Name": n.get_text(strip=True),
                "Website": "Not Publicly Available",
                "Founder(s)/CEO": "Not Publicly Available",
                "Manager(s)/Directors": "Not Publicly Available",
                "HR Contact": "Not Publicly Available",
                "Employee Contact(s)": "Not Publicly Available",
                "Email Address(es)": "Not Publicly Available",
                "Phone Number(s)": "Not Publicly Available"
            })
    except:
        pass

    return results

# ---------------- MAIN ----------------
def crawl(industry):
    results = []
    seen = set()

    for site in google_search(industry):
        if site in seen:
            continue
        seen.add(site)

        emails, phones, f, m, hr = extract_from_website(site)

        results.append({
            "Company Name": site.split("//")[-1].split("/")[0],
            "Website": site,
            "Founder(s)/CEO": f if f else "Not Publicly Available",
            "Manager(s)/Directors": m if m else "Not Publicly Available",
            "HR Contact": hr if hr else "Not Publicly Available",
            "Employee Contact(s)": "Not Publicly Available",
            "Email Address(es)": "; ".join(emails) if emails else "Not Publicly Available",
            "Phone Number(s)": "; ".join(phones) if phones else "Not Publicly Available"
        })

    for c in crawl_indiamart(industry):
        if c["Company Name"] not in seen:
            seen.add(c["Company Name"])
            results.append(c)

    for c in crawl_justdial(industry):
        if c["Company Name"] not in seen:
            seen.add(c["Company Name"])
            results.append(c)

    return results

# ---------------- CSV ----------------
def save_csv(data, industry):
    file = f"output_{industry.replace(' ', '_')}.csv"
    with open(file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Output saved as {file}")

# ---------------- RUN ----------------
if __name__ == "__main__":
    industry = input("Enter Industry/Sector: ").strip()
    data = crawl(industry)
    if data:
        save_csv(data, industry)
    else:
        print("No data extracted.")
