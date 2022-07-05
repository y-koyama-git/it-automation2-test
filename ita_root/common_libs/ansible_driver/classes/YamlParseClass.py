import yaml

"""
  yamlファイルのパースモジュール
"""
class YamlParse:
    """
      yamlファイルのパースクラス
    """
    def __init__(self):
        self.lv_lasterrmsg = ""

    def SetLastError(err):
        """
          パースエラー情報退避
          Arguments:
            err:  パースエラー情報 
          Returns:
            None
        """
        self.lv_lasterrmsg = err

    def GetLastError():
        """
          パースエラー情報所得
          Arguments:
            None
          Returns:
            パースエラー情報
        """
        return self.lv_lasterrmsg

    def Parse(yamlfile):
        """
          yamlファイルパース処理
          Arguments:
            yamlfile: yamlファイル
          Returns:
            パース結果
            パースエラー: False
            Yaml未定義  : None
        """
        self.SetLastError("")

        # バージョン確認
        yaml_var = str(yaml.__version__).split('.')[0]

        # 対話ファイルを読み込む
        try:
            if yaml_var >= str(5):
                retParse = yaml.load(open(yamlfile).read(), Loader=yaml.FullLoader)
            else:
                retParse = yaml.load(open(yamlfile).read())

        # パーサーの例外をキャッチするようにする
        except Exception as e:

            # YAML文法ミスがある場合、例外が発生する。
            self.SetLastError(str(e))
            return False

        # yaml定義がない場合にNoneが帰る
        return retParse
