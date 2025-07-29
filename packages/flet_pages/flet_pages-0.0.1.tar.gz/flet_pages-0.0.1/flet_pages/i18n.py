import os
import json
import typing
import flet as ft


class I18n:
    """国际化翻译管理类"""

    def __init__(
        self,
        langs: typing.Dict[str, dict],
        fallback: str,
        config_dir: str = "",
        defmode: bool = True,
        client_storage: typing.Optional[ft.Page] = None,
        prefix: str = "",
    ):
        if client_storage:
            self.client_storage = client_storage.client_storage
        else:
            self.client_storage = None
            config_dir_env = os.getenv("FLET_APP_STORAGE_DATA")
            if not config_dir:
                if not config_dir_env:
                    raise ValueError(
                        "FLET_APP_STORAGE_DATA environment variable is not set."
                    )
                config_dir = config_dir_env
            self.CONFIG_FILE = os.path.join(config_dir, "i18n_config.json")
            os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
        self.prefix = prefix
        self.fallback = fallback

        self.key_list = list(langs.keys())
        self._data = self._load_or_init_config()
        self._translations = langs
        if defmode:
            global default
            default = self

    def _load_or_init_config(self) -> dict:
        """加载或初始化配置文件"""
        if self.client_storage:
            storage_key = f"{self.prefix}i18n_config"
            if self.client_storage.contains_key(storage_key):
                data = self.client_storage.get(storage_key)
                assert (
                    isinstance(data, dict)
                    and "lang" in data
                    and data["lang"] in self.key_list
                )
                return data
            else:
                data = {"lang": self.fallback}
                self.client_storage.set(storage_key, data)
                return data
        else:
            try:
                with open(self.CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    print(data)
                    assert any(
                        [
                            isinstance(data, dict),
                            "lang" in data,
                            data["lang"] in self.key_list,
                        ]
                    )
                    return data
            except:
                data = {"lang": self.fallback}
                with open(self.CONFIG_FILE, "w") as f:
                    json.dump(data, f)
                return data

    def get_lang(self) -> str:
        """获取当前语言"""
        return self._data["lang"]

    def set_lang(self, lang: str) -> str:
        """设置当前语言"""
        assert lang in self.key_list, "Invalid language"
        self._data["lang"] = lang
        if self.client_storage:
            storage_key = f"{self.prefix}i18n_config"
            self.client_storage.set(storage_key, self._data)
        else:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(self._data, f)
        return self._data["lang"]

    def add_translation(self, lang: str, key: str, value: str):
        """添加翻译条目"""
        if lang not in self._translations:
            self._translations[lang] = {}
        keys = key.split(".")
        current = self._translations[lang]
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value

    def get_locale_key(self, key: typing.Union[str, list]) -> str:
        """获取翻译文本"""
        if isinstance(key, str):
            key = key.split(".")
        lang = self.get_lang()
        the_lang = self._translations[lang]

        try:
            for k in key:
                the_lang = the_lang[k]
        except KeyError:  # fallback to fallback language
            the_lang = self._translations[self.fallback]
            for k in key:
                try:
                    the_lang = the_lang[k]
                except KeyError:
                    raise ValueError(f"Missing translation for {'.'.join(key)}")
        if not isinstance(the_lang, str):
            raise ValueError(f"Translation value is not a string: {the_lang}")
        return the_lang


default: I18n


def t(key: typing.Union[str, list]) -> str:
    """获取翻译文本的快捷函数"""
    global default
    if not default:
        raise ValueError(
            "I18n not initialized. Please initialize I18n before using t()."
        )
    return default.get_locale_key(key)
