"""
AGK Package Security and Verification System
Provides cryptographic signing, verification, and security scanning
"""

import os
import json
import hashlib
import base64
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import cryptography
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ed25519
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import cryptography.exceptions
import requests
from urllib.parse import urljoin

from agk_package import PackageManifest, PackageFile, PackageMetadata


class KeyManager:
    """Manages cryptographic keys for package signing"""

    def __init__(self, key_dir: str = None):
        if key_dir is None:
            key_dir = os.path.join(os.path.expanduser("~"), ".agk", "keys")

        self.key_dir = Path(key_dir)
        self.key_dir.mkdir(parents=True, exist_ok=True)
        self.private_key_path = self.key_dir / "private_key.pem"
        self.public_key_path = self.key_dir / "public_key.pem"

    def generate_keypair(self, passphrase: str = None) -> bool:
        """Generate RSA keypair for signing"""
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )

            # Serialize private key
            encryption = serialization.NoEncryption()
            if passphrase:
                encryption = serialization.BestAvailableEncryption(passphrase.encode())

            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption
            )

            # Serialize public key
            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            # Save keys
            with open(self.private_key_path, 'wb') as f:
                f.write(private_pem)

            with open(self.public_key_path, 'wb') as f:
                f.write(public_pem)

            return True

        except Exception as e:
            print(f"Error generating keypair: {e}")
            return False

    def load_private_key(self, passphrase: str = None) -> Optional[rsa.RSAPrivateKey]:
        """Load private key"""
        if not self.private_key_path.exists():
            return None

        try:
            with open(self.private_key_path, 'rb') as f:
                private_pem = f.read()

            password = passphrase.encode() if passphrase else None

            private_key = serialization.load_pem_private_key(
                private_pem,
                password=password
            )

            if isinstance(private_key, rsa.RSAPrivateKey):
                return private_key

        except Exception as e:
            print(f"Error loading private key: {e}")

        return None

    def load_public_key(self) -> Optional[rsa.RSAPublicKey]:
        """Load public key"""
        if not self.public_key_path.exists():
            return None

        try:
            with open(self.public_key_path, 'rb') as f:
                public_pem = f.read()

            public_key = serialization.load_pem_public_key(public_pem)

            if isinstance(public_key, rsa.RSAPublicKey):
                return public_key

        except Exception as e:
            print(f"Error loading public key: {e}")

        return None

    def get_public_key_fingerprint(self) -> Optional[str]:
        """Get SHA256 fingerprint of public key"""
        public_key = self.load_public_key()
        if not public_key:
            return None

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        fingerprint = hashlib.sha256(public_pem).hexdigest()
        return fingerprint


class PackageSigner:
    """Signs packages with cryptographic signatures"""

    def __init__(self, key_manager: KeyManager = None):
        self.key_manager = key_manager or KeyManager()

    def sign_package(self, package_path: str, passphrase: str = None) -> Optional[str]:
        """Sign a package and return signature"""
        private_key = self.key_manager.load_private_key(passphrase)
        if not private_key:
            print("No private key found. Generate one first with 'agk-pkg keygen'")
            return None

        try:
            with open(package_path, 'rb') as f:
                package_data = f.read()

            # Create signature
            signature = private_key.sign(
                package_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            # Encode signature as base64
            signature_b64 = base64.b64encode(signature).decode('utf-8')

            return signature_b64

        except Exception as e:
            print(f"Error signing package: {e}")
            return None

    def verify_signature(self, package_path: str, signature_b64: str) -> bool:
        """Verify package signature"""
        public_key = self.key_manager.load_public_key()
        if not public_key:
            print("No public key found")
            return False

        try:
            with open(package_path, 'rb') as f:
                package_data = f.read()

            # Decode signature
            signature = base64.b64decode(signature_b64)

            # Verify signature
            public_key.verify(
                signature,
                package_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            return True

        except cryptography.exceptions.InvalidSignature:
            print("Invalid signature")
            return False
        except Exception as e:
            print(f"Error verifying signature: {e}")
            return False


class SecurityScanner:
    """Scans packages for security vulnerabilities"""

    def __init__(self):
        self.vulnerability_database = self._load_vulnerability_db()

    def _load_vulnerability_db(self) -> Dict[str, Any]:
        """Load vulnerability database"""
        # This would typically load from a remote database
        # For now, return a basic set of patterns
        return {
            'patterns': {
                'hardcoded_secrets': [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'secret\s*=\s*["\'][^"\']+["\']',
                    r'api_key\s*=\s*["\'][^"\']+["\']',
                    r'token\s*=\s*["\'][^"\']+["\']'
                ],
                'dangerous_functions': [
                    r'eval\s*\(',
                    r'exec\s*\(',
                    r'execfile\s*\(',
                    r'pickle\.loads?\s*\(',
                    r'yaml\.load\s*\('
                ],
                'unsafe_imports': [
                    r'import\s+os\s*$',
                    r'import\s+subprocess\s*$',
                    r'import\s+sys\s*$',
                    r'from\s+os\s+import',
                    r'from\s+subprocess\s+import'
                ]
            },
            'risk_levels': {
                'hardcoded_secrets': 'HIGH',
                'dangerous_functions': 'HIGH',
                'unsafe_imports': 'MEDIUM'
            }
        }

    def scan_package(self, package_path: str) -> Dict[str, Any]:
        """Scan package for security vulnerabilities"""
        issues = []

        try:
            # Extract package to temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                import tarfile
                with tarfile.open(package_path, "r:gz") as tar:
                    tar.extractall(temp_dir)

                # Scan extracted files
                temp_path = Path(temp_dir)
                for agk_file in temp_path.glob("**/*.agk"):
                    file_issues = self._scan_file(agk_file)
                    if file_issues:
                        issues.extend(file_issues)

        except Exception as e:
            issues.append({
                'type': 'SCAN_ERROR',
                'severity': 'HIGH',
                'file': package_path,
                'message': f'Error scanning package: {e}'
            })

        # Calculate overall risk
        risk_score = self._calculate_risk_score(issues)

        return {
            'issues': issues,
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'scan_time': datetime.now().isoformat()
        }

    def _scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan individual file for vulnerabilities"""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            for vuln_type, patterns in self.vulnerability_database['patterns'].items():
                import re
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                    if matches:
                        issues.append({
                            'type': vuln_type,
                            'severity': self.vulnerability_database['risk_levels'].get(vuln_type, 'MEDIUM'),
                            'file': str(file_path),
                            'line': content.count('\n', 0, content.find(matches[0])) + 1,
                            'message': f'Potential security issue: {vuln_type.replace("_", " ")}',
                            'matches': matches[:3]  # Limit matches shown
                        })

        except Exception as e:
            issues.append({
                'type': 'FILE_SCAN_ERROR',
                'severity': 'LOW',
                'file': str(file_path),
                'message': f'Error scanning file: {e}'
            })

        return issues

    def _calculate_risk_score(self, issues: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score"""
        if not issues:
            return 0.0

        severity_weights = {
            'LOW': 1,
            'MEDIUM': 5,
            'HIGH': 10
        }

        total_score = sum(severity_weights.get(issue.get('severity', 'MEDIUM'), 5) for issue in issues)
        return min(total_score / len(issues), 10.0)  # Normalize to 0-10 scale

    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level from score"""
        if risk_score >= 7.0:
            return 'CRITICAL'
        elif risk_score >= 5.0:
            return 'HIGH'
        elif risk_score >= 3.0:
            return 'MEDIUM'
        else:
            return 'LOW'


class PackageVerifier:
    """Verifies package integrity and authenticity"""

    def __init__(self, key_manager: KeyManager = None):
        self.key_manager = key_manager or KeyManager()
        self.signer = PackageSigner(key_manager)

    def verify_package(self, package_path: str, signature: str = None,
                      expected_fingerprint: str = None) -> Dict[str, Any]:
        """Comprehensive package verification"""
        results = {
            'integrity_check': False,
            'signature_check': False,
            'fingerprint_check': False,
            'security_scan': {},
            'verified': False,
            'issues': []
        }

        try:
            # Check file integrity
            results['integrity_check'] = self._check_integrity(package_path)
            if not results['integrity_check']:
                results['issues'].append('Package integrity check failed')

            # Check signature if provided
            if signature:
                results['signature_check'] = self.signer.verify_signature(package_path, signature)
                if not results['signature_check']:
                    results['issues'].append('Package signature verification failed')

            # Check fingerprint if provided
            if expected_fingerprint:
                actual_fingerprint = self.key_manager.get_public_key_fingerprint()
                results['fingerprint_check'] = actual_fingerprint == expected_fingerprint
                if not results['fingerprint_check']:
                    results['issues'].append('Public key fingerprint mismatch')

            # Security scan
            scanner = SecurityScanner()
            scan_results = scanner.scan_package(package_path)
            results['security_scan'] = scan_results

            if scan_results['issues']:
                results['issues'].extend([issue['message'] for issue in scan_results['issues']])

            # Overall verification
            integrity_ok = results['integrity_check']
            signature_ok = signature is None or results['signature_check']
            fingerprint_ok = expected_fingerprint is None or results['fingerprint_check']
            security_ok = scan_results['risk_level'] in ['LOW', 'MEDIUM']

            results['verified'] = integrity_ok and signature_ok and fingerprint_ok and security_ok

        except Exception as e:
            results['issues'].append(f'Verification error: {e}')

        return results

    def _check_integrity(self, package_path: str) -> bool:
        """Check package file integrity"""
        try:
            # Calculate file hash
            with open(package_path, 'rb') as f:
                file_hash = hashlib.sha256()
                for chunk in iter(lambda: f.read(4096), b""):
                    file_hash.update(chunk)

            # Check if package is readable
            import tarfile
            with tarfile.open(package_path, "r:gz") as tar:
                tar.getmembers()  # Try to read archive structure

            return True

        except Exception:
            return False


class TrustManager:
    """Manages trusted publishers and keys"""

    def __init__(self, trust_dir: str = None):
        if trust_dir is None:
            trust_dir = os.path.join(os.path.expanduser("~"), ".agk", "trust")

        self.trust_dir = Path(trust_dir)
        self.trust_dir.mkdir(parents=True, exist_ok=True)
        self.trusted_keys_path = self.trust_dir / "trusted_keys.json"
        self.trusted_publishers_path = self.trust_dir / "trusted_publishers.json"

    def add_trusted_key(self, fingerprint: str, name: str, description: str = ""):
        """Add a trusted key fingerprint"""
        trusted_keys = self._load_trusted_keys()

        trusted_keys[fingerprint] = {
            'name': name,
            'description': description,
            'added_at': datetime.now().isoformat()
        }

        self._save_trusted_keys(trusted_keys)

    def remove_trusted_key(self, fingerprint: str):
        """Remove a trusted key"""
        trusted_keys = self._load_trusted_keys()
        if fingerprint in trusted_keys:
            del trusted_keys[fingerprint]
            self._save_trusted_keys(trusted_keys)

    def is_trusted_key(self, fingerprint: str) -> bool:
        """Check if a key fingerprint is trusted"""
        trusted_keys = self._load_trusted_keys()
        return fingerprint in trusted_keys

    def _load_trusted_keys(self) -> Dict[str, Any]:
        """Load trusted keys"""
        if not self.trusted_keys_path.exists():
            return {}

        try:
            with open(self.trusted_keys_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_trusted_keys(self, trusted_keys: Dict[str, Any]):
        """Save trusted keys"""
        with open(self.trusted_keys_path, 'w') as f:
            json.dump(trusted_keys, f, indent=2)


# Command-line interface
def main():
    """CLI for security tools"""
    import argparse

    parser = argparse.ArgumentParser(description="AGK Package Security Tools")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Key generation
    keygen_parser = subparsers.add_parser('keygen', help='Generate keypair')
    keygen_parser.add_argument('--passphrase', help='Key passphrase')

    # Signing
    sign_parser = subparsers.add_parser('sign', help='Sign a package')
    sign_parser.add_argument('package', help='Package file path')
    sign_parser.add_argument('--passphrase', help='Key passphrase')

    # Verification
    verify_parser = subparsers.add_parser('verify', help='Verify a package')
    verify_parser.add_argument('package', help='Package file path')
    verify_parser.add_argument('--signature', help='Package signature')
    verify_parser.add_argument('--fingerprint', help='Expected key fingerprint')

    # Security scan
    scan_parser = subparsers.add_parser('scan', help='Scan package for vulnerabilities')
    scan_parser.add_argument('package', help='Package file path')

    # Trust management
    trust_parser = subparsers.add_parser('trust', help='Manage trusted keys')
    trust_subparsers = trust_parser.add_subparsers(dest='trust_command')

    trust_add_parser = trust_subparsers.add_parser('add', help='Add trusted key')
    trust_add_parser.add_argument('fingerprint', help='Key fingerprint')
    trust_add_parser.add_argument('name', help='Key name')
    trust_add_parser.add_argument('--description', help='Key description')

    trust_remove_parser = trust_subparsers.add_parser('remove', help='Remove trusted key')
    trust_remove_parser.add_argument('fingerprint', help='Key fingerprint')

    trust_list_parser = trust_subparsers.add_parser('list', help='List trusted keys')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'keygen':
            key_manager = KeyManager()
            if key_manager.generate_keypair(args.passphrase):
                fingerprint = key_manager.get_public_key_fingerprint()
                print("✓ Keypair generated successfully")
                print(f"Public key fingerprint: {fingerprint}")
                print(f"Keys saved to: {key_manager.key_dir}")
            else:
                print("✗ Failed to generate keypair")

        elif args.command == 'sign':
            signer = PackageSigner()
            signature = signer.sign_package(args.package, args.passphrase)
            if signature:
                print("✓ Package signed successfully")
                print(f"Signature: {signature}")
            else:
                print("✗ Failed to sign package")

        elif args.command == 'verify':
            verifier = PackageVerifier()
            results = verifier.verify_package(args.package, args.signature, args.fingerprint)

            if results['verified']:
                print("✓ Package verification successful")
            else:
                print("✗ Package verification failed")

            print(f"Integrity check: {'✓' if results['integrity_check'] else '✗'}")
            print(f"Signature check: {'✓' if results['signature_check'] else '✗'}")
            print(f"Fingerprint check: {'✓' if results['fingerprint_check'] else '✗'}")

            if results['security_scan']['issues']:
                print(f"Security issues found: {len(results['security_scan']['issues'])}")
                print(f"Risk level: {results['security_scan']['risk_level']}")

            if results['issues']:
                print("\nIssues:")
                for issue in results['issues']:
                    print(f"  - {issue}")

        elif args.command == 'scan':
            scanner = SecurityScanner()
            results = scanner.scan_package(args.package)

            print(f"Security scan completed")
            print(f"Risk level: {results['risk_level']}")
            print(f"Risk score: {results['risk_score']:.1f}/10")

            if results['issues']:
                print(f"\nIssues found ({len(results['issues'])}):")
                for issue in results['issues']:
                    print(f"  {issue['severity']}: {issue['message']} ({issue['file']})")
            else:
                print("\nNo security issues found")

        elif args.command == 'trust':
            trust_manager = TrustManager()

            if args.trust_command == 'add':
                trust_manager.add_trusted_key(args.fingerprint, args.name, args.description or "")
                print(f"✓ Added trusted key: {args.fingerprint}")

            elif args.trust_command == 'remove':
                trust_manager.remove_trusted_key(args.fingerprint)
                print(f"✓ Removed trusted key: {args.fingerprint}")

            elif args.trust_command == 'list':
                trusted_keys = trust_manager._load_trusted_keys()
                if trusted_keys:
                    print("Trusted keys:")
                    for fingerprint, info in trusted_keys.items():
                        print(f"  {fingerprint}: {info['name']}")
                        if info['description']:
                            print(f"    {info['description']}")
                        print(f"    Added: {info['added_at']}")
                        print()
                else:
                    print("No trusted keys")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()