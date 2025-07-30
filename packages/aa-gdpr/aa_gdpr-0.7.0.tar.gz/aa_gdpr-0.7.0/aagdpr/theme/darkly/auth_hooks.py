from urllib.parse import urljoin

from django.conf import settings

from allianceauth import hooks
from allianceauth.theme.hooks import ThemeHook


class DarklyThemeHook(ThemeHook):
    """
    Bootswatch Darkly Theme
    https://bootswatch.com/darkly/
    """

    def __init__(self):
        ThemeHook.__init__(
            self,
            "Darkly",
            "Flatly in night mode! (AA-GDPR)",
            html_tags={"data-theme": "darkly"},
            css=[
                {
                    "url": urljoin(
                        settings.STATIC_URL,
                        "aagdpr/ajax/libs/bootswatch/5.3.3/darkly/bootstrap.min.css",
                    ),
                    "integrity": "sha512-8OEr4eAsUR//UdHIuCeoiIfpEbDjbENSDEbwEevO20WryBPxfTPtW2oTOT4wATtF/rP+8RaddGKW2CxoDjLHIA==",
                }
            ],
            js=[
                {
                    "url": urljoin(
                        settings.STATIC_URL,
                        "aagdpr/ajax/libs/popper.js/2.11.8/umd/popper.min.js",
                    ),
                    "integrity": "sha512-TPh2Oxlg1zp+kz3nFA0C5vVC6leG/6mm1z9+mA81MI5eaUVqasPLO8Cuk4gMF4gUfP5etR73rgU/8PNMsSesoQ==",
                },
                {
                    "url": urljoin(
                        settings.STATIC_URL,
                        "aagdpr/ajax/libs/bootstrap/5.3.3/js/bootstrap.min.js",
                    ),
                    "integrity": "sha512-ykZ1QQr0Jy/4ZkvKuqWn4iF3lqPZyij9iRv6sGqLRdTPkY69YX6+7wvVGmsdBbiIfN/8OdsI7HABjvEok6ZopQ==",
                },
            ],
            header_padding="4.5em",
        )


@hooks.register("theme_hook")
def register_darkly_hook():
    return DarklyThemeHook()
