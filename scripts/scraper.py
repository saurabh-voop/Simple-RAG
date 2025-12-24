import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
import os


class BankScraper:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.data = []

        # ADD ALL LOAN URLS HERE
        self.loan_urls = [
            "https://bankofmaharashtra.bank.in/personal-banking/loans/home-loan",
            "https://bankofmaharashtra.bank.in/mahabank-vehicle-loan-scheme-for-two-wheelers-loans",
            "https://bankofmaharashtra.bank.in/maha-super-flexi-housing-loan-scheme",
            "https://bankofmaharashtra.bank.in/pradhan-mantri-awas-yojana-2",
            "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan", 
            "https://bankofmaharashtra.bank.in/mahabank-vehicle-loan-scheme-for-second-hand-car", 
            "https://bankofmaharashtra.bank.in/topup-home-loan", 
            "https://bankofmaharashtra.bank.in/educational-loans", 
            "https://bankofmaharashtra.bank.in/gold-loan", 
            "https://bankofmaharashtra.bank.in/personal-banking/loans/personal-loan",
            "https://bankofmaharashtra.bank.in/loan-against-property",
            "https://bankofmaharashtra.bank.in/maha-adhaar-loan",
            "https://bankofmaharashtra.bank.in/lad", 
            "https://bankofmaharashtra.bank.in/mahabank-green-financing-scheme", 
            "https://bankofmaharashtra.bank.in/mahabank-rooftop-solar-panel-loan" 
            
        ]

    # ------------------ Utilities ------------------

    def fetch_page(self, url):
        try:
            r = requests.get(url, headers=self.headers, timeout=15)
            if r.status_code != 200:
                print(f"[WARN] Status {r.status_code}: {url}")
                return None
            return BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            print(f"[ERROR] Fetch failed {url}: {e}")
            return None

    def get_main_container(self, soup):
        return (
            soup.find("div", id="block-system-main") or
            soup.find("div", class_="block-system-main-block") or
            soup.find("div", id="region-content") or
            soup.find("div", class_="region-content") or
            soup.find("div", class_="outerWrape") or
            soup.find("main") or
            soup.body
        )

    def normalize_section(self, raw):
        raw = raw.lower()
        mapping = {
            "interest": "Interest Rate",
            "processing": "Processing Fees / Charges",
            "eligibility": "Eligibility",
            "document": "Documents Required",
            "margin": "Margin",
            "tenure": "Loan Tenure",
            "repayment": "Repayment / EMI",
            "emi": "Repayment / EMI",
            "security": "Security / Collateral",
            "deduction": "Deductions",
            "purpose": "Purpose of Loan",
            "feature": "Features and Benefits",
            "benefit": "Features and Benefits",
            "faq": "FAQ",
            "apply": "How to Apply",
            "request": "Request / Processing Period"
        }

        for k, v in mapping.items():
            if k in raw:
                return v

        return "General"

    # ------------------ Linked Page Scraper ------------------

    def scrape_linked_page(self, link_url, loan_name, section):
        soup = self.fetch_page(link_url)
        if not soup:
            return

        container = self.get_main_container(soup)
        if not container:
            return

        for tag in container.find_all(["p", "li"]):
            text = tag.get_text(" ", strip=True)
            if text and len(text) > 25:
                self.data.append({
                    "loan_name": loan_name,
                    "section": section,
                    "text": text,
                    "source_url": link_url
                })

    # ------------------ Table Scraper ------------------

    def scrape_tables(self, container, url, loan_name):
        for table in container.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all(["th", "td"])
                if len(cells) < 2:
                    continue

                label = cells[0].get_text(" ", strip=True)
                value_cell = cells[1]
                section = self.normalize_section(label)

                link = value_cell.find("a", href=True)
                if link:
                    link_url = urljoin(url, link["href"])

                    # store parent link (important for RAG)
                    self.data.append({
                        "loan_name": loan_name,
                        "section": section,
                        "text": f"{label}: Refer details",
                        "link_url": link_url,
                        "source_url": url
                    })

                    # scrape linked page content
                    self.scrape_linked_page(link_url, loan_name, section)

                else:
                    value = value_cell.get_text(" ", strip=True)
                    if value:
                        self.data.append({
                            "loan_name": loan_name,
                            "section": section,
                            "text": f"{label}: {value}",
                            "source_url": url
                        })

    # ------------------ Section Scraper ------------------

    def scrape_sections(self, container, url, loan_name):
        headers = container.find_all(["h2", "h3", "h4"])

        for header in headers:
            section = self.normalize_section(header.get_text(strip=True))
            collected_text = []

            sibling = header.find_next_sibling()

            while sibling and sibling.name not in ["h2", "h3", "h4"]:
                # extract links inside section
                links = sibling.find_all("a", href=True)
                for link in links:
                    link_text = link.get_text(" ", strip=True) or "Related link"
                    link_url = urljoin(url, link["href"])

                    self.data.append({
                        "loan_name": loan_name,
                        "section": section,
                        "text": link_text,
                        "link_url": link_url,
                        "source_url": url
                    })

                text = sibling.get_text(" ", strip=True)
                if text and len(text) > 25:
                    collected_text.append(text)

                sibling = sibling.find_next_sibling()

            if collected_text:
                self.data.append({
                    "loan_name": loan_name,
                    "section": section,
                    "text": " ".join(collected_text),
                    "source_url": url
                })

    # ------------------ Page Scraper ------------------

    def scrape_page(self, url):
        soup = self.fetch_page(url)
        if not soup:
            return

        container = self.get_main_container(soup)
        if not container:
            return

        h1 = soup.find("h1")
        loan_name = h1.get_text(strip=True) if h1 else "Unknown Loan"

        self.scrape_tables(container, url, loan_name)
        self.scrape_sections(container, url, loan_name)

    # ------------------ Runner ------------------

    def scrape_all(self):
        for url in self.loan_urls:
            print(f"[SCRAPING] {url}")
            self.scrape_page(url)
            time.sleep(1)

    def save(self, filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_dir)
        filepath = os.path.join(project_root, filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        print(f"[DONE] Saved {len(self.data)} records → {filepath}")


# ------------------ MAIN ------------------

if __name__ == "__main__":
    scraper = BankScraper()
    scraper.scrape_all()
    scraper.save("data/raw_loan_data-1.json")
