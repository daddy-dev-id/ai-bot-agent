/**
 * Projects.co.id Scraper Scheduler
 * Runs scraper every 15 minutes with session management
 */

import cron from 'node-cron';
import { runScraper } from './crawlee-scraper.js';
import dotenv from 'dotenv';

dotenv.config();

const INTERVAL_MINUTES = parseInt(process.env.SCRAPE_INTERVAL_MINUTES || '15');

console.log(`🚀 Starting Projects.co.id scraper scheduler`);
console.log(`   Interval: ${INTERVAL_MINUTES} minutes`);
console.log(`   Press Ctrl+C to stop\n`);

// Run immediately on start
console.log('🔄 Running initial scrape...');
await runScraper().catch(err => {
    console.error('❌ Error in initial scrape:', err);
});

// Schedule recurring scrapes
const cronExpression = `*/${INTERVAL_MINUTES} * * * *`;
console.log(`📅 Scheduled: ${cronExpression} (every ${INTERVAL_MINUTES} minutes)`);

cron.schedule(cronExpression, async () => {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`🔄 Scheduled scrape - ${new Date().toISOString()}`);
    console.log(`${'='.repeat(60)}`);
    
    try {
        await runScraper();
    } catch (err) {
        console.error('❌ Error in scheduled scrape:', err);
    }
});

// Keep process alive
process.on('SIGINT', () => {
    console.log('\n⏹️  Scheduler stopped by user');
    process.exit(0);
});

