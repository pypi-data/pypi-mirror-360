#############################################
# File Name: ddreport
# Author: duanliangcong
# Mail: 137562703@qq.com
# Created Time:  2022-11-02 15:00:00
#############################################
from _pytest.python import Function
from _pytest.runner import runtestprotocol
from collections.abc import Iterable
from jsonpath import jsonpath
from .api import DDreportQuery
from .db import DDreportMysql, DDreportPg
from .func import DDreportFunctions, DataDiff
from .handle import Process
import ast
import json
import os
import pytest
import time


test_result = {
    "desc": "",
    "tester": "",
    "start_time": "",
    "end_time": "",
    "failed": 0,
    "passed": 0,
    "skipped": 0,
    "error": 0,
    "db_connect_time": ""
}

case_table = []

replace_data = [{'name': '<', 'value': '&autoxyhth;'}, {'name': '>', 'value': '&autodyhth;'}]


class Gvalues(object):
    __slots__ = '__value'

    def __init__(self):
        self.__value = dict()

    def set(self, key, value):
        self.__value.update({key: value})

    def get(self, key):
        return self.__value.get(key)

    def append(self, key, value):
        self.__value.get(key).append(value)

    def extend(self, key, value):
        self.__value.get(key).extend(value)

    def insert(self, key, index, value):
        self.__value.get(key).insert(index, value)


class Image(object):
    def __init__(self):
        self.__src = ''
        self._dirname = []

    def src(self, value):
        self.__src = value


_dict_data = {
    "apiresult": False,
    "response": {},
    "host": "",
    "mysql_config": None,
    "pgsql_config": None,
    "loop_name": "",
    "fail": False,
    "status": "passed",
    "imgs": Image(),
    "temp_query": {"ddquery": None},
    "imgdir": [],
}

GG = Gvalues()

_paramet_dict_data = dict()

def pytest_addoption(parser):
    """添加main的可调用参数"""
    # group = parser.getgroup("ddreport")

    parser.addoption(
        "--ddreport",
        action="store",
        default=None,
        help="测试报告标识",
    )
    parser.addoption(
        "--desc",
        action="store",
        default=None,
        help="当前测试报告的说明",
    )
    parser.addoption(
        "--tester",
        action="store",
        default=None,
        help="测试人员",
    )
    parser.addoption(
        "--envpath",
        action="store",
        default=None,
        help="环境配置路径",
    ),
    parser.addoption(
        "--envname",
        action="store",
        default=None,
        help="环境名称",
    ),
    parser.addoption(
        "--recv",
        action="store",
        default=None,
        help="接收一个字典类型的参数",
    ),
    parser.addoption(
        "--ok",
        action="store",
        default=None,
        help="是否打印正确的api请求信息",
    ),
    parser.addoption(
        "--imgdir",
        action="store",
        default=None,
        help="失败截图存放目录名称",
    )


def pytest_report_teststatus(config, report):
    # 更新终端打印（.  s   F  E）
    if report.outcome == 'error':
        return report.outcome, 'E', None


def pytest_sessionstart(session):
    # 是否展示正确的请求及响应信息
    apiresult = session.config.getoption('--ok')
    test_result['desc'] = session.config.getoption('--desc') or ''
    test_result['begin_time'] = time.strftime("%Y-%m-%d %H:%M:%S")
    test_result['tester'] = session.config.getoption('--tester') or ''
    test_result['envname'] = session.config.getoption('--envname') or ''
    test_result['show_paased'] = apiresult == "true"
    _dict_data["apiresult"] = apiresult == "true"
    # 创建UI自动化失败截图的保存目录
    if (imgdir := session.config.getoption('--imgdir')) and (dp := session.config.getoption('--ddreport')):
        img_dir_path = [os.path.dirname(dp), imgdir]
        _dict_data["imgdir"] = img_dir_path
        os.makedirs(os.path.join(*img_dir_path), exist_ok=True)


    # 记录命令传过来的参数
    receive_dict = session.config.getoption("--recv")
    if receive_dict:
        try:
            receive_dict = json.loads(receive_dict)
        except Exception:
            try:
                receive_dict = ast.literal_eval(receive_dict)
            except Exception:
                receive_dict = {}
        for k, v in receive_dict.items():
            GG.set(k, v)
    # 环境获取
    envpath = session.config.getoption("--envpath")
    envname = session.config.getoption("--envname")
    env_data = get_env(envpath, envname)
    _dict_data["host"] = env_data.get('host') or ''
    _dict_data["mysql_config"] = env_data.get('mysql')
    _dict_data["pgsql_config"] = env_data.get('pgsql')

def pytest_sessionfinish(session, exitstatus):

    class CustomJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            try:
                # 尝试调用对象的默认序列化方法
                return super().default(obj)
            except TypeError:
                # 如果遇到非可序列化的对象，则将其转为字符串
                return str(obj)

    def replace_info(data):
        for item_rep in replace_data:
            data = data.replace(item_rep['name'], item_rep['value'])
        return data

    test_result['end_time'] = time.strftime("%Y-%m-%d %H:%M:%S")
    ddreport_path = session.config.getoption('--ddreport')
    if ddreport_path:
        # 报告概览内容
        form_data = json.dumps(test_result, cls=CustomJSONEncoder)
        form_data = replace_info(form_data)
        # table
        report_table = json.dumps(case_table, cls=CustomJSONEncoder)
        report_table = replace_info(report_table)
        # 报告路径
        report_dir_file = ddreport_path.replace('\\', '/').strip()
        if not report_dir_file.endswith('.html'):
            report_dir, report_name = report_dir_file, f'report_{time.strftime("%Y%m%d-%H%M%S")}.html'
        else:
            report_dir, report_name = '/'.join(report_dir_file.split('/')[:-1]), report_dir_file.split('/')[-1]
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        report_save_path = os.path.join(report_dir, report_name)
        # 读取测试报告文件
        template_path = os.path.join(os.path.dirname(__file__), 'template', 'index.html')
        with open(f'{template_path}', 'r', encoding='utf-8') as f:
            template = f.read()
        report_template = template.replace("const formData = {}", f"const formData = {form_data}")
        report_template = report_template.replace("const sourceData = []", f"const sourceData = {report_table}")
        report_template = report_template.replace("const formatList = []", f"const formatList = {replace_data}")
        with open(report_save_path, 'w', encoding='utf-8') as f:
            f.write(report_template)


def pytest_runtest_protocol(item, nextitem):

    # 笛卡尔乘积索引
    def cartesian_product_index(input_list):
        if len(input_list) == 0:
            return [[]]
        result = []
        for ele, element in enumerate(input_list[0]):
            for sub_index in cartesian_product_index(input_list[1:]):
                result.append([(ele, element)] + sub_index)
        return result

    # copy-item-function
    def copy_item(curitem):
        newitem = Function.from_parent(name=curitem.originalname, parent=curitem.parent, callspec=curitem.callspec,
                                       fixtureinfo=curitem._fixtureinfo, originalname=curitem.originalname)
        return newitem

    # item.funcargs赋值
    def item_funcargs(item):
        for k, v in _paramet_dict_data.items():
            item.funcargs[k] = _paramet_dict_data[k]

    module_name = item._request.node.module.__name__
    class_name = item._request.node.parent.obj.__name__
    function_name = item._request.node.originalname
    all_name = (module_name + class_name + function_name)
    if _dict_data["loop_name"] == all_name:
        return True
    # 是否使用动态参数化
    is_cus_loop = False
    data_list = list()
    for i in item.own_markers:
        if i.name == "parametrize":
            args_key = i.args[0]
            args_var = i.args[-1]
            if isinstance(args_var, set):
                is_cus_loop = True
                _dict_data["loop_name"] = all_name
                var_name = list(args_var)[0]
                if var_name.startswith("drt."):
                    data = GG.get(var_name[4:]) or None
                else:
                    data = item.module.__dict__.get(var_name, None)
            else:
                data = args_var
            if not isinstance(data, Iterable):
                data = [data]
            data_list.append({args_key: data})
    if is_cus_loop:
        ks = list(map(lambda x: list(x.keys())[0], data_list))
        vals = list(map(lambda x: list(x.values())[0], data_list))
        index_list = cartesian_product_index(vals)
        import copy
        for loop_data in index_list:
            item = copy_item(item)
            params_d = dict()
            indices_d = dict()
            for n, it in enumerate(loop_data):
                indices_val = it[0]
                params_val = it[1]
                indices_d.update({ks[n]: indices_val})
                params_d.update({ks[n]: params_val})
            item.callspec.params.update(params_d)
            item.callspec.indices.update(indices_d)
            item_funcargs(item)
            runtestprotocol(item, nextitem=None)
        return True
    else:
        item_funcargs(item)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    call.duration = '%.2f' % float(call.duration)  # 科学计数转普通格式
    info = {}
    if report.when == 'call':
        # 过滤不需要的funcargs
        _paramet_dict_data.clear()
        params_keys = [om.args[0] for om in item.own_markers if om.args]
        for k in item.fixturenames:
            if k in ["_session_faker", "request"]:
                continue
            elif params_keys and k in params_keys:
                continue
            else:
                _paramet_dict_data[k] = item.funcargs[k]
        info = node_handle(report, item, call)
        test_result[report.outcome] += 1
        # 失败结束标签
        if item.funcargs:
            for k, ele_func in item.funcargs.items():
                if ele_func.__class__.__name__ == "DDreportClass" and ele_func.failexit is True:
                    _dict_data["fail"] = True
                    _dict_data["status"] = report.outcome
                    if report.outcome != "passed":
                        info["fail_tag"] = "用例标记为: 非成功用例，程序结束"
    elif report.outcome == 'failed':
        report.outcome = 'error'
        info = node_handle(report, item, call)
        test_result['error'] += 1
    elif report.outcome == 'skipped':
        info = node_handle(report, item, call)
        test_result[report.outcome] += 1
    if report.when == 'teardown':
        # 是否有图片信息
        if (img_src := _dict_data["imgs"]._Image__src):
            _dict_data["response"].update(dict(img=img_src + ""))
        case_table.append(_dict_data["response"])
        # 初始化数据
        _dict_data["imgs"]._Image__src = ""
        _dict_data["temp_query"]["ddquery"] = {}
        # 是否条件结束程序
        if _dict_data["fail"] and _dict_data["status"] != "passed":
            pytest.exit("条件终止程序")
        # 修改条件结束参数
        if item.funcargs:
            for k, ele_func in item.funcargs.items():
                if ele_func.__class__.__name__ == "DDreportClass":
                    ele_func.failexit = False
                    _dict_data.update({"fail": False, "status": "passed"})
    _dict_data["response"] = info


def node_handle(node, item, call):
    d = dict()
    # 模块
    d['model'] = item.module.__name__
    # 类
    d['classed'] = '' if item.parent.obj == item.module else item.parent.obj.__name__
    # 方法
    d['method'] = item.originalname
    # 描述
    d['doc'] = item.function.__doc__
    # 响应时间
    d['duration'] = float(call.duration)
    # 结果
    d['status'] = node.outcome
    # 详细内容
    if node.sections:
        d["print"] = node.sections[-1][1]
    # 异常信息展示
    if call.excinfo:
        excobj = node.longrepr
        try:
            if d['status'] == 'skipped':
                d["skipped"] = excobj[-1]
            else:
                # 错误的响应信息，如没有设置verfy
                d.update(call.excinfo.value.value.query_info)
                d.update(call.excinfo.value.value.error_info)
        except Exception:
            # 异常情况
            try:
                exc_list = ["file " + excobj.reprcrash.path + ", line " + str(excobj.reprcrash.lineno), excobj.reprcrash.message]
            except Exception:
                try:
                    exc_list = excobj.tblines
                    errorstring = excobj.errorstring
                    exc_list.append(errorstring)
                except Exception:
                    exc_list = [str(call.excinfo)]
            d.update(dict(msg_dict="\n".join(exc_list)))
    # 打印正确请求
    query_data = _dict_data["temp_query"].get("ddquery")
    if query_data:
        pro = Process()
        pro.data_process(query_data, None)
        if d['status'] == "passed" and _dict_data["apiresult"] is False:
            for show_key in ["print", "img", "status_code"]:
                if show_key in pro.query_info:
                    d[show_key] = pro.query_info[show_key]
        else:
            d.update(pro.query_info)
    return d


def get_env(env_path, env_name):
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            envs = json.loads(f.read())
        return jsonpath(envs, f'$..[?(@.name=="{env_name}")]')[0]
    except Exception:
        return dict()


class DDreportClass:
    def __init__(self):
        self.host = _dict_data["host"]
        self.failexit = False  # 失败后结束程序
        self.gval = GG
        self.api = DDreportQuery(GG, self.host, _dict_data["temp_query"])
        self.func = DDreportFunctions()
        self.assertion = DataDiff()
        self.image = _dict_data["imgs"]
        self.image._dirname = _dict_data["imgdir"]
        self.mysql = None
        self.pgsql = None
        if _dict_data.get("mysql_config"):
            t1 = time.time()
            self.mysql = DDreportMysql(_dict_data["mysql_config"])
            test_result["db_connect_time"] += f"( mysql={round(time.time() - t1, 2)}s )"
        if _dict_data.get("pgsql_config"):
            t2 = time.time()
            self.pgsql = DDreportPg(_dict_data["pgsql_config"])
            test_result["db_connect_time"] += f"( pgsql={round(time.time() - t2, 2)}s )"
        super().__init__()


def ddreport():
    return DDreportClass()
