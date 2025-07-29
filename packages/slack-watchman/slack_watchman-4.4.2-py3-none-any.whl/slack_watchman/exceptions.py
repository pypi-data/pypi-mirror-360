class MissingEnvVarError(Exception):
    """ Exception raised when an environment variable is missing.
    """

    def __init__(self, env_var):
        self.env_var = env_var
        self.message = f'Missing Environment Variable: {self.env_var}'
        super().__init__(self.message)


class MissingCookieEnvVarError(Exception):
    """ Exception raised when a cookie environment variable is missing.
    """

    def __init__(self, env_var):
        self.env_var = env_var
        self.message = (f'Cookie authentication has been selected, but missing '
                        f'required environment variable: {self.env_var}')
        super().__init__(self.message)


class MissingCookieAuthError(Exception):
    """ Exception raised when a cookie auth is selected, but no cookie is set.
    """

    def __init__(self):
        self.message = ('Cookie authentication has been selected, but missing no authentication data '
                        'has been provided. Please set the environment variables SLACK_WATCHMAN_COOKIE and '
                        'SLACK_WATCHMAN_URL')
        super().__init__(self.message)


class MisconfiguredConfFileError(Exception):
    """ Exception raised when the config file watchman.conf is missing.
    """

    def __init__(self):
        self.message = "The file watchman.conf doesn't contain config details for Slack Watchman"
        super().__init__(self.message)


class MissingConfigVariable(Exception):
    """ Exception raised when config entry is missing.
    """

    def __init__(self, config_entry):
        self.config_entry = config_entry
        self.message = f'Missing variable in the config file: {self.config_entry}'
        super().__init__(self.message)


class InvalidCookieError(Exception):
    """ Exception raised when the provided cookie is not valid, or it does not
        nave access to the workspace given.
    """

    def __init__(self, domain):
        self.message = "The cookie may not be valid or, if it is valid," \
                       f" the user it belongs to cant authenticate to the Slack workspace {domain}"
        super().__init__(self.message)


class SlackScopeError(Exception):
    """ Exception raised when the authed user doesn't have the required API scopes
    """

    def __init__(self, scope):
        self.scope = scope
        self.message = f'Slack API token is missing the required scope: {self.scope}'
        super().__init__(self.message)


class SlackAPIError(Exception):
    """ Exception raised for a generic Slack API error
    """

    def __init__(self, error_message):
        self.error_message = error_message
        self.message = f'Slack API error: {self.error_message}'
        super().__init__(self.message)


class SlackAPIRateLimit(Exception):
    """ Exception raised for a Slack rate limit warning
    """

    def __init__(self):
        self.message = 'Slack API rate limit reached - cooling off'
        super().__init__(self.message)
