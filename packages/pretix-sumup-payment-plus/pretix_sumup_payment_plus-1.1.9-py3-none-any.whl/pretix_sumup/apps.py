from django.utils.translation import gettext_lazy

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_sumup"
    verbose_name = "Pretix SumUp Payment"

    class PretixPluginMeta:
        name = "SumUp"
        author = "Christoph Walcher & Botond Moksony"
        description = gettext_lazy("Accept credit card payments via SumUp")
        visible = True
        version = __version__
        category = "PAYMENT"
        compatibility = "pretix>=2.7.0"

    def ready(self):
        from . import signals  # NOQA
