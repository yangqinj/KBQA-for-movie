# KBQA-for-movie

这是参考知乎专栏[知识图谱-给AI装个大脑](https://www.zhihu.com/column/knowledgegraph)完成的基于规则的豆瓣电影知识图谱问答Demo。

## 数据说明和环境配置 
+ 数据为爬虫爬取的豆瓣Top250电影，包括电影（250部）和名人（3922个）信息。名人包括所有的演员和导演，因此电影和名人之间有两种关系（`starring`以及`directedBy`）。
+ jena使用的是3.16.0版本，本体推理配置后无法查询导数据，因此只支持基础的数据查询。基础数据查询对应的文件为`jena/apache-jena-fuseki-3.16.0/run_tdb`，推理对应的文件为`jena/apache-jena-fuseki-3.16.0/run_tdb_inf`。
+ d2rq使用的是0.8.1版本


## TODO
+ 使用jieba作为分词工具，无法正确分词英文名字的中文音译，比如`娜塔莉·波特曼`会被分词为`娜塔莉/·/波特曼`。
+ 图谱中区分了演员和导演，即存在`starring`和`directedBy`两种关系，在问题模板中却没有明确区分。

   

