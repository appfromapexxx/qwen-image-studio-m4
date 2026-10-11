// Run with node --test tests/test_ui_turbo8.js. No browser, service or GPU required.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname, '../studio/index.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const functions = script.split('// ---------- events ----------')[0];
// Execute the actual size/reference event handlers as well as the production functions.
const events = script.split('\n').filter(line => /^\$\("#(?:bases|refMax)"\)\.onclick =/.test(line)).join('\n');
assert.equal(events.split('\n').length, 2, 'size/reference handlers must be found');
const lockedIds = ['steps', 'cfg', 'imgCfg', 'negative', 'fast', 'fastThreshold', 'sampler', 'scheduler', 'shift'];

function harness() {
  const nodes = new Map(), requests = [];
  function element() {
    const classes = new Set();
    return {
      value: '', checked: false, disabled: false, textContent: '', options: [], dataset: {},
      classList: {
        add: value => classes.add(value), remove: value => classes.delete(value),
        contains: value => classes.has(value),
        toggle(value, on) { on ??= !classes.has(value); on ? classes.add(value) : classes.delete(value); },
      },
      closest() { return this; }, querySelectorAll: () => [],
    };
  }
  function node(selector) {
    if (!nodes.has(selector)) nodes.set(selector, element());
    return nodes.get(selector);
  }
  function buttons(id, attribute) {
    const section = html.match(new RegExp(`<div class="seg" id="${id}">([\\s\\S]*?)</div>`))[1];
    return [...section.matchAll(new RegExp(`<button[^>]*data-${attribute}="([^"]+)"`, 'g'))].map(match => {
      const button = element(); button.dataset[attribute] = match[1]; return button;
    });
  }
  const groups = {
    '#presets button': buttons('presets', 'p'), '#bases button': buttons('bases', 'b'),
    '#refMax button': buttons('refMax', 'v'), '.turbo-lock': [element()],
  };
  groups['.turbo-lock'][0].querySelectorAll = () => lockedIds.map(id => node('#' + id));
  Object.entries({ batch: 1, seed: -1, cfg: 6, fastThreshold: 0.2, cw: 1024, ch: 1024 }).forEach(([id, value]) => {
    node('#' + id).value = String(value);
  });
  const context = vm.createContext({
    document: { querySelector: node, querySelectorAll: selector => groups[selector] || [] },
    setTimeout: () => 0, clearTimeout() {},
    fetch: async (url, options) => {
      requests.push({ url, body: JSON.parse(options.body) });
      return { ok: true, json: async () => ({ ids: ['test-job'] }) };
    },
  });
  // Gallery drawing, lightbox and polling are outside these control/request boundary tests.
  vm.runInContext(functions + '\nrenderFav = renderRefs = closeLb = poll = () => {};\n' + events +
    '\nglobalThis.ui = { S, applyPreset, update, snapshot, restore, reuse, submit };', context);
  const ui = context.ui;
  ui.S.turbo8Ok = true;
  return { ui, node, requests, click: (id, value) => {
    const attribute = id === 'bases' ? 'b' : 'v';
    const button = groups['#' + id + ' button'].find(b => b.dataset[attribute] === String(value));
    assert.ok(button, `missing ${id} button ${value}`);
    node('#' + id).onclick({ target: button });
  } };
}

function assertTurbo8({ ui, node }) {
  assert.equal(ui.S.turbo8, true);
  assert.equal(ui.S.preset, 'turbo8');
  assert.equal(Number(node('#steps').value), 8);
  assert.equal(Number(node('#cfg').value), 1);
  assert.equal(node('#sampler').value, 'euler');
  assert.equal(node('#turbo').checked, false);
  lockedIds.forEach(id => assert.equal(node('#' + id).disabled, true, `${id} must be locked`));
  assert.ok(node('#turboRow').classList.contains('hidden'));
  assert.ok(node('#schedRow').classList.contains('hidden'));
}

test('Turbo 8 keeps its model identity through output and reference size changes', () => {
  const h = harness();
  h.ui.applyPreset('turbo8');
  assertTurbo8(h);
  h.click('bases', 512);
  h.click('refMax', 768);
  assert.equal(h.ui.S.base, 512);
  assert.equal(h.ui.S.refMax, 768);
  assertTurbo8(h);
  h.click('bases', 'custom');
  assert.equal(h.ui.S.base, 'custom');
  assertTurbo8(h);
});

test('saved settings restore Turbo 8 and selecting an existing preset clears it', () => {
  const h = harness();
  h.ui.applyPreset('turbo8');
  h.click('bases', 512);
  const saved = h.ui.snapshot();
  assert.equal(saved.preset, 'turbo8');
  for (const preset of ['turbo', 'draft', 'balanced', 'quality']) {
    h.ui.applyPreset(preset);
    assert.equal(h.ui.S.turbo8, false);
    assert.equal(h.ui.snapshot().preset, null);
    assert.equal(h.node('#turbo').checked, preset === 'turbo');
    assert.equal(h.node('#steps').disabled, preset === 'turbo');
    h.ui.restore(saved);
    assert.equal(h.ui.S.base, 512);
    assertTurbo8(h);
  }
});

test('gallery reuse restores Turbo 8 and legacy Turbo identity independently', () => {
  const h = harness();
  h.ui.reuse({ meta: { mode: 'edit', prompt: 'red hat', preset: 'turbo8',
    width: 512, height: 768, seed: 42, refs: ['reference.png'], steps: 8, cfg: 1 } });
  assertTurbo8(h);
  assert.equal(h.ui.S.base, 'custom');
  assert.equal(h.ui.S.refs[0].name, 'reference.png');
  h.ui.reuse({ meta: { mode: 'gen', prompt: 'teapot', turbo: true,
    width: 768, height: 768, seed: 7, steps: 4, cfg: 1 } }, true);
  assert.equal(h.ui.S.turbo8, false);
  assert.equal(h.node('#turbo').checked, true);
  assert.equal(h.ui.S.turboSched, 'trained');
  assert.equal(Number(h.node('#seed').value), -1);
});

test('submission enforces Turbo 8 despite stale controls and retains edit inputs', async () => {
  const h = harness();
  h.ui.applyPreset('turbo8');
  h.ui.S.refs = [{ name: 'reference.png', width: 768, height: 768 }];
  h.ui.S.mask = { name: 'mask.png' };
  Object.entries({ prompt: 'red hat', steps: 42, cfg: 9, imgCfg: 7, negative: 'blur',
    sampler: 'heun', scheduler: 'karras', shift: 3 }).forEach(([id, value]) => h.node('#' + id).value = String(value));
  h.node('#fast').checked = h.node('#turbo').checked = true;
  await h.ui.submit();
  assert.equal(h.requests.length, 1);
  const { url, body } = h.requests[0];
  assert.equal(url, '/api/jobs');
  assert.deepEqual(Object.fromEntries(['preset', 'steps', 'cfg', 'sampler', 'turbo', 'fast',
    'img_cfg', 'negative', 'scheduler', 'flow_shift'].map(key => [key, body[key]])), {
    preset: 'turbo8', steps: 8, cfg: 1, sampler: 'euler', turbo: false, fast: false,
    img_cfg: null, negative: '', scheduler: 'default', flow_shift: null,
  });
  assert.deepEqual(body.refs, ['reference.png']);
  assert.equal(body.mask, 'mask.png');
  h.ui.S.turbo8Ok = false;
  await h.ui.submit();
  assert.equal(h.requests.length, 1, 'missing model must prevent submission');
  assert.match(h.node('#formErr').textContent, /Turbo 8-step model is missing/);
});
