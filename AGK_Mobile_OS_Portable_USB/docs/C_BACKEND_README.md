# AGK C Backend - System Programming Guide

The AGK C Backend enables system programming capabilities in the AGK language, allowing you to write low-level system software including operating systems, device drivers, and embedded applications.

## Features

### 🚀 System Programming Support
- **Native C Code Generation**: Converts AGK code to optimized C code
- **Hardware Access**: Direct access to CPU registers, I/O ports, and memory
- **Kernel Development**: Full support for OS kernel development
- **Device Drivers**: Template-based device driver development
- **Cross-Platform**: Support for Linux, Windows, macOS, and embedded systems

### 🔧 Core Components

#### 1. C Code Generator (`agk_c_codegen.py`)
- Converts AGK AST to native C code
- Supports all AGK language constructs
- Generates clean, readable C code
- Includes system-specific optimizations

#### 2. System Programming Extensions (`agk_system_ast.py`)
- Extended AST nodes for system programming
- Memory management operations
- Hardware I/O operations
- Kernel-level constructs

#### 3. Build System (`agk_c_build.py`)
- Makefile generation
- CMake integration
- Cross-compilation support
- Kernel module builds
- Bare-metal builds

#### 4. Main Backend (`agk_c_backend.py`)
- Complete compilation pipeline
- One-click build and run
- System programming mode
- Kernel development mode

## Quick Start

### Basic Usage

```python
from agk_c_backend import compile_agk_to_c_backend

# Compile AGK to C executable
backend = compile_agk_to_c_backend(
    agk_source="""
    define function main:
        print("Hello, System Programming!")
        return 0
    """,
    output_dir="system_program",
    project_name="hello_system",
    build_type="release",
    run_after_build=True
)
```

### System Programming Example

```python
import "os"
import "hardware"

define function system_program_main:
    # Memory allocation
    create buffer as pointer
    set buffer to memory_allocate(1024)

    # File operations
    create fd as int
    set fd to file_open("data.txt", O_CREAT | O_WRONLY)
    file_write(fd, "System programming with AGK!", 29)
    file_close(fd)

    # Hardware access (if available)
    create port_value as int
    set port_value to port_in(0x60)  # Read keyboard port

    # Atomic operations
    atomic_increment(shared_counter)

    memory_free(buffer)
    return 0
```

## System Libraries

### OS Library (`stdlib/os.agk`)
Provides standard operating system interfaces:

```python
# Memory Management
create buffer as pointer = memory_allocate(1024)
memory_free(buffer)

# File Operations
create fd as int = file_open("file.txt", O_RDONLY)
file_close(fd)

# Process Management
create pid as int = process_create("ls", ["-l"])
process_wait(pid)

# Threading
create thread_id as int = thread_create(worker_function, data)
thread_join(thread_id, null)

# Networking
create socket as int = network_socket(AF_INET, SOCK_STREAM, 0)
network_bind(socket, address, address_len)
```

### Kernel Library (`stdlib/kernel.agk`)
Kernel-level programming interfaces:

```python
# Kernel Module
module_init(my_init_function)
module_exit(my_exit_function)

# Memory Management
create kmem as pointer = kmalloc(4096, GFP_KERNEL)
kfree(kmem)

# Synchronization
spin_lock(&my_lock)
spin_unlock(&my_lock)

# Interrupts
request_irq(IRQ_KEYBOARD, keyboard_handler, 0, "keyboard", null)

# Kernel Printing
printk(KERN_INFO, "Kernel message: %s", "hello")
```

### Hardware Library (`stdlib/hardware.agk`)
Direct hardware access primitives:

```python
# CPU Registers
write_register(REG_EAX, 0x1234)
create eax_value as int = read_register(REG_EAX)

# I/O Ports
outb(0x60, 0xFF)  # Write to keyboard port
create keycode as int = inb(0x60)  # Read from keyboard port

# Assembly Blocks
execute_assembly("mov eax, 42", [], [output_register])

# Memory Barriers
memory_barrier()
atomic_increment(&counter)
```

## Development Templates

### Bootloader Template
The `bootloader_template.agk` provides a complete x86 bootloader:

```python
define function bootloader_entry:
    # Initialize hardware
    disable_interrupts()
    clear_screen()

    # Load kernel from disk
    load_kernel()

    # Switch to protected mode
    switch_to_protected_mode()

    # Jump to kernel
    jump_to_kernel()
```

### Kernel Template
The `kernel_template.agk` provides a basic kernel framework:

```python
define function kernel_main:
    # Initialize subsystems
    initialize_memory()
    initialize_interrupts()
    initialize_processes()

    # Start scheduler
    start_scheduler()
```

### Device Driver Template
The `driver_template.agk` provides a complete device driver framework:

```python
define function driver_init:
    # Register device
    register_chrdev(0, "mydevice", file_operations)

    # Set up interrupt handler
    request_irq(device_irq, device_handler, 0, "mydevice", null)

    return 0
```

## Build System

### Standard Build
```python
build_system = CBuildSystem("my_app")
build_system.add_source_file("main.c")
build_system.build_with_make("output")
```

### Kernel Module Build
```python
kernel_build = KernelBuildSystem("my_module")
kernel_build.set_kernel_source("/usr/src/linux")
kernel_build.build_with_make("output")
```

### Bare Metal Build
```python
bare_metal_build = BareMetalBuildSystem("firmware")
bare_metal_build.set_target_arch("arm")
bare_metal_build.set_linker_script("linker.ld")
bare_metal_build.build_with_make("output")
```

## Cross-Compilation

```python
backend = CBackend("cross_app")
backend.set_cross_compile("arm-linux-gnueabihf")
backend.add_library("m")  # Math library
backend.build_project()
```

## Advanced Features

### System Programming Mode
```python
backend = SystemProgrammingBackend("system_app")
backend.enable_system_extensions(True)
backend.create_kernel_module(agk_source, "/usr/src/linux")
```

### Hardware Access
```python
# Direct memory access
write_memory_byte(0xB8000, 'A')  # Write to video memory
write_memory_word(0xB8002, 0x1F41)  # Write colored character

# PCI Configuration
create device_id as int = pci_config_read(bus, device, 0, PCI_DEVICE_ID, 2)

# CPUID Instruction
create features as list = cpuid(CPUID_FEATURES, 0)
```

### Interrupt Handling
```python
# Register interrupt handler
request_irq(11, ethernet_handler, IRQF_SHARED, "ethernet", device)

# Interrupt service routine
define function device_interrupt:
    # Handle interrupt
    acknowledge_interrupt()
    wake_up(&wait_queue)
    return 1  # Handled
```

## Platform Support

### Linux
- Full system call support
- Kernel module development
- Device driver framework
- POSIX compliance

### Windows
- Win32 API integration
- DLL development
- Windows driver framework

### macOS
- Darwin kernel support
- IOKit integration
- Mach system calls

### Embedded Systems
- ARM Cortex-M support
- Bare-metal builds
- Custom linker scripts
- Startup code generation

## Examples

### Memory Management
```python
define function memory_demo:
    # Allocate memory
    create buffer as pointer = memory_allocate(1024)
    create kernel_buffer as pointer = kmalloc(4096, GFP_KERNEL)

    # Use memory
    memory_set(buffer, 0, 1024)
    memory_copy(kernel_buffer, buffer, 1024)

    # Free memory
    memory_free(buffer)
    kfree(kernel_buffer)
```

### Device Driver
```python
define function char_device_driver:
    module_init(driver_init)
    module_exit(driver_exit)

    define function driver_init:
        # Register character device
        register_chrdev(0, "mydev", file_ops)
        return 0

    define function driver_open:
        # Handle device open
        return 0
```

### System Call
```python
define function custom_system_call:
    create syscall_number as int = 350
    create result as int = system_call(syscall_number, [arg1, arg2])
    return result
```

## Best Practices

1. **Memory Management**: Always free allocated memory
2. **Synchronization**: Use appropriate locks for shared resources
3. **Interrupt Handling**: Keep interrupt handlers short and simple
4. **Error Handling**: Check return values and handle errors gracefully
5. **Documentation**: Document hardware interfaces and system calls

## Troubleshooting

### Common Issues

1. **Permission Denied**: Run with sudo for hardware access
2. **Kernel Panic**: Check interrupt handlers and memory management
3. **Build Failures**: Verify cross-compiler installation
4. **Runtime Errors**: Use debugging tools and printk statements

### Debugging

```python
# Kernel debugging
printk(KERN_DEBUG, "Variable value: %d", variable)

// System program debugging
print("Debug: entering function")
dump_stack()
```

## Contributing

To extend the C backend:

1. Add new AST nodes in `agk_system_ast.py`
2. Implement C code generation in `agk_c_codegen.py`
3. Add build system support in `agk_c_build.py`
4. Update documentation in this README

## License

The AGK C Backend is part of the AGK Language project and follows the same license terms.