#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os
import json
from configparser import ConfigParser
from app.jmedia.Getter import avsox, javbus, javdb, mgstage, dmm, jav321, xcity
from app.utils.types import JavDomainType


def is_uncensored(number):
    """
    是否为无码
    """
    if re.match('^\d{4,}', number) or re.match(
            'n\d{4}', number) or 'HEYZO' in number.upper():
        return True
    prefix_list = str('S2M|BT|LAF|SMD').split('|')
    for pre in prefix_list:
        if pre.upper() in number.upper():
            return True
    return False


def getDataState(json_data):
    """
    元数据获取失败检测
    """
    if json_data['title'] == '' or json_data['title'] == 'None' or json_data[
            'title'] == 'null':
        return 0
    else:
        return 1


def escapePath(path, Config):  # Remove escape literals
    """
    去掉异常字符
    """
    escapeLiterals = Config['escape']['literals']
    backslash = '\\'
    for literal in escapeLiterals:
        path = path.replace(backslash + literal, '')
    return path


def movie_lists(escape_folder, movie_type, movie_path):
    """
    获取视频列表
    """
    if escape_folder != '':
        escape_folder = re.split('[,，]', escape_folder)
    total = []
    file_type = movie_type.split('|')
    file_root = movie_path.replace('\\', '/')
    for root, dirs, files in os.walk(file_root):
        if escape_folder != '':
            flag_escape = 0
            for folder in escape_folder:
                if folder in root:
                    flag_escape = 1
                    break
            if flag_escape == 1:
                continue
        for f in files:
            file_type_current = os.path.splitext(f)[1]
            file_name = os.path.splitext(f)[0]
            if re.search(r'^\..+', file_name):
                continue
            if file_type_current in file_type:
                path = root + '/' + f
                # path = path.replace(file_root, '.')
                path = path.replace("\\\\", "/").replace("\\", "/")
                total.append(path)
    return total


def getNumber(filepath):
    """
    获取番号
    """
    filepath = filepath.replace('-C.', '.').replace('-c.', '.')
    filename = os.path.splitext(filepath.split('/')[-1])[0]
    part = ''
    if re.search('-CD\d+', filename):
        part = re.findall('-CD\d+', filename)[0]
    if re.search('-cd\d+', filename):
        part = re.findall('-cd\d+', filename)[0]
    filename = filename.replace(part, '')
    filename = str(re.sub("-\d{4}-\d{1,2}-\d{1,2}", "", filename))  # 去除文件名中时间
    filename = str(re.sub("\d{4}-\d{1,2}-\d{1,2}-", "", filename))  # 去除文件名中时间
    if re.search('^\D+\.\d{2}\.\d{2}\.\d{2}',
                 filename):  # 提取欧美番号 sexart.11.11.11
        try:
            file_number = re.search('\D+\.\d{2}\.\d{2}\.\d{2}',
                                    filename).group()
            return file_number
        except:
            return os.path.splitext(filepath.split('/')[-1])[0]
    elif re.search('XXX-AV-\d{4,}', filename.upper()):  # 提取xxx-av-11111
        file_number = re.search('XXX-AV-\d{4,}', filename.upper()).group()
        return file_number
    elif '-' in filename or '_' in filename:  # 普通提取番号 主要处理包含减号-和_的番号
        if 'FC2' or 'fc2' in filename:
            filename = filename.upper().replace('PPV', '').replace('--', '-')
        if re.search('FC2-\d{5,}', filename):  # 提取类似fc2-111111番号
            file_number = re.search('FC2-\d{5,}', filename).group()
        elif re.search('[a-zA-Z]+-\d+', filename):  # 提取类似mkbd-120番号
            file_number = re.search('\w+-\d+', filename).group()
        elif re.search('\d+[a-zA-Z]+-\d+', filename):  # 提取类似259luxu-1111番号
            file_number = re.search('\d+[a-zA-Z]+-\d+', filename).group()
        elif re.search('[a-zA-Z]+-[a-zA-Z]\d+', filename):  # 提取类似mkbd-s120番号
            file_number = re.search('[a-zA-Z]+-[a-zA-Z]\d+', filename).group()
        elif re.search('\d+-[a-zA-Z]+', filename):  # 提取类似 111111-MMMM 番号
            file_number = re.search('\d+-[a-zA-Z]+', filename).group()
        elif re.search('\d+-\d+', filename):  # 提取类似 111111-000 番号
            file_number = re.search('\d+-\d+', filename).group()
        elif re.search('\d+_\d+', filename):  # 提取类似 111111_000 番号
            file_number = re.search('\d+_\d+', filename).group()
        else:
            file_number = filename
        return file_number
    else:  # 提取不含减号-的番号，FANZA CID 保留ssni00644，将MIDE139改成MIDE-139
        try:
            file_number = os.path.splitext(filename.split('/')[-1])[0]
            find_num = re.findall(r'\d+', file_number)[0]
            find_char = re.findall(r'\D+', file_number)[0]
            if len(find_num) <= 4 and len(find_char) > 1:
                file_number = find_char + '-' + find_num
            return file_number
        except:
            return os.path.splitext(filepath.split('/')[-1])[0]


def getDataFromJSON(file_number,
                    domain,
                    jav_site,
                    appoint_url,
                    config=None):  # 从JSON返回元数据
    """
    根据番号获取数据
    """
    # ==========网站规则添加开始==========
    isuncensored = is_uncensored(file_number)
    json_data = {}
    json_data['isuncensored'] = isuncensored
    if jav_site == JavDomainType.ALL.value:  # 从全部网站刮削
        # ==========无码抓取:111111-111,n1111,HEYZO-1111,SMD-115
        if isuncensored:
            json_data = json.loads(
                javbus.main_uncensored(file_number, appoint_url,
                                       domain=domain))
            if getDataState(json_data) == 0:
                json_data = json.loads(
                    javdb.main(file_number, appoint_url, True, domain=domain))
            if getDataState(json_data) == 0 and 'HEYZO' in file_number.upper():
                json_data = json.loads(
                    jav321.main(file_number, appoint_url, True, domain=domain))
            if getDataState(json_data) == 0:
                json_data = json.loads(
                    avsox.main(file_number, appoint_url, domain=domain))
        # ==========259LUXU-1111
        elif re.match('\d+[a-zA-Z]+-\d+',
                      file_number) or 'SIRO' in file_number.upper():
            json_data = json.loads(
                mgstage.main(file_number, appoint_url, domain=domain))
            file_number = re.search('[a-zA-Z]+-\d+', file_number).group()
            if getDataState(json_data) == 0:
                json_data = json.loads(
                    jav321.main(file_number, appoint_url, domain=domain))
            if getDataState(json_data) == 0:
                json_data = json.loads(
                    javdb.main(file_number, appoint_url, domain=domain))
            if getDataState(json_data) == 0:
                json_data = json.loads(
                    javbus.main(file_number, appoint_url, domain=domain))
        # ==========FC2-111111
        elif 'FC2' in file_number.upper():
            json_data = json.loads(
                javdb.main(file_number, appoint_url, domain=domain))
        # ==========ssni00321
        elif re.match('\D{2,}00\d{3,}', file_number
                      ) and '-' not in file_number and '_' not in file_number:
            json_data = json.loads(
                dmm.main(file_number, appoint_url, domain=domain))
        # ==========sexart.15.06.14
        elif re.search('\D+\.\d{2}\.\d{2}\.\d{2}', file_number):
            json_data = json.loads(
                    javbus.main_us(file_number, appoint_url, domain=domain))
            if getDataState(json_data) == 0:
                json_data = json.loads(javdb.main_us(file_number, appoint_url, domain=domain))
        # ==========MIDE-139
        else:
            json_data = json.loads(
                javbus.main(file_number, appoint_url, domain=domain))
            if getDataState(json_data) == 0:
                json_data = json.loads(
                    jav321.main(file_number, appoint_url, domain=domain))
            if getDataState(json_data) == 0:
                json_data = json.loads(
                    xcity.main(file_number, appoint_url, domain=domain))
            if getDataState(json_data) == 0:
                json_data = json.loads(
                    javdb.main(file_number, appoint_url, domain=domain))
            if getDataState(json_data) == 0:
                json_data = json.loads(
                    avsox.main(file_number, appoint_url, domain=domain))
    elif re.match('\D{2,}00\d{3,}',
                  file_number) and jav_site != JavDomainType.XCITY.value:
        json_data = {
            'title': '',
            'actor': '',
            'website': '',
        }
    elif jav_site == JavDomainType.MGSTAGE.value:  # 仅从mgstage
        json_data = json.loads(
            mgstage.main(file_number, appoint_url, domain=domain))
    elif jav_site == JavDomainType.JAVBUS.value:  # 仅从javbus
        if isuncensored:
            json_data = json.loads(
                javbus.main_uncensored(file_number, appoint_url,
                                       domain=domain))
        elif re.search('\D+\.\d{2}\.\d{2}\.\d{2}', file_number):
            json_data = json.loads(
                javbus.main_us(file_number, appoint_url, domain=domain))
        elif re.search('[a-z]+-?\d+', file_number, flags=re.IGNORECASE):
            json_data = json.loads(
                javbus.main(file_number, appoint_url, domain=domain))
        else:
            json_data = {
            'title': '',
            'actor': '',
            'website': ''}
    elif jav_site == JavDomainType.JAV321.value:  # 仅从jav321
        json_data = json.loads(
            jav321.main(file_number, isuncensored, appoint_url, domain=domain))
    elif jav_site == JavDomainType.JAVDB.value:  # 仅从javdb
        if re.search('\D+\.\d{2}\.\d{2}\.\d{2}', file_number):
            json_data = json.loads(javdb.main_us(file_number, appoint_url, domain=domain))
        else:
            json_data = json.loads(
                javdb.main(file_number,
                           appoint_url,
                           isuncensored,
                           domain=domain))
    elif jav_site == JavDomainType.AVSOX.value:  # 仅从avsox
        json_data = json.loads(
            avsox.main(file_number, appoint_url, domain=domain))
    elif jav_site == JavDomainType.XCITY.value:  # 仅从xcity
        json_data = json.loads(
            xcity.main(file_number, appoint_url, domain=domain))
    elif jav_site == JavDomainType.DMM.value:  # 仅从dmm
        json_data = json.loads(
            dmm.main(file_number, appoint_url, domain=domain))

    # ==========网站规则添加结束==========
    # print(json_data)
    # ==========超时或未找到
    if json_data['website'] == 'timeout':
        return json_data
    elif json_data['title'] == '':
        return json_data
    # ==========处理得到的信息
    title = json_data['title']
    number = json_data['number']
    actor_list = str(json_data['actor']).strip("[ ]").replace("'", '').split(
        ',')  # 字符串转列表
    release = json_data['release']
    try:
        cover_small = json_data['cover_small']
    except:
        cover_small = ''
    tag = str(json_data['tag']).strip("[ ]").replace("'", '').replace(
        " ", '').split(',')  # 字符串转列表 @
    actor = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')
    if actor == '':
        actor = 'Unknown'

    # ==========处理异常字符========== #\/:*?"<>|
    title = title.replace(actor, '')
    title = title.replace('\\', '')
    title = title.replace('/', '')
    title = title.replace('-', '')
    title = title.replace(':', '')
    title = title.replace('*', '')
    title = title.replace('?', '')
    title = title.replace('"', '')
    title = title.replace('<', '')
    title = title.replace('>', '')
    title = title.replace('|', '')
    title = title.replace(' ', '.')
    title = title.replace('【', '')
    title = title.replace('】', '')
    release = release.replace('/', '-')
    tmpArr = cover_small.split(',')
    if len(tmpArr) > 0:
        cover_small = tmpArr[0].strip('\"').strip('\'')
    for key, value in json_data.items():
        if key == 'title' or key == 'studio' or key == 'director' or key == 'series' or key == 'publisher':
            json_data[key] = str(value).replace('/', '')
    # ==========处理异常字符 END========== #\/:*?"<>|

    if config:
        naming_media = config['Name_Rule']['naming_media']
        naming_file = config['Name_Rule']['naming_file']
        folder_name = config['Name_Rule']['folder_name']
        json_data['naming_media'] = naming_media
        json_data['naming_file'] = naming_file
        json_data['folder_name'] = folder_name

    # 返回处理后的json_data
    json_data['title'] = title
    json_data['number'] = number
    json_data['actor'] = actor
    json_data['release'] = release
    json_data['cover_small'] = cover_small
    json_data['tag'] = tag
    return json_data


def get_info(json_data):
    """
    返回json里的数据
    """
    for key, value in json_data.items():
        if value == '' or value == 'N/A':
            json_data[key] = 'unknown'
    title = json_data['title']
    studio = json_data['studio']
    publisher = json_data['publisher']
    year = json_data['year']
    outline = json_data['outline']
    runtime = json_data['runtime']
    director = json_data['director']
    actor_photo = json_data['actor_photo']
    actor = json_data['actor']
    release = json_data['release']
    tag = json_data['tag']
    number = json_data['number']
    cover = json_data['cover']
    website = json_data['website']
    series = json_data['series']
    return title, studio, publisher, year, outline, runtime, director, actor_photo, actor, release, tag, number, cover, website, series
