import json
import logging
import time
import uuid
from logging import handlers
from pathlib import Path
from typing import Union, List

import bcrypt
import cherrypy
import pyotp
import qrcode
import qrcode.image.svg
from cherrypy.process.plugins import SignalHandler
from mako.lookup import TemplateLookup
from qrcode.main import QRCode

from push_service.service import PushService


class PushServiceWebUI:
    """
    A CherryPy web UI for the PushService that allows users to create channels, subscribe, unsubscribe, and send messages.
    It also provides an admin interface for managing channels and subscriptions.
    The web UI supports two-factor authentication using TOTP and allows the admin to set a password.
    The web UI can be configured to enable or disable channel creation and admin access.
    """
    FAILED_LOGIN_DELAY = 10
    MINUMUM_PASSWORD_LENGTH = 8

    def __init__(self, push_service: PushService, admin_password_file: Union[Path, str],
                 otp_secret_file: Union[Path, str],
                 template_lookup_dir: Union[str, Path, List[Union[str, Path]], None] = None,
                 enable_admin: bool = False, enable_channel_creation: bool = False,
                 enabled_channels: Union[List[str], None] = None):
        """
        Initializes the PushServiceWebUI with the given parameters.
        :param push_service: PushService instance that manages channels and subscriptions.
        :param admin_password_file: Path to the file that stores the admin password hash.
        :param otp_secret_file: Path to the file that stores the TOTP secret for two-factor authentication.
        :param template_lookup_dir: Directory or list of directories where eventual user-provided custom Mako templates are stored.
                                    If None, defaults to the 'templates' directory in the same directory as this file.
        :param enable_admin: If True, enables the admin interface for managing channels and subscriptions.
        :param enable_channel_creation: If True, allows users to create new channels.
        :param enabled_channels: List of channels to enable in the web UI. If None, all channels are enabled.
        """
        self._push_service = push_service
        self._enable_admin = enable_admin
        self._enable_channel_creation = enable_channel_creation
        self._enabled_channels = enabled_channels
        if template_lookup_dir is None:
            template_lookup_dir = [Path(__file__).parent / 'templates']
        elif isinstance(template_lookup_dir, (str, Path)):
            template_lookup_dir = [template_lookup_dir]
        self._template_lookup = TemplateLookup(directories=template_lookup_dir)
        if isinstance(otp_secret_file, str):
            self._otp_secret_file = Path(otp_secret_file)
        elif isinstance(otp_secret_file, Path):
            self._otp_secret_file = otp_secret_file
        else:
            raise ValueError('otp_secret_file must be a str or a Path')
        if not otp_secret_file.parent.exists():
            otp_secret_file.parent.mkdir(parents=True, exist_ok=True)
        if otp_secret_file.exists():
            self._otp_secret = otp_secret_file.read_text('utf-8').strip()
        else:
            self._otp_secret = None

        if isinstance(admin_password_file, str):
            self._admin_password_file = Path(admin_password_file)
        elif isinstance(admin_password_file, Path):
            self._admin_password_file = admin_password_file

        if not admin_password_file.parent.exists():
            admin_password_file.parent.mkdir(parents=True, exist_ok=True)
        if self._admin_password_file.exists():
            self._admin_password_hash = self._admin_password_file.read_bytes().strip()
        else:
            self._admin_password_hash = None

    def get_config(self):
        return {'/':
            {
                'tools.sessions.on': True
            }
        }

    @cherrypy.expose
    def index(self):
        """
        Homepage with (if enabled) channel creation button, admin login, and list of channels.
        """
        is_admin = cherrypy.session.get('is_admin', False)
        template = self._template_lookup.get_template('index.html')
        scheme = cherrypy.request.scheme
        host = cherrypy.request.headers.get('Host')
        base_url = f"{scheme}://{host}/"
        return template.render(base_url=base_url, channels=self._push_service.get_channels(), is_admin=is_admin,
                               enable_channel_creation=self._enable_channel_creation, enable_admin=self._enable_admin)

    @cherrypy.expose
    def login(self, otp=None, password=None, confirm_password=None):
        """
        Handles the admin login process.
        If the admin password is not set, it prompts the user to set a new password.
        If the TOTP secret is not set, it generates a new TOTP secret and displays a QR code for the user to scan.
        If the admin password and the TOPT secret are set, it requires the user to enter the password and a TOTP code.
        """
        if not self._enable_admin:
            raise cherrypy.HTTPError(403, 'Admin login is disabled.')

        if not self._otp_secret:
            self._otp_secret = pyotp.random_base32()
            self._otp_secret_file.write_text(self._otp_secret, encoding='utf-8')
            totp = pyotp.TOTP(self._otp_secret)
            totp_url = totp.provisioning_uri(f"admin@push_service({cherrypy.url()})", issuer_name="PushService")
            qr = qrcode.QRCode(image_factory=qrcode.image.svg.SvgPathImage)
            qr.add_data(totp_url)
            qr.make(fit=True)
            img = qr.make_image()
            img_str = img.to_string(encoding="utf8").decode()
            template = self._template_lookup.get_template('otp.html')
            return template.render(img_str=img_str)

        if self._admin_password_hash is None:
            if cherrypy.request.method == 'POST':
                password = cherrypy.request.params.get('password')
                confirm_password = cherrypy.request.params.get('confirm_password')
                if not password or not confirm_password:
                    time.sleep(PushServiceWebUI.FAILED_LOGIN_DELAY)
                    raise cherrypy.HTTPError(400, 'All fields are required.')
                if password != confirm_password:
                    time.sleep(PushServiceWebUI.FAILED_LOGIN_DELAY)
                    raise cherrypy.HTTPError(400, 'Passwords do not match.')
                if len(password) < PushServiceWebUI.MINUMUM_PASSWORD_LENGTH:
                    time.sleep(PushServiceWebUI.FAILED_LOGIN_DELAY)
                    raise cherrypy.HTTPError(400,
                                             f'Password must be at least {PushServiceWebUI.MINUMUM_PASSWORD_LENGTH} characters.')
                pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                self._admin_password_file.write_bytes(pw_hash)
                self._admin_password_hash = pw_hash
                raise cherrypy.HTTPRedirect("login")
            else:
                template = self._template_lookup.get_template('password_setup.html')
                return template.render()

        if cherrypy.request.method == 'POST':
            password = cherrypy.request.params.get('password')
            otp = cherrypy.request.params.get('otp')
            if not password or not otp:
                time.sleep(PushServiceWebUI.FAILED_LOGIN_DELAY)
                raise cherrypy.HTTPError(400, 'Password and OTP required.')
            if not self._admin_password_hash or not bcrypt.checkpw(password.encode('utf-8'), self._admin_password_hash):
                time.sleep(PushServiceWebUI.FAILED_LOGIN_DELAY)
                raise cherrypy.HTTPError(401, 'Invalid password.')
            totp = pyotp.TOTP(self._otp_secret)
            if not totp.verify(otp):
                time.sleep(PushServiceWebUI.FAILED_LOGIN_DELAY)
                raise cherrypy.HTTPError(401, 'Invalid OTP.')
            cherrypy.session['is_admin'] = True
            raise cherrypy.HTTPRedirect("/")

        template = self._template_lookup.get_template('login.html')
        return template.render()

    @cherrypy.expose
    def logout(self):
        """
        Logs out the admin user by deleting the session variable and redirecting to the homepage.
        """
        try:
            del cherrypy.session['is_admin']
        except KeyError:
            pass
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def create(self):
        """
        Creates a new channel with a UUID and redirects to the show page.
        """
        if not ( self._enable_channel_creation or (self._enable_admin and cherrypy.session.get('is_admin', False))):
            raise cherrypy.HTTPRedirect("/")
        channel = str(uuid.uuid4())
        self._push_service.add_channel(channel)
        raise cherrypy.HTTPRedirect(f"/{channel}")

    @cherrypy.expose
    def default(self, channel, action=None, *args):
        """
        Routes actions to the various methods.
        """
        is_admin = cherrypy.session.get('is_admin', False)
        if not self._push_service.channel_exists(channel) or (self._enabled_channels is not None and channel not in self._enabled_channels):
            raise cherrypy.HTTPError(404)
        elif action is None:
            template = self._template_lookup.get_template('channel.html')
            return template.render(channel=channel, subscriptions=self._push_service.get_subscriptions(channel),
                                   is_admin=is_admin)
        elif not self._push_service.channel_exists(channel):
            raise cherrypy.HTTPError(404)
        elif action == "subscription.js":
            return self.subscription_js(channel)
        elif action == "service_worker.js":
            return self.service_worker_js(channel)
        elif action == 'delete':
            if not is_admin:
                raise cherrypy.HTTPError(401)
            return self.delete_channel(channel)
        elif action == 'subscribe':
            return self.subscribe(channel)
        elif action == 'unsubscribe':
            return self.unsubscribe(channel)
        elif action == 'delete_subscription':
            if not is_admin:
                raise cherrypy.HTTPError(401)
            if len(args) != 1:
                raise cherrypy.HTTPError(400)
            try:
                subscription_id = int(args[0])
            except:
                raise cherrypy.HTTPError(400)
            return self.delete_subscription(channel, subscription_id)
        elif action == 'send':
            return self.send(channel)
        elif action == 'messages':
            return self.messages(channel)
        else:
            raise cherrypy.HTTPError(404)

    def subscription_js(self, channel):
        """
        Returns the JavaScript code for subscribing to the push service.
        :param channel: The channel to subscribe to.
        :return: A JavaScript code snippet that can be included in a web page to handle the subscription to the specified channel.
        """
        cherrypy.response.headers['Content-Type'] = 'application/javascript'
        template = self._template_lookup.get_template('subscription.js')
        template.output_encoding = 'utf-8'
        return template.render(channel=channel, vapid_public_key=self._push_service.get_vapid_public_key(channel))

    def service_worker_js(self, channel):
        """
        Returns the JavaScript code for the service worker that handles push notifications.
        :param channel: The channel for which the service worker is being created.
        :return: A JavaScript code snippet that can be registered as a service worker to handle push notifications for the specified channel.
        """
        cherrypy.response.headers['Content-Type'] = 'application/javascript'
        template = self._template_lookup.get_template('service_worker.js')
        template.output_encoding = 'utf-8'
        return template.render(channel=channel, server_address=cherrypy.request.base + cherrypy.request.script_name)

    def delete_channel(self, channel):
        """
        Deletes a channel and all its subscriptions.
        :param channel: The channel to delete.
        :return: A JSON response indicating success or failure.
        """
        try:
            self._push_service.delete_channel(channel)

            cherrypy.response.status = 200
        except Exception as e:
            cherrypy.response.status = 400
            return json.dumps({"status": "error", "message": str(e)})

    def subscribe(self, channel):
        """
        Subscribes a user to a channel by reading the subscription information from the request body.
        :param channel: The channel to subscribe to.
        :return: A JSON response indicating success or failure.
        """
        try:
            body = cherrypy.request.body.read().decode()
            subscription_info = json.loads(body)

            if not subscription_info and not 'endpoint' in subscription_info and not 'keys' in subscription_info:
                raise ValueError("Missing subscription in the request.")

            self._push_service.add_subscription(channel, subscription_info, cherrypy.request.remote.ip)

            cherrypy.response.status = 200
        except Exception as e:
            cherrypy.response.status = 400
            return json.dumps({"status": "error", "message": str(e)})

    def unsubscribe(self, channel):
        """
        Unsubscribes a user from a channel by reading the subscription information from the request body.
        :param channel: The channel to unsubscribe from.
        :return: A JSON response indicating success or failure.
        """
        try:
            body = cherrypy.request.body.read().decode()
            subscription_info = json.loads(body)

            if not subscription_info and not 'endpoint' in subscription_info and not 'keys' in subscription_info:
                raise ValueError("Missing subscription in the request.")

            self._push_service.delete_subscription(channel, subscription_info)

            cherrypy.response.status = 200
        except Exception as e:
            cherrypy.response.status = 400
            return json.dumps({"status": "error", "message": str(e)})

    def delete_subscription(self, channel, subscription_id):
        """
        Deletes a subscription by its ID.
        :param channel: The channel from which the subscription is being deleted.
        :param subscription_id: The ID of the subscription to delete.
        :return: A JSON response indicating success or failure.
        """
        try:
            self._push_service.delete_subscription_by_id(channel, subscription_id)

            cherrypy.response.status = 200
        except Exception as e:
            cherrypy.response.status = 400
            return json.dumps({"status": "error", "message": str(e)})

    def send(self, channel):
        """
        Sends a message to the specified channel.
        :param channel: The channel to which the message is being sent.
        :return: A JSON response indicating success or failure.
        """
        try:
            message_content = cherrypy.request.body.read().decode()

            sender = cherrypy.request.remote.ip

            self._push_service.send_message(channel, message_content, sender)

            cherrypy.response.status = 200
        except Exception as e:
            cherrypy.response.status = 400
            return json.dumps({"status": "error", "message": str(e)})

    def messages(self, channel):
        """
        Returns the messages for a given channel in JSON format.
        :param channel: The channel for which to retrieve messages.
        :return: A JSON response containing the messages for the specified channel.
        """
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(self._push_service.get_messages(channel)).encode('utf-8')


def setup_log(log_dir: Path, environment='production'):
    """
    Sets up the logging for the CherryPy web server.
    :param log_dir: Directory where the log files will be stored.
    :param environment: The environment in which the server is running (e.g., 'production', 'development').
    """
    if log_dir:
        if isinstance(log_dir, str):
            log_dir = Path(log_dir)

        if log_dir.exists():
            if not log_dir.is_dir():
                raise FileExistsError(f'{log_dir} exists and it is not a directory')
        else:
            log_dir.mkdir(parents=True)

        cherrypy.config.update({
            'environment': environment,
            'log.error_file': '',
            'log.access_file': ''})

        error_handler = handlers.RotatingFileHandler(log_dir / 'error.log', maxBytes=10 ** 6, backupCount=5)
        error_handler.setLevel(logging.DEBUG)
        cherrypy.log.error_log.addHandler(error_handler)

        access_handler = handlers.RotatingFileHandler(log_dir / 'access.log', maxBytes=10 ** 6, backupCount=5)
        access_handler.setLevel(logging.DEBUG)
        cherrypy.log.access_log.addHandler(access_handler)


def run_webui(
        push_service: PushService,
        host: str,
        port: Union[int, str],
        ssl_certificate: Union[Path, str, None],
        ssl_private_key: Union[Path, str, None],
        ssl_chain: Union[Path, str, None],
        log_dir: Union[Path, str, None],
        otp_secret_file: Union[Path, str],
        admin_password_file: Union[Path, str],
        enabled_channels: Union[List[str], None] = None,
        enable_channel_creation=False,
        enable_admin=False,
        stop_function=None,
):
    """
    Runs the CherryPy web server for the PushServiceWebUI.
    :param push_service: PushService instance that manages channels and subscriptions.
    :param host: The host address on which the web server will listen.
    :param port: The port on which the web server will listen.
    :param ssl_certificate: Path or string to the SSL certificate file for HTTPS support.
    :param ssl_private_key: Path or string to the SSL private key file for HTTPS support.
    :param ssl_chain: Path or string to the SSL certificate chain file for HTTPS support.
    :param log_dir: Directory where the log files will be stored. If not set, a directory named 'push_service_logs' will be created in the current working directory.
    :param otp_secret_file: Path to the file that stores the TOTP secret for two-factor authentication.
    :param admin_password_file: Path to the file that stores the admin password hash.
    :param enabled_channels: List of channels to enable in the web UI. If None, all channels are enabled.
    :param enable_channel_creation: If True, allows users to create new channels.
    :param enable_admin: If True, enables the admin interface for managing channels and subscriptions.
    :param stop_function: Optional function that is called after the server is started and that stops the server when it returns (e.g., waiting for the enter key). If None, the server will block until it is stopped by a signal (SIGTERM, SIGHUP, SIGQUIT, SIGINT).
    """
    setup_log(log_dir)

    if ssl_certificate:
        cherrypy.server.ssl_module = 'builtin'
        cherrypy.server.ssl_certificate = ssl_certificate
        cherrypy.server.ssl_private_key = ssl_private_key
        if ssl_chain:
            cherrypy.server.ssl_certificate_chain = ssl_chain

    cherrypy.server.socket_host = host
    cherrypy.server.socket_port = port

    base_url = f'http{"s" if ssl_certificate else ""}://{host}:{port}/'
    if enabled_channels is None:
        print(f'Push service webui listening on {base_url}')
    else:
        enabled_channels = [channel for channel in enabled_channels if push_service.channel_exists(channel)]
        if len(enabled_channels) == 0:
            print(f'No valid channels found for push service webui.')
            return
        print(f'Push service webui enabled for subscription to the following channels:')
        for channel in enabled_channels:
            channel_url = f'{base_url}{channel}'
            print(channel_url)
            qr = QRCode()
            qr.add_data(channel_url)
            qr.print_ascii()

    webui = PushServiceWebUI(push_service=push_service, admin_password_file=admin_password_file,
                             otp_secret_file=otp_secret_file,
                             enable_admin=enable_admin, enable_channel_creation=enable_channel_creation,
                             enabled_channels=enabled_channels)
    cherrypy.tree.mount(webui, config=webui.get_config())

    signal_handler = SignalHandler(cherrypy.engine)
    signal_handler.handlers['SIGTERM'] = cherrypy.engine.exit
    signal_handler.handlers['SIGHUP'] = cherrypy.engine.exit
    signal_handler.handlers['SIGQUIT'] = cherrypy.engine.exit
    signal_handler.handlers['SIGINT'] = cherrypy.engine.exit
    signal_handler.subscribe()

    cherrypy.engine.start()
    if stop_function is None:
        cherrypy.engine.block()
    else:
        stop_function()
        cherrypy.engine.exit()
