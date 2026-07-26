import re

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_aplica_design_v03_com_assets_locais():
    response = client.get("/")
    assert response.status_code == 200
    assert "Aprenda a enxergar o que está escondido" in response.text
    assert "/static/css/v03.css" in response.text
    assert "/static/img/v03/hero-estereograma.png" in response.text
    assert "/static/img/v03/hero-estereograma.png?v=5" in response.text
    assert "GUIDE 108 · V2.0" in response.text
    assert 'href="/como-ver"' in response.text
    assert 'href="/como-funciona"' in response.text
    assert "fonts.googleapis.com" not in response.text
    assert "unpkg.com" not in response.text


def test_assets_principais_da_home_sao_servidos():
    for path, signature in (
        ("/static/fonts/InstrumentSans-Variable.ttf", b"\x00\x01\x00\x00"),
        ("/static/fonts/IBMPlexMono-Regular.ttf", b"\x00\x01\x00\x00"),
        ("/static/img/v03/hero-estereograma.png", b"\x89PNG"),
        ("/static/img/v03/hero-depth.png", b"\x89PNG"),
        ("/static/img/v03/og-estereograma.png", b"\x89PNG"),
        ("/static/js/htmx-1.9.12.min.js", b"(function"),
        ("/static/js/studio.js", b"(() =>"),
        ("/static/js/como-ver.js", b"(() =>"),
        ("/static/js/como-funciona.js", b"(() =>"),
    ):
        response = client.get(path)
        assert response.status_code == 200
        assert response.content.startswith(signature)


def test_studio_renderiza():
    response = client.get("/studio")
    assert response.status_code == 200
    assert "O que você quer esconder" in response.text
    assert "/static/js/studio.js" in response.text


def test_como_ver_entrega_tutorial_em_tres_passos():
    response = client.get("/como-ver")
    assert response.status_code == 200
    assert "Treine o olhar, um passo de cada vez" in response.text
    assert response.text.count("data-step=") == 3
    assert "Não consigo ver" in response.text
    assert "Revelar resposta" in response.text
    assert "v03-eye-guide" in response.text
    assert "relaxe o foco" in response.text
    assert "/static/js/como-ver.js" in response.text


def test_como_funciona_usa_formula_e_codigo_reais():
    response = client.get("/como-funciona")
    assert response.status_code == 200
    assert "A profundidade nasce de um deslocamento" in response.text
    assert "sep(z)" in response.text
    assert "look_left[right] = left" in response.text
    assert 'id="depth-z"' in response.text
    assert "Engenharia da engine" in response.text
    assert "452–477 ms" in response.text
    assert "6 / 6" in response.text
    assert "docs/ENGINE_STUDY.md" in response.text
    assert "/static/js/como-funciona.js" in response.text


def test_studio_restaura_parametros_de_link_compartilhado():
    response = client.get(
        "/studio",
        params={
            "subject_type": "text",
            "subject": "OLÁ",
            "texture": "mono",
            "depth": "marked",
            "seed": 123,
            "eye_separation": 180,
        },
    )
    assert response.status_code == 200
    assert "Parâmetros restaurados" in response.text
    assert 'id="subject-text" value="text" checked' in response.text
    assert 'id="texture-mono" value="mono" checked' in response.text
    assert 'id="depth-marked" value="marked" checked' in response.text
    assert 'id="seed" min="0" max="4294967295" value="123"' in response.text


def test_studio_usa_mosaico_como_textura_inicial():
    response = client.get("/studio")
    assert response.status_code == 200
    assert 'id="texture-mosaic" value="mosaic" checked' in response.text


def test_playground_antigo_redireciona():
    response = client.get("/playground", follow_redirects=False)
    assert response.status_code == 308
    assert response.headers["location"] == "/studio"


def test_rotas_antigas_redirecionam_sem_expor_esbocos():
    for path, target in (
        ("/aprender", "/como-ver"),
        ("/aprender/visao-binocular", "/como-ver"),
        ("/aprender/algoritmo", "/como-funciona"),
        ("/galeria", "/#obra"),
    ):
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 308
        assert response.headers["location"] == target


def test_publicacao_tem_saude_seo_e_headers_de_seguranca():
    health = client.get("/healthz")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    home = client.get("/")
    assert 'rel="canonical" href="http://testserver/"' in home.text
    assert 'property="og:image"' in home.text
    assert "frame-ancestors 'none'" in home.headers["content-security-policy"]
    assert home.headers["x-content-type-options"] == "nosniff"

    robots = client.get("/robots.txt")
    assert "Sitemap: http://testserver/sitemap.xml" in robots.text
    sitemap = client.get("/sitemap.xml")
    assert sitemap.status_code == 200
    assert "http://testserver/studio" in sitemap.text


def test_preview_invalido_retorna_erro_amigavel():
    response = client.post(
        "/studio/preview",
        data={"subject_type": "text", "text_subject": "TEXTO LONGO DEMAIS"},
    )
    assert response.status_code == 400
    assert "Não foi possível gerar" in response.text


def test_preview_entrega_png_por_url_sem_base64():
    response = client.post(
        "/studio/preview",
        data={"subject_type": "preset", "subject": "esfera", "seed": "42"},
    )
    assert response.status_code == 200
    assert "data:image" not in response.text
    assert 'data-subject="esfera"' in response.text
    assert 'data-seed="42"' in response.text
    assert 'data-engine="v2.0"' in response.text
    assert 'data-guide-separation="100"' in response.text
    assert "v03-result-guides" in response.text
    assert "Copiar link" in response.text

    match = re.search(r"/renders/([a-f0-9]{32})\.png", response.text)
    assert match is not None
    image = client.get(f"/renders/{match.group(1)}.png")
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/png"
    assert image.content.startswith(b"\x89PNG")
