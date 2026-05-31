const https = require('https');
const http = require('http');

// ── CONFIG ──────────────────────────────────────────────
const BOT_TOKEN = '8754473230:AAEF0yKKLMtLZLrd53k-xVy9PlackW15v_A';
const MANAGER_CHAT_ID = '8131102104';
const PORT = process.env.PORT || 3000;
// ────────────────────────────────────────────────────────

function sendTelegramMessage(text) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      chat_id: MANAGER_CHAT_ID,
      text: text,
      parse_mode: 'HTML'
    });
    const options = {
      hostname: 'api.telegram.org',
      path: `/bot${BOT_TOKEN}/sendMessage`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body)
      }
    };
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

const server = http.createServer(async (req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  if (req.method === 'POST' && req.url === '/api/order') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', async () => {
      try {
        const order = JSON.parse(body);
        const now = new Date().toLocaleString('ru-RU', {
          timeZone: 'Asia/Tashkent',
          day: '2-digit', month: '2-digit', year: 'numeric',
          hour: '2-digit', minute: '2-digit'
        });

        const message = `
📋 <b>Новая заявка с сайта!</b>

👤 <b>Имя:</b> ${order.name || '—'}
📱 <b>Телефон:</b> ${order.phone || '—'}
💬 <b>Telegram/Instagram:</b> ${order.telegram || '—'}
📚 <b>Тематика:</b> ${order.theme || '—'}
🖼 <b>Количество фото:</b> ${order.photosCount || '—'}
💬 <b>Пожелания:</b> ${order.comment || 'не указаны'}
⏰ <b>Время заявки:</b> ${now}

<i>Ответьте клиенту как можно скорее! 🚀</i>
        `.trim();

        await sendTelegramMessage(message);

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: true }));
      } catch (err) {
        console.error('Error:', err);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: false, error: err.message }));
      }
    });
    return;
  }

  // Health check
  if (req.method === 'GET' && req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'Flashbook bot server running ✅' }));
    return;
  }

  res.writeHead(404);
  res.end();
});

server.listen(PORT, () => {
  console.log(`✅ Flashbook bot server running on port ${PORT}`);
});
