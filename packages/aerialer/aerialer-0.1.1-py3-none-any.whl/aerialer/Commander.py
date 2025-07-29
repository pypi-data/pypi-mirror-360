__author__ = "Jianfeng Sun"
__version__ = "v1.0"
__copyright__ = "Copyright 2025"
__license__ = "GPL v3.0"
__email__ = "jianfeng.sunmt@gmail.com"
__maintainer__ = "Jianfeng Sun"


class Commander:

    def __init__(
            self,
            **kwargs,
    ):
        self.kwargs = kwargs

    def tool_py_list(self, ):
        parts = []
        for i in range(len(self.cmd_config)):
            parts.append(self.cmd_config[i])
        cmd = " ".join(parts)
        # print(cmd)
        return cmd

    def tool_py_dict(self, ):
        cc = self.kwargs['config'].get("cmd", {})
        parts = []
        for k, v in cc.items():
            if v == "":
                parts.append(k)
            else:
                parts.extend([k, str(v)])
        cmd = " ".join(parts)
        # print(cmd)
        line = [cmd]
        self.kwargs['cmd_line'].extend(line)
        # Blank line between this and the rest
        if self.kwargs['cmd_line']:
            self.kwargs['cmd_line'].append("")
        return cmd

    def pre(self, ):
        if 'pre' in self.kwargs['config'].keys():
            lines = self.kwargs['config'].get("pre", [])

            self.kwargs['cmd_line'].extend(lines)

            # Blank line between this and the rest
            if self.kwargs['cmd_line']:
                self.kwargs['cmd_line'].append("")

    def post(self, ):
        if 'post' in self.kwargs['config'].keys():
            lines = self.kwargs['config'].get("post", [])

            self.kwargs['cmd_line'].extend(lines)

            # Blank line between this and the rest
            if self.kwargs['cmd_line']:
                self.kwargs['cmd_line'].append("")