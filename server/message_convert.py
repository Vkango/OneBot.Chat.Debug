import os
import shutil
import re

class message_convert:
    def escape_text(self, text):
        """转义纯文本中的特殊字符"""
        return text.replace('&', '&amp;').replace('[', '&#91;').replace(']', '&#93;')

    def escape_cq_param(self, param):
        """转义CQ码内部参数值中的特殊字符"""
        return param.replace('&', '&amp;').replace('[', '&#91;').replace(']', '&#93;').replace(',', '&#44;')

    def unescape_text(self, text):
        """反转义纯文本中的特殊字符"""
        return text.replace('&#93;', ']').replace('&#91;', '[').replace('&amp;', '&')

    def unescape_cq_param(self, param):
        """反转义CQ码内部参数值中的特殊字符"""
        return param.replace('&#44;', ',').replace('&#93;', ']').replace('&#91;', '[').replace('&amp;', '&')

    def array2cq(self, message, image_copied = False):
        """数组格式转CQ码"""
        result = ""
        for i in message:
            if i['type'] == 'text':
                result += self.escape_text(i['data']['text'])
            if i['type'] == 'image':
                if not image_copied:
                    file_path = i['data']['url']
                    file_name = os.path.basename(file_path)
                    new_file_path = os.path.join('client', 'images', file_name)
                    os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
                    shutil.copy(file_path, new_file_path)
                    result += f"[CQ:image,file=./images/{self.escape_cq_param(file_name)}]"
                else:
                    result += f"[CQ:image,file={self.escape_cq_param(i['data']['url'])}]"
            if i['type'] == 'face':
                result += f"[CQ:face,id={self.escape_cq_param(i['data']['id'])}]"
            if i['type'] == 'at':
                result += f"[CQ:at,qq={self.escape_cq_param(i['data']['qq'])}]"
        return result

    def cq2array(self, message, image_copied = False):
        """CQ码格式转数组格式"""
        pattern = re.compile(r'\[CQ:(?P<type>\w+),file=(?P<file>[^\]]+)\]|\[CQ:(?P<type2>\w+),id=(?P<id>[^\]]+)\]|\[CQ:(?P<type3>\w+),qq=(?P<qq>[^\]]+)\]')
        result = []
        last_end = 0
        for match in pattern.finditer(message):
            if match.start() > last_end:
                result.append({
                    "type": "text",
                    "data": {
                        "text": self.unescape_text(message[last_end:match.start()])
                    }
                })
            if match.group('type') == 'image':
                if image_copied:
                    result.append({
                        "type": "image",
                        "data": {
                            "url": self.unescape_cq_param(match.group('file'))
                        }
                    })
                else:
                    file_path = self.unescape_cq_param(match.group('file'))
                    file_name = os.path.basename(file_path)
                    new_file_path = os.path.join('client', 'images', file_name)
                    os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
                    shutil.copy(file_path, new_file_path)
                    result.append({
                        "type": "image",
                        "data": {
                            "url": f'./images/{self.escape_cq_param(file_name)}'
                        }
                    })
            elif match.group('type2') == 'face':
                result.append({
                    "type": "face",
                    "data": {
                        "id": self.unescape_cq_param(match.group('id'))
                    }
                })
            elif match.group('type3') == 'at':
                result.append({
                    "type": "at",
                    "data": {
                        "qq": self.unescape_cq_param(match.group('qq'))
                    }
                })
            last_end = match.end()
        if last_end < len(message):
            result.append({
                "type": "text",
                "data": {
                    "text": self.unescape_text(message[last_end:])
                }
            })
        return result
