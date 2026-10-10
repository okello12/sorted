// Loads the product modules exactly as the page gets them (the files listed in src/manifest.json, in order) into
// one plain context, and returns the Product object. No DOM, no page: the modules must not need one.
import fs from 'fs';
import vm from 'vm';
import path from 'path';
import { fileURLToPath } from 'url';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
export function load() {
  const man = JSON.parse(fs.readFileSync(path.join(root, 'src/manifest.json'), 'utf8'));
  const ctx = vm.createContext({});
  let code = man.files.map(f => fs.readFileSync(path.join(root, f.path), 'utf8')).join('\n');
  // The page runs them inside its own function, so their `var`s are not globals there. Do the same here and return.
  vm.runInContext('(function(){' + code + '\n;this.Product=Product})()', ctx);
  return ctx.Product;
}
export const results = { pass: 0, fails: [] };
export function ok(c, m) {
  if (c) results.pass++; else { results.fails.push(m); console.log('FAIL ' + m); }
}
export function eq(a, b, m) { const x = JSON.stringify(a), y = JSON.stringify(b); ok(x === y, m + ' (got ' + x + ', want ' + y + ')'); }
export function done(name) {
  console.log(name + ': ' + results.pass + ' passed, ' + results.fails.length + ' failed');
  console.log('ERRORS []');
  console.log('FAILS ' + JSON.stringify(results.fails));
  if (results.fails.length) process.exitCode = 1;
}
