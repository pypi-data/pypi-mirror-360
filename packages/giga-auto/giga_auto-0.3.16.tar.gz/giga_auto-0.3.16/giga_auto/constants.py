import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "giga_auto", "config")

class DBType:
    oracle = 'oracle'
    mysql = 'mysql'
    sqlserver = 'sqlserver'
    mongodb = 'mongodb'


class CaseTypeEnum:
    """
    - 'emptyFilter' 空筛选项查询
    - 'exactMatch' 精确查询
    - 'fuzzySearch' 模糊查询
    - 'defaultQuery' 默认查询
    - 'emptyResult' 空结果查询
    - 'timeRange' 查询创建时间范围
    """
    emptyFilter = 'emptyFilter'
    exactMatch = 'exactMatch'
    fuzzySearch = 'fuzzySearch'
    defaultQuery = 'defaultQuery'
    emptyResult = 'emptyResult'
    timeRange = 'timeRange'