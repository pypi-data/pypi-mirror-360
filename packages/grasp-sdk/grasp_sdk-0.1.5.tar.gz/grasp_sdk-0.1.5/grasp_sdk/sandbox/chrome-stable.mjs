import httpProxy from 'http-proxy';
import http from 'http';
import { spawn } from 'child_process';

import { Logtail } from '@logtail/node';
import * as Sentry from "@sentry/node";

const logtail = new Logtail(process.env.BS_SOURCE_TOKEN, {
  endpoint: `https://${process.env.BS_INGESTING_HOST}`,
});

Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Setting this option to true will send default PII data to Sentry.
  // For example, automatic IP address collection on events
  sendDefaultPii: true,
  _experiments: {
    enableLogs: true, // 启用日志功能
  },
});

const logger = {
  info: async (message, context) => {
    Sentry.logger.info(message, context);
    return logtail.info(message, context);
  },
  warn: async (message, context) => {
    Sentry.logger.warn(message, context);
    return logtail.warn(message, context);
  },
  error: async (message, context) => {
    Sentry.logger.error(message, context);
    return logtail.error(message, context);
  },
}

function parseWebSocketFrame(buffer) {
  if (buffer.length < 2) {
    throw new Error('Incomplete WebSocket frame.');
  }

  const firstByte = buffer.readUInt8(0);
  const fin = (firstByte & 0x80) !== 0;
  const opcode = firstByte & 0x0f;

  // 仅处理文本帧（opcode 为 0x1）
  if (opcode !== 0x1) {
    throw new Error(`Unsupported opcode: ${opcode}`);
  }

  const secondByte = buffer.readUInt8(1);
  const isMasked = (secondByte & 0x80) !== 0;
  let payloadLength = secondByte & 0x7f;
  let offset = 2;

  if (payloadLength === 126) {
    if (buffer.length < offset + 2) {
      throw new Error('Incomplete extended payload length.');
    }
    payloadLength = buffer.readUInt16BE(offset);
    offset += 2;
  } else if (payloadLength === 127) {
    if (buffer.length < offset + 8) {
      throw new Error('Incomplete extended payload length.');
    }
    // 注意：JavaScript 无法精确表示超过 2^53 的整数
    const highBits = buffer.readUInt32BE(offset);
    const lowBits = buffer.readUInt32BE(offset + 4);
    payloadLength = highBits * 2 ** 32 + lowBits;
    offset += 8;
  }

  let maskingKey;
  if (isMasked) {
    if (buffer.length < offset + 4) {
      throw new Error('Incomplete masking key.');
    }
    maskingKey = buffer.slice(offset, offset + 4);
    offset += 4;
  }

  if (buffer.length < offset + payloadLength) {
    throw new Error('Incomplete payload data.');
  }

  const payloadData = buffer.slice(offset, offset + payloadLength);

  if (isMasked) {
    for (let i = 0; i < payloadLength; i++) {
      payloadData[i] ^= maskingKey[i % 4];
    }
  }

  return payloadData.toString('utf8');
}

const sandboxId = process.env.SANDBOX_ID;
const cdpPort = Number(process.env.CDP_PORT);
const headless = process.env.HEADLESS !== 'false';
const enableAdblock = process.env.ADBLOCK !== 'false';
const timeoutMS = process.env.SANBOX_TIMEOUT;
const workspace = process.env.WORKSPACE;
const keepAliveMS = Number(process.env.KEEP_ALIVE_MS) || 0;
const args = [];

try {
  const asblockPlugin = '/home/user/.config/google-chrome/Default/Extensions/adblock';

  args.push(
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-software-rasterizer',
    '--user-data-dir=/home/user/.browser-context'
  );

  args.push(
    // 避免缓存积累影响性能
    '--disable-application-cache',

    // 关闭所有硬件加速特性，防止 GPU 相关崩溃
    '--disable-accelerated-2d-canvas',
    '--disable-accelerated-video-decode',

    // 禁用后台渲染，减少无关资源消耗
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',

    // 避免过度日志影响性能
    '--disable-logging',

    // 禁用不必要的多媒体解码
    '--mute-audio',

    // 避免崩溃时弹窗
    '--no-default-browser-check',
    '--no-first-run',
  );

  if(headless) {
    args.push('--headless=new');
  }

  if(enableAdblock) {
    args.push(...[
      `--disable-extensions-except=${asblockPlugin}`,
      `--load-extension=${asblockPlugin}`,
    ])
  }

  args.push(...[
    `--remote-debugging-port=${cdpPort}`,
    '--remote-debugging-address=0.0.0.0',
    ...JSON.parse(process.env.BROWSER_ARGS),
    'about:blank',
  ]);

  console.log(args);

  let chromePath = '/usr/bin/google-chrome';

  // 启动 Chrome 并启用远程调试
  const chrome = spawn(chromePath, args, {
    env: { ...process.env, DISPLAY: ':99' }
  });

  chrome.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
  });
  
  chrome.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });
  
  chrome.on('close', (code) => {
    console.log(`Chrome process exited with code ${code}`);
  });

  // Keep the process alive
  process.on('SIGTERM', async () => {
    console.log('Received SIGTERM, closing browser...');
    await logger.warn('Received SIGTERM signal', { sandboxId });
    Sentry.addBreadcrumb({
      category: 'process',
      message: 'Received SIGTERM signal',
      level: 'info',
      data: { sandboxId }
    });
    chrome.kill();
    process.exit(0);
  });

  process.on('SIGINT', async () => {
    console.log('Received SIGINT, closing browser...');
    await logger.warn('Received SIGINT signal', { sandboxId });
    Sentry.addBreadcrumb({
      category: 'process',
      message: 'Received SIGINT signal',
      level: 'info',
      data: { sandboxId }
    });
    chrome.kill();
    process.exit(0);
  });

  // 创建代理服务：从 ${this.config.cdpPort! + 1} 转发到 127.0.0.1:${this.config.cdpPort!}
  const proxy = httpProxy.createProxyServer({
    target: `http://127.0.0.1:${cdpPort}`,
    ws: true,               // Enable WebSocket support
    changeOrigin: true
  });

  let wsId = null;

  // Log WebSocket messages
  proxy.on('open', () => {
    console.log('🔌 CDP WebSocket connection established');
    wsId = Date.now();
    logger.info('CDP WebSocket connection established', { sandboxId, wsId });
    Sentry.addBreadcrumb({
      category: 'websocket',
      message: 'CDP connection established',
      level: 'info',
      data: { sandboxId }
    });

    const closeId = wsId;
    proxy.once('close', async (req, socket, head) => {
      console.log('🔒 CDP WebSocket connection closed');
      await logger.info('CDP WebSocket connection closed', { sandboxId });
      Sentry.addBreadcrumb({
        category: 'websocket',
        message: 'CDP connection closed',
        level: 'info',
        data: { sandboxId }
      });
      setTimeout(() => {
        if(wsId === closeId) {
          console.log('❌ Force closed...', wsId);
          process.exit(0);
        }
      }, keepAliveMS);
    });
  });

  proxy.on('proxyReqWs', (proxyReq, req, socket, options, head) => {
    console.log('📡 New CDP WebSocket connection request:', req.url);
    logger.info('New CDP WebSocket connection request', { url: req.url, sandboxId });
    Sentry.addBreadcrumb({
      category: 'websocket',
      message: 'New CDP connection request',
      level: 'info',
      data: { url: req.url, sandboxId }
    });
  });

  proxy.on('error', (err, req, res) => {
    console.error('❌ CDP WebSocket proxy error:', err);
    logger.error('CDP WebSocket proxy error', { error: err.message, url: req?.url, sandboxId });
    Sentry.captureException(err, {
      tags: { type: 'websocket_proxy_error', sandboxId },
      extra: { url: req?.url }
    });
  });
  
  const server = http.createServer(async (req, res) => {
    if (req.url === '/health') {
      res.end('ok');
      return;
    }
    if (req.url === '/json/version' || req.url === '/json/version/') {
      try {
        // 向本地 CDP 发请求，获取原始 JSON
        const jsonRes = await fetch(`http://127.0.0.1:${cdpPort}/json/version`);
        const data = await jsonRes.json();
        // 替换掉本地的 WebSocket 地址为代理暴露地址
        data.webSocketDebuggerUrl = data.webSocketDebuggerUrl.replace(
          `ws://127.0.0.1:${cdpPort}`,
          `wss://${req.headers.host}`
        );
        await logger.info('CDP version info requested', { url: req.url, response: data, sandboxId });
        Sentry.addBreadcrumb({
          category: 'http',
          message: 'CDP version info requested',
          level: 'info',
          data: { url: req.url, response: data, sandboxId }
        });
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(data));
      } catch(ex) {
        console.error('Failed to fetch CDP version:', ex.message);
        await logger.error('Failed to fetch CDP version', { error: ex.message, sandboxId });
        Sentry.captureException(ex, {
          tags: { type: 'cdp_version_error', sandboxId }
        });
        res.writeHead(500);
        res.end('Internal Server Error');
      }
    } else {
      proxy.web(req, res, {}, async (err) => {
        console.error('Proxy error:', err);
        await logger.error('HTTP proxy error', { error: err.message, url: req.url, sandboxId });
        Sentry.captureException(err, {
          tags: { type: 'proxy_error', sandboxId },
          extra: { url: req.url }
        });
        res.writeHead(502);
        res.end('Bad gateway');
      });
    }
  });

  server.on('upgrade', (req, socket, head) => {
    // 监听 WebSocket 数据
    let _buffers = [];
    socket.on('data', (data) => {
      let message = '';
      try {
        _buffers.push(data);
        // console.log(`💬 ${_buffers.length}`);
        message = parseWebSocketFrame(Buffer.concat(_buffers)); // 复制data不能破坏原始数据
        _buffers.length = 0;
        if (message.startsWith('{')){  // 只解析 JSON 消息
          const parsed = JSON.parse(message);
          console.log('📨 CDP WebSocket message:', parsed);
          logger.info('CDP WebSocket message received', {
            data: parsed,
            sandboxId: process.env.SANDBOX_ID,
          });
          Sentry.addBreadcrumb({
            category: 'websocket',
            message: 'CDP message received',
            level: 'debug',
            data: { ...parsed, sandboxId }
          });
        }
      } catch (err) {
        const msg = err.message;
        if(!msg.includes('Incomplete')) {
          // 记录解析错误
          console.warn('⚠️ Failed to parse CDP WebSocket message:', err.message, _buffers.length);
          _buffers.length = 0;
          Sentry.captureException(err, {
            tags: { type: 'websocket_error', sandboxId }
          });
          logger.warn('Failed to parse CDP WebSocket message', {
            error: err.message,
            data: message,
            sandboxId: process.env.SANDBOX_ID
          });
        }
      }
    });

    socket.on('error', (err) => {
      console.error('❌ CDP WebSocket error:', err);
      logger.error('CDP WebSocket error', { error: err.message, sandboxId });
      Sentry.captureException(err, {
        tags: { type: 'websocket_error', sandboxId }
      });
    });

    proxy.ws(req, socket, head);
  });

  server.listen(cdpPort + 1, '0.0.0.0', () => {
    console.log(`🎯 Proxy server listening on http://0.0.0.0:${cdpPort + 1} → http://127.0.0.1:${cdpPort}`);
    logger.info('Proxy server started', {
      port: cdpPort + 1,
      target: cdpPort,
      sandboxId,
      settings: {
        type: 'chromium',
        args,
        headless,
        enableAdblock,
        timeoutMS,
        workspace,
        sandboxId
      },
    });
    Sentry.addBreadcrumb({
      category: 'server',
      message: 'Proxy server started',
      level: 'info',
      data: { 
        port: cdpPort + 1,
        target: cdpPort,
        sandboxId,
        settings: {
          type: 'chrome-stable',
          args,
          headless,
          enableAdblock,
          timeoutMS,
          workspace,
          sandboxId
        },
      }
    });
  });
} catch(ex) {
  console.error('Failed to launch Browser:', ex);
  logger.error('Failed to launch Chrome', {
    error: ex.message,
    args,
    headless,
    cdpPort,
    enableAdblock,
    sandboxId
  });
  Sentry.captureException(ex, {
    tags: { type: 'launch_error', sandboxId },
    extra: { args, headless, cdpPort, enableAdblock }
  });
  process.exit(1);
}