import collections
from typing import List, Dict, Tuple

from .regexp import Regexp
from .value import Value, create_value


def get_dict_with_ok(dic: dict, key: str) -> Tuple[any, bool]:
    if dic is not None:
        if key in dic:
            return dic[key], True
    return None, False


class Node:
    def __init__(self):
        self.parent: Node = None
        self.children: List[Node] = None
        self.value: Value = None
        self.name: str = None
        self.indent: int = 0
        self.level: int = 0
        self.index: int = 0
        self.info: Dict[str, Value] = None

    def __repr__(self):
        return str(self.value)

    def children_to_string(self) -> str:
        result = ""
        for node in self.children:
            result += str(node.value) + "\r\n" + node.children_to_string()
        return result

    def extract_value_info(self, level: int, rules: List[str]):
        if self.level == level:
            for rule in rules:
                exp = Regexp(rule)
                find = exp.find_map(self.value)
                if find is not None:
                    for k in find:
                        self.info[k] = find[k]
        else:
            for child in self.children:
                child.extract_value_info(level, rules)
        return self

    def extract_value_info_by_func(self, level: int, key: str, func):
        if self.level == level:
            self.info[key] = func(self.value)
        else:
            for child in self.children:
                child.extract_value_info_by_func(level, key, func)
        return self

    def extract_value(self, rule: str, func) -> Dict:
        content = func(self)
        return Regexp(rule).find_map(content)

    def prune(self, deep: int, func_or_regstr, isTop=True):
        new_node = self.copy()
        new_node.clear_children()
        for child in self.children:
            if isinstance(func_or_regstr, str):
                ret = Regexp(func_or_regstr).is_match(child.value)
            else:
                ret = func_or_regstr(child)
            if ret or ret == 1:  # 1或True删除该节点(跳过添加)
                continue
            elif ret == 2:  # 2把子节点移到父节点去
                for cc in child.children:
                    new_node.children.append(cc)
                continue
            # 0或False直接添加回原节点
            new_node.children.append(child)
        if deep > 0:
            for i, child in enumerate(new_node.children):
                new_node.children[i] = child.prune(deep - 1, func_or_regstr, False)
        if isTop:
            new_node.recalculate_level()
        return new_node

    def recalculate_level(self):
        if self.parent is None:
            self.level = 0
        else:
            self.level = self.parent.level + 1
        for i, child in enumerate(self.children):
            child.parent = self
            child.index = i
            child.recalculate_level()
        return self

    def get_info(self, key: str):
        val, ok = get_dict_with_ok(self.info, key)
        return val

    def get_child_by_value(self, value: str):
        for child in self.children:
            if child.value == value:
                return child
        return None

    def get_child_by_value_exp(self, rule: str):
        exp = Regexp(rule)
        for child in self.children:
            if exp.is_match(child.value):
                return child
        return None

    def get_child_by_name(self, name: str):
        for child in self.children:
            if child.name == name:
                return child
        return None

    def get_children_by_name(self, name: str):
        children = []
        for child in self.children:
            if child.name.strip() == name.strip():
                children.append(child)
        return children

    def find_children_info_nodes(self, key: str):
        nodes: List[Node] = []
        for child in self.children:
            if child.info is not None:
                val, ok = get_dict_with_ok(child.info, key)
                if ok:
                    nodes.append(child)
        return nodes

    def find_children_info_values(self, key: str):
        values: List[Value] = []
        for child in self.children:
            if child.info is not None:
                val, ok = get_dict_with_ok(child.info, key)
                if ok:
                    values.append(val)
        return values

    def find_children_info_value(self, key: str) -> Value:
        for child in self.children:
            if child.info is not None:
                val, ok = get_dict_with_ok(child.info, key)
                if ok:
                    return val
        return None

    def children_to_table(self, head_line_count=1):
        # 找出每个字段的开头位置
        row_list = []
        index_list = []
        for child in self.children:
            start_title_map = collections.OrderedDict()
            last_char = " "
            last_val = ""
            last_start = 0
            for i, char in enumerate(child.value.to_str()):
                if char != " " and last_char == " ":
                    last_start = i
                    last_val = char
                elif char != " " and last_char != " ":
                    last_val += char
                elif char == " " and last_char != " ":
                    start_title_map[last_start] = last_val
                    if not (last_start in index_list):
                        index_list.append(last_start)
                if char != " " and i == len(child.value.to_str()) - 1:
                    start_title_map[last_start] = last_val
                    if not (last_start in index_list):
                        index_list.append(last_start)
                last_char = char
            row_list.append(start_title_map)

        # 变成列
        index_list.sort()
        col_dict = collections.OrderedDict()
        for idx in index_list:
            col_dict[idx] = []
            for row in row_list:
                val, ok = get_dict_with_ok(row, idx)
                if ok:
                    col_dict[idx].append(val)
                else:
                    col_dict[idx].append("")

        # 合并多行表头
        row_count = 0
        for k in col_dict:
            col = col_dict[k]
            new_col = []
            head_string = ""
            for i in range(head_line_count):
                head_string += col[i].strip() + "\n"
            new_col.append(head_string.strip())
            for i in range(head_line_count, len(col), 1):
                new_col.append(col[i])
            col_dict[k] = new_col
            row_count = len(new_col)

        # 提取表头长度信息
        header = collections.OrderedDict()
        last_header = 0
        for k in col_dict:
            head_string = col_dict[k][0]
            if head_string == "":
                continue
            head_len = 0
            for h in head_string.split("\n"):
                if len(h) > head_len:
                    head_len = len(h)
            header[head_string] = [k, k + head_len]
            if k > last_header:
                last_header = k
        # 转化为字典
        result = {}
        for h in header:
            result[h] = []
            for i in range(1, row_count, 1):
                vals = ""
                for col in col_dict:
                    if header[h][0] <= col < header[h][1] or (header[h][0] == last_header and header[h][0] <= col):
                        v = col_dict[col][i]
                        vals += v
                        if v != "":
                            vals += " "
                result[h].append(vals.strip())
        return result

    def slice_children(self, start, end, include_start=False, include_end=False):
        start = Regexp(start)
        end = Regexp(end)
        result = []
        find_start = False
        for child in self.children:
            if not find_start:
                if start.is_match(child.value):
                    find_start = True
                    if include_start:
                        result.append(child)
            else:
                if end.is_match(child.value):
                    if include_end:
                        result.append(child)
                    break
                result.append(child)
        return list_to_node(result, "slice")

    def contain_line(self, value):
        for child in self.children:
            if child.value.to_str() == value:
                return True
        return False

    def contain(self, value_list, logic="and"):
        if logic == "and":
            for i, value in enumerate(value_list):
                for child in self.children:
                    if value in child.value.to_str():
                        if i == len(value_list) - 1:
                            return True
                        continue
                return False
        elif logic == "or":
            for i, value in enumerate(value_list):
                for child in self.children:
                    if value in child.value.to_str():
                        return True
            return False


    def set_name(self, name):
        self.name = name
        return self

    def set_value(self, name):
        self.value = create_value(name)
        return self

    def copy(self):
        return create_node(self.parent, self.children, self.value,
                           self.name, self.indent, self.level,
                           self.index, self.info)

    def clear_children(self):
        self.children: List[Node] = []

    def split_children(self, rule):
        result = []
        split_one = []
        rule = Regexp(rule)
        for child in self.children:
            if rule.is_match(child.value):
                result.append(list_to_node(split_one, "split"))
                split_one = []
            else:
                split_one.append(child)
        return list_to_node(result, "splitChildren")


def create_node(parent: Node = None, children: List[Node] = None, value=None,
                name: str = None, indent: int = None, level: int = None,
                index: int = None, info: Dict[str, Value] = None) -> Node:
    if children is None:
        children = []
    if info is None:
        info = {}
    node = Node()
    node.parent = parent
    node.children = children
    node.value = create_value(value)
    node.name = name
    node.indent = indent
    node.level = level
    node.index = index
    node.info = info
    return node


def list_to_node(lis, name: str) -> Node:
    root = create_node(value="root", name=name)
    if len(lis) > 0 and isinstance(lis[0], Node):
        for n in lis:
            root.children.append(n)
    else:
        for n in lis:
            root.children.append(create_node(value=n))
    return root.recalculate_level()


def string_to_node_tree(content: str, rules: List[str]) -> Node:
    max_level = len(rules)
    total_node = []
    split_content = content.splitlines(keepends=False)
    for line in split_content:
        node = create_node(value=line, level=max_level)
        for i, r in enumerate(rules):
            find = Regexp(r).find_map(line)
            if find is not None and len(find) > 0:
                node.level = i
                node.name = list(find.values())[0]
        total_node.append(node)
    # 生成节点树
    root = []
    last_level_node = {}
    for i, node in enumerate(total_node):
        if node.level == 0:
            # 根节点
            root.append(node)
        else:
            if i > 0:
                last_node, ok = get_dict_with_ok(last_level_node, node.level - 1)
                if ok:
                    if last_node.level == node.level:
                        # 同层级
                        node.parent = last_node.parent
                    else:
                        # 不同层级
                        node.parent = last_node
                if node.parent is not None:
                    node.parent.children.append(node)
        last_level_node[node.level] = node
    return list_to_node(root, "NodeTree").recalculate_level()


def string_to_indent_node(content: str) -> Node:
    total_node = []
    total_indent = []
    # 生成缩进
    split_content = content.splitlines(keepends=False)
    for line in split_content:
        if line.strip() == "":
            continue
        node = create_node(value=line)
        for i, c in enumerate(line):
            if c != ' ':
                node.indent = i
                if not i in total_indent:
                    total_indent.append(i)
                break
        total_node.append(node)

    # 生成缩进与缩进等级的映射
    total_indent.sort()
    indent2level = {}
    for i, v in enumerate(total_indent):
        indent2level[v] = i
    # 根据缩进等级生成节点
    root = []
    max_level = len(indent2level)
    last_level_node = {}
    for i, node in enumerate(total_node):
        node.level = indent2level[node.indent]
        if node.level == 0:
            # 无缩进，放入根节点
            root.append(node)
        else:
            if i > 0:
                last_node, ok = get_dict_with_ok(last_level_node, node.level - 1)
                if ok:
                    if last_node.level > total_node[i - 1].level:
                        last_node = total_node[i - 1]
                    if last_node.level == node.level:
                        # 同缩进
                        node.parent = last_node.parent
                    else:
                        # 不同缩进
                        node.parent = last_node
                    node.parent.children.append(node)
                else:
                    last_node = total_node[i - 1]
                    if last_node.level == node.level:
                        # 同缩进
                        node.parent = last_node.parent
                    else:
                        # 不同缩进
                        node.parent = last_node
                    node.parent.children.append(node)
        last_level_node[node.level] = node

    return list_to_node(root, "IndentNode").recalculate_level()
