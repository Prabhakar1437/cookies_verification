import json
import os
from django.conf import settings
from django.db import models
from cryptography.fernet import Fernet



class UserData(models.Model):
    username = models.CharField(unique=True, max_length=100, blank=False)
    password = models.CharField(max_length=256)  # Increased max_length for encoded password
    cookies = models.TextField(blank=False)

    @staticmethod
    def get_fernet():
        key = settings.ENCRYPTION_KEY.encode()
        return Fernet(key)

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.pk:  # Only encode password for new instances
            f = self.get_fernet()
            self.password = f.encrypt(self.password.encode()).decode()
        self._save_cookies_to_json()
        super().save(*args, **kwargs)

    def get_decoded_password(self):
        f = self.get_fernet()
        return f.decrypt(self.password.encode()).decode()

    def _save_cookies_to_json(self):
        cookies_dir = os.path.join(settings.BASE_DIR, 'user_cookies')
        if not os.path.exists(cookies_dir):
            os.makedirs(cookies_dir)
        file_path = os.path.join(cookies_dir, f'{self.username}_cookies.json')
        
        try:
            cookies_list = json.loads(self.cookies)
        except json.JSONDecodeError:
            cookies_list = []

        if not isinstance(cookies_list, list):
            cookies_list = [cookies_list]

        with open(file_path, 'w') as json_file:
            json.dump(cookies_list, json_file, indent=4)

    def __str__(self):
        return self.username