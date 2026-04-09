from django.test import SimpleTestCase


class HealthcheckPackageExportsTests(SimpleTestCase):
    def test_views_package_exports_health_check(self):
        from healthcheck.views import health_check

        self.assertTrue(callable(health_check))
