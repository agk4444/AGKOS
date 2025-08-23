#!/usr/bin/env python3
"""
AGK Language System Programming AST Nodes

Extended AST nodes for operating system development, hardware access,
and low-level system programming constructs.
"""

from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from agk_ast import ASTNode, TypeNode, Parameter


@dataclass
class MemoryAllocate(ASTNode):
    """Memory allocation (malloc, kmalloc, etc.)"""
    size: ASTNode
    alignment: Optional[ASTNode] = None
    allocation_type: str = "heap"  # heap, stack, dma, kernel


@dataclass
class MemoryFree(ASTNode):
    """Memory deallocation (free, kfree, etc.)"""
    pointer: ASTNode


@dataclass
class MemoryCopy(ASTNode):
    """Memory copy operation (memcpy)"""
    destination: ASTNode
    source: ASTNode
    size: ASTNode


@dataclass
class MemorySet(ASTNode):
    """Memory set operation (memset)"""
    destination: ASTNode
    value: ASTNode
    size: ASTNode


@dataclass
class FileOpen(ASTNode):
    """File open operation"""
    filename: ASTNode
    flags: ASTNode
    mode: Optional[ASTNode] = None


@dataclass
class FileClose(ASTNode):
    """File close operation"""
    file_descriptor: ASTNode


@dataclass
class FileRead(ASTNode):
    """File read operation"""
    file_descriptor: ASTNode
    buffer: ASTNode
    count: ASTNode


@dataclass
class FileWrite(ASTNode):
    """File write operation"""
    file_descriptor: ASTNode
    buffer: ASTNode
    count: ASTNode


@dataclass
class FileSeek(ASTNode):
    """File seek operation"""
    file_descriptor: ASTNode
    offset: ASTNode
    whence: ASTNode


@dataclass
class ProcessCreate(ASTNode):
    """Process creation (fork, exec, etc.)"""
    command: ASTNode
    arguments: List[ASTNode]
    environment: Optional[List[ASTNode]] = None


@dataclass
class ProcessWait(ASTNode):
    """Process wait operation"""
    process_id: ASTNode
    status: Optional[ASTNode] = None


@dataclass
class ThreadCreate(ASTNode):
    """Thread creation"""
    function: ASTNode
    arguments: List[ASTNode]
    thread_id: Optional[ASTNode] = None


@dataclass
class ThreadJoin(ASTNode):
    """Thread join operation"""
    thread_id: ASTNode
    return_value: Optional[ASTNode] = None


@dataclass
class MutexCreate(ASTNode):
    """Mutex creation"""
    mutex: ASTNode
    attributes: Optional[ASTNode] = None


@dataclass
class MutexLock(ASTNode):
    """Mutex lock operation"""
    mutex: ASTNode


@dataclass
class MutexUnlock(ASTNode):
    """Mutex unlock operation"""
    mutex: ASTNode


@dataclass
class NetworkSocket(ASTNode):
    """Network socket creation"""
    domain: ASTNode  # AF_INET, AF_UNIX, etc.
    type: ASTNode    # SOCK_STREAM, SOCK_DGRAM, etc.
    protocol: ASTNode


@dataclass
class NetworkBind(ASTNode):
    """Network socket bind"""
    socket: ASTNode
    address: ASTNode
    address_len: ASTNode


@dataclass
class NetworkListen(ASTNode):
    """Network socket listen"""
    socket: ASTNode
    backlog: ASTNode


@dataclass
class NetworkAccept(ASTNode):
    """Network socket accept"""
    socket: ASTNode
    address: Optional[ASTNode] = None
    address_len: Optional[ASTNode] = None


@dataclass
class NetworkConnect(ASTNode):
    """Network socket connect"""
    socket: ASTNode
    address: ASTNode
    address_len: ASTNode


@dataclass
class NetworkSend(ASTNode):
    """Network send operation"""
    socket: ASTNode
    buffer: ASTNode
    length: ASTNode
    flags: Optional[ASTNode] = None


@dataclass
class NetworkReceive(ASTNode):
    """Network receive operation"""
    socket: ASTNode
    buffer: ASTNode
    length: ASTNode
    flags: Optional[ASTNode] = None


@dataclass
class SystemCall(ASTNode):
    """Direct system call"""
    call_number: ASTNode
    arguments: List[ASTNode]


@dataclass
class SystemInfo(ASTNode):
    """System information query"""
    info_type: str  # "uname", "sysinfo", "cpuinfo", etc.


@dataclass
class AtomicOperation(ASTNode):
    """Atomic operation"""
    operation: str  # "increment", "decrement", "add", "sub", "and", "or", "xor"
    target: ASTNode
    value: Optional[ASTNode] = None


@dataclass
class MemoryBarrier(ASTNode):
    """Memory barrier/fence"""
    barrier_type: str  # "read", "write", "full"


@dataclass
class InterruptHandler(ASTNode):
    """Interrupt handler definition"""
    interrupt_number: ASTNode
    handler_function: ASTNode
    flags: Optional[ASTNode] = None


@dataclass
class PortIO(ASTNode):
    """Port I/O operation (in/out instructions)"""
    operation: str  # "in", "out"
    port: ASTNode
    value: Optional[ASTNode] = None
    size: str = "byte"  # "byte", "word", "dword"


@dataclass
class MMIOAccess(ASTNode):
    """Memory-mapped I/O access"""
    address: ASTNode
    value: Optional[ASTNode] = None
    operation: str = "read"  # "read", "write"
    size: str = "dword"  # "byte", "word", "dword", "qword"


@dataclass
class DeviceRegister(ASTNode):
    """Device register access"""
    device: str
    register: str
    value: Optional[ASTNode] = None
    operation: str = "read"


@dataclass
class KernelModule(ASTNode):
    """Kernel module definition"""
    name: str
    init_function: Optional[ASTNode] = None
    exit_function: Optional[ASTNode] = None
    license: str = "GPL"
    author: Optional[str] = None
    description: Optional[str] = None


@dataclass
class KernelThread(ASTNode):
    """Kernel thread creation"""
    function: ASTNode
    data: Optional[ASTNode] = None
    name: Optional[str] = None


@dataclass
class WaitQueue(ASTNode):
    """Kernel wait queue operations"""
    operation: str  # "init", "wait", "wake_up", "wake_up_all"
    wait_queue: ASTNode
    condition: Optional[ASTNode] = None


@dataclass
class SpinlockOperation(ASTNode):
    """Spinlock operations"""
    operation: str  # "init", "lock", "unlock", "trylock"
    spinlock: ASTNode


@dataclass
class TimerOperation(ASTNode):
    """Kernel timer operations"""
    operation: str  # "init", "add", "del", "pending"
    timer: ASTNode
    expires: Optional[ASTNode] = None
    function: Optional[ASTNode] = None
    data: Optional[ASTNode] = None


@dataclass
class TaskletOperation(ASTNode):
    """Tasklet operations"""
    operation: str  # "init", "schedule", "kill"
    tasklet: ASTNode
    function: Optional[ASTNode] = None
    data: Optional[ASTNode] = None


@dataclass
class BootloaderEntry(ASTNode):
    """Bootloader entry point"""
    entry_function: ASTNode
    stack_size: Optional[ASTNode] = None
    heap_size: Optional[ASTNode] = None


@dataclass
class AssemblyBlock(ASTNode):
    """Inline assembly block"""
    assembly_code: str
    input_operands: List[ASTNode] = None
    output_operands: List[ASTNode] = None
    clobbered_registers: List[str] = None
    volatile: bool = False

    def __post_init__(self):
        if self.input_operands is None:
            self.input_operands = []
        if self.output_operands is None:
            self.output_operands = []
        if self.clobbered_registers is None:
            self.clobbered_registers = []


@dataclass
class RegisterAccess(ASTNode):
    """CPU register access"""
    register: str
    value: Optional[ASTNode] = None
    operation: str = "read"


@dataclass
class SystemProgrammingInclude(ASTNode):
    """System programming include directive"""
    include_type: str  # "header", "library", "module"
    name: str
    path: Optional[str] = None


# System programming function definitions
@dataclass
class SystemFunctionDef(ASTNode):
    """System programming function definition"""
    name: str
    parameters: List[Parameter]
    return_type: Optional[TypeNode]
    body: List[ASTNode]
    system_call_number: Optional[int] = None
    requires_privilege: bool = False
    interrupt_level: bool = False


@dataclass
class DriverDefinition(ASTNode):
    """Device driver definition"""
    name: str
    device_type: str  # "char", "block", "network", "usb", etc.
    major_number: Optional[ASTNode] = None
    minor_number: Optional[ASTNode] = None
    file_operations: Dict[str, ASTNode] = None

    def __post_init__(self):
        if self.file_operations is None:
            self.file_operations = {}


@dataclass
class InterruptRequest(ASTNode):
    """Interrupt request line operations"""
    operation: str  # "request", "free", "enable", "disable"
    irq_number: ASTNode
    handler: Optional[ASTNode] = None
    flags: Optional[ASTNode] = None
    device_name: Optional[str] = None


@dataclass
class DMAOperation(ASTNode):
    """Direct Memory Access operations"""
    operation: str  # "alloc", "free", "map", "unmap", "sync"
    channel: Optional[ASTNode] = None
    buffer: Optional[ASTNode] = None
    size: Optional[ASTNode] = None
    direction: Optional[str] = None


@dataclass
class PCIConfig(ASTNode):
    """PCI configuration space access"""
    operation: str  # "read", "write"
    bus: ASTNode
    device: ASTNode
    function: ASTNode
    register: ASTNode
    value: Optional[ASTNode] = None
    size: str = "dword"


@dataclass
class GPIOOperation(ASTNode):
    """General Purpose I/O operations"""
    operation: str  # "set_direction", "read", "write", "toggle"
    pin: ASTNode
    value: Optional[ASTNode] = None
    direction: Optional[str] = None


class SystemASTVisitor:
    """Visitor for system programming AST nodes"""

    def visit_memory_allocate(self, node: MemoryAllocate):
        pass

    def visit_memory_free(self, node: MemoryFree):
        pass

    def visit_memory_copy(self, node: MemoryCopy):
        pass

    def visit_memory_set(self, node: MemorySet):
        pass

    def visit_file_open(self, node: FileOpen):
        pass

    def visit_file_close(self, node: FileClose):
        pass

    def visit_file_read(self, node: FileRead):
        pass

    def visit_file_write(self, node: FileWrite):
        pass

    def visit_file_seek(self, node: FileSeek):
        pass

    def visit_process_create(self, node: ProcessCreate):
        pass

    def visit_process_wait(self, node: ProcessWait):
        pass

    def visit_thread_create(self, node: ThreadCreate):
        pass

    def visit_thread_join(self, node: ThreadJoin):
        pass

    def visit_mutex_create(self, node: MutexCreate):
        pass

    def visit_mutex_lock(self, node: MutexLock):
        pass

    def visit_mutex_unlock(self, node: MutexUnlock):
        pass

    def visit_network_socket(self, node: NetworkSocket):
        pass

    def visit_network_bind(self, node: NetworkBind):
        pass

    def visit_network_listen(self, node: NetworkListen):
        pass

    def visit_network_accept(self, node: NetworkAccept):
        pass

    def visit_network_connect(self, node: NetworkConnect):
        pass

    def visit_network_send(self, node: NetworkSend):
        pass

    def visit_network_receive(self, node: NetworkReceive):
        pass

    def visit_system_call(self, node: SystemCall):
        pass

    def visit_system_info(self, node: SystemInfo):
        pass

    def visit_atomic_operation(self, node: AtomicOperation):
        pass

    def visit_memory_barrier(self, node: MemoryBarrier):
        pass

    def visit_interrupt_handler(self, node: InterruptHandler):
        pass

    def visit_port_io(self, node: PortIO):
        pass

    def visit_mmio_access(self, node: MMIOAccess):
        pass

    def visit_device_register(self, node: DeviceRegister):
        pass

    def visit_kernel_module(self, node: KernelModule):
        pass

    def visit_kernel_thread(self, node: KernelThread):
        pass

    def visit_wait_queue(self, node: WaitQueue):
        pass

    def visit_spinlock_operation(self, node: SpinlockOperation):
        pass

    def visit_timer_operation(self, node: TimerOperation):
        pass

    def visit_tasklet_operation(self, node: TaskletOperation):
        pass

    def visit_bootloader_entry(self, node: BootloaderEntry):
        pass

    def visit_assembly_block(self, node: AssemblyBlock):
        pass

    def visit_register_access(self, node: RegisterAccess):
        pass

    def visit_system_programming_include(self, node: SystemProgrammingInclude):
        pass

    def visit_system_function_def(self, node: SystemFunctionDef):
        pass

    def visit_driver_definition(self, node: DriverDefinition):
        pass

    def visit_interrupt_request(self, node: InterruptRequest):
        pass

    def visit_dma_operation(self, node: DMAOperation):
        pass

    def visit_pci_config(self, node: PCIConfig):
        pass

    def visit_gpio_operation(self, node: GPIOOperation):
        pass