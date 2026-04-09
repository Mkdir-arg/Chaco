from importlib import import_module

from django.test import SimpleTestCase


class DashboardPackageExportsTests(SimpleTestCase):
    def test_views_and_signals_packages_are_importable(self):
        from dashboard.api_views import metricas_dashboard
        from dashboard.views import DashboardView

        self.assertIsNotNone(DashboardView)
        self.assertTrue(callable(metricas_dashboard))
        self.assertIsNotNone(import_module("dashboard.signals"))
