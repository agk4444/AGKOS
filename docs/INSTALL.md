# AGK Language Compiler - Installation & Usage Guide

A revolutionary compiler that transforms natural language programming into executable Python code, combining the best features of C++, Java, and Python.

## 🚀 Quick Start

### Prerequisites

- **Python 3.7+** (Python 3.8+ recommended)
- **Git** (for cloning the repository)
- **Command-line terminal** (Windows Command Prompt, PowerShell, Terminal, or bash)

### Optional Dependencies (for Standalone Builds)

For creating standalone executables that don't require Python:

```bash
# Install PyInstaller for single-executable builds
pip install "PyInstaller>=4.0"

# Install Nuitka for optimized native compilation
pip install "nuitka>=1.8.0"

# Install HTTP client for API features
pip install "requests>=2.25.0"

# Install cryptography for secure API key storage
pip install "cryptography>=3.4.0"

# Docker for containerized deployment
# Install Docker Desktop from https://docker.com
```

**Note:** All standalone build dependencies are included in `requirements.txt` for easy installation.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/agk4444/AGKCompiler.git
   cd AGKCompiler
   ```

2. **Install required dependencies:**
   ```bash
   pip install cryptography
   ```

   The API management features require the `cryptography` package for secure API key storage.

3. **Make the compiler executable (optional):**
   ```bash
   chmod +x agk_compiler.py
   ```

## 🚀 Standalone Executable Installation (No Python Required)

The AGK compiler can be built as standalone executables that don't require Python to be installed on the target system.

### Quick Standalone Build

1. **Install build dependencies:**
   ```bash
   # Install all build requirements (PyInstaller, Nuitka, requests, cryptography)
   pip install -r requirements.txt

   # Or install individually:
   # pip install "PyInstaller>=4.0" "nuitka>=1.8.0" "requests>=2.25.0" "cryptography>=3.4.0"
   ```

   **Required Dependencies:**
   - **PyInstaller** (>=4.0): Creates single-executable files
   - **Nuitka** (>=1.8.0): Optimized native compilation
   - **requests** (>=2.25.0): HTTP client for API features
   - **cryptography** (>=3.4.0): Secure API key storage

2. **Build standalone executable:**

   **Linux/macOS:**
   ```bash
   # Quick build script
   ./make_standalone.sh

   # Or run Python script directly
   python build_standalone.py
   ```

   **Windows:**
   ```cmd
   REM Using Command Prompt
   make_standalone.cmd

   REM Or using PowerShell
   .\make_standalone.ps1

   REM Or using Batch file
   make_standalone.bat

   REM Or run Python script directly
   python build_standalone.py
   ```

3. **Choose your build option:**
   - **PyInstaller**: Single executable file
   - **Nuitka**: Optimized native compilation
   - **Docker**: Containerized deployment
   - **Web Version**: Browser-based compiler

### Using Standalone Executables

#### PyInstaller Build
```bash
# After building, run without Python
./dist/agk_compiler your_program.agk

# On Windows
dist\agk_compiler.exe your_program.agk
```

#### Docker Build
```bash
# Build and run with Docker
docker run -v $(pwd):/app/workspace agk-compiler-standalone your_program.agk
```

#### Web Version
```bash
# Open in browser (no installation needed)
agk_compiler_web.html
```

## 🖥️ Operating System Development (NEW!)

The AGK compiler now supports **complete operating system development** with a C backend for system programming:

### OS Development Setup
```bash
# Install system development dependencies
pip install -r requirements.txt

# The C backend is included in the standard installation
# and supports building operating systems, kernels, and device drivers
```

### Building OS Components
```bash
# Compile bootloader with C backend
python agk_compiler.py bootloader_template.agk --backend c

# Compile kernel with C backend
python agk_compiler.py kernel_template.agk --backend c

# Compile device driver with C backend
python agk_compiler.py driver_template.agk --backend c
```

### OS Development Features
- **Complete C backend compilation** for system programming
- **Hardware access primitives** (I/O ports, CPU registers, interrupts)
- **Memory management** (allocation, deallocation, copying)
- **Kernel development** (modules, synchronization, memory management)
- **Device driver framework** (interrupt handling, I/O operations)
- **Build system integration** (Makefile, CMake, kernel module builds)

## 📦 Package Management System (NEW!)

The AGK compiler includes a comprehensive **package management system** for sharing, distributing, and managing libraries with professional-grade security and distribution features.

### Package Management Installation

The package management system is included in the standard AGK installation:

```bash
# Install AGK with all components including package management
pip install -r requirements.txt

# The package management tools are now available
agk-pkg --help
```

### Package Management Features

- **🔒 Security First**: RSA-based package signing with integrity verification
- **📋 Semantic Versioning**: Full support for version ranges (^1.0.0, ~1.2.0, etc.)
- **🔄 Dependency Resolution**: Automatic resolution of complex dependency trees
- **🌐 Registry System**: Local and remote package repositories
- **🛡️ Integrity Checks**: SHA256 verification and manifest validation
- **📊 Publishing Workflow**: Complete CI/CD-style package publishing
- **🧪 Validation Tools**: Pre-publish validation and testing
- **🔍 Discovery**: Package search and information tools

### Quick Package Management Start

```bash
# Initialize a new package
agk-pkg init my-awesome-package

# Install packages with dependencies
agk-pkg install web json@1.5.0 crypto

# Search for packages
agk-pkg search web-framework

# Build and publish
agk-pkg build
agk-pkg publish

# Security features
agk-pkg security keygen
agk-pkg security sign my-package-1.0.0.agk-pkg
```

### Package Management Commands

- **`agk-pkg init <name>`**: Initialize a new package
- **`agk-pkg install <packages>`**: Install packages with dependencies
- **`agk-pkg search <query>`**: Search for available packages
- **`agk-pkg build`**: Build your package for distribution
- **`agk-pkg publish`**: Publish package to registry
- **`agk-pkg security keygen`**: Generate RSA keys for signing
- **`agk-pkg security sign <package>`**: Sign a package with your key
- **`agk-pkg security verify <package>`**: Verify package signature

### Package Registry

The system supports both local and remote package registries:

- **Local Registry**: SQLite-based registry for development
- **Remote Registry**: REST API-based registry for distribution
- **Package Discovery**: Search and browse available packages
- **Version Management**: Semantic versioning with compatibility checking

### Standalone Installation Benefits

- ✅ **No Python Required**: Works on any system
- ✅ **Easy Distribution**: Single files or containers
- ✅ **Professional Appearance**: Native application feel
- ✅ **Cross-Platform**: Windows, macOS, Linux support
- ✅ **Multiple Options**: Choose your preferred deployment method
- ✅ **OS Development**: Build operating systems with C backend

## 🐳 Docker Installation (Alternative Method)

Docker provides a consistent environment across all platforms and eliminates dependency issues.

### Docker Prerequisites

- **Docker Desktop** or **Docker Engine**
- **Git** (for cloning the repository)

### Docker Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/agk4444/AGKCompiler.git
   cd AGKCompiler
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t agk-compiler .
   ```

   This will create a Docker image with all necessary dependencies and the AGK compiler ready to use.

3. **Verify the installation:**
   ```bash
   docker run --rm agk-compiler
   ```

   You should see the help information for the AGK compiler.

### Using Docker

#### Compile a Single File
```bash
docker run --rm -v $(pwd):/app/workspace agk-compiler python agk_compiler.py workspace/your_program.agk
```

#### Start Interactive REPL
```bash
docker run --rm -it agk-compiler python agk_compiler.py --repl
```

#### Save Generated Code to File
```bash
docker run --rm -v $(pwd):/app/workspace agk-compiler python agk_compiler.py workspace/input.agk workspace/output.py
```

#### Example Docker Session
```bash
# Create a simple AGK program
echo 'define function hello that returns String:
    return "Hello from Docker!"' > hello.agk

# Compile using Docker
docker run --rm -v $(pwd):/app/workspace agk-compiler python agk_compiler.py workspace/hello.agk

# Compile and save output
docker run --rm -v $(pwd):/app/workspace agk-compiler python agk_compiler.py workspace/hello.agk workspace/hello.py

# Run the generated Python code
python hello.py
```

### Docker Benefits

- **Consistent Environment**: Works identically on Windows, macOS, and Linux
- **No Dependencies**: All requirements are included in the container
- **Isolated**: Doesn't interfere with your system Python installation
- **Reproducible**: Same results every time
- **Easy Cleanup**: Remove the container when done

### Docker Troubleshooting

**Build Issues:**
```bash
# Force rebuild without cache
docker build --no-cache -t agk-compiler .

# View build logs
docker build -t agk-compiler . 2>&1 | tee build.log
```

**Permission Issues:**
```bash
# On Linux/Mac
sudo docker run --rm -v $(pwd):/app/workspace agk-compiler python agk_compiler.py workspace/your_program.agk

# On Windows (PowerShell)
docker run --rm -v ${PWD}:/app/workspace agk-compiler python agk_compiler.py workspace/your_program.agk
```

**Container Cleanup:**
```bash
# Remove the image
docker rmi agk-compiler

# Remove all unused containers
docker container prune

# Remove all unused images
docker image prune
```

## 📖 Usage

### Basic Compilation

Compile an AGK source file to Python:

```bash
python agk_compiler.py your_program.agk
```

This will:
- Parse your natural language code
- Perform semantic analysis
- Generate Python code
- Display the generated code in the terminal

### Save Output to File

Generate Python code and save it to a file:

```bash
python agk_compiler.py your_program.agk output.py
```

### Interactive REPL Mode

Start the interactive REPL for quick experimentation:

```bash
python agk_compiler.py --repl
```

In REPL mode, you can:
- Type natural language code directly
- Get immediate compilation results
- Test small code snippets
- Type `quit`, `exit`, or `q` to exit
- Type `help` or `h` for assistance

## 💡 Writing AGK Code

### Basic Function Definition

```agk
define function calculate_total that takes items:
    create total as Integer
    set total to 0
    return total
```

### Function with Return Type

```agk
define function greet that takes name as String and returns String:
    return "Hello, " + name + "!"
```

### Conditional Statements

```agk
define function check_number that takes n as Integer:
    if n is greater than 10:
        return "Big number!"
    else:
        return "Small number!"
```

### Loops

```agk
define function sum_list that takes numbers:
    create total as Integer
    for each number in numbers:
        set total to total + number
    return total
```

### Variable Declarations

```agk
define function example:
    create counter as Integer
    create message as String
    set counter to 42
    set message to "Hello World"
    return message
```

## 🔧 Advanced Usage

### Command-Line Options

| Option | Description |
|--------|-------------|
| `python agk_compiler.py source.agk` | Compile and display generated code |
| `python agk_compiler.py source.agk output.py` | Compile and save to file |
| `python agk_compiler.py --repl` | Start interactive REPL mode |
| `python agk_compiler.py --help` | Show help information |

### Understanding Compiler Output

When you compile AGK code, you'll see:

```
Compiling AGK source file: example.agk
==================================================
Phase 1: Lexical Analysis...
Phase 2: Parsing...
Phase 3: Semantic Analysis...
Phase 4: Code Generation...
Generated Code:
==================================================
def calculate_total(items):
    total: int
    total = 0
    return total
```

The compiler goes through four phases:
1. **Lexical Analysis**: Breaks code into tokens
2. **Parsing**: Builds Abstract Syntax Tree
3. **Semantic Analysis**: Type checking and validation
4. **Code Generation**: Produces Python code

### Error Handling

The compiler provides helpful error messages:

- **Syntax Errors**: Point to the exact location in your code
- **Semantic Errors**: Catch type mismatches and undefined variables
- **Warnings**: Alert you to potential issues (like unused variables)

## 📁 Project Structure

```
AGK_language/
├── README.md              # Project overview and features
├── INSTALL.md             # This installation guide
├── agk_compiler.py        # Main compiler entry point
├── agk_lexer.py          # Lexical analyzer
├── agk_parser.py         # Parser and grammar rules
├── agk_ast.py           # Abstract Syntax Tree definitions
├── agk_semantic.py      # Semantic analyzer
├── agk_codegen.py       # Code generator
├── agk_package.py       # Package management system (NEW!)
├── agk_registry.py      # Package registry (NEW!)
├── agk_pkg.py           # Package management CLI (NEW!)
├── agk_dependency_resolver.py # Dependency resolution (NEW!)
├── agk_publisher.py     # Package publishing (NEW!)
├── agk_security.py      # Package security (NEW!)
├── build_standalone.py   # Standalone executable build system
├── requirements.txt      # Build dependencies
├── make_standalone.sh    # Linux/macOS build script
├── make_standalone.bat   # Windows batch build script
├── make_standalone.cmd   # Windows CMD build script
├── make_standalone.ps1   # Windows PowerShell build script
├── make_standalone.sh    # Linux/macOS build script
├── make_standalone.bat   # Windows build script
├── simple_test.agk      # Simple example program
├── test_program.agk     # More complex example
├── debug_lexer.py       # Debugging utilities
├── stdlib/              # Standard library modules (22 libraries)
│   ├── database.agk     # SQLite database integration
│   ├── http.agk         # HTTP client for REST APIs
│   ├── fs.agk           # Advanced file system operations
│   ├── json.agk         # Enhanced JSON processing
│   ├── ui.agk           # User interface components
│   ├── network.agk      # Socket programming
│   ├── logging.agk      # Structured logging framework
│   ├── test.agk         # Unit testing framework
│   ├── stats.agk        # Statistics and data analysis
│   ├── regex.agk        # Regular expressions
│   ├── game.agk         # Game development framework
│   └── ...              # 11 more libraries
├── templates/           # Application templates
│   ├── desktop_app_template.agk      # Desktop applications
│   ├── web_app_template.agk          # Web applications
│   ├── server_api_template.agk       # REST API servers
│   ├── mobile_app_template.agk       # Mobile applications
│   ├── browser_app_template.agk      # Web browsers
│   ├── llm_template.agk              # AI applications
│   ├── general_template.agk          # Business applications
│   ├── database_template.agk         # Database demos
│   ├── http_template.agk             # HTTP client demos
│   ├── fs_template.agk               # File system demos
│   ├── ui_template.agk               # UI component demos
│   ├── test_template.agk             # Testing demos
│   ├── logging_template.agk          # Logging demos
│   ├── json_template.agk             # JSON processing demos
│   ├── network_template.agk          # Network demos
│   ├── regex_template.agk            # Regex demos
│   ├── stats_template.agk            # Statistics demos
│   └── game_template.agk             # Game demos
└── APP_TEMPLATES_README.md           # Templates usage guide
```

## 🐛 Troubleshooting

### Common Issues

**1. "Python not found" error**
- Ensure Python 3.7+ is installed
- Add Python to your system PATH
- Try `python3` instead of `python`

**2. "Permission denied" error**
- On Unix/Linux: `chmod +x agk_compiler.py`
- On Windows: Right-click the file and check "Run as administrator"

**3. "Module not found" errors**
- Ensure you're running from the project directory
- Check that all .py files are present

**4. Compilation errors**
- Check your AGK syntax against the examples
- Look at the line and column numbers in error messages
- Try the REPL mode for quick testing

**5. Standalone build issues**
- Ensure PyInstaller/Nuitka are installed: `pip install pyinstaller nuitka`
- Check Docker installation for container builds
- Verify write permissions in the output directory
- Try running with administrator privileges on Windows

### Getting Help

1. **REPL Help**: Type `help` in REPL mode
2. **Example Files**: Study `simple_test.agk` and `test_program.agk`
3. **Template Library**: Explore 19 professional templates for learning
4. **Library Demos**: Use `*_template.agk` files to learn each library
5. **Error Messages**: Read compiler error messages carefully
6. **Template Guide**: See `APP_TEMPLATES_README.md` for detailed template usage

## 🌟 Example Session

Here's a complete example of using the AGK compiler:

```bash
# 1. Create a simple AGK program
echo 'define function hello that returns String:
    return "Hello from AGK!"' > hello.agk

# 2. Compile it
python agk_compiler.py hello.agk

# 3. Save the generated Python code
python agk_compiler.py hello.agk hello.py

# 4. Run the generated Python code
python hello.py
```

## 🚀 Next Steps

After installation, you can:

1. **Try the examples**: Compile and run the provided example files
2. **Experiment in REPL**: Use `--repl` mode for quick testing
3. **Explore templates**: Use 19 professional templates to learn AGK features
4. **Learn libraries**: Study 11 library templates for each standard library
5. **Use package management**: Install and publish AGK packages with `agk-pkg`
5. **Build applications**: Start with application templates for common use cases
6. **Create standalone**: Build distributable executables with the standalone system
7. **Write your own programs**: Use the syntax examples above
8. **Contribute**: Help improve the compiler or add new features

## 📚 Template Ecosystem

The AGK Language now includes a comprehensive template ecosystem:

### Application Templates (10)
- **Desktop Apps**: Interactive GUI applications
- **Web Apps**: Full-stack web applications
- **API Servers**: REST API backend services
- **Mobile Apps**: Touch-based mobile applications
- **Browser Apps**: Custom web browser applications
- **AI Apps**: LLM-powered intelligent applications
- **Business Apps**: General-purpose business applications
- **OS Bootloader**: Complete x86 bootloader implementation
- **OS Kernel**: Full kernel framework with memory management
- **Device Drivers**: Hardware device driver templates

### Library Templates (11)
- **Database**: SQLite integration and CRUD operations
- **HTTP Client**: REST API operations and JSON handling
- **File System**: Advanced file operations and path management
- **UI Components**: Form creation and validation
- **Testing**: Unit testing and assertion frameworks
- **Logging**: Structured logging and performance monitoring
- **JSON**: Parsing, validation, and transformation
- **Network**: Socket programming and client-server apps
- **Regex**: Pattern matching and text processing
- **Statistics**: Data analysis and visualization
- **Game Development**: Entity-component system and game mechanics

### Learning Path
1. **Start with examples**: Use `simple_test.agk` and `test_program.agk`
2. **Learn libraries**: Study each `*_template.agk` file
3. **Build applications**: Use application templates for real projects
4. **Create distributables**: Use standalone build system for deployment

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Try the example programs to verify your setup
3. Use the REPL mode for quick experimentation
4. Review the generated Python code to understand compilation

## 🎉 Happy Coding!

The AGK Language Compiler is designed to make programming more intuitive and natural. Start with simple functions and gradually explore more advanced features. Your natural language code will be transformed into efficient, readable Python code!

For more information about AGK language features, see `README.md`.