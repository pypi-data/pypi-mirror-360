# Push Service

Push Service is a Python implementation of the [Push API](https://www.w3.org/TR/push-api/).

It allows users to create push channels, subscribe to them, and send notifications. The service is designed to be flexible, implementing both a command line interface and a web user interface.

It includes a web user interface inspired to notify.run, but its main design feature is the separation of the subscription web interface from the notification logic. 
This allows users to send notifications without requiring a running web server.

The web interface supports SSL, which is required to enable subscriptions to servers listening on non-localhost addresses.

## Installation

```bash
pip install push_service
```

## Features and Commands

### Managing channels

Channels can be created, listed, and deleted using the command line interface. The commands are as follows:

```bash
push_service list
push_service create my_channel
push_service delete my_channel
```
### Subscriptions
Subscriptions to channels can be managed using the `subscription` command. This command starts a temporary web interface for subscribing to a specific channel:

```bash
push_service subscription my_channel
```
```commandline
Push service webui enabled for subscription to the following channels:
http://127.0.0.1:8000/my_channel

    █▀▀▀▀▀█    █ █▄▄▀██▀▄ █▀▀▀▀▀█    
    █ ███ █  █▀ ▀█▄▄▀▀▄▀▀ █ ███ █    
    █ ▀▀▀ █ ▄▄ ▄ ██ ▀▀ ▄█ █ ▀▀▀ █    
    ▀▀▀▀▀▀▀ ▀▄▀ █ █ ▀▄█ ▀ ▀▀▀▀▀▀▀    
    █  █▄█▀ █ █ ▀ ▄█ ▀▄ ▀█▄█ ▄  ▄    
    ▄▀▀██ ▀ ▄▄▀▄  ▄▄▀▀▄████ ▀███     
     ▄▀▄ ▀▀█▀▄▀▀   ▄▀█ ▄  ▀█ ▀▄▀▀    
    ▀▀▄▄▄▀▀█▀█▀▄█▄▄▀█▄█▄ ▄▀▀▄▄▀█▀    
    ▀▀▀▀▄ ▀ █▄▄█▀▀▀█ █ ▀▄▄▄  ▀ ▀▄    
    ▀ ▀█  ▀▀██ █▀█ ▄▀▄▀ ▀█ ▀ ▀ ██    
    ▀ ▀ ▀ ▀ ▄▀█  ▄▀▀█▄ ▀█▀▀▀█ █▄▄    
    █▀▀▀▀▀█ ▄██▄▀█▀▄█ █▄█ ▀ █▄▄█     
    █ ███ █ ▄▄█▀█ █ ▀▀  ███▀█▀ ▄▀    
    █ ▀▀▀ █   ▀ ██▄ █▄  ██ ███ ▄▀    
    ▀▀▀▀▀▀▀ ▀▀▀▀▀▀ ▀ ▀ ▀▀▀  ▀  ▀     
                                     
Press Enter to stop the subscription webui...
```

This command will start a web server that allows users to subscribe to the specified channel. 
The web interface will be available at `http[s]://<host>:<port>/subscribe/my_channel`, where `<host>` and `<port>` are specified by the `--host` and `--port` parameters, respectively.

The web interface supports SSL, which is required to enable subscriptions to URLs different from localhost.
SSL certificates must be provided by the user, and can be specified using the `--ssl_certificate`, `--ssl_private_key`, and `--ssl_chain` parameters.

Subscription is the only moment when the web server is required.
Once a device is subscribed to a channel, it can receive messages even if the web server is not running, as the logic for sending messages is independent of the web interface.
#### IP list
To help users choose the host for the web interface and subscription commands, the `iplist` command can be used to list the IP addresses of the host:

```bash
push_service iplist
```
```commandline
Available IPs for the host:
Available IP addresses:
All IPV4 interfaces: 0.0.0.0
All IPV6 interfaces: ::
Ethernet: xxx.yyy.wwww.zzz
Ethernet: [xxxx:yyyy:ww:zz:xxxx:yyyy:wwww:zzzz]
Wi-Fi: xxx.yyy.wwww.zzz
Wi-Fi: [xxxx:yyyy:ww:zz:xxxx:yyyy:wwww:zzzz]
...
```

### Push messages

Pushing a message requires only the access to the database file and the encryption password. 
No web server is required to send messages, which makes it easy to integrate the push service into other applications.

```bash
push_service message my_channel "Hello, world!"
```

#### JSON messages
Messages can be sent as simple text string or in **JSON format**, allowing for structured data to be pushed to subscribers. The message should be a valid JSON string in the following format:

```json
{
  "title": "Notification Title",
  "body": "Notification Body",
  "icon": "https://example.com/icon.png",
  "url": "https://example.com"
}
```

### Web user interface
This package also implement a complete web user interface in the style of the notify.run website, allowing users to create channels, subscribe to thems and sending notification messages.

It can be started using the `webui` command:

```bash
push_service webui
```

The web interface can be configured to enable admin features (login/logout, channel deletion) and channel creation by setting the `--enable_admin` and `--enable_channel_creation` parameters, respectively.

The admin account is protected by a password, which is asked at the first login and stored (crypted) in a file specified by the `--admin_password_file` parameter (or, by default in the `.push_service/admin_password` file in user's home directory).
A two-factor authentication is mandatory, based on a one-time password (OTP) stored in a file specified by the `--otp_secret_file` parameter (or, by default in the `.push_service/otp_secret` file in user's home directory).
The OTP secret is created if it does not exist and shown at the first login as a QR code in the web interface, so that it can be scanned by an authenticator app (e.g., Google Authenticator, Authy).
In the case of losing the OTP authentication access, deleting the OTP secret file will present the admin with a new QR code at the next login.
**Keep the access to the password and otp files safe and limited to ensure the security of admin access!**

### Database
The data related to the channels is stored in a SQLite database file, which by default is named `channels.db` and it is stored in the `.push_service` subdirectory of user's home directory.
Thanks to the use of SQLAlchemy, the actual database can be replaced with many other database types by changing the `--db_url` parameter.

#### Database encryption
The data in the database is encrypted using a password stored in a file, which is created if it does not exist.
The password file is created by default as `.push_service/channel_db_encryption_password` in the user's home directory, but it can be changed using the `--encryption_password_file` parameter.
**Keep the access to this file safe and limited to ensure the security of your channels!**

### Configuration file

Command-line arguments can be set in a configuration file, which allows for easier management of the service settings. 
Any `--` prefixed argument can be set in the configuration file, which is then passed to the `push_service` command using the `-c` or `--config` option.

An example of configuration file setting all the parameters is as follows:
```yaml
db_url = sqlite:///my_dir/channels.db
encryption_password_file = /my_dir/channel_db_encryption_password
push_service_email = push_service@example.com
log_dir = /my_dir/logs
host = 192.168.0.1
port = 9876
otp_secret_file = /my_dir/otp_secret
admin_password_file = /my_dir/admin_password
ssl_certificate = /my_dir/server-crt.pem
ssl_chain = /my_dir/server-chain.pem
ssl_private_key = /my_dir/server-key.pem
```

Usage of the configuration file:
```bash
push_service -c config_file.yaml webui
```

## Help message

This is the help message for the `push_service` command, which details the available commands and options:

```bash
push_service -h
```
```
usage: push_service [-h] [-c CONFIG] [-s SAVE] [--db_url DB_URL] [--encryption_password_file ENCRYPTION_PASSWORD_FILE] [--push_service_email PUSH_SERVICE_EMAIL] [--log_dir LOG_DIR] [--host HOST] [--port PORT] [--ssl_certificate SSL_CERTIFICATE] [--ssl_private_key SSL_PRIVATE_KEY]
                    [--ssl_chain SSL_CHAIN] [--enable_admin] [--enable_channel_creation] [--otp_secret_file OTP_SECRET_FILE] [--admin_password_file ADMIN_PASSWORD_FILE]
                    {list,create,delete,subscription,message,webui,iplist} ...

positional arguments:
  {list,create,delete,subscription,message,webui,iplist}
                        command to execute
    list                list all channel names
    create              create a new channel
    delete              delete a channel
    subscription        start a temporary webui for a channel
    message             send a message to a channel
    webui               start the full webui for the push service
    iplist              list the IPs of the host, to help choosing the host for webui and subscription commands

options:
  -h, --help            print a detailed help message
  -c CONFIG, --config CONFIG
                        read configuration from a file (default: None)
  -s SAVE, --save SAVE  saves configuration to a file (default: None)
  --db_url DB_URL       database connection string (default: sqlite:////home/user/.push_service/channels.db)
  --encryption_password_file ENCRYPTION_PASSWORD_FILE
                        file storing the encryption password (created if missing) (default: /home/user/pushservice/channels_db_encryption_password)
  --push_service_email PUSH_SERVICE_EMAIL
                        email address associated with the push service (default: push_service@example.com)
  --log_dir LOG_DIR     local directory for log files {subscription,webui} (default: D:\Users\esuli\Documents\Software\push_service\push_service_logs)
  --host HOST           host server address {subscription,webui} (default: 127.0.0.1)
  --port PORT           host server port {subscription,webui} (default: 8000)
  --ssl_certificate SSL_CERTIFICATE
                        SSL certificate file {subscription,webui} (default: None)
  --ssl_private_key SSL_PRIVATE_KEY
                        SSL private key file {subscription,webui} (default: None)
  --ssl_chain SSL_CHAIN
                        SSL chain file {subscription,webui} (default: None)
  --enable_admin        enable admin features (login/logout, channel deletion) {webui} (default: False)
  --enable_channel_creation
                        enable channel creation feature {webui} (default: False)
  --otp_secret_file OTP_SECRET_FILE
                        path to file storing OTP secret (created if missing) {webui} (default: /home/user/.push_service/otp_secret)
  --admin_password_file ADMIN_PASSWORD_FILE
                        path to file storing admin password (created if missing) {webui} (default: /home/user/.push_service/admin_password)

Args that start with '--' can also be set in a config file (specified via -c). Config file syntax allows: key=value, flag=true, stuff=[a,b,c] (for details, see syntax at https://goo.gl/R74nmi). In general, command-line values override config file values which override defaults.

Command 'list'
usage: push_service list

Command 'create'
usage: push_service create [name]

positional arguments:
  name  name of the channel to create, if not given, a random name is generated

Command 'delete'
usage: push_service delete name

positional arguments:
  name  name of the channel to delete

Command 'subscription'
usage: push_service subscription name

positional arguments:
  name  name of the channel to subscribe to

Command 'message'
usage: push_service message name message

positional arguments:
  name     name of the channel to send the message to
  message  message to send to the channel

Command 'webui'
usage: push_service webui

Command 'iplist'
usage: push_service iplist
```

## License

See the [LICENSE](LICENSE) file.
```