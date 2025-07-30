'''
Author: hexu
Date: 2021-10-25 15:20:34
LastEditTime: 2023-05-26 14:26:04
LastEditors: Hexu
Description: 本地使用和安装包的入口文件
FilePath: /iw-algo-fx/intelliw/interface/entrypoint.py
'''
import os
import zipfile
import shutil
from intelliw.config import config, dataset_config
from absl.flags import argparse_flags as argparse


def __parse_args():
    parser = argparse.ArgumentParser(
        description="Entry files for local debug and pypi packages")

    parser.add_argument("-p", "--path", default=os.getcwd(),
                        type=str, help="project's path, default is 'os.getcwd()'")
    parser.add_argument("-o", "--output_path", default="intelliw_output_dir",
                        type=str, help="package file output path")
    parser.add_argument("task", nargs="?", default="version", type=str,
                        help="""version: intelliw version | init: initialize the product | init_docs: initialize the document |
                        init_debug: initialize the debug file | import_alg | import_model | train | infer |
                        package_iwa | package_iwm | package_iwp | default is 'import_alg'""")

    init = parser.add_argument_group(
        '[init/init_docs/init_debug]', description='intelliw init -o output_path -n mydemo')
    init.add_argument("-n", "--name", default="example",
                      type=str, help="algorithms name")

    train = parser.add_argument_group(
        '[train]', description='intelliw train -p project_path -r set_ratio')
    train.add_argument("-c", "--csv", default=None,
                       type=str, help="path of csv files as training data")
    train.add_argument("-C", "--corpus", default=None,
                       type=str, help="path of nlp corpus dir as training data")
    train.add_argument('-r', "--set_ratio", default="0.7:0.3:0", type=str,
                       help="train set:valid set:test set ratio, between 0.0 and 1.0, default is 0.7:0.3:0")
    train.add_argument('-t', "--test_size", default=None, type=str,
                       help="test_size, between 0.0 and 1.0, default not use")
    train.add_argument("-d", "--dataset", default="",
                       type=str, help="dataset id by aiworker")

    infer = parser.add_argument_group(
        '[infer]', description='intelliw infer -p project_path -P 8080')
    infer.add_argument("-P", "--port", default=8888, type=int,
                       help="port to listen, default: 8888")

    parser.add_argument_group('[package_iwa/package_iwm]',
                              description='intelliw package_iwa -p project_path -o output_path; package help: zip algorithms to iwa/iwm')
    parser.add_argument_group('[import_alg/import_model]',
                              description='intelliw import_alg -p project_path; import help: test algorithm import')

    return parser.parse_args()


def __args_to_framework_arg(args, path):
    from intelliw.interface import controller
    framework_args = controller.FrameworkArgs()
    framework_args.path = path

    if args.task == 'train':
        framework_args.task = 'train'
    elif args.task == 'infer':
        framework_args.port = args.port

    task_map = {'import_alg': 'importalg', 'import_model': 'importmodel',
                'train': 'train', 'infer': 'apiservice', 'custom': 'custom'}
    framework_args.method = task_map.get(args.task)
    assert framework_args.method is not None, f'failed to execute, unknown task: {args.task}'
    return framework_args


def __package(task: str, alg_path: str, output_path: str):
    """Package files in a directory and save them as a zip file"""

    task_map = {
        'package': '.iwa',
        'package_iwa': '.iwa',
        'package_iwm': '.iwm',
        'package_iwp': '.iwp'
    }
    if task not in task_map:
        raise ValueError(
            f'Unknown package task: {task}, supported tasks are {task_map.keys()}'
        )

    alg_path = os.path.abspath(alg_path)
    dir_name = os.path.basename(alg_path)
    output_path = os.path.abspath(output_path)
    file_name = dir_name + task_map[task]
    output = os.path.join(output_path, file_name)

    # 删除存在的文件
    if os.path.exists(output):
        os.remove(output)
    # 创建保存的文件夹
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(alg_path):
            if any(root.find(x) >= 0 for x in ('__pycache__', '.git', '.idea')):
                continue
            relative_path = root.replace(alg_path, "")
            if relative_path.startswith(os.sep):
                relative_path = relative_path[len(os.sep):]
            output_relative_path = os.path.join(dir_name, relative_path)
            for file in files:
                if file.startswith('.DS_Store'):
                    continue
                print(os.path.join(root, file), " to zip file:",
                      os.path.join(output_relative_path, file))
                zipf.write(os.path.join(root, file),
                           os.path.join(output_relative_path, file))


def __init_algorithms(name: str, output_path: str, task: str):
    package_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def alter(file, old_str, new_str):
        file_data = ""
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                if old_str in line:
                    line = line.replace(old_str, new_str)
                file_data += line
        with open(file, "w", encoding="utf-8") as f:
            f.write(file_data)

    if output_path == "intelliw_output_dir":
        output_path = os.getcwd()

    if not os.path.exists(output_path):
        raise FileNotFoundError(f"No such file or directory: '{output_path}'")

    if task == "init_docs":
        docs_dir = os.path.join(package_path, "docs")
        shutil.copytree(docs_dir, os.path.join(output_path, "docs"))
    if task == "init_debug":
        debug_file = os.path.join(package_path, "utils", "debug_controller.py")
        shutil.copyfile(debug_file, os.path.join(
            output_path, "debug_controller.py"))
    else:
        output_path = os.path.join(output_path, name)
        algorithms_dir = os.path.join(package_path, "algorithms_demo")
        algorithm_yaml = os.path.join(output_path, "algorithm.yaml")
        shutil.copytree(algorithms_dir, output_path)

        docs_dir = os.path.join(package_path, "docs")
        output_docs_dir = os.path.join(output_path, "docs")
        shutil.copytree(docs_dir, output_docs_dir)

        debug_file = os.path.join(package_path, "utils", "debug_controller.py")
        output_debug_file = os.path.join(output_path, "debug_controller.py")
        shutil.copyfile(debug_file, output_debug_file)

        alter(algorithm_yaml, "AlgorithmName", name)

        pycache = os.path.join(name, "__pycache__")
        if os.path.exists(pycache):
            shutil.rmtree(pycache)


def __dataset(dataset_id=None, set_ratio: str=None, test_size=None, local_csv=None, local_corpus=None):
    """
    config dataset
    """
    dataset_ratio = [0.7, 0.3, 0]
    if test_size:
        try:
            ts = float(test_size)
            if ts > 1 or ts < 0:
                raise Exception(
                    f"test_size 比例范围错误:{set_ratio}, 和范围为 [0, 1]")
            dataset_ratio = [1-ts, 0, ts]

        except:
            raise Exception(
                f"test_size 格式错误:{test_size}, 请参考 --test_size 0.3")
    elif set_ratio:
        try:
            tmp_ratios = [float(ratio) for ratio in set_ratio.split(":")]
            if len(tmp_ratios) >=4 or any([ratio < 0 and ratio> 1 for ratio in tmp_ratios]):
                raise Exception(
                    f"数据集比例格式错误:{set_ratio}, 请参考 -r 0.7:0.2:0.1")
            else:
                tmp_sum = sum(tmp_ratios)
                if tmp_sum > 1.0 or tmp_sum < 0:
                    raise Exception(
                        f"数据集比例范围错误:{set_ratio}, 和范围为 [0, 1]")
                if len(tmp_ratios) == 3:   
                    dataset_ratio[0] = tmp_ratios[0]
                    dataset_ratio[1] = tmp_ratios[1]
                    dataset_ratio[2] = tmp_ratios[2]
                elif len(tmp_ratios) == 2:   
                    dataset_ratio[0] = tmp_ratios[0]
                    dataset_ratio[1] = tmp_ratios[1]
                    dataset_ratio[2] = 1-tmp_ratios[0]-tmp_ratios[1]
                elif len(tmp_ratios) == 1:   
                    dataset_ratio[0] = tmp_ratios[0]
                    dataset_ratio[1] = 1-tmp_ratios[0]
                    dataset_ratio[2] = 0
        except:
            raise Exception(
                f"数据集比例格式错误:{set_ratio}, 请参考 -r 0.7:0.2:0.1")
    dataset_config.set_dataset_config(
        dataset_id, dataset_ratio, local_csv, local_corpus)


def run():
    """
    run
    """
    args = __parse_args()

    # version
    if args.task.startswith("version"):
        return

    # init
    if args.task.startswith("init"):
        __init_algorithms(args.name, args.output_path, args.task)
        return

    # package
    if args.task.startswith("package"):
        __package(args.task, args.path, args.output_path)
        return

    # set task
    config.update_by_env()
    import intelliw.interface.controller as controller
    if args.task == 'train':
        from intelliw.utils.gen_model_cfg import generate_model_config_from_algorithm_config as __generate
        # 处理 yaml 文件
        model_yaml_path, algo_yaml_path = os.path.join(
            args.path, 'model.yaml'), os.path.join(args.path, 'algorithm.yaml')

        __generate(algo_yaml_path, model_yaml_path)

        __dataset(args.dataset, args.set_ratio, args.test_size, args.csv, args.corpus)

    framework_args = __args_to_framework_arg(args, args.path)
    config.RUNNING_MODE = 'SCAFFOLDING'
    controller.main(framework_args)


if __name__ == '__main__':
    run()
