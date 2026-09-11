'use strict';
const fs = require('node:fs');
const path = require('node:path');

// Only reviewed marketing files enter the static artifact. No recursive copy.
function build(root, checkOnly = false) {
  root = fs.realpathSync(root);
  const files = JSON.parse(fs.readFileSync(path.join(root, 'deploy/public-files.json'), 'utf8'));
  if (!Array.isArray(files) || !files.length || new Set(files).size !== files.length) {
    throw new Error('Invalid public file manifest');
  }
  function checked(relative) {
    let current = root;
    for (const part of relative.split('/')) {
      current = path.join(current, part);
      if (fs.existsSync(current) && fs.lstatSync(current).isSymbolicLink()) {
        throw new Error('Symlinks are not allowed in the public build');
      }
    }
    return current;
  }
  const snapshots = files.map(relative => {
    if (typeof relative !== 'string' || !/^(?:[a-z0-9-]+\.html|robots\.txt|sitemap\.xml|assets\/[A-Za-z0-9_/-]+\.(?:jpg|png|svg))$/.test(relative)) {
      throw new Error('Private or unsafe path in public manifest');
    }
    const source = checked(relative);
    if (!fs.statSync(source).isFile()) throw new Error('Public source must be a regular file');
    const data = fs.readFileSync(source);
    if (/\.(?:html|svg|xml|txt)$/.test(relative)) {
      const text = data.toString('utf8');
      if (/https?:\/\/[^\s"'<>]*\.invalid\b/i.test(text)) throw new Error('Placeholder URL in public source: ' + relative);
      if (/sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{30,}/.test(text)) throw new Error('Possible credential in public source');
    }
    return {relative, data};
  });
  const destination = checked('dist');
  const allowed = new Set(files);
  function inspectExisting(directory, prefix = '') {
    for (const entry of fs.readdirSync(directory, {withFileTypes:true})) {
      const name = prefix + entry.name;
      if (entry.isSymbolicLink()) throw new Error('Symlink in existing output');
      if (entry.isDirectory()) inspectExisting(path.join(directory, entry.name), name + '/');
      else if (!entry.isFile() || !allowed.has(name)) throw new Error('Unexpected file in existing output; inspect it before rebuilding');
    }
  }
  if (fs.existsSync(destination)) inspectExisting(destination);
  if (!checkOnly) {
    for (const {relative, data} of snapshots) {
      const target = checked('dist/' + relative);
      fs.mkdirSync(path.dirname(target), {recursive:true});
      fs.writeFileSync(target, data);
    }
  }
  return {mode:checkOnly ? 'check' : 'build', output:'dist', files};
}

module.exports = {build};
if (require.main === module) {
  try {
    if (process.argv.slice(2).some(arg => arg !== '--check')) throw new Error('Only --check is supported');
    const result = build(path.resolve(__dirname, '..'), process.argv.includes('--check'));
    console.log(JSON.stringify(result));
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
