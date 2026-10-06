import { chromium } from '/Users/mac/Desktop/Nexora_Agent/node_modules/.pnpm/node_modules/playwright/index.mjs';

async function uploadReel() {
  const videoPath = '/Users/mac/Desktop/CPR Strategy /daily-reel-engine/morning_reel.mp4';
  const caption = `🎯 Today's Nifty & Bank Nifty CPR Intraday Radar!

Level to level quantitative setups with Central Pivot Range.
Narrow CPR setup detected -> High trending breakout potential.

📊 Key Levels:
• Pivot, TC, BC, R1, S1 marked on chart.
• Follow rule-based discipline. 0% emotion.

👉 Get the Complete CPR Pro Toolkit (Indicator + Calculator + PDF Guide):
Link in Bio! 🔗

#nifty50 #banknifty #intradaytrading #cprindicator #priceaction #stockmarkettamil #alphatrader #optionstrading #tradingstrategy #sharemarkettamil`;

  console.log('Launching browser...');
  const context = await chromium.launchPersistentContext('/Users/mac/Desktop/CPR Strategy /.instagram-automation/profile', {
    headless: true,
    viewport: { width: 1280, height: 900 }
  });
  const page = context.pages()[0] || await context.newPage();

  try {
    console.log('Navigating to Instagram...');
    await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(4000);

    console.log('Clicking Create...');
    const createBtn = page.locator('svg[aria-label="New post"], a[role="link"]:has-text("Create"), span:has-text("Create")').first();
    await createBtn.click();
    await page.waitForTimeout(3000);

    console.log('Setting video file...');
    const fileInput = page.locator('input[type="file"]').first();
    await fileInput.setInputFiles(videoPath);
    await page.waitForTimeout(6000);

    const okBtn = page.locator('button:has-text("OK"), button:has-text("Got it")');
    if (await okBtn.count() > 0) {
      console.log('Dismissing modal...');
      await okBtn.first().click();
      await page.waitForTimeout(2000);
    }

    console.log('Clicking Next 1...');
    await page.locator('div[role="button"]:has-text("Next"), button:has-text("Next")').last().click();
    await page.waitForTimeout(4000);

    if (await page.locator('div[role="button"]:has-text("Next"), button:has-text("Next")').count() > 0) {
      console.log('Clicking Next 2...');
      await page.locator('div[role="button"]:has-text("Next"), button:has-text("Next")').last().click();
      await page.waitForTimeout(4000);
    }

    console.log('Filling caption...');
    const captionBox = page.locator('div[aria-label="Write a caption..."], div[role="textbox"]').first();
    if (await captionBox.count() > 0) {
      await captionBox.click();
      await page.keyboard.insertText(caption);
      await page.waitForTimeout(2000);
    }

    console.log('Locating Share button...');
    const shareLoc = page.getByText('Share', { exact: true });
    const count = await shareLoc.count();
    console.log(`Found ${count} exact Share elements`);
    
    if (count > 0) {
      const box = await shareLoc.last().boundingBox();
      console.log('Share button box:', box);
      if (box) {
        // Direct mouse click on exact center of Share button
        await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
        console.log('Dispatched mouse click at center of Share button!');
      } else {
        await shareLoc.last().click({ force: true });
      }
    }

    console.log('Waiting for upload and sharing to complete (40s)...');
    await page.waitForTimeout(40000);
    
    await page.screenshot({ path: '/Users/mac/Desktop/ig_reel_upload_result.png' });
    console.log('Completed! Screenshot saved.');
    
    // Check profile
    await page.goto('https://www.instagram.com/alpha_traderz_/', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);
    await page.screenshot({ path: '/Users/mac/Desktop/ig_profile_with_reel.png' });
    console.log('Profile screenshot saved to /Users/mac/Desktop/ig_profile_with_reel.png');
  } finally {
    await context.close();
  }
}

uploadReel().catch(console.error);
