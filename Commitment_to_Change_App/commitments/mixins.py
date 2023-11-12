from django.contrib.auth.mixins import UserPassesTestMixin


class ClinicianLoginRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_clinician


class ProviderLoginRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_provider
