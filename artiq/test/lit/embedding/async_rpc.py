# RUN: env ARTIQ_DUMP_LLVM=%t %python -m artiq.compiler.testbench.embedding +compile %s
# RUN: OutputCheck %s --file-to-check=%t.ll

from artiq.language.core import *
from artiq.language.types import *

# CHECK: call void @send_async_rpc

@rpc(flags={"async"})
def foo():
    pass

@kernel
def entrypoint():
    foo()
