import re

MATCH_STR = r'\$\{([\w._-]+)\}'

def parse_replace_config(raw_dict):
    # 初始化两个字典
    todo_dict = raw_dict.copy()
    done_dict = {}
    max_iterations = 10  # 最大循环次数
    iteration = 0
    progress = True  # 标记每次循环是否有所进展

    while todo_dict and iteration < max_iterations and progress:
        progress = False
        keys_to_process = list(todo_dict.keys())  # 遍历前获取当前所有键的副本
        # print("="*20)
        # print(f"循环次数 {iteration}，剩余待处理键：{todo_dict.keys()}")
        for key in keys_to_process:
            current_value = todo_dict[key]
            # 尝试替换所有变量引用（使用 done_dict 中的已知值）
            new_value = replace_variables(current_value, done_dict)
            
            # 如果替换后不再包含变量
            if not has_variables(new_value):
                # 将处理好的键移到 done_dict
                done_dict[key] = new_value
                del todo_dict[key]
                progress = True  # 标记有进展
            elif new_value != current_value:
                todo_dict[key] = new_value
                progress = True
            else:
                pass
                # print(f"循环次数 {iteration}，无法替换变量 {key} 的值：{current_value}")
                

        iteration += 1
    # 
    if todo_dict:
        for key, value in todo_dict.items():
            done_dict[key] = value

    return done_dict

def replace_variables(value, done_dict):
    """递归替换变量，直到无法再替换"""
    while True:
        matches = re.findall(MATCH_STR, value)
        if not matches:
            break
        replaced = False
        for var in matches:
            # print(f"value: {value}, match: {var}")
            if var in done_dict:
                replacement = done_dict[var]
                value = value.replace(f"${{{var}}}", replacement)
                replaced = True
        if not replaced:
            break  # 没有可替换的变量，退出循环
    return value

def has_variables(value):
    """检查值中是否还存在未替换的变量"""
    return bool(re.search(MATCH_STR, value))

if __name__ == "__main__":
    # 示例数据
    data = [
        "udhsdweb-url=https://${udhsdweb-host}",
        "udhsdweb-host=yssdweb-bip-test.yonyoucloud.com",
        "a=https://${udhsdweb-host}",
        "public.domain.gpaas.url=${public.domain.schema}${public.domain.gpaas.host}",
        "public.domain.url=${public.domain.schema}${public.domain.host}",
        "ymc.public.domain.url=${public.domain.gpaas.url}",
        "ymc.public.domain.url1=${ymc.public.domain.url1}",
        "public.domain.gpaas.host=yms-foreingn-gpaas-w.yyuap.com:9011",
        "public.domain.host=bip-test-xxx.yyuap.com",
        "public.domain.schema=https://",
        "domain.yonbip-scm-scmsa_1=https://bip-test.yonyoucloud.com/yonbip-scm-scmsa",
        "support.udh.udhOpenUrl=${domain.yonbip-scm-scmsa_1}",

    ]
    data = {key: value for value in data for key, value in [line.split('=', 1) for line in data]}

    # 调用函数并输出结果
    result = parse_replace_config(data)
    print(result)