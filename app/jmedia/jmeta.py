from app.helper import WordsHelper
from app.jmedia.Function.Function import getNumber
from app.utils.types import MediaType


class JMeta(object):
    """
    媒体信息基类
    """
    type = MediaType.JAV
    tmdb_id = '-1'
    category = ''
    # 媒体标题
    title = None
    # 媒体原发行标题
    original_title = None
    # 是否无码
    uncensored = False
    # 是否流出
    leak = False
    # 是否处理的文件
    fileflag = False
    # 原字符串
    org_string = None
    # 副标题
    subtitle = None
    # 是否有中文字幕
    cn_sub = False
    # 识别的中文名
    cn_name = None
    # 识别码
    number = None
    # 制造商
    studio = None
    # 媒体发行商
    publisher = None
    # 媒体发行年份
    year = None
    # 媒体发行日期
    release_date = None
    # 播放时长
    runtime = 0
    # 描述
    overview = None
    # 系列
    series = None
    # 评分
    score = None
    # 导演
    director = None
    # 演员
    actor = None
    # 标签
    tag = None
    # 封面图片
    backdrop_path = None
    poster_path = None
    thumb_path = None
    fanart_backdrop = None
    fanart_poster = None
    # 其它信息
    jav_info = {}

    def __init__(self, title, subtitle=None, fileflag=False):
        if not title:
            return

        self.org_string = title

        # 应用自定义识别词
        title, _, _ = WordsHelper().process(title)
        if subtitle:
            subtitle, _, _ = WordsHelper().process(subtitle)

        self.number = getNumber(title)
        self.title = title
        self.subtitle = subtitle
        self.fileflag = fileflag

    def get_title_string(self):
        str = ""
        title = self.cn_name if self.cn_name else self.title
        if title:
            if self.number:
                str = "%s " % self.number
                if self.cn_sub:
                    str = "%s-C" % str
                if self.uncensored:
                    str = "%s 【无码】" % str
                str = "%s %s" % (str, title)
            else:
                str = title
        return str

    def get_number(self):
        return self.number

    def get_poster_image(self, original=None):
        return self.poster_path

    def get_message_image(self):
        return self.poster_path

    def get_resource_type_string(self):
        return ''

    def set_info(self, json_data):
        self.jav_info = json_data
        self.number = json_data.get('number', '')
        self.title = json_data.get('title', '')
        self.original_title = json_data.get('title', '')
        self.studio = json_data.get('studio', '')
        self.publisher = json_data.get('publisher', '')
        self.year = json_data.get('year', '')
        self.overview = json_data.get('outline', '')
        self.score = json_data.get('score', '')
        self.runtime = json_data.get('runtime', '')
        self.director = json_data.get('director', '')
        self.actor_photo = json_data.get('actor_photo', '')
        self.actor = json_data.get('actor', '')
        self.release_date = json_data.get('release', '')
        self.tag = json_data.get('tag', '')
        self.poster_path = json_data.get('cover', '')
        self.website = json_data.get('website', '')
        self.leak = json_data.get('leak', False)
        self.cn_sub = json_data.get('cn_sub', False)
        self.series = json_data.get('series', '')
        self.uncensored = json_data.get('uncensored', False)

        if self.leak and '流出' not in self.tag:
            self.tag.append('流出')

        if self.uncensored and '无码' not in self.tag:
            self.tag.append('无码')

        if self.cn_sub and '中文' not in self.tag:
            self.tag.append('中文')
