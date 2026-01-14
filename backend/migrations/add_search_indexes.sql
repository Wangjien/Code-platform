-- 数据库性能优化索引
-- 执行时间：建议在维护窗口期间执行

-- 1. 代码表搜索优化索引（SQLite兼容语法）
CREATE INDEX IF NOT EXISTS idx_codes_title ON codes(title);
CREATE INDEX IF NOT EXISTS idx_codes_description ON codes(description);

-- 2. 复合查询索引优化
CREATE INDEX IF NOT EXISTS idx_codes_status_language ON codes(status, language);
CREATE INDEX IF NOT EXISTS idx_codes_status_category ON codes(status, category_id);
CREATE INDEX IF NOT EXISTS idx_codes_author_status_created ON codes(author_id, status, created_at DESC);

-- 3. 用户分类相关索引
CREATE INDEX IF NOT EXISTS idx_codes_user_category_status ON codes(user_category_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_categories_user_sort ON user_categories(user_id, sort_order);

-- 4. 标签搜索优化
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
CREATE INDEX IF NOT EXISTS idx_code_tags_composite ON code_tags(tag_id, code_id);

-- 5. 评论相关索引
CREATE INDEX IF NOT EXISTS idx_comments_code_created ON comments(code_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_comments_author ON comments(author_id, created_at DESC);

-- 6. 结果表索引
CREATE INDEX IF NOT EXISTS idx_results_code_type ON results(code_id, type);

-- 7. 用户表搜索优化
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role_active ON users(role, is_active);

-- 8. 收藏功能索引
CREATE INDEX IF NOT EXISTS idx_favorites_user_created ON favorites(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_favorites_code ON favorites(code_id);

-- 性能说明：
-- - 前缀索引(prefix index)：节省存储空间，适用于文本字段的前缀搜索
-- - 复合索引：优化多条件查询，索引字段顺序很重要
-- - 建议在低峰期执行，大表创建索引可能需要较长时间

-- 使用说明：
-- 1. SQLite环境：直接执行
-- 2. MySQL环境：可能需要调整语法
-- 3. 执行前建议备份数据库
