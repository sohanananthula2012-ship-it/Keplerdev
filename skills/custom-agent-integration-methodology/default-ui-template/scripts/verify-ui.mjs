import { mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { chromium } from 'playwright-core';

const url = process.env.CUSTOM_AGENT_CHAT_URL || 'http://127.0.0.1:5174/';
const chromePath = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputDir = process.env.CUSTOM_AGENT_CHAT_SCREENSHOT_DIR || '/tmp';
const prompt = process.env.CUSTOM_AGENT_CHAT_PROMPT || '查询下 2026 年世界杯什么时候开始，在哪办？';
const questionPrompt = process.env.CUSTOM_AGENT_CHAT_QUESTION_PROMPT || '我想了解下世界杯，你询问下我的诉求。用 ask user question。';
const oldAllBlackShellColors = ['#000000', '#050' + '505'];

function assertCheck(condition, message) {
  if (!condition) throw new Error(message);
}

async function verifyPage(browser, label, viewport, createSession) {
  const page = await browser.newPage({ viewport });
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForSelector('.bps-composer textarea', { timeout: 15000 });

  const initialVisualState = await page.evaluate(() => {
    const shell = document.querySelector('.bps-shell');
    const sidebar = document.querySelector('.bps-session-sidebar');
    const emptyState = document.querySelector('.bps-empty-state');
    const composer = document.querySelector('.bps-composer');
    const shellStyle = shell ? getComputedStyle(shell) : null;
    const sidebarStyle = sidebar ? getComputedStyle(sidebar) : null;
    const sidebarRect = sidebar?.getBoundingClientRect();
    const composerRect = composer?.getBoundingClientRect();
    const emptyRect = emptyState?.getBoundingClientRect();
    const initialTheme = shell?.getAttribute('data-theme') || '';
    const initialLogoFamily = shell?.getAttribute('data-logo-family') || '';

    if (shell) {
      shell.setAttribute('data-theme', 'dark');
    }
    const darkStyle = shell ? getComputedStyle(shell) : null;
    const darkBackground = darkStyle?.backgroundColor || '';

    if (shell) {
      shell.setAttribute('data-logo-family', 'green');
    }
    const greenStyle = shell ? getComputedStyle(shell) : null;
    const greenBackgroundImage = greenStyle?.backgroundImage || '';

    if (shell) {
      if (initialTheme) shell.setAttribute('data-theme', initialTheme);
      else shell.removeAttribute('data-theme');
      if (initialLogoFamily) shell.setAttribute('data-logo-family', initialLogoFamily);
      else shell.removeAttribute('data-logo-family');
    }

    return {
      hasShell: Boolean(shell),
      theme: initialTheme,
      logoFamily: initialLogoFamily,
      hasEmptyState: Boolean(emptyState),
      hasComposerChip: Boolean(document.querySelector('.bps-composer-agent-chip')),
      hasSessionCard: Boolean(sidebar),
      shellBgVar: shellStyle?.getPropertyValue('--bps-bg').trim() || '',
      shellBackgroundColor: shellStyle?.backgroundColor || '',
      shellBackgroundImage: shellStyle?.backgroundImage || '',
      darkBgVar: darkStyle?.getPropertyValue('--bps-bg').trim() || '',
      darkBackground,
      greenBackgroundImage,
      sidebarPosition: sidebarStyle?.position || '',
      sidebarDisplay: sidebarStyle?.display || '',
      sidebarWidth: sidebarRect ? Math.round(sidebarRect.width) : 0,
      emptyBottom: emptyRect ? Math.round(emptyRect.bottom) : 0,
      composerTop: composerRect ? Math.round(composerRect.top) : 0,
    };
  });

  assertCheck(initialVisualState.hasShell, `${label}: shell was not rendered`);
  assertCheck(initialVisualState.hasEmptyState, `${label}: empty state was not rendered before the first message`);
  assertCheck(initialVisualState.hasComposerChip, `${label}: composer agent chip was not rendered`);
  assertCheck(initialVisualState.hasSessionCard, `${label}: session card was not rendered`);
  assertCheck(
    !oldAllBlackShellColors.includes(initialVisualState.shellBgVar.toLowerCase()),
    `${label}: default shell background variable is still all-black (${initialVisualState.shellBgVar})`,
  );
  assertCheck(
    initialVisualState.shellBackgroundImage && initialVisualState.shellBackgroundImage !== 'none',
    `${label}: default shell background does not include the public-site gradient`,
  );
  assertCheck(
    !oldAllBlackShellColors.includes(initialVisualState.darkBgVar.toLowerCase()),
    `${label}: explicit dark theme fell back to the old black shell (${initialVisualState.darkBgVar || initialVisualState.darkBackground})`,
  );
  assertCheck(
    initialVisualState.greenBackgroundImage.includes('linear-gradient'),
    `${label}: green logo-family background was not applied`,
  );
  if (viewport.width >= 760) {
    assertCheck(initialVisualState.sidebarPosition === 'absolute', `${label}: desktop session card is not floating`);
    assertCheck(initialVisualState.sidebarWidth >= 250 && initialVisualState.sidebarWidth <= 280, `${label}: desktop session card width ${initialVisualState.sidebarWidth} is not Public Site-like`);
  }
  assertCheck(
    initialVisualState.emptyBottom <= initialVisualState.composerTop + 24,
    `${label}: empty state overlaps the composer`,
  );

  if (createSession) {
    await page.waitForSelector('.bps-new-session', { timeout: 15000 });
    await page.locator('.bps-new-session').click();
    await page.waitForSelector('.bps-session-item.is-active', { timeout: 15000 });
  }

  await page.locator('.bps-composer textarea').fill(prompt);
  await page.locator('.bps-composer textarea').press('Enter');
  if (createSession) {
    await page.waitForFunction(() => {
      const text = document.body.innerText;
      const hasPreparing = text.includes('Agent is preparing') || text.includes('Agent 准备中');
      const hasResponding = text.includes('Agent responding') || text.includes('Agent 响应中');
      return hasPreparing && hasResponding;
    }, null, { timeout: 8000 });
    const startupWaiting = await page.evaluate(() => {
      const startupBlocks = [...document.querySelectorAll('.bps-startup')];
      const latestStartupText = startupBlocks[startupBlocks.length - 1]?.textContent || '';
      const thinkingBlocks = [...document.querySelectorAll('.bps-thinking')];
      const latestThinkingText = thinkingBlocks[thinkingBlocks.length - 1]?.textContent || '';
      return {
        hasPreparing: latestStartupText.includes('Agent is preparing') || latestStartupText.includes('Agent 准备中'),
        hasResponding: latestStartupText.includes('Agent responding') || latestStartupText.includes('Agent 响应中'),
        hasAgentReady: latestStartupText.includes('Agent ready') || latestStartupText.includes('Agent 就绪'),
        hasThoughtDone: latestThinkingText.includes('Thought for') || latestThinkingText.includes('思考了'),
      };
    });
    assertCheck(startupWaiting.hasPreparing, `${label}: startup preparing header was not rendered`);
    assertCheck(startupWaiting.hasResponding, `${label}: startup responding row was not rendered`);
    assertCheck(!startupWaiting.hasAgentReady, `${label}: startup showed ready before first response`);
    assertCheck(!startupWaiting.hasThoughtDone, `${label}: startup-only phase showed finished thinking`);
  }

  await page.waitForFunction(() => document.body.innerText.includes('已连接'), null, { timeout: 20000 });
  await page.waitForSelector('.bps-composer-button[aria-label="发送"]', { timeout: 15000 });
  await page.waitForSelector('.bps-tool-list .bps-collapsible-header', { timeout: 15000 });
  await page.waitForSelector('.bps-thinking .bps-collapsible-header', { timeout: 15000 });
  await page.waitForTimeout(1200);
  const finalClosed = await page.evaluate(() => {
    const thinkingHeaders = [...document.querySelectorAll('.bps-thinking .bps-collapsible-header')];
    const toolHeaders = [...document.querySelectorAll('.bps-tool-list .bps-collapsible-header')];
    return {
      hasSendButton: Boolean(document.querySelector('.bps-composer-button[aria-label="发送"]')),
      hasStopButton: Boolean(document.querySelector('.bps-composer-button[aria-label="停止"]')),
      activeSessionText: document.querySelector('.bps-session-item.is-active')?.textContent || '',
      thinkingCollapsed: thinkingHeaders.length > 0 && thinkingHeaders.every((header) => header.getAttribute('aria-expanded') === 'false'),
      toolCollapsed: toolHeaders.length > 0 && toolHeaders.every((header) => header.getAttribute('aria-expanded') === 'false'),
    };
  });
  assertCheck(finalClosed.hasSendButton, `${label}: composer did not return to send state`);
  assertCheck(!finalClosed.hasStopButton, `${label}: composer still shows stop state after normal completion`);
  assertCheck(!finalClosed.activeSessionText.includes('运行中'), `${label}: active session still shows running after normal completion`);
  assertCheck(finalClosed.thinkingCollapsed, `${label}: thinking section did not auto-collapse after normal completion`);
  assertCheck(finalClosed.toolCollapsed, `${label}: tool section did not auto-collapse after normal completion`);

  for (let attempt = 0; attempt < 2; attempt += 1) {
    const expanded = await page.evaluate(() => {
      const buttons = [
        ...document.querySelectorAll('.bps-thinking .bps-collapsible-header'),
        ...document.querySelectorAll('.bps-tool-list .bps-collapsible-header'),
      ];
      buttons.forEach((button) => {
        if (button.getAttribute('aria-expanded') === 'false') {
          button.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
        }
      });
      return buttons.every((button) => button.getAttribute('aria-expanded') === 'true');
    });
    await page.waitForTimeout(350);
    if (expanded) break;
  }
  await page.waitForSelector('.bps-tool-row', { timeout: 15000 });
  await page.waitForSelector('.bps-thinking-text', { timeout: 15000 });
  await page.waitForTimeout(500);

  await mkdir(outputDir, { recursive: true });
  const screenshot = join(outputDir, `custom-agent-chat-${label}.png`);
  await page.screenshot({ path: screenshot, fullPage: false });

  const result = await page.evaluate(() => {
    function styleFor(selector) {
      const element = document.querySelector(selector);
      if (!element) return null;
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return {
        display: style.display,
        fontSize: style.fontSize,
        lineHeight: style.lineHeight,
        width: Math.round(rect.width),
        height: Math.round(rect.height),
      };
    }

    const text = document.body.innerText;
    return {
      text,
      sessionCount: document.querySelectorAll('.bps-session-item').length,
      hasActiveSession: Boolean(document.querySelector('.bps-session-item.is-active')),
      hasAgentReady: text.includes('Agent 就绪'),
      hasThinking: text.includes('思考') && Boolean(document.querySelector('.bps-thinking-text')),
      hasToolAction: text.includes('已完成') && Boolean(document.querySelector('.bps-tool-row')),
      hasMarkdownTable: Boolean(document.querySelector('.bps-markdown table')),
      hasRawMarkdownTable: text.includes('| 项目 | 状态 |'),
      hasAssistantAnswer: text.includes('已连接') && Boolean(document.querySelector('.bps-assistant-message')),
      hasDebugEventCard: text.includes('usage.update') || text.includes('RUN_STARTED') || text.includes('TEXT_MESSAGE_CONTENT'),
      transcript: styleFor('.bps-transcript'),
      composer: styleFor('.bps-composer'),
      userBubble: styleFor('.bps-user-bubble'),
      assistant: styleFor('.bps-assistant-message'),
      thinking: styleFor('.bps-thinking-text'),
      sidebar: styleFor('.bps-session-sidebar'),
    };
  });

  result.screenshot = screenshot;
  result.initialVisualState = initialVisualState;

  assertCheck(result.hasAssistantAnswer, `${label}: assistant answer was not rendered`);
  assertCheck(result.hasThinking, `${label}: thinking UI was not rendered`);
  assertCheck(result.hasToolAction, `${label}: tool action UI was not rendered`);
  assertCheck(result.hasMarkdownTable, `${label}: Markdown table was not rendered as a table`);
  assertCheck(!result.hasRawMarkdownTable, `${label}: raw Markdown table text is visible`);
  assertCheck(!result.hasDebugEventCard, `${label}: raw/debug event leaked into the transcript`);
  assertCheck(result.assistant?.fontSize === '14px', `${label}: assistant font size is ${result.assistant?.fontSize}`);
  assertCheck(result.assistant?.lineHeight === '22px', `${label}: assistant line-height is ${result.assistant?.lineHeight}`);
  assertCheck(result.thinking?.fontSize === '14px', `${label}: thinking font size is ${result.thinking?.fontSize}`);
  assertCheck(result.userBubble?.width <= 568, `${label}: user bubble width ${result.userBubble?.width} exceeds 568px`);
  assertCheck(result.transcript?.width <= 800, `${label}: transcript width ${result.transcript?.width} exceeds 800px`);
  assertCheck(result.composer?.width <= 800, `${label}: composer width ${result.composer?.width} exceeds 800px`);

  await page.close();
  return result;
}

async function verifyAskUserQuestion(browser) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  let answerRequestCount = 0;
  page.on('request', (request) => {
    const requestUrl = request.url();
    if (request.method() === 'POST' && requestUrl.includes('/tool-calls/') && requestUrl.endsWith('/answer')) {
      answerRequestCount += 1;
    }
  });
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForSelector('.bps-composer textarea', { timeout: 15000 });
  await page.waitForSelector('.bps-new-session', { timeout: 15000 });
  await page.locator('.bps-new-session').click();
  await page.waitForSelector('.bps-session-item.is-active', { timeout: 15000 });

  await page.locator('.bps-composer textarea').fill(questionPrompt);
  await page.locator('.bps-composer textarea').press('Enter');
  await page.waitForSelector('[data-testid="bps-floating-question-card"]', { timeout: 20000 });
  await page.waitForSelector('.bps-tool-list .bps-collapsible-header', { timeout: 15000 });

  const waiting = await page.evaluate(() => {
    const text = document.body.innerText;
    const card = document.querySelector('[data-testid="bps-floating-question-card"]');
    const transcriptCard = document.querySelector('.bps-transcript .bps-question-card');
    const thinkingHeaders = [...document.querySelectorAll('.bps-thinking .bps-collapsible-header')];
    const latestThinkingHeader = thinkingHeaders[thinkingHeaders.length - 1];
    const toolHeaders = [...document.querySelectorAll('.bps-tool-list .bps-collapsible-header')];
    return {
      hasFloatingCard: Boolean(card),
      hasTranscriptQuestionCard: Boolean(transcriptCard),
      hasInlineLegacyCopy: text.includes('需要你确认'),
      hasQuestionHeader: text.includes('问题') || text.includes('Questions'),
      hasToolGroup: Boolean(document.querySelector('.bps-tool-list .bps-collapsible-header')),
      hasExpandedToolGroup: toolHeaders.length > 0 && toolHeaders.every((header) => header.getAttribute('aria-expanded') === 'true'),
      hasThinkingHeader: Boolean(latestThinkingHeader),
      hasExpandedThinking: Boolean(latestThinkingHeader) && latestThinkingHeader.getAttribute('aria-expanded') === 'true',
      thinkingTitle: latestThinkingHeader?.textContent || '',
      hasSendButton: Boolean(document.querySelector('.bps-composer-button[aria-label="发送"]')),
      hasStopButton: Boolean(document.querySelector('.bps-composer-button[aria-label="停止"]')),
      hasRawJson: text.includes('"questions"') || text.includes('tool_call_id'),
      cardRect: card ? (() => {
        const rect = card.getBoundingClientRect();
        return {
          top: Math.round(rect.top),
          bottom: Math.round(rect.bottom),
          width: Math.round(rect.width),
        };
      })() : null,
      composerRect: (() => {
        const rect = document.querySelector('.bps-composer')?.getBoundingClientRect();
        return rect ? {
          top: Math.round(rect.top),
          bottom: Math.round(rect.bottom),
          width: Math.round(rect.width),
        } : null;
      })(),
    };
  });

  assertCheck(waiting.hasFloatingCard, 'ask-user-question: floating card was not rendered');
  assertCheck(!waiting.hasTranscriptQuestionCard, 'ask-user-question: waiting card leaked into transcript');
  assertCheck(!waiting.hasInlineLegacyCopy, 'ask-user-question: legacy inline confirm copy is visible');
  assertCheck(waiting.hasQuestionHeader, 'ask-user-question: question card header was not rendered');
  assertCheck(waiting.hasToolGroup, 'ask-user-question: tool group was not rendered');
  assertCheck(waiting.hasExpandedToolGroup, 'ask-user-question: tool group should stay expanded while waiting for the user');
  assertCheck(waiting.hasThinkingHeader, 'ask-user-question: thinking header was not rendered');
  assertCheck(waiting.hasSendButton, 'ask-user-question: composer should keep send state while waiting for question answer');
  assertCheck(!waiting.hasStopButton, 'ask-user-question: composer should not show stop state while only waiting for question answer');
  assertCheck(!waiting.hasRawJson, 'ask-user-question: raw JSON leaked into UI');
  assertCheck(waiting.cardRect && waiting.composerRect && waiting.cardRect.bottom <= waiting.composerRect.top + 12, 'ask-user-question: floating card is not above composer');

  await mkdir(outputDir, { recursive: true });
  const waitingScreenshot = join(outputDir, 'custom-agent-chat-ask-user-question-waiting.png');
  await page.screenshot({ path: waitingScreenshot, fullPage: false });

  await page.locator('.bps-question-option').first().click();
  await page.waitForFunction(() => {
    const count = document.querySelector('.bps-question-count')?.textContent || '';
    return count.includes('2/2') || count.includes('1/1');
  }, null, { timeout: 5000 });
  const countText = await page.locator('.bps-question-count').innerText().catch(() => '');
  if (countText.includes('/2')) {
    await page.locator('.bps-question-option').first().click();
  }
  await page.locator('.bps-question-primary').click();
  await page.waitForFunction(() => !document.querySelector('[data-testid="bps-floating-question-card"]'), null, { timeout: 15000 });
  await page.waitForFunction(() => document.body.innerText.includes('个问题已回答') || document.body.innerText.includes('Questions Answered'), null, { timeout: 15000 });
  await page.waitForFunction(() => document.body.innerText.includes('已收到你的选择') || document.body.innerText.includes('已跳过这些问题'), null, { timeout: 15000 });
  await page.waitForTimeout(500);

  const screenshot = join(outputDir, 'custom-agent-chat-ask-user-question.png');
  await page.screenshot({ path: screenshot, fullPage: false });

  const answered = await page.evaluate(() => {
    const text = document.body.innerText;
    const answerMatches = text.match(/赛程和开幕时间/g) || [];
    const thinkingHeaders = [...document.querySelectorAll('.bps-thinking .bps-collapsible-header')];
    const toolHeaders = [...document.querySelectorAll('.bps-tool-list .bps-collapsible-header')];
    return {
      hasFloatingCard: Boolean(document.querySelector('[data-testid="bps-floating-question-card"]')),
      hasAnswerSummary: text.includes('个问题已回答') || text.includes('Questions Answered'),
      hasLegacyAnswerSummary: text.includes('Question:') || text.includes('Answer:') || text.includes('问题：') || text.includes('回答：'),
      hasAssistantContinuation: text.includes('已收到你的选择') || text.includes('已跳过这些问题'),
      answerMentionCount: answerMatches.length,
      thinkingCollapsed: thinkingHeaders.length > 0 && thinkingHeaders.every((header) => header.getAttribute('aria-expanded') === 'false'),
      toolCollapsed: toolHeaders.length > 0 && toolHeaders.every((header) => header.getAttribute('aria-expanded') === 'false'),
      hasSendButton: Boolean(document.querySelector('.bps-composer-button[aria-label="发送"]')),
      hasStopButton: Boolean(document.querySelector('.bps-composer-button[aria-label="停止"]')),
      activeSessionText: document.querySelector('.bps-session-item.is-active')?.textContent || '',
      startupCount: document.querySelectorAll('.bps-startup').length,
    };
  });
  assertCheck(!answered.hasFloatingCard, 'ask-user-question: floating card remained after answer');
  assertCheck(answered.hasAnswerSummary, 'ask-user-question: answer summary was not rendered');
  assertCheck(!answered.hasLegacyAnswerSummary, 'ask-user-question: legacy Question/Answer summary is visible');
  assertCheck(answered.answerMentionCount === 1, `ask-user-question: answer was rendered ${answered.answerMentionCount} times`);
  assertCheck(answered.thinkingCollapsed, 'ask-user-question: thinking section did not collapse after completion');
  assertCheck(answered.toolCollapsed, 'ask-user-question: tool section did not collapse after completion');
  assertCheck(answered.hasSendButton, 'ask-user-question: composer did not return to send state');
  assertCheck(!answered.hasStopButton, 'ask-user-question: composer still shows stop state after completion');
  assertCheck(!answered.activeSessionText.includes('运行中'), 'ask-user-question: active session still shows running after completion');
  assertCheck(answered.hasAssistantContinuation, 'ask-user-question: assistant did not continue after answer');
  assertCheck(answered.startupCount === 1, `ask-user-question: expected one startup block, saw ${answered.startupCount}`);
  assertCheck(answerRequestCount === 1, `ask-user-question: expected one answer request, saw ${answerRequestCount}`);

  await page.waitForTimeout(2000);
  const settled = await page.evaluate(() => {
    const text = document.body.innerText;
    return {
      hasFloatingCard: Boolean(document.querySelector('[data-testid="bps-floating-question-card"]')),
      hasSendButton: Boolean(document.querySelector('.bps-composer-button[aria-label="发送"]')),
      hasStopButton: Boolean(document.querySelector('.bps-composer-button[aria-label="停止"]')),
      activeSessionText: document.querySelector('.bps-session-item.is-active')?.textContent || '',
      hasAnswerSummary: text.includes('个问题已回答') || text.includes('Questions Answered'),
    };
  });
  assertCheck(!settled.hasFloatingCard, 'ask-user-question: floating card returned after settle');
  assertCheck(settled.hasSendButton, 'ask-user-question: composer did not stay in send state after settle');
  assertCheck(!settled.hasStopButton, 'ask-user-question: stale running state restored the stop button after settle');
  assertCheck(!settled.activeSessionText.includes('运行中'), 'ask-user-question: active session returned to running after settle');
  assertCheck(settled.hasAnswerSummary, 'ask-user-question: answer summary disappeared after settle');

  await page.close();
  return { ...waiting, screenshot, waitingScreenshot, answerRequestCount };
}

const browser = await chromium.launch({
  headless: true,
  executablePath: chromePath,
  args: ['--no-sandbox'],
});

try {
  const desktop = await verifyPage(browser, 'desktop', { width: 1280, height: 900 }, true);
  const mobile = await verifyPage(browser, 'mobile', { width: 390, height: 844 }, false);
  const askUserQuestion = await verifyAskUserQuestion(browser);
  console.log(JSON.stringify({
    ok: true,
    url,
    screenshots: [desktop.screenshot, mobile.screenshot, askUserQuestion.waitingScreenshot, askUserQuestion.screenshot],
    checks: {
      desktop: {
        initialVisualState: desktop.initialVisualState,
        sessionCount: desktop.sessionCount,
        hasActiveSession: desktop.hasActiveSession,
        hasAgentReady: desktop.hasAgentReady,
        assistant: desktop.assistant,
        userBubble: desktop.userBubble,
        transcript: desktop.transcript,
        composer: desktop.composer,
        sidebar: desktop.sidebar,
      },
      mobile: {
        initialVisualState: mobile.initialVisualState,
        hasAgentReady: mobile.hasAgentReady,
        assistant: mobile.assistant,
        userBubble: mobile.userBubble,
        transcript: mobile.transcript,
        composer: mobile.composer,
        sidebar: mobile.sidebar,
      },
      askUserQuestion: {
        hasFloatingCard: askUserQuestion.hasFloatingCard,
        hasQuestionHeader: askUserQuestion.hasQuestionHeader,
        hasToolGroup: askUserQuestion.hasToolGroup,
        hasExpandedToolGroup: askUserQuestion.hasExpandedToolGroup,
        hasExpandedThinking: askUserQuestion.hasExpandedThinking,
        thinkingTitle: askUserQuestion.thinkingTitle,
        answerRequestCount: askUserQuestion.answerRequestCount,
        waitingScreenshot: askUserQuestion.waitingScreenshot,
        answeredScreenshot: askUserQuestion.screenshot,
        cardRect: askUserQuestion.cardRect,
        composerRect: askUserQuestion.composerRect,
      },
    },
  }, null, 2));
} finally {
  await browser.close();
}
