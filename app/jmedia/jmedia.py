import os
from time import sleep

import log

from app.utils.types import JavDomainType
from config import Config
from .jmeta import JMeta
from app.jmedia.Function.Function import get_info, getDataFromJSON, escapePath, getNumber
from app.jmedia.Function.getHtml import get_html, get_proxies, get_config


class JavMedia:
    config = None

    def __init__(self):
        self.config = Config().get_config('jav')

    def get_media_info_on_files(self, file_list, chinese=True):
        """
        根据文件清单，搜刮TMDB信息，用于文件名称的识别
        :param file_list: 文件清单，如果是列表也可以是单个文件，也可以是一个目录
        :param in_path: 转移的路径，可能是一个文件也可以是一个目录
        :param chinese: 原标题为英文时是否从别名中检索中文名称
        :return: 带有TMDB信息的每个文件对应的MetaInfo对象字典
        """
        count = 0
        jav_domain = str(self.config.get('jav_domain'))
        jav_site = str(self.config.get('jav_site'))
        if 'http' not in jav_domain.lower():
            jav_domain = r"https://%s" % jav_domain
        if "/" == jav_domain[-1]:
            jav_domain = jav_domain[:-1]

        return_media_infos = {}
        for file_path in file_list:
            count += 1
            try:
                fileName, _ = os.path.splitext(os.path.basename(file_path))
                jMeta = JMeta(fileName)
                log.info("【Rmt】Making Data for [" + file_path +
                         "], the number is [" + jMeta.get_number() + "]")
                result = self.Core_Main(filepath=file_path,
                                        jMeta=jMeta,
                                        jav_site=jav_site,
                                        domain=jav_domain)
                return_media_infos[file_path] = result
                log.info(
                    "【Rmt】======================================================"
                )
            except Exception as error_info:
                log.error('【Rmt】Error in AVDC_Main: ' + str(error_info))
                log.info(
                    "【Rmt】======================================================"
                )
        return return_media_infos

    def Core_Main(self, filepath, jMeta, jav_site, domain, appoint_url=''):
        # ======获取json_data
        json_data = self.get_json_data(jav_site=jav_site,
                                       number=jMeta.get_number(),
                                       appoint_url=appoint_url,
                                       domain=domain)
        # ======是否找到影片信息
        if json_data['website'] == 'timeout':
            log.warn(
                '【Rmt】Connect Failed! Please check your Proxy or Network!')
            jMeta.set_info(json_data=json_data)
            return jMeta
        elif json_data['title'] == '':
            jMeta.set_info(json_data=json_data)
            return jMeta
        elif 'http' not in json_data['cover']:
            raise Exception('Cover Url is None!')
        elif json_data['imagecut'] == 3 and 'http' not in json_data[
                'cover_small']:
            raise Exception('Cover_small Url is None!')

        # ======判断-C,-CD后缀,无码,流出
        if '-c.' in filepath or '-C.' in filepath or '中文' in filepath or '字幕' in filepath:
            json_data['cn_sub'] = True
        if json_data['imagecut'] == 3:  # imagecut=3为无码
            json_data['uncensored'] = True
        if '流出' in os.path.split(filepath):
            json_data['leak'] = True
        jMeta.set_info(json_data=json_data)
        return jMeta

    def get_json_data(self, jav_site, domain, number, appoint_url):
        if jav_site == JavDomainType.JAVDB:  # javdb模式 西门大官人#javbus
            self.add_text_main('【Rmt】Please Wait Three Seconds！')
            sleep(3)
        json_data = getDataFromJSON(jav_site=jav_site,
                                    file_number=number,
                                    appoint_url=appoint_url,
                                    domain=domain)
        return json_data
