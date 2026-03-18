const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:5173', { timeout: 10000 });
    console.log('✅ Page loaded successfully');
    
    // Check page title
    const title = await page.title();
    console.log('Title:', title);
    
    // Wait a bit for content to render
    await page.waitForTimeout(2000);
    
    // Check for content
    const content = await page.content();
    if (content.includes('Clock') || content.includes('clock') || content.includes('World')) {
      console.log('✅ Clock content found');
    }
    
    // Take screenshot
    await page.screenshot({ path: 'test-screenshot.png' });
    console.log('✅ Screenshot saved: test-screenshot.png');
    
  } catch (err) {
    console.log('❌ Error:', err.message);
  }
  
  await browser.close();
})();