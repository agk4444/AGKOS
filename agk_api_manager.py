#!/usr/bin/env python3
"""
AGK Language API Key Management System

Secure management of API keys for external services like LLM providers.
"""

import os
import json
import base64
from typing import Dict, Optional, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class APIKeyManager:
    """Secure API key management system"""

    def __init__(self, storage_file: str = ".agk_api_keys"):
        self.storage_file = storage_file
        self.keys: Dict[str, str] = {}
        self.encryption_key = self._generate_encryption_key()
        self._load_keys()

    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key from system properties"""
        # Use system information to create a consistent key
        system_info = f"{os.name}-{os.getlogin()}-{os.getcwd()}"
        salt = b'agk_api_key_salt_2024'

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(system_info.encode()))

    def _load_keys(self):
        """Load encrypted API keys from storage"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'rb') as f:
                    encrypted_data = f.read()

                if encrypted_data:
                    cipher = Fernet(self.encryption_key)
                    decrypted_data = cipher.decrypt(encrypted_data)
                    self.keys = json.loads(decrypted_data.decode())
            except Exception as e:
                print(f"Warning: Could not load API keys: {e}")

    def _save_keys(self):
        """Save API keys to encrypted storage"""
        try:
            cipher = Fernet(self.encryption_key)
            data = json.dumps(self.keys).encode()
            encrypted_data = cipher.encrypt(data)

            with open(self.storage_file, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Warning: Could not save API keys: {e}")

    def set_key(self, service: str, api_key: str) -> bool:
        """Set API key for a service"""
        try:
            self.keys[service.lower()] = api_key
            self._save_keys()
            return True
        except Exception as e:
            print(f"Error setting API key: {e}")
            return False

    def get_key(self, service: str) -> Optional[str]:
        """Get API key for a service"""
        return self.keys.get(service.lower())

    def remove_key(self, service: str) -> bool:
        """Remove API key for a service"""
        try:
            if service.lower() in self.keys:
                del self.keys[service.lower()]
                self._save_keys()
                return True
            return False
        except Exception as e:
            print(f"Error removing API key: {e}")
            return False

    def list_services(self) -> List[str]:
        """List all services with stored keys"""
        return list(self.keys.keys())

    def has_key(self, service: str) -> bool:
        """Check if API key exists for service"""
        return service.lower() in self.keys

    def clear_all(self) -> bool:
        """Clear all stored API keys"""
        try:
            self.keys.clear()
            if os.path.exists(self.storage_file):
                os.remove(self.storage_file)
            return True
        except Exception as e:
            print(f"Error clearing API keys: {e}")
            return False

    def get_key_preview(self, service: str) -> Optional[str]:
        """Get preview of API key (first 8 chars + ...)"""
        key = self.get_key(service)
        if key and len(key) > 8:
            return key[:8] + "..."
        return key


class LLMProvider:
    """LLM provider configurations"""

    PROVIDERS = {
        'openai': {
            'name': 'OpenAI',
            'models': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'],
            'base_url': 'https://api.openai.com/v1',
            'auth_header': 'Bearer'
        },
        'anthropic': {
            'name': 'Anthropic',
            'models': ['claude-3-haiku', 'claude-3-sonnet', 'claude-3-opus'],
            'base_url': 'https://api.anthropic.com/v1',
            'auth_header': 'Bearer'
        },
        'google': {
            'name': 'Google AI',
            'models': ['gemini-pro', 'gemini-pro-vision'],
            'base_url': 'https://generativelanguage.googleapis.com/v1beta',
            'auth_header': 'Bearer'
        },
        'meta': {
            'name': 'Meta (Llama)',
            'models': ['llama-2-7b', 'llama-2-13b', 'llama-2-70b'],
            'base_url': 'https://api.meta.ai/v1',
            'auth_header': 'Bearer'
        }
    }

    @classmethod
    def get_provider_info(cls, service: str) -> Optional[Dict]:
        """Get provider information"""
        return cls.PROVIDERS.get(service.lower())

    @classmethod
    def list_providers(cls) -> List[str]:
        """List available providers"""
        return list(cls.PROVIDERS.keys())

    @classmethod
    def validate_model(cls, service: str, model: str) -> bool:
        """Validate if model is supported by provider"""
        provider = cls.get_provider_info(service)
        if provider:
            return model in provider['models']
        return False


class APIKeyValidator:
    """API key validation utilities"""

    @staticmethod
    def validate_openai_key(api_key: str) -> bool:
        """Validate OpenAI API key format"""
        return api_key.startswith('sk-') and len(api_key) > 20

    @staticmethod
    def validate_anthropic_key(api_key: str) -> bool:
        """Validate Anthropic API key format"""
        return api_key.startswith('sk-ant-') and len(api_key) > 30

    @staticmethod
    def validate_google_key(api_key: str) -> bool:
        """Validate Google AI API key format"""
        return len(api_key) > 20 and api_key.isalnum()

    @staticmethod
    def validate_key(service: str, api_key: str) -> bool:
        """Validate API key format for any service"""
        validators = {
            'openai': APIKeyValidator.validate_openai_key,
            'anthropic': APIKeyValidator.validate_anthropic_key,
            'google': APIKeyValidator.validate_google_key,
            'meta': lambda k: len(k) > 20
        }

        validator = validators.get(service.lower())
        if validator:
            return validator(api_key)
        return len(api_key) > 10  # Basic validation


# Global API key manager instance
api_manager = APIKeyManager()


def set_api_key(service: str, api_key: str) -> bool:
    """Set API key for a service (with validation)"""
    if not APIKeyValidator.validate_key(service, api_key):
        print(f"Warning: API key format may be invalid for {service}")

    success = api_manager.set_key(service, api_key)
    if success:
        print(f"API key set successfully for {service}")
    return success


def get_api_key(service: str) -> Optional[str]:
    """Get API key for a service"""
    return api_manager.get_key(service)


def remove_api_key(service: str) -> bool:
    """Remove API key for a service"""
    success = api_manager.remove_key(service)
    if success:
        print(f"API key removed for {service}")
    return success


def list_api_keys():
    """List all services with API keys"""
    services = api_manager.list_services()
    if not services:
        print("No API keys configured")
        return

    print("Configured API services:")
    for service in services:
        preview = api_manager.get_key_preview(service)
        print(f"  {service}: {preview}")


def clear_all_api_keys() -> bool:
    """Clear all API keys"""
    return api_manager.clear_all()


def setup_common_providers():
    """Setup configuration for common LLM providers"""
    print("Setting up common LLM providers...")
    print("Available providers:", ', '.join(LLMProvider.list_providers()))
    print("\nTo set an API key, use:")
    print("  set_api_key('openai', 'your-openai-api-key')")
    print("  set_api_key('anthropic', 'your-anthropic-api-key')")
    print("  etc.")


# Environment variable integration
def load_keys_from_environment():
    """Load API keys from environment variables"""
    env_mapping = {
        'OPENAI_API_KEY': 'openai',
        'ANTHROPIC_API_KEY': 'anthropic',
        'GOOGLE_AI_API_KEY': 'google',
        'META_API_KEY': 'meta'
    }

    loaded = []
    for env_var, service in env_mapping.items():
        if env_var in os.environ:
            api_key = os.environ[env_var]
            if set_api_key(service, api_key):
                loaded.append(service)

    if loaded:
        print(f"Loaded API keys from environment: {', '.join(loaded)}")


if __name__ == "__main__":
    # Load keys from environment on import
    load_keys_from_environment()

    # Setup for interactive use
    setup_common_providers()