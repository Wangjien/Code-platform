#!/bin/bash

# 一键部署脚本
# 使用方法: ./deploy.sh [dev|prod] [sqlite|mysql]

set -e

# 颜色输出函数
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查必要的工具
check_requirements() {
    print_info "检查部署环境..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    print_success "环境检查通过"
}

# 检查端口占用
check_ports() {
    local ports=("8080" "6379")
    if [[ "$DB_TYPE" == "mysql" ]]; then
        ports+=("3306")
    fi
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "端口 $port 已被占用，请确认是否继续"
            read -p "是否继续部署? (y/N): " continue_deploy
            if [[ ! "$continue_deploy" =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    done
}

# 生成环境变量文件
generate_env() {
    print_info "配置环境变量..."
    
    if [[ ! -f ".env" ]]; then
        cp .env.docker .env
        print_warning "已创建 .env 文件，请根据实际情况修改配置"
    fi
    
    # 根据部署类型调整配置
    if [[ "$ENV" == "prod" ]]; then
        sed -i.bak "s/FLASK_ENV=.*/FLASK_ENV=production/" .env
        print_info "已设置为生产环境"
    else
        sed -i.bak "s/FLASK_ENV=.*/FLASK_ENV=development/" .env
        print_info "已设置为开发环境"
    fi
    
    print_success "环境变量配置完成"
}

# 构建镜像
build_images() {
    print_info "构建Docker镜像..."
    
    docker-compose build --no-cache
    
    print_success "镜像构建完成"
}

# 启动服务
start_services() {
    print_info "启动服务..."
    
    if [[ "$DB_TYPE" == "mysql" ]]; then
        # 使用MySQL
        docker-compose up -d mysql redis
        print_info "等待MySQL启动..."
        sleep 10
        
        # 检查MySQL是否准备就绪
        max_attempts=30
        attempt=1
        while [[ $attempt -le $max_attempts ]]; do
            if docker-compose exec mysql mysqladmin ping -h localhost --silent; then
                print_success "MySQL已就绪"
                break
            fi
            print_info "等待MySQL启动... ($attempt/$max_attempts)"
            sleep 2
            ((attempt++))
        done
        
        if [[ $attempt -gt $max_attempts ]]; then
            print_error "MySQL启动超时"
            exit 1
        fi
        
        # 修改docker-compose.yml启用MySQL
        sed -i.bak 's/# - mysql/- mysql/' docker-compose.yml
        sed -i.bak 's/DATABASE_URI=sqlite/# DATABASE_URI=sqlite/' docker-compose.yml
        sed -i.bak 's/# - DATABASE_URI=mysql/- DATABASE_URI=mysql/' docker-compose.yml
    fi
    
    # 启动应用服务
    docker-compose up -d
    
    print_success "服务启动完成"
}

# 健康检查
health_check() {
    print_info "进行健康检查..."
    
    max_attempts=30
    attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f http://localhost:8080/health >/dev/null 2>&1; then
            print_success "应用健康检查通过"
            break
        fi
        print_info "等待应用启动... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        print_error "应用启动超时，请检查日志"
        docker-compose logs app
        exit 1
    fi
}

# 显示部署信息
show_deployment_info() {
    print_success "🎉 部署完成！"
    echo
    echo "📋 部署信息:"
    echo "  • 应用地址: http://localhost:8080"
    echo "  • 环境类型: $ENV"
    echo "  • 数据库类型: $DB_TYPE"
    if [[ "$DB_TYPE" == "mysql" ]]; then
        echo "  • MySQL地址: localhost:3306"
    fi
    echo "  • Redis地址: localhost:6379"
    echo
    echo "🔧 常用命令:"
    echo "  • 查看日志: docker-compose logs -f"
    echo "  • 重启服务: docker-compose restart"
    echo "  • 停止服务: docker-compose down"
    echo "  • 查看状态: docker-compose ps"
    echo
    echo "📊 服务状态:"
    docker-compose ps
}

# 创建备份
create_backup() {
    if [[ -d "backups" ]]; then
        backup_name="backup-$(date +%Y%m%d-%H%M%S)"
        mkdir -p "backups/$backup_name"
        
        # 备份数据库
        if [[ "$DB_TYPE" == "sqlite" ]]; then
            docker-compose exec app cp /app/backend/instance/bio_code_share.db "/tmp/$backup_name.db" || true
            docker cp $(docker-compose ps -q app):/tmp/$backup_name.db "backups/$backup_name/" || true
        elif [[ "$DB_TYPE" == "mysql" ]]; then
            docker-compose exec mysql mysqldump -u app_user -p${DB_PASSWORD:-apppassword} bio_code_share > "backups/$backup_name/database.sql" || true
        fi
        
        print_success "数据已备份到 backups/$backup_name/"
    fi
}

# 主函数
main() {
    echo "🚀 代码分享平台一键部署脚本"
    echo "=================================="
    
    # 解析参数
    ENV=${1:-dev}  # dev 或 prod
    DB_TYPE=${2:-sqlite}  # sqlite 或 mysql
    
    print_info "部署配置: 环境=$ENV, 数据库=$DB_TYPE"
    
    # 验证参数
    if [[ ! "$ENV" =~ ^(dev|prod)$ ]]; then
        print_error "无效的环境类型: $ENV (支持: dev, prod)"
        exit 1
    fi
    
    if [[ ! "$DB_TYPE" =~ ^(sqlite|mysql)$ ]]; then
        print_error "无效的数据库类型: $DB_TYPE (支持: sqlite, mysql)"
        exit 1
    fi
    
    # 执行部署流程
    check_requirements
    check_ports
    generate_env
    
    # 创建备份（如果存在旧数据）
    if docker-compose ps | grep -q "Up"; then
        print_info "检测到运行中的服务，创建备份..."
        create_backup
        docker-compose down
    fi
    
    build_images
    start_services
    health_check
    show_deployment_info
    
    print_success "🎊 部署成功完成！"
}

# 错误处理
trap 'print_error "部署过程中发生错误，请检查上面的错误信息"' ERR

# 执行主函数
main "$@"
