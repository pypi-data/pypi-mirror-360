import argparse
import random
import string
import uuid
from pathlib import Path

from configargparse import ArgParser

import push_service.available_addresses
import push_service.webui
from push_service.service import PushService

# Default database connection string, using SQLite
CONNECT_SQLITE_DB = "sqlite:///" + str(Path.home() / '.push_service' / 'channels.db')


class _HelpAction(argparse._HelpAction):
    """
    Custom help action to print a detailed help message including subcommands.
    This action overrides the default help action to provide a more comprehensive help message.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()
        subparsers_actions = [
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)]
        for subparsers_action in subparsers_actions:
            for choice, subparser in subparsers_action.choices.items():
                print()
                print("Command '{}'".format(choice))
                subparser.print_help()
        parser.exit()


def get_encryption_password(encryption_password_file):
    """
    Retrieves the encryption password from a file or generates a new one if the file does not exist.
    :param encryption_password_file: Path to the file storing the encryption password.
    :return: The encryption password as a string.
    """
    if isinstance(encryption_password_file, str):
        encryption_password_file = Path(encryption_password_file)
    if not encryption_password_file.parent.exists():
        encryption_password_file.parent.mkdir(parents=True, exist_ok=True)
    if encryption_password_file.exists():
        try:
            with encryption_password_file.open(mode='rt', encoding='utf-8') as input_file:
                encryption_password = input_file.readline().strip()
        except:
            print(f'Cannot load the encryption password from {encryption_password_file}')
            exit(-1)
    else:
        print(f'Generating encryption password and storing it in {encryption_password_file}')
        encryption_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(30))
        with encryption_password_file.open(mode='wt', encoding='utf-8') as output_file:
            output_file.write(encryption_password)

    return encryption_password


def main():
    """"
    Command line interface for push service
    Usage:
    - list
      lists all channels names
    - [<options>] create [<name>]
      creates a new channel with the given name, if no name is given, a random name is generated
    - [<options>] delete <name>
      deletes the channel with the given name
    - [<options>] subscription <name>
      start a temporary webui only for the channel with the given name, shows the url to connect to for the subscriber (both as ascii and QR code), waits for the enter key to close the webui
    - [<options>] message <name> <message>
      sends a message to the channel with the given name, the message is a string (simple text or JSON), the message is sent to all subscribers of the channel
    - [<options>] webui
      starts the full webui for the push service, shows all channels and their subscribers, allows to send messages to channels, and manage channels
    - [<options>] iplist
      lists the available IP addresses of the host, to help users choose the host for webui and subscription commands
    """
    parser = ArgParser(add_help=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-h', '--help', action=_HelpAction, help='print a detailed help message')

    parser.add_argument('-c', '--config', help='read configuration from a file', is_config_file=True)
    parser.add_argument('-s', '--save', help='saves configuration to a file', is_write_out_config_file_arg=True)
    parser.add_argument('--db_url', help='database connection string', type=str, default=CONNECT_SQLITE_DB)
    parser.add_argument('--encryption_password_file', help='file storing the encryption password (created if missing)',
                        type=str,
                        default=Path.home() / '.push_service' / 'channel_db_encryption_password')
    parser.add_argument('--push_service_email', help='email address associated with the push service',
                        type=str, default='push_service@example.com')
    parser.add_argument('--log_dir', help='local directory for log files {subscription,webui}', type=str,
                        default=Path.home() / '.push_service' / 'logs')
    parser.add_argument('--host', help='host server address {subscription,webui}', type=str, default='127.0.0.1')
    parser.add_argument('--port', help='host server port {subscription,webui}', type=int, default=8000)
    parser.add_argument('--ssl_certificate', help='SSL certificate file {subscription,webui}', type=str)
    parser.add_argument('--ssl_private_key', help='SSL private key file {subscription,webui}', type=str)
    parser.add_argument('--ssl_chain', help='SSL chain file {subscription,webui}', type=str)
    parser.add_argument('--enable_admin', help='enable admin features (login/logout, channel deletion) {webui}',
                        action='store_true')
    parser.add_argument('--enable_channel_creation', help='enable channel creation feature {webui}',
                        action='store_true')
    parser.add_argument('--otp_secret_file', help='path to file storing OTP secret (created if missing) {webui}',
                        type=str,
                        default=Path.home() / '.push_service' / 'otp_secret')
    parser.add_argument('--admin_password_file',
                        help='path to file storing admin password (created if missing) {webui}',
                        type=str,
                        default=Path.home() / '.push_service' / 'admin_password')
    # commands
    subparsers = parser.add_subparsers(dest='command', required=False, help='command to execute')
    subparsers.add_parser('list', help='list all channel names', add_help=False)
    create_parser = subparsers.add_parser('create', help='create a new channel', add_help=False)
    create_parser.add_argument('name', nargs='?',
                               help='name of the channel to create, if not given, a random name is generated')
    delete_parser = subparsers.add_parser('delete', help='delete a channel', add_help=False)
    delete_parser.add_argument('name', help='name of the channel to delete')
    subscription_parser = subparsers.add_parser('subscription', help='start a temporary webui for a channel',
                                                add_help=False)
    subscription_parser.add_argument('name', help='name of the channel to subscribe to')
    message_parser = subparsers.add_parser('message', help='send a message to a channel', add_help=False)
    message_parser.add_argument('name', help='name of the channel to send the message to')
    message_parser.add_argument('message', help='message to send to the channel')
    subparsers.add_parser('webui', help='start the full webui for the push service', add_help=False)
    subparsers.add_parser('iplist',
                          help='list the IPs of the host, to help choosing the host for webui and subscription commands',
                          add_help=False)

    # parse arguments
    args = parser.parse_args()

    # actions based on the command
    if args.command == 'list':
        # List all channels
        with PushService(db_url=args.db_url,
                         encryption_password=get_encryption_password(args.encryption_password_file),
                         push_service_email=args.push_service_email) as service:
            for channel in service.get_channels():
                print(f"{channel}")
    elif args.command == 'create':
        # Create a new channel
        if args.name is None:
            # Generate a random channel name if not provided
            print('Generating a random channel name...')
            channel_name = str(uuid.uuid4())
        else:
            channel_name = args.name
            if not channel_name.isidentifier() or len(channel_name) < 3 or len(channel_name) > 256:
                print(
                    f"Invalid channel name '{channel_name}'. Channel names must be alphanumeric and can include underscores.")
                exit(-1)
        with PushService(db_url=args.db_url,
                         encryption_password=get_encryption_password(args.encryption_password_file),
                         push_service_email=args.push_service_email) as service:
            try:
                service.add_channel(channel_name)
            except ValueError as e:
                print(f"Error creating channel '{channel_name}': {e}")
                exit(-1)
            print(f"Channel '{channel_name}' created successfully.")
    elif args.command == 'delete':
        # Delete a channel
        with PushService(db_url=args.db_url,
                         encryption_password=get_encryption_password(args.encryption_password_file),
                         push_service_email=args.push_service_email) as service:
            service.delete_channel(args.name)
    elif args.command == 'subscription':
        # Start a temporary webui for a channel
        with PushService(db_url=args.db_url,
                         encryption_password=get_encryption_password(args.encryption_password_file),
                         push_service_email=args.push_service_email) as service:
            push_service.webui.run_webui(service, host=args.host, port=args.port,
                            ssl_certificate=args.ssl_certificate, ssl_private_key=args.ssl_private_key,
                            ssl_chain=args.ssl_chain, log_dir=args.log_dir, enabled_channels=[args.name],
                            enable_channel_creation=False, enable_admin=False,
                            otp_secret_file=args.otp_secret_file,
                            admin_password_file=args.admin_password_file,
                            stop_function=lambda: input("Press Enter to stop the subscription webui..."))
            print("Subscription webui closed")
    elif args.command == 'message':
        # Send a message to a channel
        with PushService(db_url=args.db_url,
                         encryption_password=get_encryption_password(args.encryption_password_file),
                         push_service_email=args.push_service_email) as service:
            try:
                service.send_message(args.name, args.message, 'cli')
            except ValueError as e:
                print(f"Error sending message to channel '{args.name}': {e}")
                exit(-1)
            print(f"Message sent to channel '{args.name}': {args.message}")
    elif args.command == 'webui':
        # Start the full webui for the push service
        with PushService(db_url=args.db_url,
                         encryption_password=get_encryption_password(args.encryption_password_file),
                         push_service_email=args.push_service_email) as service:
            push_service.webui.run_webui(service, host=args.host, port=args.port, ssl_certificate=args.ssl_certificate,
                            ssl_private_key=args.ssl_private_key, ssl_chain=args.ssl_chain,
                            log_dir=args.log_dir, enable_admin=args.enable_admin,
                            enable_channel_creation=args.enable_channel_creation,
                            otp_secret_file=args.otp_secret_file,
                            admin_password_file=args.admin_password_file)
    elif args.command == 'iplist':
        # List available IP addresses. Utilized to help users choose the host for webui and subscription commands.
        print("Available IP addresses:")
        for interface_name, address in push_service.available_addresses.list_available_addresses():
            print(f"{interface_name}: {address}")
    else:
        # If no command is given, print the help message
        _HelpAction(None)(parser, None, None)


if __name__ == '__main__':
    main()
