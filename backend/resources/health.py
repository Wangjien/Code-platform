"""
健康检查API资源
提供应用状态和系统信息
"""
from flask import current_app
from flask_restful import Resource
from models import db
from sqlalchemy import text
import os
import psutil
import time
from datetime import datetime

class HealthCheck(Resource):
    """健康检查接口"""
    
    def get(self):
        """
        获取应用健康状态
        返回系统基本信息和数据库连接状态
        """
        try:
            start_time = time.time()
            
            # 检查数据库连接
            db_status = self._check_database()
            
            # 获取系统信息
            system_info = self._get_system_info()
            
            # 检查响应时间
            response_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'environment': current_app.config.get('ENV', 'development'),
                'database': db_status,
                'system': system_info,
                'response_time_ms': response_time
            }, 200
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'response_time_ms': round((time.time() - start_time) * 1000, 2)
            }, 503
    
    def _check_database(self):
        """检查数据库连接状态"""
        try:
            # 执行简单查询测试连接
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            
            db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if db_uri.startswith('sqlite'):
                db_type = 'SQLite'
            elif 'mysql' in db_uri:
                db_type = 'MySQL'
            elif 'postgresql' in db_uri:
                db_type = 'PostgreSQL'
            else:
                db_type = 'Unknown'
            
            return {
                'status': 'connected',
                'type': db_type
            }
        except Exception as e:
            return {
                'status': 'disconnected',
                'error': str(e)
            }
    
    def _get_system_info(self):
        """获取系统信息"""
        try:
            # CPU和内存使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage_percent': cpu_percent,
                'memory': {
                    'total_mb': round(memory.total / 1024 / 1024, 2),
                    'available_mb': round(memory.available / 1024 / 1024, 2),
                    'used_percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / 1024 / 1024 / 1024, 2),
                    'free_gb': round(disk.free / 1024 / 1024 / 1024, 2),
                    'used_percent': round((disk.used / disk.total) * 100, 2)
                },
                'uptime_seconds': time.time() - psutil.boot_time()
            }
        except Exception:
            return {
                'error': 'Unable to retrieve system information'
            }
