"""Offline artifact checks; no Vercel account or deployment is invoked."""
import json
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import urllib.parse

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
    assert forms[0]['action'] == 'https://formsubmit.co/bookings@miamipapanoel.com'
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
            for key in ('data-i18n', 'data-i18n-alt', 'data-i18n-placeholder', 'data-i18n-aria') if key in attrs}
    for lang in ('en', 'es'):
        assert all(translations[lang].get(key) for key in keys)
    links = [attrs.get('href', '') for tag, attrs, _, _ in page.elements if tag == 'a']
    assert not any('/operator' in href or '/login' in href for href in links)
    if filename == 'index.html':
        assert sum(tag == 'section' for tag, _, _, _ in page.elements) == 4
        assert sum(tag == 'dialog' for tag, _, _, _ in page.elements) == 1
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


def jpeg_has_gps(path):
    """True when a JPEG's Exif IFD0 carries a GPSInfo pointer (tag 0x8825). Pure Python, no Pillow."""
    data = path.read_bytes()
    if data[:2] != b'\xff\xd8':
        return False
    offset = 2
    while offset + 4 <= len(data) and data[offset] == 0xFF:
        marker, size = data[offset + 1], int.from_bytes(data[offset + 2:offset + 4], 'big')
        if marker == 0xE1 and data[offset + 4:offset + 10] == b'Exif\x00\x00':
            tiff = data[offset + 10:offset + 2 + size]
            endian = 'little' if tiff[:2] == b'II' else 'big'
            ifd = int.from_bytes(tiff[4:8], endian)
            count = int.from_bytes(tiff[ifd:ifd + 2], endian)
            return any(int.from_bytes(tiff[ifd + 2 + 12 * n:ifd + 4 + 12 * n], endian) == 0x8825
                       for n in range(count))
        if marker in (0xDA, 0xD9):
            break
        offset += 2 + size
    return False


def test_no_published_image_carries_gps_metadata():
    manifest = json.loads((ROOT / 'deploy/public-files.json').read_text())
    photos = [p for p in manifest if p.lower().endswith(('.jpg', '.jpeg'))]
    assert len(photos) >= 5
    leaking = [p for p in photos if jpeg_has_gps(ROOT / p)]
    assert leaking == [], leaking


GALLERY_PHOTOS = [  # Owner confirmed guest photo waivers; editorial order is deliberate
    'assets/premium/santa-family-event-1600-premium.jpg',
    'assets/santa-seated-holiday-portrait.jpg',
    'assets/optimized/extra-20231210-160208-1200.jpg',
    'assets/premium/santa-community-event-1600-premium.jpg',
    'assets/premium/santa-pet-visit-1600-premium.jpg',
]


def test_homepage_gallery_is_compact_accessible_and_allowlisted():
    text = (ROOT / 'index.html').read_text(encoding='utf-8')
    assert text.index('class="hero"') < text.index('id="gallery"') < text.index('id="packages"') < text.index('id="faq"')
    page = CustomerPage(text)
    manifest = set(json.loads((ROOT / 'deploy/public-files.json').read_text()))
    links = [attrs for tag, attrs, _, _ in page.elements
             if tag == 'a' and 'photo' in attrs.get('class', '').split()]
    thumbs = [attrs for tag, attrs, _, _ in page.elements
              if tag == 'img' and attrs.get('loading') == 'lazy' and attrs.get('data-i18n-alt', '').startswith('photos.')]
    assert [a['href'] for a in links] == [i['src'] for i in thumbs] == GALLERY_PHOTOS
    group = next(i for i in thumbs if 'santa-community-event' in i['src'])
    assert 'group-photo' in group.get('class', '').split()
    assert '.photo img.group-photo { object-fit:contain; }' in text
    for attrs in thumbs:
        assert attrs['src'] in manifest and (ROOT / attrs['src']).is_file(), attrs['src']
        assert attrs['alt'] and attrs['width'] and attrs['height'] and attrs['decoding'] == 'async'
    hero = next(attrs for tag, attrs, _, _ in page.elements if tag == 'img' and attrs.get('class') == 'hero-photo')
    assert hero['src'] == 'assets/santa-standing-holiday-portrait.jpg' and hero['data-i18n-alt'] == 'photos.standing'
    # click-to-enlarge viewer: native <dialog>, labelled, obvious close, prev/next, keyboard arrows
    dialog = next(attrs for tag, attrs, _, _ in page.elements if tag == 'dialog')
    assert dialog['id'] == 'lightbox' and dialog['aria-label'] and dialog['data-i18n-aria'] == 'gallery.viewer'
    buttons = {attrs['id']: attrs for tag, attrs, _, _ in page.elements if tag == 'button' and 'id' in attrs}
    assert {'lightboxClose', 'lightboxPrev', 'lightboxNext'} <= set(buttons)
    assert all(buttons[name]['type'] == 'button' for name in ('lightboxClose', 'lightboxPrev', 'lightboxNext'))
    for token in ('lightbox.showModal()', 'lightbox.close()', '"ArrowLeft"', '"ArrowRight"',
                  'lightboxClose.focus()', 'event.preventDefault()', 'typeof lightbox.showModal === "function"'):
        assert token in text, token
    # nothing on the page invents trust: no reviews, counts, insurance, awards or superlatives
    body = text.split('<main>')[1].split('</main>')[0].lower()
    for claim in ('review', 'insured', 'insurance', 'award', 'best in', '#1', 'five-star', '5-star', 'families served'):
        assert claim not in body, claim


REQUIREMENTS = ('chair_ready', 'air_conditioning', 'gift_photo_adult', 'parking_ready')
MESSAGE_HARNESS = """
const fs = require('node:fs'), vm = require('node:vm');
const cfg = JSON.parse(fs.readFileSync(0, 'utf8'));
const node = (id) => {
  const value = cfg.values[id] ?? '';
  return cfg.selects.includes(id)
    ? {tagName: 'SELECT', value, selectedIndex: 0, options: [{textContent: value}]}
    : {tagName: 'INPUT', value};
};
const sandbox = {currentLanguage: cfg.language, message: {textContent: ''}, messageSummary: {value: ''},
  smsLink: {href: ''}, whatsappLink: {href: ''}, emailLink: {href: ''},
  document: {getElementById: node, querySelector: (selector) => {
    const name = /input\\[name="([^"]+)"\\]/.exec(selector)[1];
    return {checked: cfg.checked.includes(name)};
  }}};
vm.runInNewContext(cfg.code + '\\nbuildMessage();', sandbox, {timeout: 1000});
console.log(JSON.stringify({text: sandbox.message.textContent, summary: sandbox.messageSummary.value,
  sms: sandbox.smsLink.href, whatsapp: sandbox.whatsappLink.href, email: sandbox.emailLink.href}));
"""


def book_message(language, checked, **values):
    """Run the real buildMessage() from book.html under a minimal DOM shim."""
    script = re.search(r'<script>(.*)</script>', (ROOT / 'book.html').read_text(encoding='utf-8'), re.S).group(1)
    code = '\n'.join(re.search(pattern, script, re.S).group(0) for pattern in (
        r'const requirements = \[.*?\];', r'const messageLabels = \{.*?\n    \};',
        r'function value\(id\) \{.*?\n    \}', r'function displayValue\(id\) \{.*?\n    \}',
        r'function requirementChecked\(name\) \{.*?\n    \}', r'function buildMessage\(\) \{.*?\n    \}'))
    config = {'code': code, 'language': language, 'checked': list(checked),
              'selects': ['package', 'eventType'], 'values': values}
    result = subprocess.run(['node', '-e', MESSAGE_HARNESS], input=json.dumps(config),
                            capture_output=True, encoding='utf-8', check=True, timeout=10)
    return json.loads(result.stdout)


@pytest.mark.parametrize('language', ['en', 'es'])
def test_posted_email_uses_selected_language(language):
    text = (ROOT / 'book.html').read_text(encoding='utf-8')
    patterns = (r'const fields = \[.*?\];', r'const requirements = \[.*?\];',
                r'const messageLabels = \{.*?\n    \};',
                r'function localizeSubmission\(data\) \{.*?\n    \}')
    code = '\n'.join(re.search(pattern, text, re.S).group(0) for pattern in patterns)
    harness = '''
const fs = require('node:fs'), vm = require('node:vm');
const cfg = JSON.parse(fs.readFileSync(0, 'utf8'));
const data = new Map(Object.entries({name:'TEST', email:'test@example.com',
 package:'Family Visit', eventType:'Family / home', chair_ready:'yes',
 message_summary:'TEST summary', routing_note:'internal', _honey:'',
 _next:'https://miamipapanoel.com/thank-you'}));
vm.runInNewContext(cfg.code + '\\nlocalizeSubmission(data);', {
 currentLanguage:cfg.language, data,
 displayValue: id => cfg.language === 'es' ?
   (id === 'package' ? 'Visita Familiar' : 'Familia / casa') :
   (id === 'package' ? 'Family Visit' : 'Family / home')
}, {timeout:1000});
console.log(JSON.stringify(Object.fromEntries(data)));
'''
    result = subprocess.run(['node', '-e', harness],
                            input=json.dumps({'code': code, 'language': language}),
                            capture_output=True, encoding='utf-8', check=True, timeout=10)
    data = json.loads(result.stdout)
    assert data['_replyto'] == 'test@example.com'
    assert data['_honey'] == '' and data['_next'].endswith('/thank-you')
    assert not {'name', 'package', 'eventType', 'message_summary', 'routing_note'} & data.keys()
    if language == 'es':
        assert data['_subject'] == 'Solicitud de visita Miami Papa Noel'
        assert data['Nombre'] == 'TEST' and data['Opción de visita'] == 'Visita Familiar'
        assert data['Idioma'] == 'Español' and data['silla firme sin brazos'] == 'Sí'
    else:
        assert data['_subject'] == 'Miami Papa Noel visit request'
        assert data['Name'] == 'TEST' and data['Visit option'] == 'Family Visit'
        assert data['Language'] == 'English' and data['sturdy armless chair'] == 'Yes'
    assert 'addEventListener("formdata", (event) => localizeSubmission(event.formData))' in text


def test_alternate_message_reports_preparation_acknowledgements():
    text = (ROOT / 'book.html').read_text(encoding='utf-8')
    page = CustomerPage(text)
    boxes = {attrs['name'] for tag, attrs, _, _ in page.elements
             if tag == 'input' and attrs.get('type') == 'checkbox' and 'required' in attrs}
    assert boxes == set(REQUIREMENTS)
    assert re.search(r'const requirements = \["chair_ready", "air_conditioning", "gift_photo_adult", "parking_ready"\];', text)
    assert re.search(r'requirements\.forEach\(\(name\) => \{\s*document\.querySelector\(\'input\[name="\' \+ name \+ \'"\]\'\)'
                     r'\.addEventListener\("change", buildMessage\);', text)
    labels = json.loads(subprocess.run(
        ['node', '-e', "const fs=require('node:fs'), vm=require('node:vm');"
         "console.log(JSON.stringify(vm.runInNewContext('('+fs.readFileSync(0,'utf8')+')',{}, {timeout:1000})));"],
        input=re.search(r'const messageLabels = (\{.*?\n    \});', text, re.S).group(1),
        capture_output=True, encoding='utf-8', check=True, timeout=5).stdout)
    assert set(labels['en']) == set(labels['es'])
    assert {'confirmed', 'confirmedNone', 'pending', 'pendingNone', *REQUIREMENTS} <= set(labels['en'])

    synthetic = dict(name='Synthetic Family', phone='305-555-0100', package='Family Visit',
                     eventType='Family / home', source='website', gifts='two labeled gifts')
    nothing = book_message('en', [], **synthetic)
    assert 'Preparation confirmed: none yet\nStill to confirm: sturdy armless chair, A/C on, ' \
           'adult for gifts and photos, parking within 100 ft\n' in nothing['text']
    assert 'Name: Synthetic Family\n' in nothing['text'] and 'Gift details:\ntwo labeled gifts' in nothing['text']
    assert nothing['summary'] == nothing['text']
    partial = book_message('en', ['chair_ready', 'parking_ready'], **synthetic)
    assert 'Preparation confirmed: sturdy armless chair, parking within 100 ft\n' \
           'Still to confirm: A/C on, adult for gifts and photos\n' in partial['text']
    spanish = book_message('es', REQUIREMENTS, **synthetic)
    assert 'Preparación confirmada: silla firme sin brazos, aire acondicionado encendido, ' \
           'adulto encargado de regalos y fotos, estacionamiento a menos de 100 pies\n' \
           'Falta confirmar: nada\n' in spanish['text']
    for result in (nothing, partial, spanish):
        encoded = urllib.parse.quote(result['text'], safe="-_.!~*'()")  # encodeURIComponent's unreserved set
        assert result['sms'] == 'sms:+17869759557?&body=' + encoded
        assert result['whatsapp'] == 'https://wa.me/17869759557?text=' + encoded
        assert result['email'].startswith('mailto:bookings@miamipapanoel.com?subject=') and result['email'].endswith('&body=' + encoded)
