import json
"""
  変数解析結果をJSON文字列にエンコード・デコードするモジュール
"""


class VarStructAnalJsonConv:
    """
      変数解析結果をJSON文字列にエンコード・デコードするクラス
    """
    def VarStructAnalJsonDumps(self, vars_list, array_vars_list, tpf_vars_list, ITA2User_var_list, GBL_vars_list):
        """
          変数解析結果をJSON文字列でエンコードする
          Arguments:
            vars_list: 一般変数情報
            array_vars_list: 多段変数情報
            tpf_vars_list: テンプレート変数情報
            ITA2User_var_list: 読替変数情報 (未使用)
            GBL_vars_list: グローバル変数情報
          Returns:
            変数解析結果をJSON文字列でエンコードした文字列
        """
        json_dict = {}
        json_dict['Vars_list'] = vars_list
        json_dict['Array_vars_list'] = array_vars_list
        json_dict['TPF_vars_list'] = tpf_vars_list
        json_dict['ITA2User_vars_list'] = ITA2User_var_list
        json_dict['GBL_vars_list'] = GBL_vars_list

        return json.dumps(json_dict)

    def VarStructAnalJsonLoads(self, json_string):
        """
          JSON文字列でエンコードされている変数解析結果をデコードする。
          Returns:
            json_string: JSON文字列でエンコードしている変数解析結果
          Arguments:
            vars_list: 一般変数情報
            array_vars_list: 多段変数情報
            tpf_vars_list: テンプレート変数情報
            ITA2User_var_list: 読替変数情報 (未使用)
            GBL_vars_list: グローバル変数情報
        """
        json_dict = json.loads(json_string)
        vars_list = json_dict['Vars_list']
        array_vars_list = json_dict['Array_vars_list']
        tpf_vars_list = json_dict['TPF_vars_list']
        ITA2User_var_list = json_dict['ITA2User_vars_list']
        GBL_vars_list = json_dict['GBL_vars_list']
        return vars_list, array_vars_list, tpf_vars_list, ITA2User_var_list, GBL_vars_list
