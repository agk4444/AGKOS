# AGK Language Compiler

A revolutionary compiler that combines the best features of C++, Java, and Python with natural language syntax.

## Vision

AGK (pronounced "awk") is a programming language that aims to be:
- **Powerful**: Combines performance of C++, safety of Java, and expressiveness of Python
- **Natural**: Uses English-like syntax that's intuitive to read and write
- **Modern**: Supports contemporary programming paradigms and best practices

## Target Language Features

### From Python
- Simple, clean syntax
- Dynamic typing with optional type hints
- List comprehensions and generator expressions
- Decorators and context managers
- Duck typing philosophy

### From Java
- Strong static typing system
- Interface-based programming
- Exception handling with checked exceptions
- Package/namespace system
- Automatic memory management

### From C++
- Template metaprogramming
- Operator overloading
- Multiple inheritance
- Performance optimizations
- Low-level system access (when needed)

## Natural Language Syntax Examples

Instead of:
```python
def calculate_total(items):
    total = 0
    for item in items:
        total += item
    return total
```

You would write:
```
define function calculate_total that takes items:
    create total as 0
    for each item in items:
        add item to total
    return total
```

Instead of:
```java
public class Person implements Serializable {
    private String name;
    private int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String getName() {
        return name;
    }
}
```

You would write:
```
define class Person that implements Serializable:
    private name as String
    private age as Integer

    define constructor that takes name as String, age as Integer:
        set this name to name
        set this age to age

    define function get_name that returns String:
        return this name
```

## Architecture

The compiler consists of several key components:
1. **Natural Language Lexer**: Tokenizes English-like syntax
2. **Natural Language Parser**: Parses tokens into an Abstract Syntax Tree
3. **Semantic Analyzer**: Performs type checking and validation
4. **Code Generator**: Generates optimized target code
5. **Symbol Table**: Manages variables, functions, and types
6. **Error Reporter**: Provides clear, helpful error messages

## Standard Library System

AGK includes a comprehensive standard library system with **7 powerful libraries**:

### Core Libraries
- **`math`**: Mathematical functions (`sqrt`, `absolute`, `pi`, `e`)
- **`string`**: String manipulation (`length`, `uppercase`, `lowercase`)
- **`list`**: List operations (`create_list`, `append`, `length`)
- **`io`**: Input/output functions (`print`, `println`, `read_line`)

### Advanced Libraries
- **`llm`**: Large Language Model integration (GPT-4, Claude, Llama)
  - AI conversation management
  - Code generation and explanation
  - Text summarization and translation
  - Multiple model support

- **`gto`**: Game Theory Optimization algorithms
  - Nash equilibrium calculation
  - Prisoner's Dilemma utilities
  - Auction theory optimization
  - Evolutionary game theory simulation

- **`web`**: Full-stack web development
  - HTTP server creation and management
  - RESTful API development
  - HTML generation utilities
  - WebSocket support
  - Form handling and validation
  - Session management
  - File upload capabilities

## Library Usage Examples

### AI Integration
```agk
import llm

create client as LLMClient
set client to llm.create_llm_client("api_key", llm.gpt4())
create response as String
set response to llm.ask_llm(client, "Explain quantum physics")

create summary as String
set summary to llm.summarize_text(client, "Long article text...")
```

### Game Theory Analysis
```agk
import gto

create game as Game
set game to gto.create_prisoners_dilemma()
create equilibrium as List
set equilibrium to gto.find_nash_equilibrium(game)

create optimal_bid as Float
set optimal_bid to gto.calculate_optimal_bid(100.0, 3)
```

### Web Development
```agk
import web

create server as WebServer
set server to web.create_server(8080)
create route as Route
set route to web.create_route("/", "GET")
set server to web.add_route(server, route, my_handler)
web.start_server(server)
```

## Installation & Usage

### Quick Start
```bash
# Clone the repository
git clone https://github.com/hnethery/zen-mcp-modified.git
cd zen-mcp-modified

# Compile AGK code
python agk_compiler.py your_program.agk

# Start interactive REPL
python agk_compiler.py --repl
```

### Docker Support
```bash
# Build Docker image
docker build -t agk-compiler .

# Compile with Docker
docker run --rm -v $(pwd):/app/workspace agk-compiler python agk_compiler.py workspace/your_program.agk
```

## Architecture

The compiler consists of several key components:
1. **Natural Language Lexer**: Tokenizes English-like syntax
2. **Natural Language Parser**: Parses tokens into an Abstract Syntax Tree
3. **Semantic Analyzer**: Performs type checking and validation
4. **Code Generator**: Generates optimized Python code
5. **Symbol Table**: Manages variables, functions, and types
6. **Error Reporter**: Provides clear, helpful error messages
7. **Library System**: Comprehensive standard library with 7 modules

## Project Structure

```
AGK_language/
├── agk_compiler.py        # Main compiler entry point
├── agk_lexer.py          # Natural language lexer
├── agk_parser.py         # Parser with grammar rules
├── agk_ast.py           # AST data structures
├── agk_semantic.py      # Semantic analyzer + library imports
├── agk_codegen.py       # Python code generator
├── stdlib/              # Standard library modules
│   ├── math.agk         # Mathematical functions
│   ├── string.agk       # String operations
│   ├── list.agk         # List utilities
│   ├── io.agk           # Input/output functions
│   ├── llm.agk          # AI integration
│   ├── gto.agk          # Game theory
│   └── web.agk          # Web development
├── README.md            # This documentation
├── INSTALL.md           # Installation guide
├── Dockerfile           # Docker containerization
└── simple_test.agk      # Example programs
```

## Key Features

- ✅ **Natural Language Syntax**: English-like programming constructs
- ✅ **Multi-Paradigm Support**: Object-oriented, functional, procedural
- ✅ **Type Safety**: Optional type annotations with validation
- ✅ **Comprehensive Libraries**: 7 standard libraries for various domains
- ✅ **AI Integration**: Built-in LLM support for GPT-4, Claude, etc.
- ✅ **Game Theory**: Advanced optimization algorithms
- ✅ **Web Development**: Full-stack web application support
- ✅ **Cross-Platform**: Works on Windows, macOS, and Linux
- ✅ **Docker Support**: Containerized deployment
- ✅ **Interactive REPL**: Immediate code testing and experimentation

## Development Status

🎉 **This project is feature-complete and production-ready!**

**Core Compiler**: ✅ Complete (7/7 components)
**Standard Libraries**: ✅ Complete (4/4 core libraries)
**Advanced Libraries**: ✅ Complete (3/3 advanced libraries)
**Documentation**: ✅ Complete (README, INSTALL.md)
**Docker Support**: ✅ Complete
**Git Repository**: ✅ Complete with comprehensive commits

### Future Enhancements
- Enhanced error handling and reporting
- Additional test frameworks
- Extended REPL features
- Performance optimizations
- Community library contributions

The AGK Language Compiler transforms natural language programming into a powerful, modern development platform capable of building AI applications, game theory models, web services, and traditional software systems - all using intuitive English-like syntax!