from commitments.templatetags.percentformat import percent_format


class TestPercentFormat:
    """Tests for percent_format"""

    def test_adds_percentage_to_number_string(self):
        assert percent_format("1.0", 1) == "1.0%"

    def test_respects_precision_like_floatformat(self):
        assert percent_format("2.13", 3) == "2.130%"

    def test_non_number_does_not_add_percentage(self):
        assert percent_format("N/A") == ""
