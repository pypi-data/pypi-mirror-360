# -*- coding: utf-8 -*-


class ConfigGroupsHelper:
    """
    ConfigGroupsHelper
    """
    def __init__(self, config_groups, config_groups_type="list"):
        self.__group_config = {}
        if config_groups_type == "list":
            self.__init_config_list(config_groups)
        elif config_groups_type == "dict":
            self.__init_config_dict(config_groups)

    def __init_config_dict(self, config_groups_dict, talk_groups=None):
        init_groups = {}
        chat_groups = dict(config_groups_dict)
        if talk_groups:
            if type(talk_groups) is dict:
                chat_groups = {
                    "default": talk_groups
                }

        if chat_groups:
            for item in chat_groups.keys():
                init_groups[item] = chat_groups[item]

        self.__group_config = init_groups

    def __init_config_list(self, config_groups, talk_groups=None):
        init_groups = {}
        chat_groups = config_groups
        if talk_groups:
            if type(talk_groups) is dict:
                chat_groups = [talk_groups]
            else:
                chat_groups = talk_groups

        if chat_groups:
            for item in chat_groups:
                init_groups[item['name']] = item

        self.__group_config = init_groups

    def get_config_by_name(self, config_name):
        config = None
        if config_name not in self.__group_config.keys():
            err_msg = "配置名称不存在，请检查！！"
            print(err_msg)
            exit(1)
        else:
            config = self.__group_config[config_name]
        return config

    def list_config_groups(self, config_name=""):
        groups = self.__group_config.keys()
        print("%s-配置组:\n" % config_name)
        for item_group in groups:
            desc = self.__group_config[item_group]['desc']
            print("\tName: %s\tDesc:[%s]" % (item_group, desc))
