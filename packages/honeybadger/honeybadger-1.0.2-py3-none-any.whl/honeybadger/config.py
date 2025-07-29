import os
import socket
from six.moves import zip
from six import iteritems


class Configuration(object):
    DEVELOPMENT_ENVIRONMENTS = ["development", "dev", "test"]

    OPTIONS = (
        ("api_key", str),
        ("project_root", str),
        ("environment", str),
        ("development_environments", list),
        ("hostname", str),
        ("endpoint", str),
        ("params_filters", list),
        ("force_report_data", bool),
        ("force_sync", bool),
        ("excluded_exceptions", list),
        ("report_local_variables", bool),
        ("before_notify", callable),
        # Insights options
        ("events_batch_size", int),
        ("events_max_queue_size", int),
        ("events_timeout", float),
        ("events_max_batch_retries", int),
        ("events_throttle_wait", float),
    )

    def __init__(self, *args, **kwargs):
        self.api_key = ""
        self.project_root = os.getcwd()
        self.environment = "production"
        self.development_environments = self.DEVELOPMENT_ENVIRONMENTS
        self.hostname = socket.gethostname()
        self.endpoint = "https://api.honeybadger.io"
        self.params_filters = [
            "password",
            "password_confirmation",
            "credit_card",
            "CSRF_COOKIE",
        ]
        self.force_report_data = False
        self.force_sync = self.is_aws_lambda_environment
        self.excluded_exceptions = []
        self.report_local_variables = False
        self.before_notify = lambda notice: notice

        self.events_max_batch_retries = 3
        self.events_max_queue_size = 10_000
        self.events_batch_size = 1000
        self.events_timeout = 5.0
        self.events_throttle_wait = 60.0

        self.set_12factor_config()
        self.set_config_from_dict(kwargs)

    def set_12factor_config(self):
        for option in list(zip(*self.OPTIONS))[0]:
            val = os.environ.get(
                "HONEYBADGER_{}".format(option.upper()), getattr(self, option)
            )
            option_types = dict(self.OPTIONS)

            try:
                if option_types[option] is list:
                    val = val.split(",")
                elif option_types[option] is int:
                    val = int(val)
                elif option_types[option] is bool:
                    val = bool(val)
            except:
                pass

            setattr(self, option, val)

    def set_config_from_dict(self, config):
        for key, value in iteritems(config):
            if key in list(zip(*self.OPTIONS))[0]:
                setattr(self, key, value)

    def is_dev(self):
        """Returns wether you are in a dev environment or not

        Default dev environments are defined in the constant DEVELOPMENT_ENVIRONMENTS

        :rtype: bool
        """
        return self.environment in self.development_environments

    @property
    def is_aws_lambda_environment(self):
        """
        Checks if you are in an AWS Lambda environment by checking for the existence
        of "AWS_LAMBDA_FUNCTION_NAME" in the environment variables.

        :rtype: bool
        """
        return os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None
