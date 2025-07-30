from urllib.parse import urljoin

from django.conf import settings

from allianceauth import hooks
from allianceauth.theme.hooks import ThemeHook


class MateriaThemeHook(ThemeHook):
    """
    Bootswatch Materia Theme
    https://bootswatch.com/materia/
    """

    def __init__(self):
        ThemeHook.__init__(
            self,
            "Materia",
            "Material is the metaphor (AA-GDPR)",
            html_tags={"data-theme": "materia"},
            css=[
                {
                    "url": urljoin(
                        settings.STATIC_URL,
                        "aagdpr/ajax/libs/bootswatch/5.3.3/materia/bootstrap.min.css",
                    ),
                    "integrity": "sha512-7P47bvR3ZXlZ6m5grBVOPL6eqBh809+YbglXH+Kz9yDbAAV5DH0R+MpsNMZ9Onbcsn3UMIZrDQg1uBt0uetpsg==",
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
            header_padding="5.25em",
        )


@hooks.register("theme_hook")
def register_materia_hook():
    return MateriaThemeHook()
