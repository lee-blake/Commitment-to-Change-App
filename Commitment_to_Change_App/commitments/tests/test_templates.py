"""Tests for template logic.

Not all template logic needs testing here - rendering variables should instead be tested
at the integration level. Generally, any logic that is not essential to the function of a page 
but could break in a way that damages usability should be tested here."""

from django.template import loader

from commitments.fake_data_objects import FakeCommitmentData, FakeCommitmentTemplateData


class TestExamplesAssociatedCourse:
    """Tests for 'commitments/Commitment/commitment_edit_preface_modals.html'"""

    def test_not_a_suggested_commit_returns_smart_reminder(self):
        commitment = FakeCommitmentData()
        commitment.source_template = None
        template = loader.get_template(
            "commitments/Commitment/commitment_edit_preface_modals.html"
        )
        rendered_content = template.render({"commitment": commitment})
        assert "S.M.A.R.T." in rendered_content

    def test__suggested_commit_returns_cannot_edit_reminder(self):
        commitment = FakeCommitmentData()
        commitment.source_template = FakeCommitmentTemplateData()
        template = loader.get_template(
            "commitments/Commitment/commitment_edit_preface_modals.html"
        )
        rendered_content = template.render({"commitment": commitment})
        assert "not eligible for editing" in rendered_content
