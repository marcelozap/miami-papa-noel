"""Offline artifact checks; no Vercel account or deployment is invoked."""
import json
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


def run_build(root, check=False):
    return subprocess.run(['node', str(root / 'scripts/build_public_site.cjs'),
                           *(['--check'] if check else [])], cwd=root,
                          capture_output=True, text=True, timeout=30)


@pytest.fixture
def project(tmp_path):
    (tmp_path / 'scripts').mkdir()
    (tmp_path / 'deploy').mkdir()
    shutil.copyfile(ROOT / 'scripts/build_public_site.cjs', tmp_path / 'scripts/build_public_site.cjs')
    (tmp_path / 'deploy/public-files.json').write_text('["index.html"]')
    (tmp_path / 'index.html').write_text('<p>Public synthetic page</p>')
    return tmp_path


def test_actual_manifest_and_vercel_configuration():
    result = run_build(ROOT, check=True)
    assert result.returncode == 0, result.stderr
    files = json.loads(result.stdout)['files']
    assert {'index.html', 'book.html', 'robots.txt', 'sitemap.xml'} <= set(files)
    assert not any(p.startswith(('business/', 'docs/', 'tools/')) for p in files)
    config = json.loads((ROOT / 'vercel.json').read_text())
    assert config['outputDirectory'] == 'dist'
    assert config['buildCommand'] == 'node scripts/build_public_site.cjs'
    for page in ('index.html', 'book.html'):
        text = (ROOT / page).read_text(encoding='utf-8')
        assert '.invalid' not in text
        assert 'Chat with Mrs. Claus' not in text
        assert 'href="/checkout"' in text
        assert 'tel:+17869759557' in text


def test_selected_solo_portraits_are_public_and_accessible():
    expected = {
        'assets/santa-standing-holiday-portrait.jpg': (
            'photos.standing', '6cec0183843d65bee955f28ebc229af6b0aed044e13b678d353aad00743dacd3'),
        'assets/santa-seated-holiday-portrait.jpg': (
            'photos.seated', 'cc7c41c4315ea20008bbe210c8611e0c00d2992765d9e818695f1d52997c0883'),
    }
    manifest = json.loads((ROOT / 'deploy/public-files.json').read_text())
    assert set(expected) <= set(manifest)
    assert not any('WA0089' in path or 'WA0027' in path for path in manifest)
    page = (ROOT / 'index.html').read_text(encoding='utf-8')
    literal = re.search(
        r'const translations = (\{.*?\});\s*const whatsappMessages', page, re.S).group(1)
    parsed = subprocess.run(
        ['node', '-e', "const fs = require('node:fs'); const vm = require('node:vm');"
         "console.log(JSON.stringify(vm.runInNewContext('(' + fs.readFileSync(0, 'utf8') + ')', {}, {timeout:1000})));"],
        input=literal, capture_output=True, encoding='utf-8', check=True, timeout=5)
    translations = json.loads(parsed.stdout)

    class Images(HTMLParser):
        def __init__(self):
            super().__init__()
            self.images = {}

        def handle_starttag(self, tag, attrs):
            if tag == 'img':
                attrs = dict(attrs)
                if attrs.get('src') in expected:
                    self.images[attrs['src']] = attrs

    parser = Images()
    parser.feed(page)
    assert set(parser.images) == set(expected)
    for path, (key, digest) in expected.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
        attrs = parser.images[path]
        assert (attrs['width'], attrs['height']) == ('1600', '1200')
        assert attrs['data-i18n-alt'] == key
        assert attrs['alt'] == translations['en'][key]
        assert translations['es'][key] != translations['en'][key]
    assert parser.images['assets/santa-standing-holiday-portrait.jpg']['fetchpriority'] == 'high'
    assert parser.images['assets/santa-seated-holiday-portrait.jpg']['loading'] == 'lazy'


class CustomerPage(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.elements = []
        self.details = []
        self.in_form = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form':
            self.in_form = True
        if tag == 'details':
            self.details.append(attrs.get('id', attrs.get('class')))
        self.elements.append((tag, attrs, self.in_form, tuple(self.details)))

    def handle_endtag(self, tag):
        if tag == 'form':
            self.in_form = False
        if tag == 'details':
            self.details.pop()


def test_simplified_request_keeps_routing_and_required_fields():
    page = CustomerPage((ROOT / 'book.html').read_text(encoding='utf-8'))
    forms = [attrs for tag, attrs, _, _ in page.elements if tag == 'form']
    assert len(forms) == 1
    assert forms[0]['action'] == 'https://formsubmit.co/santa@miamipapanoel.com'
    assert forms[0]['method'] == 'POST'
    controls = {attrs['name']: (attrs, inside, groups)
                for tag, attrs, inside, groups in page.elements
                if tag in ('input', 'select', 'textarea') and 'name' in attrs}
    required = {'name', 'phone', 'date', 'city', 'chair_ready',
                'air_conditioning', 'gift_photo_adult', 'parking_ready'}
    assert {name for name, (attrs, _, _) in controls.items() if 'required' in attrs} == required
    for name in required:
        _, inside, groups = controls[name]
        assert inside and not groups, name
    for name in ('email', 'time', 'guests', 'eventType', 'details', 'gifts'):
        _, inside, groups = controls[name]
        assert inside and groups == ('optional-details',), name
    assert controls['_next'][0]['value'] == 'https://miamipapanoel.com/thank-you'
    assert controls['_honey'][1] and controls['message_summary'][1]
    buttons = [attrs for tag, attrs, inside, _ in page.elements if tag == 'button' and inside]
    assert len(buttons) == 1 and buttons[0]['type'] == 'submit'
    assert not any('open' in attrs for tag, attrs, _, _ in page.elements if tag == 'details')


@pytest.mark.parametrize('filename,following', [('index.html', 'whatsappMessages'),
                                               ('book.html', 'messageLabels')])
def test_customer_pages_translate_all_visible_copy_and_link_to_real_pages(filename, following):
    text = (ROOT / filename).read_text(encoding='utf-8')
    page = CustomerPage(text)
    literal = re.search(r'const translations = (\{.*?\});\s*const ' + following, text, re.S).group(1)
    parsed = subprocess.run(
        ['node', '-e', "const fs=require('node:fs'), vm=require('node:vm');"
         "console.log(JSON.stringify(vm.runInNewContext('('+fs.readFileSync(0,'utf8')+')',{}, {timeout:1000})));"],
        input=literal, capture_output=True, encoding='utf-8', check=True, timeout=5)
    translations = json.loads(parsed.stdout)
    keys = {attrs[key] for _, attrs, _, _ in page.elements
            for key in ('data-i18n', 'data-i18n-alt', 'data-i18n-placeholder') if key in attrs}
    for lang in ('en', 'es'):
        assert all(translations[lang].get(key) for key in keys)
    links = [attrs.get('href', '') for tag, attrs, _, _ in page.elements if tag == 'a']
    assert not any('/operator' in href or '/login' in href for href in links)
    if filename == 'index.html':
        assert sum(tag == 'section' for tag, _, _, _ in page.elements) == 3
        assert sum(tag == 'article' for tag, _, _, _ in page.elements) == 3
        assert any(href.startswith('/book?') for href in links)
        assert {'gallery', 'services', 'packages', 'faq'} <= {
            attrs['id'] for _, attrs, _, _ in page.elements if 'id' in attrs}


def test_build_excludes_private_and_unlisted_files(project):
    (project / 'business').mkdir()
    (project / 'business/operator.html').write_text('private synthetic')
    (project / 'lead-tracker.csv').write_text('synthetic')
    (project / '.env').write_text('SYNTHETIC_ONLY=1')
    assert run_build(project).returncode == 0
    assert sorted(p.relative_to(project / 'dist').as_posix()
                  for p in (project / 'dist').rglob('*') if p.is_file()) == ['index.html']


@pytest.mark.parametrize('entry', ['business/operator.html', '../index.html', '/index.html',
                                  'assets/../lead-tracker.csv', '.env', 'lead-tracker.csv'])
def test_unsafe_manifest_entries_refused(project, entry):
    (project / 'deploy/public-files.json').write_text(json.dumps([entry]))
    assert run_build(project).returncode != 0
    assert not (project / 'dist').exists()


def test_placeholder_refused_before_output_created(project):
    (project / 'index.html').write_text('<a href="https://inquiry.example.invalid/">Chat</a>')
    assert run_build(project).returncode != 0
    assert not (project / 'dist').exists()


def test_stale_private_output_refused_not_deleted(project):
    (project / 'dist').mkdir()
    secret = project / 'dist/notes.csv'
    secret.write_text('synthetic retained')
    assert run_build(project).returncode != 0
    assert secret.read_text() == 'synthetic retained'


def test_output_symlink_refused(project, tmp_path_factory):
    target = tmp_path_factory.mktemp('not-published')
    try:
        (project / 'dist').symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip('symlink privilege unavailable')
    assert run_build(project).returncode != 0
    assert not list(target.iterdir())
