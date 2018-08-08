from haystack import indexes

from .models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """
    SKU索引数据模型类
    """
    # text接受 关键词 前端传的关键字text=keyword,搜索的范围是下面的定义的字段
    # text是复合字段
    text = indexes.CharField(document=True, use_template=True)
    id = indexes.IntegerField(model_attr='id')
    name = indexes.CharField(model_attr='name')
    price = indexes.DecimalField(model_attr='price')
    default_image_url = indexes.CharField(model_attr='default_image_url')
    comments = indexes.IntegerField(model_attr='comments')

    def get_model(self):
        """返回建立索引的模型类"""
        # 搜索的是get_model指定的字段
        return SKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        # 需要返回的结果,例如下架的商品不能返回
        return self.get_model().objects.filter(is_launched=True)