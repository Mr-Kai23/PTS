# 自行定义模板标签
# 在settings文件中配置
from django.template.defaulttags import register


# 模板中获取字典的值
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
