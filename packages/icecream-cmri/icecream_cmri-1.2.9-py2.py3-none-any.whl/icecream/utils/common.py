"""
@author:cmcc
@file: common.py
@time: 2021-09-07 16:05
"""
import types
import logging
import os
import copy
import yaml
import pathlib
import chardet
import traceback
import hashlib
import ast
import ulid
import importlib
from datetime import datetime
import mimetypes
from typing import Any, Set, Text, Callable, List, Dict, Union


logger = logging.getLogger(__name__)


class File2ContentType:

    EXTEND_CONTENT_TYPE = {
        '.*': 'application/octet-stream',
        '.tif': 'application/x-tif',
        '.001': 'application/x-001',
        '.301': 'application/x-301',
        '.323': 'text/h323',
        '.906': 'application/x-906',
        '.907': 'drawing/907',
        '.a11': 'application/x-a11',
        '.acp': 'audio/x-mei-aac',
        '.ai': 'application/postscript',
        '.aif': 'audio/aiff',
        '.aifc': 'audio/aiff',
        '.aiff': 'audio/aiff',
        '.anv': 'application/x-anv',
        '.asa': 'text/asa',
        '.asf': 'video/x-ms-asf',
        '.asp': 'text/asp',
        '.asx': 'video/x-ms-asf',
        '.au': 'audio/basic',
        '.avi': 'video/avi',
        '.awf': 'application/vnd.adobe.workflow',
        '.biz': 'text/xml',
        '.bmp': 'application/x-bmp',
        '.bot': 'application/x-bot',
        '.c4t': 'application/x-c4t',
        '.c90': 'application/x-c90',
        '.cal': 'application/x-cals',
        '.cat': 'application/vnd.ms-pki.seccat',
        '.cdf': 'application/x-netcdf',
        '.cdr': 'application/x-cdr',
        '.cel': 'application/x-cel',
        '.cer': 'application/x-x509-ca-cert',
        '.cg4': 'application/x-g4',
        '.cgm': 'application/x-cgm',
        '.cit': 'application/x-cit',
        '.class': 'java/*',
        '.cml': 'text/xml',
        '.cmp': 'application/x-cmp',
        '.cmx': 'application/x-cmx',
        '.cot': 'application/x-cot',
        '.crl': 'application/pkix-crl',
        '.crt': 'application/x-x509-ca-cert',
        '.csi': 'application/x-csi',
        '.css': 'text/css',
        '.cut': 'application/x-cut',
        '.dbf': 'application/x-dbf',
        '.dbm': 'application/x-dbm',
        '.dbx': 'application/x-dbx',
        '.dcd': 'text/xml',
        '.dcx': 'application/x-dcx',
        '.der': 'application/x-x509-ca-cert',
        '.dgn': 'application/x-dgn',
        '.dib': 'application/x-dib',
        '.dll': 'application/x-msdownload',
        '.doc': 'application/msword',
        '.dot': 'application/msword',
        '.drw': 'application/x-drw',
        '.dtd': 'text/xml',
        '.dwf': 'application/x-dwf',
        '.dwg': 'application/x-dwg',
        '.dxb': 'application/x-dxb',
        '.dxf': 'application/x-dxf',
        '.edn': 'application/vnd.adobe.edn',
        '.emf': 'application/x-emf',
        '.eml': 'message/rfc822',
        '.ent': 'text/xml',
        '.epi': 'application/x-epi',
        '.eps': 'application/postscript',
        '.etd': 'application/x-ebx',
        '.exe': 'application/x-msdownload',
        '.fax': 'image/fax',
        '.fdf': 'application/vnd.fdf',
        '.fif': 'application/fractals',
        '.fo': 'text/xml',
        '.frm': 'application/x-frm',
        '.g4': 'application/x-g4',
        '.gbr': 'application/x-gbr',
        '.': 'application/x-',
        '.gif': 'image/gif',
        '.gl2': 'application/x-gl2',
        '.gp4': 'application/x-gp4',
        '.hgl': 'application/x-hgl',
        '.hmr': 'application/x-hmr',
        '.hpg': 'application/x-hpgl',
        '.hpl': 'application/x-hpl',
        '.hqx': 'application/mac-binhex40',
        '.hrf': 'application/x-hrf',
        '.hta': 'application/hta',
        '.htc': 'text/x-component',
        '.htm': 'text/html',
        '.html': 'text/html',
        '.htt': 'text/webviewhtml',
        '.htx': 'text/html',
        '.icb': 'application/x-icb',
        '.ico': 'application/x-ico',
        '.iff': 'application/x-iff',
        '.ig4': 'application/x-g4',
        '.igs': 'application/x-igs',
        '.iii': 'application/x-iphone',
        '.img': 'application/x-img',
        '.ins': 'application/x-internet-signup',
        '.isp': 'application/x-internet-signup',
        '.IVF': 'video/x-ivf',
        '.java': 'java/*',
        '.jfif': 'image/jpeg',
        '.jpe': 'image/jpeg',  # 'application/x-jpe',
        '.jpeg': 'image/jpeg',
        '.jpg': 'image/jpeg',  # 'application/x-jpg',
        '.js': 'application/x-javascript',
        '.jsp': 'text/html',
        '.la1': 'audio/x-liquid-file',
        '.lar': 'application/x-laplayer-reg',
        '.latex': 'application/x-latex',
        '.lavs': 'audio/x-liquid-secure',
        '.lbm': 'application/x-lbm',
        '.lmsff': 'audio/x-la-lms',
        '.ls': 'application/x-javascript',
        '.ltr': 'application/x-ltr',
        '.m1v': 'video/x-mpeg',
        '.m2v': 'video/x-mpeg',
        '.m3u': 'audio/mpegurl',
        '.m4e': 'video/mpeg4',
        '.mac': 'application/x-mac',
        '.man': 'application/x-troff-man',
        '.math': 'text/xml',
        '.mdb': 'application/x-mdb',
        '.mfp': 'application/x-shockwave-flash',
        '.mht': 'message/rfc822',
        '.mhtml': 'message/rfc822',
        '.mi': 'application/x-mi',
        '.mid': 'audio/mid',
        '.midi': 'audio/mid',
        '.mil': 'application/x-mil',
        '.mml': 'text/xml',
        '.mnd': 'audio/x-musicnet-download',
        '.mns': 'audio/x-musicnet-stream',
        '.mocha': 'application/x-javascript',
        '.movie': 'video/x-sgi-movie',
        '.mp1': 'audio/mp1',
        '.mp2': 'audio/mp2',
        '.mp2v': 'video/mpeg',
        '.mp3': 'audio/mp3',
        '.mp4': 'video/mpeg4',
        '.mpa': 'video/x-mpg',
        '.mpd': 'application/vnd.ms-project',
        '.mpe': 'video/x-mpeg',
        '.mpeg': 'video/mpg',
        '.mpg': 'video/mpg',
        '.mpga': 'audio/rn-mpeg',
        '.mpp': 'application/vnd.ms-project',
        '.mps': 'video/x-mpeg',
        '.mpt': 'application/vnd.ms-project',
        '.mpv': 'video/mpg',
        '.mpv2': 'video/mpeg',
        '.mpw': 'application/vnd.ms-project',
        '.mpx': 'application/vnd.ms-project',
        '.mtx': 'text/xml',
        '.mxp': 'application/x-mmxp',
        '.net': 'image/pnetvue',
        '.nrf': 'application/x-nrf',
        '.nws': 'message/rfc822',
        '.odc': 'text/x-ms-odc',
        '.out': 'application/x-out',
        '.p10': 'application/pkcs10',
        '.p12': 'application/x-pkcs12',
        '.p7b': 'application/x-pkcs7-certificates',
        '.p7c': 'application/pkcs7-mime',
        '.p7m': 'application/pkcs7-mime',
        '.p7r': 'application/x-pkcs7-certreqresp',
        '.p7s': 'application/pkcs7-signature',
        '.pc5': 'application/x-pc5',
        '.pci': 'application/x-pci',
        '.pcl': 'application/x-pcl',
        '.pcx': 'application/x-pcx',
        '.pdf': 'application/pdf',
        '.pdx': 'application/vnd.adobe.pdx',
        '.pfx': 'application/x-pkcs12',
        '.pgl': 'application/x-pgl',
        '.pic': 'application/x-pic',
        '.pko': 'application/vnd.ms-pki.pko',
        '.pl': 'application/x-perl',
        '.plg': 'text/html',
        '.pls': 'audio/scpls',
        '.plt': 'application/x-plt',
        '.png': 'image/png',  # 'application/x-png',
        '.pot': 'application/vnd.ms-powerpoint',
        '.ppa': 'application/vnd.ms-powerpoint',
        '.ppm': 'application/x-ppm',
        '.pps': 'application/vnd.ms-powerpoint',
        '.ppt': 'application/x-ppt',
        '.pr': 'application/x-pr',
        '.prf': 'application/pics-rules',
        '.prn': 'application/x-prn',
        '.prt': 'application/x-prt',
        '.ps': 'application/postscript',
        '.ptn': 'application/x-ptn',
        '.pwz': 'application/vnd.ms-powerpoint',
        '.r3t': 'text/vnd.rn-realtext3d',
        '.ra': 'audio/vnd.rn-realaudio',
        '.ram': 'audio/x-pn-realaudio',
        '.ras': 'application/x-ras',
        '.rat': 'application/rat-file',
        '.rdf': 'text/xml',
        '.rec': 'application/vnd.rn-recording',
        '.red': 'application/x-red',
        '.rgb': 'application/x-rgb',
        '.rjs': 'application/vnd.rn-realsystem-rjs',
        '.rjt': 'application/vnd.rn-realsystem-rjt',
        '.rlc': 'application/x-rlc',
        '.rle': 'application/x-rle',
        '.rm': 'application/vnd.rn-realmedia',
        '.rmf': 'application/vnd.adobe.rmf',
        '.rmi': 'audio/mid',
        '.rmj': 'application/vnd.rn-realsystem-rmj',
        '.rmm': 'audio/x-pn-realaudio',
        '.rmp': 'application/vnd.rn-rn_music_package',
        '.rms': 'application/vnd.rn-realmedia-secure',
        '.rmvb': 'application/vnd.rn-realmedia-vbr',
        '.rmx': 'application/vnd.rn-realsystem-rmx',
        '.rnx': 'application/vnd.rn-realplayer',
        '.rp': 'image/vnd.rn-realpix',
        '.rpm': 'audio/x-pn-realaudio-plugin',
        '.rsml': 'application/vnd.rn-rsml',
        '.rt': 'text/vnd.rn-realtext',
        '.rtf': 'application/x-rtf',
        '.rv': 'video/vnd.rn-realvideo',
        '.sam': 'application/x-sam',
        '.sat': 'application/x-sat',
        '.sdp': 'application/sdp',
        '.sdw': 'application/x-sdw',
        '.sit': 'application/x-stuffit',
        '.slb': 'application/x-slb',
        '.sld': 'application/x-sld',
        '.slk': 'drawing/x-slk',
        '.smi': 'application/smil',
        '.smil': 'application/smil',
        '.smk': 'application/x-smk',
        '.snd': 'audio/basic',
        '.sol': 'text/plain',
        '.sor': 'text/plain',
        '.spc': 'application/x-pkcs7-certificates',
        '.spl': 'application/futuresplash',
        '.spp': 'text/xml',
        '.ssm': 'application/streamingmedia',
        '.sst': 'application/vnd.ms-pki.certstore',
        '.stl': 'application/vnd.ms-pki.stl',
        '.stm': 'text/html',
        '.sty': 'application/x-sty',
        '.svg': 'text/xml',
        '.swf': 'application/x-shockwave-flash',
        '.tdf': 'application/x-tdf',
        '.tg4': 'application/x-tg4',
        '.tga': 'application/x-tga',
        '.tiff': 'image/tiff',
        '.tld': 'text/xml',
        '.top': 'drawing/x-top',
        '.torrent': 'application/x-bittorrent',
        '.tsd': 'text/xml',
        '.txt': 'text/plain',
        '.uin': 'application/x-icq',
        '.uls': 'text/iuls',
        '.vcf': 'text/x-vcard',
        '.vda': 'application/x-vda',
        '.vdx': 'application/vnd.visio',
        '.vml': 'text/xml',
        '.vpg': 'application/x-vpeg005',
        '.vsd': 'application/x-vsd',
        '.vss': 'application/vnd.visio',
        '.vst': 'application/x-vst',
        '.vsw': 'application/vnd.visio',
        '.vsx': 'application/vnd.visio',
        '.vtx': 'application/vnd.visio',
        '.vxml': 'text/xml',
        '.wav': 'audio/wav',
        '.wax': 'audio/x-ms-wax',
        '.wb1': 'application/x-wb1',
        '.wb2': 'application/x-wb2',
        '.wb3': 'application/x-wb3',
        '.wbmp': 'image/vnd.wap.wbmp',
        '.wiz': 'application/msword',
        '.wk3': 'application/x-wk3',
        '.wk4': 'application/x-wk4',
        '.wkq': 'application/x-wkq',
        '.wks': 'application/x-wks',
        '.wm': 'video/x-ms-wm',
        '.wma': 'audio/x-ms-wma',
        '.wmd': 'application/x-ms-wmd',
        '.wmf': 'application/x-wmf',
        '.wml': 'text/vnd.wap.wml',
        '.wmv': 'video/x-ms-wmv',
        '.wmx': 'video/x-ms-wmx',
        '.wmz': 'application/x-ms-wmz',
        '.wp6': 'application/x-wp6',
        '.wpd': 'application/x-wpd',
        '.wpg': 'application/x-wpg',
        '.wpl': 'application/vnd.ms-wpl',
        '.wq1': 'application/x-wq1',
        '.wr1': 'application/x-wr1',
        '.wri': 'application/x-wri',
        '.wrk': 'application/x-wrk',
        '.ws': 'application/x-ws',
        '.ws2': 'application/x-ws',
        '.wsc': 'text/scriptlet',
        '.wsdl': 'text/xml',
        '.wvx': 'video/x-ms-wvx',
        '.xdp': 'application/vnd.adobe.xdp',
        '.xdr': 'text/xml',
        '.xfd': 'application/vnd.adobe.xfd',
        '.xfdf': 'application/vnd.adobe.xfdf',
        '.xhtml': 'text/html',
        '.xls': 'application/x-xls',
        '.xlw': 'application/x-xlw',
        '.xml': 'text/xml',
        '.xpl': 'audio/scpls',
        '.xq': 'text/xml',
        '.xql': 'text/xml',
        '.xquery': 'text/xml',
        '.xsd': 'text/xml',
        '.xsl': 'text/xml',
        '.xslt': 'text/xml',
        '.xwd': 'application/x-xwd',
        '.x_b': 'application/x-x_b',
        '.sis': 'application/vnd.symbian.install',
        '.sisx': 'application/vnd.symbian.install',
        '.x_t': 'application/x-x_t',
        '.ipa': 'application/vnd.iphone',
        '.apk': 'application/vnd.android.package-archive',
        '.xap': 'application/x-silverlight-app',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xlt': 'application/vnd.ms-excel',
        '.xltx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
        '.xltm': 'application/vnd.ms-excel.sheet.macroEnabled.12',
        '.xlam': 'application/vnd.ms-excel.addin.macroEnabled.12',
        '.xlsb': 'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
        '.xla': 'application/vnd.ms-excel',
    }

    @classmethod
    def get_extend_content_type(cls, extend_name):
        """
        通过文件扩展名获取对应content_type
        :param extend_name:
        :return:
        """
        return cls.EXTEND_CONTENT_TYPE.get(extend_name, "application/octet-stream")


class FileUtils:

    @classmethod
    def read_csv(cls, path, tag="ice", split=",", is_title=True, encoding="utf-8"):
        with open(path, "r", encoding=encoding) as f:
            if is_title:
                title_line = f.readline().strip().split(split)
                title = list(map(lambda x: tag + "_" + x, title_line))
            else:
                title_line = f.readline().strip().split(split)
                count = len(title_line)
                title = [tag + "_" + str(item) for item in range(count)]
                yield {"title": title, "data": title_line}
            while True:
                line = f.readline()
                if line == "":
                    break
                if "\\" in line:
                    try:
                        line = ast.literal_eval(repr(line).replace(r"\\", "\\"))
                    except Exception as e:
                        logger.error(str(e))
                data = line.strip().split(split)
                yield {"title": title, "data": data}

    @classmethod
    def get_file_encoding(cls, file_path):
        encoding = "utf-8"
        try:
            with open(file_path, "rb") as f:
                content = f.readline()
                detect_result = chardet.detect(content)
                if detect_result:
                    encoding = detect_result.get("encoding")
        except Exception:
            logger.warning("file encoding unknow")
        return encoding

    @classmethod
    def chunk_read(cls, file_path, chunk_size=65536):
        """
        分片读取文件
        :param file_path:
        :param chunk_size:
        :return:
        """
        with open(file_path, "rb") as f:
            chunk = f
            while chunk:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    @classmethod
    def deal_form_file(cls, filepath) -> tuple:
        """
        form data上传传文件
        :param filepath:
        :return:
        """
        upload_file = open(filepath, "rb")
        file_name = os.path.basename(filepath)
        mimetype, _ = mimetypes.guess_type(file_name)
        file = (
            file_name,
            upload_file,
            mimetype if mimetype else "application/octet-stream",
            # File2ContentType.get_extend_content_type(pathlib.Path(filepath).suffix)
        )
        return file


class Utils:
    @classmethod
    def get_uuid(cls):
        """
        全局生成uuid, 按容器名称计算随机数
        :param node:
        :return:
        """
        return str(ulid.ULID())

    @classmethod
    def load_yaml(cls, file_path):
        with open(file_path, "r", encoding='utf-8') as f:
            try:
                return yaml.load(f.read(), yaml.FullLoader)
            except Exception:
                logger.warning(traceback.format_exc())
                raise
    @classmethod
    def write_yaml(cls, file_path, data):
        with open(file_path, "w", encoding='utf-8') as f:
            try:
                yaml.dump(data, f, Dumper=yaml.SafeDumper, allow_unicode=True)
            except Exception:
                logger.warning(traceback.format_exc())
                raise

    @classmethod
    def load_text(cls, file_path):
        with open(file_path, "r", encoding='utf-8') as f:
            try:
                return f.read()
            except Exception:
                logger.warning(traceback.format_exc())

    # refs: ONAP,
    @classmethod
    def ignore_case_get(cls, d, key, def_val=None):
        if not key or not d:
            return def_val
        if key in d:
            return d[key]
        for k in d:
            if k.upper() == key.upper():
                return d[k]
        return def_val

    @classmethod
    def remove_dict_key(cls, d, key):
        """不区分大小写，移除字典key"""
        if not key or not d:
            return
        if key in d:
            return d.pop(key, None)
        for k in d:
            if k.upper() == key.upper():
                return d.pop(k, None)

    @classmethod
    def unique_aray(cls, array, key):
        """数据归一化"""
        result = []
        value = []
        for item in array:
            if item.get(key) not in value:
                result.append(item)
            value.append(item.get(key))
        return result

    @classmethod
    def md5_str(cls, str_data):
        m = hashlib.md5()
        m.update(str_data)
        return m.hexdigest()

    @classmethod
    def remove_useless_data(cls, data, no_value: list):
        """
        根据指定的值，移出相关key
        :param data:
        :param no_value: 无用的值
        :return:
        """
        if isinstance(data, dict):
            for key, value in copy.copy(data).items():
                if isinstance(value, dict) or isinstance(value, list):
                    cls.remove_useless_data(value, no_value)
                else:
                    if value in no_value:
                        data.pop(key)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, list) or isinstance(item, dict):
                    cls.remove_useless_data(item, no_value)

    @classmethod
    def get_module_by_path(cls, object_ref: str):
        """
        获取python module
        :param object_ref:
        :return:
        """
        modname, qualname_separator, qualname = object_ref.partition(":")
        obj = importlib.import_module(modname)
        return obj

    @classmethod
    def load_module_functions(cls, module, mode) -> Dict[Text, Callable]:
        """load python module functions.

        :param module: python module
        :param mode: choose module type
        :return:
             dict: functions mapping for specified python module

                    {
                        "func1_name": func1,
                        "func2_name": func2
                    }
        """

        module_functions = {}
        for name, item in vars(module).items():
            if isinstance(item, mode):
                module_functions[name] = item

        return module_functions

    @classmethod
    def load_builtin_functions(cls) -> Dict[Text, Callable]:
        """ load builtin module functions
        """
        # todo 内建函数，后续开放本地改部分函数
        module_name = cls.get_module_by_path("icecream.core.helper.all_function")
        builtin_classes = cls.load_module_functions(module_name, classmethod.__class__)

        module_name = cls.get_module_by_path("icecream.core.helper.system_function")
        builtin_functions = cls.load_module_functions(module_name, types.FunctionType)

        builtin_classes.update(builtin_functions)
        return builtin_classes

    @classmethod
    def make_datetime_filename(cls, prefix="temp"):
        return prefix + "_" + datetime.now().strftime("%Y%m%d%H%M%S%f")

    @classmethod
    def encoder_to_dict(cls, encoder):
        """
            处理MultipartEncoder对象使其能够json序列化
            encoder： MultipartEncoder对象
        """
        data_dict = {}
        for field_name, field_value in encoder.fields.items():
            if isinstance(field_value, tuple):
                filename, file_obj, content_type = field_value
                try:
                    file_content = file_obj.read()
                    data_dict[field_name] = {
                        'filename': filename,
                        'content': file_content,
                        'content_type': content_type
                    }
                except Exception as e:
                    print(f"Error reading file {filename}: {e}")
                finally:
                    file_obj.seek(0)
            else:
                data_dict[field_name] = field_value
        return data_dict

