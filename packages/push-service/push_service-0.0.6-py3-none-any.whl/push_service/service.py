import json
import os
from base64 import urlsafe_b64encode
from contextlib import contextmanager
from datetime import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, padding
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from py_vapid import Vapid
from pywebpush import webpush, WebPushException
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, create_engine, LargeBinary
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session, configure_mappers

Base = declarative_base()


class AESEncryption:
    """AES encryption/decryption using PBKDF2 for key derivation."""
    def __init__(self, password):
        if type(password) is not bytes:
            raise ValueError('Password must be bytes')
        self.password = password

    def _derive_key(self, salt):
        kdf = PBKDF2HMAC(
            algorithm=SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.password)

    def encrypt(self, data):
        if data is None:
            return None

        salt = os.urandom(16)
        iv = os.urandom(16)

        key = self._derive_key(salt)
        cipher = Cipher(AES(key), CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return salt + iv + ciphertext

    def decrypt(self, encrypted_data):
        if encrypted_data is None:
            return None
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]

        key = self._derive_key(salt)
        cipher = Cipher(AES(key), CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data


class Channel(Base):
    """Represents a channel for push notifications."""
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    vapid_public_key = Column(String, nullable=False)
    encrypted_vapid_private_key = Column(LargeBinary, nullable=False)

    subscriptions = relationship("Subscription", back_populates="channel")
    messages = relationship("Message", back_populates="channel")


class Subscription(Base):
    """Represents a subscription to a channel."""
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime, default=datetime.utcnow)
    ip = Column(String)
    encrypted_info = Column(LargeBinary, nullable=False)
    channel_id = Column(Integer, ForeignKey('channels.id'))
    channel = relationship("Channel", back_populates="subscriptions")


class Message(Base):
    """Represents a message sent to a channel."""
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime, default=datetime.utcnow)
    content = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    channel_id = Column(Integer, ForeignKey('channels.id'))
    channel = relationship("Channel", back_populates="messages")


class PushService:
    """Service for managing push notifications and subscriptions."""

    def __init__(self, db_url: str, encryption_password: str or bytes, push_service_email: str):
        """Initialize the PushService with a database URL and encryption password.
        :param db_url: The database URL for SQLAlchemy.
        :type db_url: str
        :param encryption_password: The password used for AES encryption.
        :type encryption_password: str or bytes
        :param push_service_email: The email address used for VAPID claims.
        :type push_service_email: str
        """
        self._engine = create_engine(db_url)
        if type(encryption_password) is str:
            encryption_password = encryption_password.encode('utf-8')
        self._encryption_password = encryption_password
        self.push_service_email = push_service_email
        self._aes_encryption = AESEncryption(encryption_password)
        Base.metadata.create_all(self._engine)
        self._sessionmaker = scoped_session(sessionmaker(bind=self._engine))
        configure_mappers()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._sessionmaker.session_factory.close_all()
        self._engine.dispose()

    @contextmanager
    def session_scope(self):
        session = self._sessionmaker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def add_channel(self, channel_name: str):
        """Add a new channel with a generated VAPID key pair.
        :param channel_name: The name of the channel to add.
        :type channel_name: str
        :raises ValueError: If the channel already exists.
        :return: None
        """
        with self.session_scope() as session:
            channel = session.query(Channel).filter_by(name=channel_name).first()
            if channel:
                raise ValueError('Channel already exists')

            vapid = ec.generate_private_key(ec.SECP256R1())
            vapid_public_key = urlsafe_b64encode(vapid.public_key().public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            )).decode('utf-8')
            encrypted_vapid_private_key = vapid.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(self._encryption_password)
            )

            channel = Channel(name=channel_name, vapid_public_key=vapid_public_key,
                              encrypted_vapid_private_key=encrypted_vapid_private_key)
            session.add(channel)

    def delete_channel(self, channel_name: str):
        """Delete a channel and all its subscriptions.
        :param channel_name: The name of the channel to delete.
        :type channel_name: str
        :return: None
        """
        with self.session_scope() as session:
            channel = session.query(Channel).filter_by(name=channel_name).first()
            if not channel:
                return

            session.delete(channel)

    def channel_exists(self, channel_name: str) -> bool:
        """Check if a channel exists.
        :param channel_name: The name of the channel to check.
        :type channel_name: str
        :return: True if the channel exists, False otherwise.
        """
        with self.session_scope() as session:
            return session.query(Channel).filter_by(name=channel_name).scalar()

    def get_channels(self) -> list:
        """Get a list of all channel names.
        :return: A list of channel names.
        :rtype: list
        """
        with self.session_scope() as session:
            return [channel.name for channel in session.query(Channel).all()]

    def add_subscription(self, channel_name: str, subscription_info: dict, request_ip):
        """Add a subscription to a channel.
        :param channel_name: The name of the channel to subscribe to.
        :type channel_name: str
        :param subscription_info: The subscription information (e.g., endpoint, keys).
        :type subscription_info: dict
        :param request_ip: The IP address of the requestor.
        :type request_ip: str
        :raises ValueError: If the channel does not exist.
        :return: None
        """
        with self.session_scope() as session:
            channel = session.query(Channel).filter_by(name=channel_name).first()
            if not channel:
                raise ValueError('Channel not found')
            encrypted_info = self._aes_encryption.encrypt(json.dumps(subscription_info).encode('utf-8'))
            subscription = Subscription(encrypted_info=encrypted_info, channel=channel, ip=request_ip)
            session.add(subscription)

    def delete_subscription(self, channel_name: str, subscription_info: dict):
        """Delete a subscription from a channel based on the subscription info.
        :param channel_name: The name of the channel.
        :type channel_name: str
        :param subscription_info: The subscription information to match.
        :type subscription_info: dict
        :return: None
        """
        with self.session_scope() as session:
            channel = session.query(Channel).filter_by(name=channel_name).first()
            if not channel:
                return
            to_delete = None
            for subscription in session.query(Subscription).filter_by(channel=channel):
                stored_subscription_info = json.loads(
                    self._aes_encryption.decrypt(subscription.encrypted_info).decode('utf-8'))
                if subscription_info == stored_subscription_info:
                    to_delete = subscription
                    break
            if not to_delete:
                return

            session.delete(to_delete)

    def delete_subscription_by_id(self, channel_name: str, subscription_id: str):
        """Delete a subscription from a channel based on the subscription ID.
        :param channel_name: The name of the channel.
        :type channel_name: str
        :param subscription_id: The ID of the subscription to delete.
        :type subscription_id: str
        :return: None
        """
        with self.session_scope() as session:
            channel = session.query(Channel).filter_by(name=channel_name).first()
            if not channel:
                return
            subscription = session.query(Subscription).filter_by(channel=channel, id=subscription_id).first()
            if not subscription:
                return
            session.delete(subscription)

    def get_subscriptions(self, channel_name: str) -> list:
        """Get all subscriptions for a channel.
        :param channel_name: The name of the channel.
        :type channel_name: str
        :return: A list of subscriptions, each represented as a dictionary with id, time, and ip.
        :rtype: list
        """
        with self.session_scope() as session:
            channel = session.query(Channel).filter_by(name=channel_name).first()
            if not channel:
                return []
            subscriptions = []
            for subscription in session.query(Subscription).filter_by(channel=channel):
                subscriptions.append({'id': subscription.id, 'time': subscription.time, 'ip': subscription.ip})
            return subscriptions

    def get_vapid_public_key(self, channel_name: str) -> str:
        """Get the VAPID public key for a channel.
        :param channel_name: The name of the channel.
        :type channel_name: str
        :return: The VAPID public key.
        :rtype: str
        """
        with self.session_scope() as session:
            channel = session.query(Channel).filter_by(name=channel_name).first()
            if not channel:
                raise ValueError('Channel not found')
            return channel.vapid_public_key

    def send_message(self, channel_name: str, content: str, sender: str, delete_subscription_on_410_error: bool =True):
        """Send a message to all subscribers of a channel.
        :param channel_name: The name of the channel to send the message to.
        :type channel_name: str
        :param content: The content of the message to send.
        :type content: str
        :param sender: The sender of the message.
        :type sender: str
        :param delete_subscription_on_410_error: Whether to delete subscriptions that return a 410 Gone error.
        :type delete_subscription_on_410_error: bool
        :raises ValueError: If the channel does not exist.
        :return: None
        """
        with self.session_scope() as session:
            channel = session.query(Channel).filter_by(name=channel_name).first()
            if not channel:
                raise ValueError('Channel not found')

            vapid_private_key = Vapid(
                serialization.load_pem_private_key(channel.encrypted_vapid_private_key, self._encryption_password))
            for subscription in channel.subscriptions:
                subscription_info = json.loads(
                    self._aes_encryption.decrypt(subscription.encrypted_info).decode('utf-8'))
                try:
                    webpush(
                        subscription_info=subscription_info,
                        data=content,
                        vapid_private_key=vapid_private_key,
                        vapid_claims={"sub": f"mailto:{self.push_service_email}"}
                    )
                except WebPushException as ex:
                    if ex.response.status_code == 410 and delete_subscription_on_410_error:
                        session.delete(subscription)
                    else:
                        print(f"Error: {ex}")

            message = Message(content=content, channel=channel, sender=sender)
            session.add(message)

    def get_messages(self, channel_name: str) -> list:
        """Get all messages sent to a channel.
        :param channel_name: The name of the channel to retrieve messages from.
        :type channel_name: str
        :raises ValueError: If the channel does not exist.
        :return: A list of messages, each represented as a dictionary with time, content, and sender.
        :rtype: list
        """
        with self.session_scope() as session:
            channel = session.query(Channel).filter_by(name=channel_name).first()
            if not channel:
                raise ValueError('Channel not found')
            return [{'time': msg.time.strftime("%Y%m%d%H%M%S"), 'content': msg.content, 'sender': msg.sender} for msg in
                    channel.messages]
