from .PartixListener import PartixListener

class PartixEvalListener(PartixListener):
    def __init__(self):
        self.meta_vars = {}   # meta @key value
        self.pass_vars = {}   # pass n 对象，格式: { n: { key: val, ... }, ... }
        self.normal_vars = {} # 普通 @key value

        self.current_value_parts = []
        self.current_value = None
        self._pass_stack = []  # 保存当前pass层级参数n的栈

    def enterValue(self, ctx):
        self.current_value_parts = []

    def exitAtom(self, ctx):
        val = None
        if ctx.ID():
            name = ctx.ID().getText()
            # 查找所有变量，优先普通，再meta，再pass里最内层（最后一个栈顶）
            val = self.normal_vars.get(name)
            if val is None:
                val = self.meta_vars.get(name)
            if val is None and self._pass_stack:
                # 找最内层pass的变量
                pass_level = self._pass_stack[-1]
                val = self.pass_vars.get(pass_level, {}).get(name)
        elif ctx.STRING():
            val = ctx.STRING().getText()[1:-1]
        elif ctx.MULTILINE_STRING():
            val = ctx.MULTILINE_STRING().getText()[3:-3]
        if val is not None:
            self.current_value_parts.append(val)

    def exitValue(self, ctx):
        self.current_value = ''.join(self.current_value_parts)

    def exitNormal_stmt(self, ctx):
        key = ctx.ID().getText()
        val = self.current_value
        if self._pass_stack:
            # 当前在pass语句里，加入对应pass参数n的字典
            pass_level = self._pass_stack[-1]
            if pass_level not in self.pass_vars:
                self.pass_vars[pass_level] = {}
            self.pass_vars[pass_level][key] = val
        else:
            self.normal_vars[key] = val

    def exitMeta_stmt(self, ctx):
        key = ctx.ID().getText()
        val = self.current_value
        self.meta_vars[key] = val

    def enterPass_stmt(self, ctx):
        n = int(ctx.ENUM().getText())
        self._pass_stack.append(n)

    def exitPass_stmt(self, ctx):
        self._pass_stack.pop()

    def enterBlock(self, ctx):
        self.meta_vars.clear()
        self.pass_vars.clear()
        self.normal_vars.clear()
        self._pass_stack.clear()

    def get_jsons(self):
        """
        返回三个字典，分别代表3个json对象：
        - meta_vars
        - pass_vars（注意是 {n: {key: val, ...}} 结构）
        - normal_vars
        """
        return self.meta_vars, self.pass_vars, self.normal_vars
