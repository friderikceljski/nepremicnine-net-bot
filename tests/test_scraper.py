from scraper import parse_properties_from_html, scrape


def test_parse_properties_from_html_extracts_name_price_and_size():
    html = """
    <div class="property-details">
      <a class="url-title-d" title="Ljubljana okolica, zazidljiva parcela"></a>
      <div>185.000 EUR</div>
      <div>1.250 m2</div>
    </div>
    """

    result = parse_properties_from_html(html)

    assert len(result) == 1
    assert result[0].name == "Ljubljana okolica, zazidljiva parcela"
    assert result[0].price == "185.000 EUR"
    assert result[0].size_m2 == "1.250 m2"


def test_parse_properties_from_html_ignores_entries_without_title_anchor():
    html = """
    <div class="property-details">
      <div>185.000 EUR</div>
      <div>1.250 m2</div>
    </div>
    """

    result = parse_properties_from_html(html)

    assert result == []


def test_parse_properties_from_html_handles_space_thousand_separator():
    html = """
    <div class="property-details">
      <a class="url-title-d" title="Parcela"></a>
      <div>150 000 EUR</div>
      <div>1 100 m2</div>
    </div>
    """

    result = parse_properties_from_html(html)

    assert result[0].price == "150 000 EUR"
    assert result[0].size_m2 == "1 100 m2"


def _raise(exc: Exception):
    raise exc


def test_scrape_falls_back_to_second_method(monkeypatch):
    html = """
    <div class=\"property-details\">
      <a class=\"url-title-d\" title=\"Fallback parcela\"></a>
      <div>170.000 EUR</div>
      <div>1.300 m2</div>
    </div>
    """

    monkeypatch.setattr("scraper.fetch_with_requests", lambda _url: _raise(RuntimeError("blocked")))
    monkeypatch.setattr("scraper.fetch_with_playwright", lambda _url: html)

    result = scrape("https://example.com", ["requests", "playwright"])

    assert len(result) == 1
    assert result[0].name == "Fallback parcela"


def test_scrape_error_lists_methods(monkeypatch):
    monkeypatch.setattr("scraper.fetch_with_requests", lambda _url: _raise(RuntimeError("fail1")))
    monkeypatch.setattr("scraper.fetch_with_playwright", lambda _url: _raise(RuntimeError("fail2")))

    try:
        scrape("https://example.com", ["requests", "playwright"])
    except RuntimeError as exc:
        assert "methods ['requests', 'playwright']" in str(exc)
        assert "requests: fail1" in str(exc)
        assert "playwright: fail2" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")
