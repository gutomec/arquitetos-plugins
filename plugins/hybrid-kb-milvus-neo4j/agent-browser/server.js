/**
 * Agent Browser Jurisprudence Search API
 * Wrapper for agent-browser CLI with specialized legal database searches
 */

const express = require('express');
const { exec, spawn } = require('child_process');
const util = require('util');
const cors = require('cors');

const execPromise = util.promisify(exec);
const app = express();

app.use(cors());
app.use(express.json());

// Court URLs for jurisprudence search
const COURTS = {
  stf: {
    name: 'Supremo Tribunal Federal',
    searchUrl: 'https://jurisprudencia.stf.jus.br/pages/search',
    inputSelector: '#searchTerms',
    submitSelector: 'button[type="submit"]'
  },
  stj: {
    name: 'Superior Tribunal de Justica',
    searchUrl: 'https://processo.stj.jus.br/jurisprudencia/',
    inputSelector: '#pesquisaLivre',
    submitSelector: '#pesquisar'
  },
  tst: {
    name: 'Tribunal Superior do Trabalho',
    searchUrl: 'https://jurisprudencia.tst.jus.br/',
    inputSelector: '#txtBuscaFacetada',
    submitSelector: '#btnBuscarFacetada'
  },
  trt4: {
    name: 'TRT 4a Regiao (RS)',
    searchUrl: 'https://www.trt4.jus.br/portais/trt4/jurisprudencia',
    inputSelector: '#pesquisa',
    submitSelector: '.btn-buscar'
  },
  tjsp: {
    name: 'Tribunal de Justica de Sao Paulo',
    searchUrl: 'https://esaj.tjsp.jus.br/cjsg/consultaCompleta.do',
    inputSelector: '#dados.buscaInteiroTeor',
    submitSelector: '#pbSubmit'
  },
  jusbrasil: {
    name: 'JusBrasil',
    searchUrl: 'https://www.jusbrasil.com.br/jurisprudencia/busca',
    inputSelector: 'input[name="q"]',
    submitSelector: 'button[type="submit"]'
  }
};

// Execute agent-browser command
async function agentBrowser(cmd, args = []) {
  const fullCmd = `agent-browser ${cmd} ${args.join(' ')}`;
  console.log(`[agent-browser] Executing: ${fullCmd}`);

  try {
    const { stdout, stderr } = await execPromise(fullCmd, {
      timeout: 60000,
      maxBuffer: 10 * 1024 * 1024
    });
    if (stderr) console.warn(`[agent-browser] stderr: ${stderr}`);
    return { success: true, output: stdout.trim() };
  } catch (error) {
    console.error(`[agent-browser] Error: ${error.message}`);
    return { success: false, error: error.message };
  }
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'agent-browser-jurisprudence' });
});

// List available courts
app.get('/courts', (req, res) => {
  const courts = Object.entries(COURTS).map(([id, court]) => ({
    id,
    name: court.name,
    searchUrl: court.searchUrl
  }));
  res.json({ courts });
});

// Open browser and navigate
app.post('/open', async (req, res) => {
  const { url } = req.body;
  if (!url) return res.status(400).json({ error: 'URL required' });

  const result = await agentBrowser('open', [url]);
  res.json(result);
});

// Get page snapshot
app.get('/snapshot', async (req, res) => {
  const interactive = req.query.interactive === 'true';
  const result = await agentBrowser('snapshot', interactive ? ['-i'] : []);
  res.json(result);
});

// Click element
app.post('/click', async (req, res) => {
  const { ref } = req.body;
  if (!ref) return res.status(400).json({ error: 'Element ref required' });

  const result = await agentBrowser('click', [ref]);
  res.json(result);
});

// Fill form field
app.post('/fill', async (req, res) => {
  const { ref, value } = req.body;
  if (!ref || !value) return res.status(400).json({ error: 'ref and value required' });

  const result = await agentBrowser('fill', [ref, `"${value}"`]);
  res.json(result);
});

// Press key
app.post('/press', async (req, res) => {
  const { key } = req.body;
  if (!key) return res.status(400).json({ error: 'Key required' });

  const result = await agentBrowser('press', [key]);
  res.json(result);
});

// Take screenshot
app.get('/screenshot', async (req, res) => {
  const path = req.query.path || '/tmp/screenshot.png';
  const full = req.query.full === 'true';

  const args = [path];
  if (full) args.push('--full');

  const result = await agentBrowser('screenshot', args);
  res.json(result);
});

// Wait for element/text
app.post('/wait', async (req, res) => {
  const { text, timeout } = req.body;
  if (!text) return res.status(400).json({ error: 'Text to wait for required' });

  const args = ['--text', `"${text}"`];
  if (timeout) args.push('--timeout', timeout);

  const result = await agentBrowser('wait', args);
  res.json(result);
});

// Close browser
app.post('/close', async (req, res) => {
  const result = await agentBrowser('close', []);
  res.json(result);
});

// Execute raw command
app.post('/exec', async (req, res) => {
  const { command, args } = req.body;
  if (!command) return res.status(400).json({ error: 'Command required' });

  const result = await agentBrowser(command, args || []);
  res.json(result);
});

// ============================================================================
// JURISPRUDENCE SEARCH ENDPOINTS
// ============================================================================

// Search jurisprudence in specific court
app.post('/search/:court', async (req, res) => {
  const { court } = req.params;
  const { query, perspective } = req.body;

  if (!query) return res.status(400).json({ error: 'Query required' });

  const courtConfig = COURTS[court];
  if (!courtConfig) {
    return res.status(400).json({
      error: `Unknown court: ${court}`,
      availableCourts: Object.keys(COURTS)
    });
  }

  console.log(`[search] Court: ${court}, Query: "${query}", Perspective: ${perspective || 'neutral'}`);

  try {
    // Step 1: Open court search page
    await agentBrowser('open', [courtConfig.searchUrl]);
    await new Promise(r => setTimeout(r, 3000)); // Wait for page load

    // Step 2: Get snapshot with interactive elements
    const snapshot = await agentBrowser('snapshot', ['-i']);

    // Step 3: Take screenshot for debugging
    await agentBrowser('screenshot', [`/tmp/${court}_before.png`]);

    // Return snapshot for Claude to process
    res.json({
      success: true,
      court: courtConfig.name,
      courtId: court,
      searchUrl: courtConfig.searchUrl,
      query,
      perspective: perspective || 'neutral',
      snapshot: snapshot.output,
      instructions: {
        inputSelector: courtConfig.inputSelector,
        submitSelector: courtConfig.submitSelector,
        nextSteps: [
          'Use /fill to enter search query in input field',
          'Use /click to submit the search form',
          'Use /snapshot to get search results',
          'Use /screenshot to capture results'
        ]
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      court: courtConfig.name
    });
  }
});

// Multi-court search (sequential)
app.post('/search/multi', async (req, res) => {
  const { query, courts = ['stf', 'stj', 'tst'], perspective } = req.body;

  if (!query) return res.status(400).json({ error: 'Query required' });

  const results = [];

  for (const court of courts) {
    const courtConfig = COURTS[court];
    if (!courtConfig) continue;

    console.log(`[multi-search] Searching ${court}: "${query}"`);

    try {
      // Open and snapshot
      await agentBrowser('open', [courtConfig.searchUrl]);
      await new Promise(r => setTimeout(r, 2000));

      const snapshot = await agentBrowser('snapshot', ['-i']);
      await agentBrowser('screenshot', [`/tmp/${court}_search.png`]);

      results.push({
        court,
        name: courtConfig.name,
        success: true,
        snapshot: snapshot.output,
        screenshot: `/tmp/${court}_search.png`
      });
    } catch (error) {
      results.push({
        court,
        name: courtConfig.name,
        success: false,
        error: error.message
      });
    }
  }

  // Close browser
  await agentBrowser('close', []);

  res.json({
    query,
    perspective: perspective || 'neutral',
    courtsSearched: courts.length,
    results
  });
});

// Get element text/content
app.post('/get', async (req, res) => {
  const { type, ref } = req.body;
  if (!type || !ref) return res.status(400).json({ error: 'type and ref required' });

  const result = await agentBrowser('get', [type, ref]);
  res.json(result);
});

// Scroll page
app.post('/scroll', async (req, res) => {
  const { direction = 'down', amount = 300 } = req.body;
  const result = await agentBrowser('scroll', [direction, amount.toString()]);
  res.json(result);
});

// ============================================================================
// START SERVER
// ============================================================================

const PORT = process.env.PORT || 3100;

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Agent Browser Jurisprudence API running on port ${PORT}`);
  console.log(`Available courts: ${Object.keys(COURTS).join(', ')}`);
});
