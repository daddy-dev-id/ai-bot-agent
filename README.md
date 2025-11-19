# AI Bot Development

Centralized repository for all bot development - web scrapers, automation bots, and data collection agents.

## 🎯 Purpose

This repository contains all bot development projects, including:
- Web scrapers for job portals and freelance platforms
- Automation bots for data collection
- Scheduled scraping agents
- Browser automation tools

## 📁 Structure

```
ai-bot-agent/
├── bots/                    # Individual bot projects
│   ├── projects-co-id/      # Projects.co.id scraper
│   ├── jobstreet/           # JobStreet scraper (planned)
│   └── freelancer-com/      # Freelancer.com scraper (planned)
├── libs/                    # Shared libraries
│   ├── session-manager/    # Session management utilities
│   ├── data-storage/        # Data storage utilities
│   └── browser-automation/  # Browser automation helpers
├── config/                  # Configuration files
└── docs/                    # Documentation
```

## 🚀 Quick Start

### Projects.co.id Scraper

```bash
cd bots/projects-co-id
npm install  # or pip install -r requirements.txt
npm run scrape:schedule
```

## 📋 Current Bots

### ✅ Projects.co.id Scraper
- **Status**: In Development
- **Branch**: `feature/projects-co-id-scraper`
- **Technology**: Crawlee (JavaScript) / Playwright (Python)
- **Features**: Scheduled scraping, session management, Cloudflare bypass

## 🔗 Related Repositories

- **AI Career Agent**: https://github.com/daddy-dev-id/ai-career-agent
  - Main career agent project
  - Bot integration and orchestration

## 📝 Development Guidelines

1. Each bot should be self-contained in `bots/[bot-name]/`
2. Use shared libraries from `libs/` for common functionality
3. Document setup and usage in each bot's README
4. Follow consistent naming conventions

## 🔒 Security

- Never commit credentials or API keys
- Use environment variables for sensitive data
- Store secrets in `.env` files (excluded from git)

---

**Repository for all bot development projects** 🤖
