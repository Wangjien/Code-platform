-- 创建数据库
CREATE DATABASE IF NOT EXISTS bio_code_share CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE bio_code_share;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建分类表
CREATE TABLE IF NOT EXISTS categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建标签表
CREATE TABLE IF NOT EXISTS tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建代码表
CREATE TABLE IF NOT EXISTS codes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    content TEXT NOT NULL,
    language VARCHAR(20) NOT NULL,
    category_id INT NOT NULL,
    author_id INT NOT NULL,
    environment TEXT,
    license VARCHAR(50) DEFAULT 'MIT',
    views INT DEFAULT 0,
    likes INT DEFAULT 0,
    downloads INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建结果表
CREATE TABLE IF NOT EXISTS results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code_id INT NOT NULL,
    type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    description VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (code_id) REFERENCES codes(id) ON DELETE CASCADE
);

-- 创建代码标签关联表
CREATE TABLE IF NOT EXISTS code_tags (
    code_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (code_id, tag_id),
    FOREIGN KEY (code_id) REFERENCES codes(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- 插入初始分类数据
INSERT IGNORE INTO categories (name, description) VALUES
('单细胞测序', '单细胞测序数据分析相关代码'),
('CNV检测', '拷贝数变异检测相关代码'),
('WES分析', '全外显子测序分析相关代码'),
('WGS分析', '全基因组测序分析相关代码'),
('转录组分析', 'RNA-seq数据分析相关代码'),
('表观组分析', '表观基因组数据分析相关代码'),
('蛋白质组分析', '蛋白质组数据分析相关代码'),
('代谢组分析', '代谢组数据分析相关代码');

-- 插入初始标签数据
INSERT IGNORE INTO tags (name, description) VALUES
('Python', 'Python编程语言'),
('R', 'R编程语言'),
('Shell', 'Shell脚本'),
('单细胞分析', '单细胞测序数据分析'),
('CNV检测', '拷贝数变异检测'),
('WES', '全外显子测序'),
('WGS', '全基因组测序'),
('RNA-seq', '转录组测序'),
('scRNA-seq', '单细胞转录组测序'),
('Seurat', 'R语言Seurat包'),
('Scanpy', 'Python语言Scanpy包'),
('pysam', 'Python语言pysam包'),
('samtools', 'SAMtools工具'),
('bcftools', 'BCFtools工具'),
('IGV', 'Integrative Genomics Viewer'),
('UMAP', 'UMAP降维算法'),
('t-SNE', 't-SNE降维算法'),
('聚类分析', '聚类分析算法'),
('差异表达', '差异表达分析'),
('功能富集', '功能富集分析');



共发现{{总胚系变异}}个，其中：
{%- if germval_class_var %}
  {%- for category, count in germval_class_var.items() %}
  - {{ category }}: {{ count }} 例
  {%- endfor %}
{%- else %}
  - 无胚系变异分类数据
{%- endif %}


{% for variant in wes_variants %}
{{ variant.基因 }}
{{ variant.转录本 }}
{{ variant.检测结果 }}
{{ variant.亚区 }}
{{ variant.突变丰度 }}
{{ variant.突变类型 }}
{{ variant.变异等级 }}
{{ variant.肿瘤样本总reads覆盖 }}
{{ variant.肿瘤样本变异reads覆盖 }}
{% endfor %}


{%tr for cnv in cnvs %}
{{ cnv.基因 }}    {{ cnv.转录本 }}    {{ cnv.检测结果 }}    {{ cnv.亚区 }}    
{{ cnv.30X覆盖率 }}    {{ cnv.100X覆盖率 }}    {{ cnv.正链reads数 }}    
{{ cnv.负链reads数 }}    {{ cnv.链偏比例 }}
{%tr endfor %}


###### 药物
{% for drug in snp_drugs %}
基因：{{ drug.基因 }}
检测位点：{{ drug.检测位点 }}
检测结果：{{ drug.检测结果 }}
药物：{{ drug.药物 }}
用药提示：{{ drug.用药提示 }}
证据等级：{{ drug.证据等级 }}
{% endfor %}



sk-0a4d2e4db320460c8314a49e45131114