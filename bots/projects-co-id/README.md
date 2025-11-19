# Projects.co.id Scraper

Automated scraper for projects.co.id with scheduled execution and session management.

## 🎯 Features

- ✅ Scheduled scraping every 15 minutes
- ✅ Persistent session management
- ✅ Cloudflare bypass support
- ✅ Dual implementation (Crawlee & Playwright)
- ✅ JSON output with timestamps
- ✅ Error handling and retry logic

## 🚀 Quick Start

### Option 1: Crawlee (Recommended) ⭐

```bash
cd bots/projects-co-id
npm install
npm run scrape:schedule  # Every 15 minutes
```

### Option 2: Playwright (Python)

```bash
cd bots/projects-co-id
pip install -r requirements-scheduler.txt
playwright install chromium
python scheduler.py  # Every 15 minutes
```

## 📋 Configuration

Create `.env` file in repository root:

```bash
PROJECTS_CO_ID_USERNAME=your-email@example.com
PROJECTS_CO_ID_PASSWORD=your-password
SCRAPE_INTERVAL_MINUTES=15
MAX_PAGES=10
```

## 📊 Output

Scraped data saved to: `data/scraped/projects-co-id/projects_co_id_YYYYMMDD_HHMMSS.json`

## 🔗 Related

- **Main Repository**: https://github.com/daddy-dev-id/ai-career-agent
- **Issues**: https://github.com/daddy-dev-id/ai-career-agent/issues?q=is%3Aissue+projects-co-id
- **PR**: https://github.com/daddy-dev-id/ai-career-agent/pull/97

---

**Part of AI Bot Development repository** 🤖
