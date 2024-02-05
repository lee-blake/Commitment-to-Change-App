"""Tests for template logic.

Not all template logic needs testing here - rendering variables should instead be tested
at the integration level. Generally, any logic that is not essential to the function of a page 
but could break in a way that damages usability should be tested here."""

from django.template import loader

from commitments.business_logic import CommitmentTemplateLogic, CommitmentStatusStatistics, \
    CourseLogic
from commitments.fake_data_objects import FakeCommitmentData, FakeCommitmentTemplateData, \
    FakeCourseData


class TestCommitmentEditPrefaceModals:
    """Tests for 'commitments/Commitment/commitment_edit_preface_modals.html'"""

    def test_not_a_suggested_commit_returns_smart_reminder(self):
        commitment = FakeCommitmentData()
        commitment.source_template = None
        template = loader.get_template(
            "commitments/Commitment/commitment_edit_preface_modals.html"
        )
        rendered_content = template.render({"commitment": commitment})
        assert "S.M.A.R.T." in rendered_content

    def test_suggested_commit_returns_cannot_edit_reminder(self):
        commitment = FakeCommitmentData()
        commitment.source_template = FakeCommitmentTemplateData()
        template = loader.get_template(
            "commitments/Commitment/commitment_edit_preface_modals.html"
        )
        rendered_content = template.render({"commitment": commitment})
        assert "not eligible for editing" in rendered_content


class TestCommitmentViewPageStatistics:
    """Tests for 'commitments/CommitmentTemplate/commitment_template_view_page_statistics.html'"""

    def test_legend_does_not_show_for_no_derived_commitments(self):
        commitment_template = CommitmentTemplateLogic(
            FakeCommitmentTemplateData(derived_commitments=[])
        )
        commitment_template.commitment_statistics = CommitmentStatusStatistics().as_json()
        template = loader.get_template(
            "commitments/CommitmentTemplate/commitment_template_view_page_statistics.html"
        )
        rendered_content = template.render({"commitment_template": commitment_template})
        assert "No commitments have been made from this template." in rendered_content


class TestCommitmentTemplateChartLegend:
    """Tests for 'commitments/CommitmentTemplate/commitment_template_chart_legend.html'"""

    def test_only_non_zeroes_show_in_legend(self):
        commitment_template_data = {
            "total": 2,
            "counts": {
                "in_progress" : 1,
                "complete" : 1,
                "discontinued" : 0,
                "expired" : 0,

            },
            "percentages": {
                "in_progress" : 50,
                "complete" : 50,
                "discontinued" : 0,
                "expired" : 0,
            },
        }
        template = loader.get_template(
            "commitments/CommitmentTemplate/commitment_template_chart_legend.html"
        )
        rendered_content = template.render({"commitment_data_object" : commitment_template_data})
        assert "In-progress: 1" in rendered_content
        assert "Complete: 1" in rendered_content
        assert "Discontinued" not in rendered_content
        assert "Past-due" not in rendered_content

    def test_only_non_zeroes_shows_in_legend_complement(self):
        commitment_template_data = {
            "total": 2,
            "counts": {
                "in_progress" : 0,
                "complete" : 0,
                "discontinued" : 1,
                "expired" : 1,

            },
            "percentages": {
                "in_progress" : 0,
                "complete" : 0,
                "discontinued" : 50,
                "expired" : 50,
            },
        }
        template = loader.get_template(
            "commitments/CommitmentTemplate/commitment_template_chart_legend.html"
        )
        rendered_content = template.render({"commitment_data_object" : commitment_template_data})
        assert "In-progress" not in rendered_content
        assert "Complete" not in rendered_content
        assert "Discontinued: 1" in rendered_content
        assert "Past-due: 1" in rendered_content

class TestCourseStatisticsBreakdownSection:
    """Tests for 'commitments/Course/course_commitment_statistics_breakdown_section.html'"""

    def test_legend_does_not_show_for_no_associated_commitments(self):
        course_logic = CourseLogic(
            FakeCourseData(associated_commitments=[])
        )
        course_logic.enrich_with_statistics()
        template = loader.get_template(
            "commitments/Course/course_commitment_statistics_breakdown_section.html"
        )
        rendered_content = template.render({"course": course_logic._data})
        assert "No commitments have been made in this course." in rendered_content