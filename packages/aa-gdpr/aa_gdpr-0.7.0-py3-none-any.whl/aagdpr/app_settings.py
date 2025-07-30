from django.conf import settings

# Attempt to load JS/CSS/Fonts from staticfiles when possible
# This does not guarantee no CDN usage
# App Developers may or may not respect this setting

AVOID_CDN = getattr(settings, "AVOID_CDN", True)
