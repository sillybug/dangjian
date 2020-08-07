"""
# -*- coding: utf-8 -*-
# @Time : 2020/8/6 10:32
# @Author : yxj
---------------------------------------------
"""
import unittest
import re

from scripts.handle_excel import HandleExcel
from libs.ddt import ddt, data
from scripts.handle_yaml import do_yaml
from scripts.handle_log import do_log
from scripts.handle_parameterize import Parameterize
from scripts.handle_request import HandleRequest


@ddt
class Testcms(unittest.TestCase):
    excel = HandleExcel('cms')   # 创建HandleExcel对象
    cases = excel.read_data_obj()     # 获取excel中register表单下的所有数据

    @classmethod
    def setUpClass(cls): # 所有用例执行前, 会被调用一次
        cls.do_request = HandleRequest()    # 创建HandleRequest对象
        # cls.do_request.add_headers(do_yaml.read('api', 'version'))  # 添加公共的请求头, url版本号

    @classmethod
    def tearDownClass(cls): # 所有用例执行结束之后, 会被调用一次
        cls.do_request.close()  # 释放session会话资源

    @data(*cases)
    def test_cms(self, case):
        # src_data = case.data
        # re.sub(r'{not_existed_tel}', '', src_data)
        # 1. 参数化
        if case.data:
            new_data = Parameterize.to_param(case.data)
        else:
            new_data = None

        # 2. 拼接完整的url
        new_url = do_yaml.read('api', 'prefixcms') + case.url
        # 3. 向服务器发起请求
        res = self.do_request.send(url=new_url,  # url地址
                                   method="get",    # 请求方法
                                   data=new_data,   # 请求参数
                                   # is_json=False   # 是否以json格式来传递数据, 默认为True
                                   )
        # 将相应报文中的数据转化为字典
        actual_value = res.json()
        # 获取用例的行号
        row = case.case_id + 1
        # 获取预期结果
        # excepted = eval(case.excepted)
        expected_result = case.expected

        msg = case.title    # 获取标题
        success_msg = do_yaml.read('msg', 'success_result')  # 获取用例执行成功的提示
        fail_msg = do_yaml.read('msg', 'fail_result')       # 获取用例执行失败的提示

        try:
            # assertEqual第三个参数为用例执行失败之后的提示信息
            # assertEqual第一个参数为期望值, 第二个参数为实际值
            self.assertEqual(expected_result, actual_value.get('message'), msg=msg)
        except AssertionError as e:
            # 将相应实际值写入到actual_col列
            self.excel.write_data(row=row,
                                  column=do_yaml.read("excel", "actual_col"),
                                  value=res.text)
            # 将用例执行结果写入到result_col
            self.excel.write_data(row=row,
                                  column=do_yaml.read("excel", "result_col"),
                                  value=fail_msg)
            # do_log.error("断言异常: {}".format(e))
            do_log.error(f"{msg}, 执行的结果为: {fail_msg}\n具体异常为: {e}\n")
            raise e
        else:
            # 将相应实际值写入到actual_col列
            self.excel.write_data(row=row,
                                  column=do_yaml.read("excel", "actual_col"),
                                  value=res.text)
            # 将用例执行结果写入到result_col
            self.excel.write_data(row=row,
                                  column=do_yaml.read("excel", "result_col"),
                                  value=success_msg)

            do_log.info(f"{msg}, 执行的结果为: {success_msg}\n")