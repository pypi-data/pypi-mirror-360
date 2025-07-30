# Stack Trace Symbolication Fixes

This document details the improvements made to the stack trace symbolication functionality in the DeNet eBPF profiler. These changes address several issues that were causing empty user stack frames in profiler output.

## Problem

When capturing stack traces using the `OffCpuProfiler`, user stacks were consistently empty in the output JSON while kernel stacks were successfully captured. The error was occurring even for processes with debug symbols, which should have allowed proper symbolication.

**Symptoms:**

- User stack arrays were empty: `"user_stack": []`
- User stack IDs were showing error codes: `"user_stack_id": 4294967282` (which is u32::MAX - 13)
- The errors occurred even with properly compiled binaries containing debug symbols

## Root Causes

After investigation, we identified several issues:

1. **Error Code Handling**: The user stack ID value of 4294967282 corresponds to a negative error code (-14 or EFAULT) from the BPF system. This indicates a memory access issue during stack unwinding.

2. **Memory Map Timing**: When trying to symbolicate stack frames, the target process may have already exited by the time we attempt to read its `/proc/{pid}/maps`. This results in empty memory maps and prevents proper symbolication.

3. **Process ID Confusion**: The code was sometimes using the wrong PID when looking up memory maps, causing incorrect maps to be used for symbolication.

4. **Permission Issues**: Even with correct capabilities (`cap_bpf` and `cap_perfmon`), the eBPF subsystem might struggle to unwind stacks due to security restrictions.

5. **Error Reporting**: Stack trace errors were not properly captured and reported in the output, making debugging difficult.

## Implemented Fixes

### 1. Early Memory Map Caching

- Added a `MemoryMapCache` system to store process memory maps as soon as processes are monitored
- Implemented `add_pid_to_monitor` to dynamically add new PIDs discovered during profiling
- Pre-cache memory maps for all PIDs before attempting stack trace symbolication

### 2. Improved Error Handling

- Added proper conversion of BPF error codes from unsigned to signed integers
- Added error field reporting in the `ProcessedOffCpuEvent` structure:
  - `user_stack_error` and `kernel_stack_error` fields show details about stack trace failures
- Improved logging with specific error information for different error codes

### 3. Duplicate Code Removal and Validation

- Removed duplicate stack frame processing code
- Added validation for stack frame addresses to skip invalid pointers
- Added additional diagnostics to report empty stacks and other error conditions

### 4. Better Debugging Information

- Added detailed logging about memory map regions
- Added process and executable information to error reports
- Implemented a diagnostic script to test stack trace functionality

## Testing

The improvements can be tested using the included `test_stack_trace.sh` script, which:

1. Compiles the `test_native.c` program with debug symbols
2. Verifies proper capabilities for the DeNet binary
3. Runs the stack trace test to check for BPF compatibility
4. Runs the profiler against the test program
5. Analyzes the results for successful symbolication

```bash
# Run the test script
./test_stack_trace.sh
```

## Future Improvements

1. **Kernel Stack Symbolication**: Implement full symbolication for kernel stacks using `/proc/kallsyms`
2. **JIT Language Support**: Add special handling for interpreted languages like Python, Java, and Node.js
3. **Live Symbol Resolution**: Consider implementing a live symbol resolution service that doesn't rely on `/proc/{pid}/maps`
4. **Debug Symbol Caching**: Add caching of debug symbols from binaries to improve performance

## Debugging Stack Trace Issues

If you encounter stack trace issues, check the following:

1. **Capabilities**: Ensure the DeNet binary has proper capabilities:
   ```bash
   sudo setcap cap_bpf,cap_perfmon=ep ./target/debug/denet
   ```

2. **Kernel Parameters**: Check kernel security parameters:
   ```bash
   sysctl kernel.unprivileged_bpf_disabled
   sysctl kernel.perf_event_paranoid
   sysctl kernel.kptr_restrict
   ```

3. **Debug Symbols**: Ensure your target binaries have debug symbols:
   ```bash
   gcc -g -O0 -o my_program my_program.c
   ```

4. **Error Information**: Examine the `user_stack_error` and `kernel_stack_error` fields in the output JSON for specific error codes and messages.

5. **Run with Debug Mode**: Use the `--debug` flag to enable verbose logging:
   ```bash
   ./target/debug/denet --features ebpf --pid $TARGET_PID --debug
   ```
