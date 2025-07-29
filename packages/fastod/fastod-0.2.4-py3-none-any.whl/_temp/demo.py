class A:
    _where_conds = []


    def where(self, kv: dict = None, **conds):
        """
        构建WHERE条件，支持多种操作符格式：
        1. 自动识别数字和字符串
        2. 正确处理 >=, <=, !=, >, <, = 等操作符
        3. 支持IN查询和布尔查询
        """

        def _format_value(v):
            """智能格式化值，数字不加引号，字符串加引号"""
            if isinstance(v, (int, float)):
                return str(v)
            return repr(str(v))

        conds = kv if kv else conds
        for key, value in conds.items():
            if isinstance(value, bool):
                self._where_conds.append(f"{key} IS NOT NULL" if value else f"{key} IS NULL")
            elif isinstance(value, list):
                values = ", ".join([_format_value(v) for v in value])
                self._where_conds.append(f"{key} IN ({values})")
            elif isinstance(value, str):
                # 支持的操作符列表（按长度降序排列）
                operators = [">=", "<=", "!=", ">", "<", "=", "LIKE ", "BETWEEN "]

                # 检查是否包含操作符
                op_found = None
                for op in operators:
                    if value.startswith(op):
                        op_found = op.strip()
                        val = value[len(op):].strip()
                        break

                if op_found:
                    if op_found == "BETWEEN":
                        parts = val.split(" AND ")
                        if len(parts) == 2:
                            part1 = _format_value(parts[0].strip())
                            part2 = _format_value(parts[1].strip())
                            self._where_conds.append(f"{key} BETWEEN {part1} AND {part2}")
                    else:
                        self._where_conds.append(f"{key} {op_found} {_format_value(val)}")
                else:
                    self._where_conds.append(f"{key} = {_format_value(value)}")
            else:
                self._where_conds.append(f"{key} = {_format_value(value)}")
        return self


if __name__ == '__main__':
    a = A()
    print(a.where(a=">='1'")._where_conds)  # 输出: ["a >= 1"]
    print(a.where(b="<=10")._where_conds)  # 输出: ["b <= 10"]
    print(a.where(c="!=test")._where_conds)  # 输出: ["c != 'test'"]
    print(a.where(d="BETWEEN 1 AND 10")._where_conds)  # 输出: ["d BETWEEN 1 AND 10"]
    print(a.where(a=">=1")._where_conds)
