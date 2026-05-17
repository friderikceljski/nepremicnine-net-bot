from scraper import parse_properties_from_html


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
