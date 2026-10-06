// Dependency-free unit tests for src/lib/pinterest.js. Run: node pinterest.test.mjs
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { buildSearchUrl, PINTEREST_SEARCH_BASE } from "./pinterest.js";

let passed = 0;
const failures = [];
const test = (name, fn) => {
  try {
    fn();
    passed += 1;
  } catch (err) {
    failures.push(`${name}\n    ${err.message.split("\n")[0]}`);
  }
};

/* ---------- buildSearchUrl ---------- */

test("search url wraps the garment, colour and 'women outfit'", () => {
  assert.equal(
    buildSearchUrl("wrap top", "terracotta"),
    `${PINTEREST_SEARCH_BASE}?q=${encodeURIComponent("wrap top terracotta women outfit")}`,
  );
});

test("search url percent-encodes spaces as %20", () => {
  assert.equal(
    buildSearchUrl("wrap top", "terracotta"),
    "https://www.pinterest.com/search/pins/?q=wrap%20top%20terracotta%20women%20outfit",
  );
});

test("search url encodes characters that would break the query", () => {
  const url = buildSearchUrl("maxi dress", "deep teal & navy");
  assert.ok(!url.includes(" "), "no raw spaces");
  assert.ok(url.includes("%26"), "ampersand is encoded");
});

test("search url targets the pins search path", () => {
  assert.ok(buildSearchUrl("jeans", "indigo").startsWith(PINTEREST_SEARCH_BASE));
});

test("search url tolerates a missing colour", () => {
  assert.equal(
    buildSearchUrl("jeans", undefined),
    "https://www.pinterest.com/search/pins/?q=jeans%20women%20outfit",
  );
});

test("search url changes when the colour changes", () => {
  assert.notEqual(buildSearchUrl("wrap top", "terracotta"), buildSearchUrl("wrap top", "navy"));
});

test("search url keeps the user's colour capitalisation", () => {
  assert.ok(buildSearchUrl("wrap top", "Terracotta").includes("q=wrap%20top%20Terracotta%20women%20outfit"));
});

/* ---------- no Pinterest is ever requested ---------- */

test("the module makes no request to Pinterest", () => {
  const source = readFileSync(new URL("./pinterest.js", import.meta.url), "utf8");
  assert.ok(!source.includes("fetch("), "no fetch");
  assert.ok(!source.includes("XMLHttpRequest"), "no XHR");
  assert.ok(!source.includes("pinit.js"), "no embed script");
  assert.ok(!source.includes("pinimg"), "no image host");
});

/* ---------- report ---------- */

if (failures.length) {
  console.error(`FAILED ${failures.length} of ${passed + failures.length}\n`);
  failures.forEach((f) => console.error(`  - ${f}\n`));
  process.exit(1);
}
console.log(`All ${passed} pinterest helper tests passed.`);
