# AGK Package Management System

A comprehensive package management system for the AGK programming language that provides dependency resolution, package distribution, security verification, and publishing tools.

## 🚀 Features

- **Package Creation & Building**: Create and build packages with metadata
- **Dependency Resolution**: Automatic resolution of package dependencies
- **Package Registry**: Local and remote package registries
- **Security & Verification**: Cryptographic signing and security scanning
- **Publishing Tools**: Complete workflow for package publishing
- **Command-Line Interface**: Easy-to-use CLI for all package operations

## 📦 Package Structure

An AGK package consists of:

```
my-package/
├── agk.toml          # Package metadata and configuration
├── README.md         # Package description
├── CHANGELOG.md      # Version history
├── src/              # Source files
│   └── main.agk
├── tests/            # Test files
│   └── test_main.agk
└── dist/             # Built packages (generated)
```

### agk.toml Configuration

```toml
[package]
name = "my-package"
version = "1.0.0"
description = "A useful AGK package"
author = "Your Name"
email = "your.email@example.com"
license = "MIT"
homepage = "https://example.com"
repository = "https://github.com/your/my-package"
keywords = ["utility", "helper"]
type = "library"  # library, application, template, or tool
agk-version = ">=1.0.0"
python-version = ">=3.8"
readme = "README.md"

[dependencies]
web = "^2.1.0"      # Compatible with 2.x versions
json = "~1.5.0"     # Compatible with 1.5.x versions
crypto = "*"        # Any version

[dev-dependencies]
test = "^1.0.0"     # Development dependencies

[entry-points]
main = "src/main.agk"

[files]
include = ["**/*.agk", "**/*.md", "LICENSE"]
exclude = ["**/*.pyc", "**/__pycache__/**", ".git/**"]
```

## 🛠️ Quick Start

### 1. Initialize a Package

```bash
# Create a new package
agk-pkg init my-package

# Or initialize in current directory
agk-pkg init
```

### 2. Build the Package

```bash
# Build for distribution
agk-pkg build
```

### 3. Install Packages

```bash
# Install from registry
agk-pkg install web
agk-pkg install json@1.5.0  # Specific version

# Install from local file
agk-pkg install ./my-package-1.0.0.agk-pkg

# Install with dependencies
agk-pkg install my-package  # Dependencies installed automatically
```

### 4. Publish a Package

```bash
# Set your registry API key
export AGK_REGISTRY_API_KEY=your_api_key_here

# Publish to registry
agk-pkg publish

# Or run the complete workflow
agk-pkg workflow
```

## 📋 Command Reference

### Package Management

```bash
agk-pkg init [name]          # Initialize new package
agk-pkg build               # Build package for distribution
agk-pkg install <package>   # Install a package
agk-pkg uninstall <package> # Uninstall a package
agk-pkg list                # List installed packages
agk-pkg info <package>      # Show package information
```

### Publishing

```bash
agk-pkg validate            # Validate package configuration
agk-pkg publish [package]   # Publish package to registry
agk-pkg workflow            # Complete publishing workflow
```

### Search & Discovery

```bash
agk-pkg search <query>      # Search for packages
```

### Security

```bash
agk-pkg security keygen                    # Generate signing keys
agk-pkg security sign <package>           # Sign a package
agk-pkg security verify <package>         # Verify package signature
agk-pkg security scan <package>           # Security vulnerability scan
agk-pkg security trust add <fp> <name>    # Add trusted key
```

## 🔒 Security Features

### Package Signing

```bash
# Generate keypair
agk-pkg security keygen

# Sign a package
agk-pkg security sign my-package-1.0.0.agk-pkg

# Verify signature
agk-pkg security verify my-package-1.0.0.agk-pkg --signature <signature>
```

### Security Scanning

```bash
# Scan for vulnerabilities
agk-pkg security scan my-package-1.0.0.agk-pkg

# Results show risk level and specific issues
```

### Trust Management

```bash
# Add trusted publisher
agk-pkg security trust add <fingerprint> "Trusted Publisher"

# List trusted keys
agk-pkg security trust list

# Remove trusted key
agk-pkg security trust remove <fingerprint>
```

## 📚 Advanced Usage

### Dependency Resolution

The system automatically resolves complex dependency trees:

```bash
# Install with all dependencies
agk-pkg install complex-app

# View dependency tree
agk-pkg info complex-app

# Export resolution for analysis
agk-pkg resolve complex-app --export resolution.json
```

### Version Management

```bash
# Install specific version
agk-pkg install my-package@2.1.0

# Install compatible version
agk-pkg install my-package@^2.0.0  # Latest 2.x
agk-pkg install my-package@~1.5.0  # Latest 1.5.x

# View available versions
agk-pkg info my-package
```

### Package Development

```bash
# Initialize with dependencies
agk-pkg init my-lib
echo 'web = "^2.0.0"' >> agk.toml
echo 'json = "*" ' >> agk.toml

# Run validation
agk-pkg validate

# Build and test
agk-pkg build
agk-pkg test

# Prepare for publishing
agk-pkg workflow --no-publish  # Validate, test, build without publishing

# Publish when ready
agk-pkg publish
```

## 🏗️ Architecture

The package management system consists of several components:

### Core Components

- **`agk_package.py`**: Package metadata and structure
- **`agk_registry.py`**: Local and remote package registries
- **`agk_pkg.py`**: Main command-line interface
- **`agk_dependency_resolver.py`**: Advanced dependency resolution
- **`agk_publisher.py`**: Publishing workflow and validation
- **`agk_security.py`**: Security and verification tools

### Package Registry

- **Local Registry**: SQLite database for installed packages
- **Remote Registry**: REST API for package distribution
- **Version Resolution**: Semantic versioning support
- **Dependency Graph**: Automatic dependency resolution

### Security System

- **Cryptographic Signing**: RSA-based package signatures
- **Security Scanning**: Vulnerability pattern detection
- **Trust Management**: Trusted publisher verification
- **Integrity Verification**: SHA256 checksum validation

## 📖 Examples

### Creating a Library Package

```bash
# Initialize
agk-pkg init my-math-lib

# Edit agk.toml
cat > agk.toml << EOF
[package]
name = "my-math-lib"
version = "1.0.0"
description = "Mathematical utilities for AGK"
author = "Math Expert"
license = "MIT"

[dependencies]
# No dependencies for this simple library
EOF

# Add source code
mkdir -p src tests

# Create main library file
cat > src/math.agk << EOF
define function fibonacci that takes n as Integer:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
EOF

# Create test file
cat > tests/test_math.agk << EOF
import test

define function test_fibonacci:
    create result as Integer = fibonacci(10)
    test.assert_equals(result, 55, "Fibonacci of 10 should be 55")
EOF

# Build and validate
agk-pkg build
agk-pkg validate

# Publish
agk-pkg publish
```

### Using the Library

```bash
# Install the library
agk-pkg install my-math-lib

# Use in your code
import my_math_lib

define function main:
    create fib_10 as Integer = fibonacci(10)
    io.print("Fibonacci(10) = " + fib_10)
```

## 🔧 Configuration

### Environment Variables

```bash
# Registry settings
AGK_REGISTRY_URL=https://registry.agk-lang.org
AGK_REGISTRY_API_KEY=your_api_key

# Author information
AGK_AUTHOR=Your Name
AGK_EMAIL=your.email@example.com

# Security settings
AGK_KEY_PASSPHRASE=your_key_passphrase

# Package directories
AGK_PACKAGE_DIR=~/.agk/packages
AGK_KEY_DIR=~/.agk/keys
```

### Registry Configuration

The default registry is `https://registry.agk-lang.org`. You can:

1. Use the default public registry
2. Set up a private registry
3. Use multiple registries

```bash
# Use custom registry
export AGK_REGISTRY_URL=https://my-registry.example.com
```

## 🐛 Troubleshooting

### Common Issues

**Package not found**
```bash
# Search for similar packages
agk-pkg search similar-name

# Check package name spelling
agk-pkg info package-name
```

**Dependency conflicts**
```bash
# View dependency tree
agk-pkg info package-name

# Try different version
agk-pkg install package-name@1.2.0
```

**Publishing fails**
```bash
# Validate first
agk-pkg validate

# Check API key
echo $AGK_REGISTRY_API_KEY

# Test with dry run
agk-pkg workflow --dry-run
```

### Getting Help

```bash
# Show help
agk-pkg --help

# Command-specific help
agk-pkg install --help
agk-pkg security --help

# Show package info
agk-pkg info package-name
```

## 🤝 Contributing

To contribute to the package management system:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Setup

```bash
# Clone and setup
git clone https://github.com/agk4444/AGKCompiler.git
cd AGKCompiler

# Install development dependencies
pip install cryptography requests toml semver

# Run tests
python -m pytest tests/

# Build package
agk-pkg build
```

## 📄 License

The AGK Package Management System is licensed under the MIT License. See the LICENSE file for details.

## 🆘 Support

- **Documentation**: [AGK Language Documentation](https://github.com/agk4444/AGKCompiler)
- **Issues**: [GitHub Issues](https://github.com/agk4444/AGKCompiler/issues)
- **Discussions**: [GitHub Discussions](https://github.com/agk4444/AGKCompiler/discussions)

## 🎯 Roadmap

Future enhancements:

- [ ] Private registry support
- [ ] Package analytics and insights
- [ ] Automated dependency updates
- [ ] Cross-platform package building
- [ ] IDE integration
- [ ] Package templates
- [ ] Community package ratings
- [ ] Advanced security features

---

**The AGK Package Management System provides a complete solution for package distribution, dependency management, and security verification, making it easy for developers to share and reuse AGK code while maintaining high standards of security and reliability.**