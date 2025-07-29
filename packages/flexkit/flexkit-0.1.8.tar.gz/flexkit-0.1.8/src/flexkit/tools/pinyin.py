import pypinyin


class Pinyin:
    @staticmethod
    def gfl(text):
        """获取汉字拼音首字母(Get First Letter)"""
        result = pypinyin.pinyin(text, style=pypinyin.Style.FIRST_LETTER)
        return "".join([item[0] for item in result])

    @staticmethod
    def cts(name: str) -> str:
        """将驼峰命名转换为下划线命名(Camel to Snake)"""
        return "".join(
            ["_" + char.lower() if char.isupper() else char for char in name]
        ).lstrip("_")

    class Test:
        @staticmethod
        def gfl_test():
            """测试Pinyin库中的gfl方法。"""
            print(Pinyin.gfl("模板"))

        @staticmethod
        def cts_test():
            """测试Pinyin库中的cts方法。"""
            print(Pinyin.cts("HelloWorld"))
