from app import app
from models import db
from models.category import Category
from models.tag import Tag

# 初始化默认分类和标签数据
with app.app_context():
    # 检查是否已有数据
    if Category.query.count() == 0:
        # 添加默认分类
        categories = [
            Category(name='单细胞测序', description='单细胞测序数据分析相关代码'),
            Category(name='CNV检测', description='拷贝数变异检测相关代码'),
            Category(name='WES分析', description='全外显子测序分析相关代码'),
            Category(name='WGS分析', description='全基因组测序分析相关代码'),
            Category(name='转录组分析', description='RNA-seq数据分析相关代码'),
            Category(name='表观组分析', description='表观基因组数据分析相关代码'),
            Category(name='蛋白质组分析', description='蛋白质组数据分析相关代码'),
            Category(name='代谢组分析', description='代谢组数据分析相关代码')
        ]
        db.session.add_all(categories)
        db.session.commit()
        print('默认分类添加成功')
    else:
        print('分类数据已存在')
    
    if Tag.query.count() == 0:
        # 添加默认标签
        tags = [
            Tag(name='Python', description='Python编程语言'),
            Tag(name='R', description='R编程语言'),
            Tag(name='Shell', description='Shell脚本'),
            Tag(name='单细胞分析', description='单细胞测序数据分析'),
            Tag(name='CNV检测', description='拷贝数变异检测'),
            Tag(name='WES', description='全外显子测序'),
            Tag(name='WGS', description='全基因组测序'),
            Tag(name='RNA-seq', description='转录组测序'),
            Tag(name='scRNA-seq', description='单细胞转录组测序'),
            Tag(name='Seurat', description='R语言Seurat包'),
            Tag(name='Scanpy', description='Python语言Scanpy包'),
            Tag(name='pysam', description='Python语言pysam包'),
            Tag(name='samtools', description='SAMtools工具'),
            Tag(name='bcftools', description='BCFtools工具'),
            Tag(name='IGV', description='Integrative Genomics Viewer'),
            Tag(name='UMAP', description='UMAP降维算法'),
            Tag(name='t-SNE', description='t-SNE降维算法'),
            Tag(name='聚类分析', description='聚类分析算法'),
            Tag(name='差异表达', description='差异表达分析'),
            Tag(name='功能富集', description='功能富集分析')
        ]
        db.session.add_all(tags)
        db.session.commit()
        print('默认标签添加成功')
    else:
        print('标签数据已存在')
