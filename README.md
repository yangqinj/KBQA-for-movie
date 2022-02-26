# KBQA-for-movie

这是参考知乎专栏[知识图谱-给AI装个大脑](https://www.zhihu.com/column/knowledgegraph)完成的基于规则的豆瓣电影知识图谱问答Demo，我也写了一个对应的踩坑文章[Apache jena fuseki实践踩坑笔记
](https://zhuanlan.zhihu.com/p/460129220?)。

## 数据说明和环境配置 
+ 数据为爬虫爬取的豆瓣Top250电影，包括电影（250部）和名人（3922个）信息。名人包括所有的演员和导演，因此电影和名人之间有两种关系（`starring`以及`directedBy`）。
+ jena使用的是3.16.0版本。
+ d2rq使用的是0.8.1版本

jena实现了无推理版本和规则推理版本，分别对应配置目录`jena/apache-jena-fuseki-3.16.0/run_tdb`和`jena/apache-jena-fuseki-3.16.0/run_tdb_inf`，可以通过配置`FUSEKI_BASE`环境变量设置使用哪一个配置文件。

   

