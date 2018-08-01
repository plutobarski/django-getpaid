from abc import abstractmethod, ABC

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class BaseProcessor(ABC):
    display_name = None
    accepted_currencies = None
    logo_url = None
    slug = None  # for friendly urls
    method = 'GET'
    template_name = None

    def __init__(self, payment):
        self.payment = payment
        self.path = payment.backend
        if self.slug is None:
            self.slug = payment.backend  # no more Mr. Friendly :P

    def get_form(self, post_data):
        """
        Only used if the payment processor requires POST requests.
        Generates a form only containg hidden input fields.
        """
        from getpaid.forms import PaymentHiddenInputsPostForm
        return PaymentHiddenInputsPostForm(items=post_data)

    def handle_callback(self, request, *args, **kwargs):
        """
        This method handles the callback from payment broker for the purpose
        of updating the payment status in our system.
        :param args:
        :param kwargs:
        :return: HttpResponse instance
        """
        raise NotImplementedError

    @classmethod
    def get_display_name(cls):
        return cls.display_name

    @classmethod
    def get_accepted_currencies(cls):
        return cls.accepted_currencies

    @classmethod
    def get_logo_url(cls):
        return cls.logo_url

    def fetch_status(self):
        """
        Logic for checking payment status with broker.
        """
        raise NotImplementedError

    @abstractmethod
    def get_redirect_params(self):
        return {}

    def get_redirect_method(self):
        return self.method

    @abstractmethod
    def get_redirect_url(self):
        return

    def get_template_names(self, view=None):
        getpaid_config = getattr(settings, 'GETPAID', {})
        backend_config = getpaid_config.get('BACKENDS', {}).get(self.path, {})

        template_name = backend_config.get('POST_TEMPLATE')
        if template_name is None:
            template_name = getpaid_config.get('POST_TEMPLATE')
        if template_name is None:
            template_name = self.template_name
        if template_name is None and hasattr(view, 'get_template_names'):
            return view.get_template_names()
        if template_name is None:
            raise ImproperlyConfigured("Couldn't determine template name!")
        return [template_name]