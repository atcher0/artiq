from llvm import core as lc
from llvm import target as lt

from artiq.compiler import ir_values

lt.initialize_all()

_syscalls = {
	"rpc":			"i+:i",
	"gpio_set":		"ii:n",
	"rtio_set":		"iii:n",
	"rtio_sync":	"i:n",
	"dds_program":	"ii:n",
}

def _str_to_functype(s):
	_chr_to_type = {
		"n": lc.Type.void,
		"i": lc.Type.int
	}
	assert(s[-2] == ":")
	type_ret = _chr_to_type[s[-1]]()

	var_arg_fixcount = None
	type_args = []
	for n, c in enumerate(s[:-2]):
		if c == "+":
			type_args.append(lc.Type.int())
			var_arg_fixcount = n
		else:
			type_args.append(_chr_to_type[c]())
	return var_arg_fixcount, lc.Type.function(type_ret, type_args, var_arg=var_arg_fixcount is not None)

class LinkInterface:
	def set_module(self, module):
		self.module = module
		self.var_arg_fixcount = dict()
		for func_name, func_type_str in _syscalls.items():
			var_arg_fixcount, func_type = _str_to_functype(func_type_str)
			if var_arg_fixcount is not None:
				self.var_arg_fixcount[func_name] = var_arg_fixcount
			self.module.add_function(func_type, "__syscall_"+func_name)

	def syscall(self, syscall_name, args, builder):
		_chr_to_value = {
			"n": ir_values.VNone,
			"i": ir_values.VInt
		}
		r = _chr_to_value[_syscalls[syscall_name][-1]]()
		if builder is not None:
			args = [arg.llvm_value for arg in args]
			if syscall_name in self.var_arg_fixcount:
				fixcount = self.var_arg_fixcount[syscall_name]
				args = args[:fixcount] \
					+ [lc.Constant.int(lc.Type.int(), len(args) - fixcount)] \
					+ args[fixcount:]
			llvm_function = self.module.get_function_named("__syscall_"+syscall_name)
			r.llvm_value = builder.call(llvm_function, args)
		return r

class Environment(LinkInterface):
	def __init__(self, ref_period):
		self.ref_period = ref_period
		self.initial_time = 8000

	def emit_object(self):
		tm = lt.TargetMachine.new(triple="or1k", cpu="generic")
		return tm.emit_object(self.module)
