// Validates Mermaid blocks with the official parser (`mermaid` package) without
// Chromium, using jsdom as the DOM. Same parser GitHub and GitLab render with.
// usage: MERMAID_MODULES=<node_modules> node mermaid-parse.mjs a.mmd b.mmd ...
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { basename, dirname, join } from 'node:path';
import { pathToFileURL } from 'node:url';

const req = createRequire(join(process.env.MERMAID_MODULES, 'noop.js'));
const { JSDOM } = req('jsdom');
const dom = new JSDOM('<!doctype html><body></body>');
globalThis.window = dom.window;
globalThis.document = dom.window.document;

const pkgPath = req.resolve('mermaid/package.json');
const entry = req(pkgPath).exports['.'].import;
const mermaid = (await import(pathToFileURL(join(dirname(pkgPath), entry)))).default;
mermaid.initialize({ startOnLoad: false });

let failed = false;
for (const file of process.argv.slice(2)) {
  try {
    await mermaid.parse(readFileSync(file, 'utf8'));
    console.log(`OK    Mermaid ${basename(file)} valid`);
  } catch (e) {
    failed = true;
    console.log(`ERROR Mermaid ${basename(file)} invalid: ${String(e.message).split('\n')[0].slice(0, 160)}`);
  }
}
process.exit(failed ? 1 : 0);
