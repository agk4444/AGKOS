# AGK Language Compiler - Installation & Usage Guide

A revolutionary compiler that transforms natural language programming into executable Python code, combining the best features of C++, Java, and Python.

## 🚀 Quick Start

### Prerequisites

- **Python 3.7+** (Python 3.8+ recommended)
- **Git** (for cloning the repository)
- **Command-line terminal** (Windows Command Prompt, PowerShell, Terminal, or bash)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hnethery/zen-mcp-modified.git
   cd zen-mcp-modified
   ```

2. **No additional dependencies required!** The compiler is written in pure Python with no external dependencies.

3. **Make the compiler executable (optional):**
   ```bash
   chmod +x agk_compiler.py
   ```

## 🐳 Docker Installation (Alternative Method)

Docker provides a consistent environment across all platforms and eliminates dependency issues.

### Docker Prerequisites

- **Docker Desktop** or **Docker Engine**
- **Git** (for cloning the repository)

### Docker Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hnethery/zen-mcp-modified.git
   cd zen-mcp-modified
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
├── simple_test.agk      # Simple example program
├── test_program.agk     # More complex example
└── debug_lexer.py       # Debugging utilities
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

### Getting Help

1. **REPL Help**: Type `help` in REPL mode
2. **Example Files**: Study `simple_test.agk` and `test_program.agk`
3. **Error Messages**: Read compiler error messages carefully

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
3. **Write your own programs**: Use the syntax examples above
4. **Contribute**: Help improve the compiler or add new features

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Try the example programs to verify your setup
3. Use the REPL mode for quick experimentation
4. Review the generated Python code to understand compilation

## 🎉 Happy Coding!

The AGK Language Compiler is designed to make programming more intuitive and natural. Start with simple functions and gradually explore more advanced features. Your natural language code will be transformed into efficient, readable Python code!

For more information about AGK language features, see `README.md`.