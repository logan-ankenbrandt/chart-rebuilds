// Validate portfolio.json with the hub's own zod contract, and check every referenced file exists.
// Usage: node src/validate_portfolio.mjs [path/to/hub/lib/contract.mjs]   (default: the sibling hub repo)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const contractPath = path.resolve(process.argv[2] || path.join(root, '..', 'portfolio', 'lib', 'contract.mjs'));
if (!fs.existsSync(contractPath)) {
  console.error(`hub contract not found at ${contractPath}`);
  process.exit(2);
}
const { portfolioSchema, referencedPaths, formatIssues } = await import(pathToFileURL(contractPath).href);
const data = JSON.parse(fs.readFileSync(path.join(root, 'portfolio.json'), 'utf8'));
const parsed = portfolioSchema.safeParse(data);
if (!parsed.success) {
  console.error(formatIssues(parsed.error.issues).join('\n'));
  process.exit(1);
}
const refs = referencedPaths(parsed.data);
const missing = refs.filter((r) => !fs.existsSync(path.join(root, r.path)));
for (const r of missing) console.error(`missing ${r.role}: ${r.path}`);
const wrongBytes = parsed.data.downloads.filter((d) => fs.statSync(path.join(root, d.path)).size !== d.bytes);
for (const d of wrongBytes) console.error(`stale byte count for ${d.path}`);
console.log(`portfolio.json matches the hub contract; ${refs.length} referenced paths, ${missing.length} missing, ${wrongBytes.length} stale sizes`);
process.exit(missing.length || wrongBytes.length ? 1 : 0);
