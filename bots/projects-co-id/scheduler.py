#!/usr/bin/env python3
"""
Projects.co.id Scraper Scheduler
Runs scraper every 15 minutes with session management.
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    print("⚠️  APScheduler not installed. Install with: pip install apscheduler")

from dotenv import load_dotenv
from scraper import ProjectsCoIdScraper

# Load environment variables
load_dotenv()


class SessionManager:
    """Manages persistent session for projects.co.id scraper."""
    
    def __init__(self, session_file: str = "data/sessions/projects_co_id_session.json"):
        self.session_file = Path(session_file)
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        self.session_data = self.load_session()
    
    def load_session(self) -> dict:
        """Load session data from file."""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading session: {e}")
        return {
            "cookies": {},
            "last_login": None,
            "session_valid": False
        }
    
    def save_session(self, cookies: dict, session_valid: bool = True):
        """Save session data to file."""
        self.session_data = {
            "cookies": cookies,
            "last_login": datetime.now().isoformat(),
            "session_valid": session_valid
        }
        try:
            with open(self.session_file, 'w') as f:
                json.dump(self.session_data, f, indent=2)
            print(f"✅ Session saved to {self.session_file}")
        except Exception as e:
            print(f"❌ Error saving session: {e}")
    
    def is_session_valid(self, max_age_hours: int = 24) -> bool:
        """Check if session is still valid."""
        if not self.session_data.get("session_valid", False):
            return False
        
        last_login = self.session_data.get("last_login")
        if not last_login:
            return False
        
        try:
            last_login_time = datetime.fromisoformat(last_login)
            age_hours = (datetime.now() - last_login_time).total_seconds() / 3600
            return age_hours < max_age_hours
        except Exception:
            return False
    
    def get_cookies(self) -> dict:
        """Get saved cookies."""
        return self.session_data.get("cookies", {})


class ScheduledScraper:
    """Scheduled scraper with session management."""
    
    def __init__(self, interval_minutes: int = 15):
        self.interval_minutes = interval_minutes
        self.session_manager = SessionManager()
        self.scraper: Optional[ProjectsCoIdScraper] = None
        self.scheduler: Optional[BlockingScheduler] = None
        
        print(f"✅ ScheduledScraper initialized")
        print(f"   Interval: {interval_minutes} minutes")
        print(f"   Session file: {self.session_manager.session_file}")
    
    def run_scrape(self):
        """Run a single scraping cycle."""
        print(f"\n{'='*60}")
        print(f"🔄 Starting scheduled scrape - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            # Initialize scraper
            self.scraper = ProjectsCoIdScraper(headless=True)
            
            # Check session validity
            if not self.session_manager.is_session_valid():
                print("⚠️  Session expired or invalid, will need to login")
                # Session will be handled by scraper
            
            # Start browser
            self.scraper.start_browser()
            
            # Load saved cookies if available
            saved_cookies = self.session_manager.get_cookies()
            if saved_cookies and self.scraper.page:
                # Add cookies to browser context
                for cookie in saved_cookies:
                    try:
                        self.scraper.page.context.add_cookies([cookie])
                    except Exception as e:
                        print(f"⚠️  Error loading cookie: {e}")
            
            # Run scraping
            projects = self.scraper.scrape_all_pages(max_pages=5)  # Limit for scheduled runs
            
            # Save results
            if projects:
                self.scraper.save_projects(projects)
                print(f"✅ Scraped {len(projects)} projects")
            else:
                print("⚠️  No projects scraped")
            
            # Save session (if logged in)
            if self.scraper.logged_in and self.scraper.page:
                try:
                    cookies = self.scraper.page.context.cookies()
                    self.session_manager.save_session(cookies, session_valid=True)
                except Exception as e:
                    print(f"⚠️  Error saving session: {e}")
            
            print(f"✅ Scrape cycle complete")
            
        except Exception as e:
            print(f"❌ Error during scrape: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Always cleanup
            if self.scraper:
                self.scraper.stop_browser()
    
    def start_scheduler(self):
        """Start the scheduler."""
        if not SCHEDULER_AVAILABLE:
            raise ImportError("APScheduler is required. Install with: pip install apscheduler")
        
        print(f"🚀 Starting scheduler (every {self.interval_minutes} minutes)...")
        print(f"   Press Ctrl+C to stop")
        
        self.scheduler = BlockingScheduler()
        
        # Add job
        self.scheduler.add_job(
            self.run_scrape,
            trigger=IntervalTrigger(minutes=self.interval_minutes),
            id='projects_co_id_scraper',
            name='Projects.co.id Scraper',
            replace_existing=True
        )
        
        # Run immediately on start
        print("🔄 Running initial scrape...")
        self.run_scrape()
        
        # Start scheduler
        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            print("\n⏹️  Scheduler stopped by user")
            self.scheduler.shutdown()


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scheduled Projects.co.id scraper")
    parser.add_argument("--interval", type=int, default=15, help="Scraping interval in minutes (default: 15)")
    parser.add_argument("--once", action="store_true", help="Run once and exit (no scheduling)")
    
    args = parser.parse_args()
    
    scheduled_scraper = ScheduledScraper(interval_minutes=args.interval)
    
    if args.once:
        print("🔄 Running single scrape...")
        scheduled_scraper.run_scrape()
    else:
        scheduled_scraper.start_scheduler()


if __name__ == "__main__":
    main()

