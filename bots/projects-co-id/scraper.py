#!/usr/bin/env python3
"""
Projects.co.id Scraper
Scrapes project listings from projects.co.id with browser automation to bypass Cloudflare.
"""

import os
import json
import time
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright not installed. Install with: pip install playwright && playwright install chromium")

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ProjectsCoIdScraper:
    """Scraper for projects.co.id using browser automation."""
    
    def __init__(self, headless: bool = True):
        """
        Initialize the scraper.
        
        Args:
            headless: Run browser in headless mode (default: True)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is required. Install with: pip install playwright && playwright install chromium")
        
        # Load credentials from environment
        self.username = os.getenv("PROJECTS_CO_ID_USERNAME")
        self.password = os.getenv("PROJECTS_CO_ID_PASSWORD")
        
        if not self.username or not self.password:
            raise ValueError("PROJECTS_CO_ID_USERNAME and PROJECTS_CO_ID_PASSWORD must be set in .env file")
        
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.logged_in = False
        
        # Configuration
        self.base_url = "https://projects.co.id"
        self.listing_url = f"{self.base_url}/public/browse_projects/listing"
        self.scrape_delay = int(os.getenv("SCRAPE_DELAY_SECONDS", "2"))
        self.max_pages = int(os.getenv("MAX_PAGES", "10"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        
        # Output directory
        self.output_dir = Path("data/scraped/projects-co-id")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ ProjectsCoIdScraper initialized")
        print(f"   Username: {self.username}")
        print(f"   Headless: {self.headless}")
        print(f"   Output: {self.output_dir}")
    
    def start_browser(self):
        """Start browser instance."""
        print("🌐 Starting browser...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.page = self.browser.new_page()
        
        # Set realistic viewport
        self.page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Set user agent
        self.page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        print("✅ Browser started")
    
    def stop_browser(self):
        """Stop browser instance."""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        print("✅ Browser stopped")
    
    def login(self) -> bool:
        """
        Login to projects.co.id.
        
        Returns:
            True if login successful, False otherwise
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        print("🔐 Logging into projects.co.id...")
        
        # Try different login URLs
        login_urls = [
            f"{self.base_url}/login",
            f"{self.base_url}/auth/login",
            f"{self.base_url}/user/login",
            f"{self.base_url}/signin"
        ]
        
        for login_url in login_urls:
            try:
                print(f"   Trying: {login_url}")
                self.page.goto(login_url, wait_until="networkidle", timeout=30000)
                
                # Wait for Cloudflare challenge if present
                time.sleep(3)
                
                # Check if we're on login page
                if "login" in self.page.url.lower() or "signin" in self.page.url.lower():
                    # Fill login form
                    email_input = self.page.query_selector('input[type="email"], input[name="email"], input[id="email"]')
                    password_input = self.page.query_selector('input[type="password"], input[name="password"], input[id="password"]')
                    
                    if email_input and password_input:
                        email_input.fill(self.username)
                        password_input.fill(self.password)
                        
                        # Submit form
                        submit_button = self.page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Login"), button:has-text("Masuk")')
                        if submit_button:
                            submit_button.click()
                            
                            # Wait for navigation
                            self.page.wait_for_load_state("networkidle", timeout=30000)
                            time.sleep(2)
                            
                            # Check if login successful
                            if "dashboard" in self.page.url.lower() or "profile" in self.page.url.lower():
                                self.logged_in = True
                                print("✅ Login successful")
                                return True
                
            except Exception as e:
                print(f"   ⚠️  Error with {login_url}: {e}")
                continue
        
        print("❌ Login failed")
        return False
    
    def scrape_listing_page(self, page_num: int = 1) -> List[Dict[str, Any]]:
        """
        Scrape a single listing page.
        
        Args:
            page_num: Page number to scrape
            
        Returns:
            List of project dictionaries
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        print(f"📄 Scraping page {page_num}...")
        
        url = f"{self.listing_url}?page={page_num}" if page_num > 1 else self.listing_url
        
        try:
            self.page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Wait for Cloudflare challenge if present
            time.sleep(5)
            
            # Wait for project listings to load
            self.page.wait_for_selector("body", timeout=30000)
            time.sleep(2)
            
            # Extract project cards
            # TODO: Update selectors based on actual HTML structure
            projects = []
            
            # Try multiple selector strategies
            selectors = [
                ".project-card",
                ".project-item",
                ".listing-item",
                "[class*='project']",
                "[class*='listing']"
            ]
            
            project_elements = []
            for selector in selectors:
                elements = self.page.query_selector_all(selector)
                if elements:
                    project_elements = elements
                    print(f"   Found {len(elements)} projects using selector: {selector}")
                    break
            
            if not project_elements:
                print("   ⚠️  No project elements found")
                return []
            
            # Extract data from each project element
            for element in project_elements:
                try:
                    project_data = self._extract_project_data(element)
                    if project_data:
                        projects.append(project_data)
                except Exception as e:
                    print(f"   ⚠️  Error extracting project: {e}")
                    continue
            
            print(f"   ✅ Extracted {len(projects)} projects")
            return projects
            
        except Exception as e:
            print(f"   ❌ Error scraping page {page_num}: {e}")
            return []
    
    def _extract_project_data(self, element) -> Optional[Dict[str, Any]]:
        """
        Extract project data from a single project element.
        
        Args:
            element: Playwright element handle
            
        Returns:
            Project data dictionary or None
        """
        try:
            # Extract title
            title_elem = element.query_selector("h3, h2, .title, [class*='title']")
            title = title_elem.inner_text() if title_elem else "No title"
            
            # Extract URL
            link_elem = element.query_selector("a[href*='/project/']")
            url = ""
            if link_elem:
                href = link_elem.get_attribute("href")
                if href:
                    url = href if href.startswith("http") else f"{self.base_url}{href}"
            
            # Extract description
            desc_elem = element.query_selector("p, .description, [class*='desc']")
            description = desc_elem.inner_text() if desc_elem else ""
            
            # Extract budget
            budget_text = element.inner_text()
            budget_match = None
            if "Rp" in budget_text or "IDR" in budget_text:
                # Try to extract budget range
                import re
                budget_pattern = r'Rp\s*([\d.,]+)\s*-\s*Rp\s*([\d.,]+)'
                match = re.search(budget_pattern, budget_text)
                if match:
                    budget_match = {
                        "min": match.group(1).replace(",", "").replace(".", ""),
                        "max": match.group(2).replace(",", "").replace(".", ""),
                        "currency": "IDR"
                    }
            
            # Extract tags/skills
            tag_elements = element.query_selector_all(".tag, [class*='tag'], [class*='skill']")
            tags = [tag.inner_text() for tag in tag_elements if tag.inner_text()]
            
            return {
                "title": title.strip(),
                "description": description.strip(),
                "url": url,
                "budget": budget_match,
                "tags": tags,
                "scraped_at": datetime.now().isoformat(),
                "platform": "projects.co.id"
            }
            
        except Exception as e:
            print(f"      ⚠️  Error extracting project data: {e}")
            return None
    
    def scrape_all_pages(self, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Scrape all listing pages.
        
        Args:
            max_pages: Maximum number of pages to scrape (default: self.max_pages)
            
        Returns:
            List of all projects
        """
        max_pages = max_pages or self.max_pages
        all_projects = []
        
        print(f"🚀 Starting to scrape {max_pages} pages...")
        
        for page_num in range(1, max_pages + 1):
            projects = self.scrape_listing_page(page_num)
            
            if not projects:
                print(f"   ⚠️  No projects found on page {page_num}, stopping")
                break
            
            all_projects.extend(projects)
            
            # Delay between pages
            if page_num < max_pages:
                time.sleep(self.scrape_delay)
        
        print(f"✅ Scraped {len(all_projects)} total projects")
        return all_projects
    
    def save_projects(self, projects: List[Dict[str, Any]], filename: Optional[str] = None):
        """
        Save scraped projects to JSON file.
        
        Args:
            projects: List of project dictionaries
            filename: Optional filename (default: auto-generated with timestamp)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"projects_co_id_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        data = {
            "scraped_at": datetime.now().isoformat(),
            "total_projects": len(projects),
            "platform": "projects.co.id",
            "projects": projects
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(projects)} projects to: {filepath}")
        return filepath
    
    def run(self, max_pages: Optional[int] = None):
        """
        Run the complete scraping workflow.
        
        Args:
            max_pages: Maximum number of pages to scrape
        """
        try:
            # Start browser
            self.start_browser()
            
            # Login (optional - may not be needed for public listings)
            # self.login()
            
            # Scrape pages
            projects = self.scrape_all_pages(max_pages)
            
            # Save results
            if projects:
                self.save_projects(projects)
            
            return projects
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            raise
        finally:
            # Always stop browser
            self.stop_browser()


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape projects.co.id listings")
    parser.add_argument("--pages", type=int, default=5, help="Number of pages to scrape")
    parser.add_argument("--headless", action="store_true", default=True, help="Run in headless mode")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Run with visible browser")
    
    args = parser.parse_args()
    
    scraper = ProjectsCoIdScraper(headless=args.headless)
    scraper.run(max_pages=args.pages)


if __name__ == "__main__":
    main()

