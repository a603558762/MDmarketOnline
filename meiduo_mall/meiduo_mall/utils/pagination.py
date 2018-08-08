from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 2
    # 前端指明查询的size,page_size=XX
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    # 自定义查询的最大数量
    max_page_size = 20
