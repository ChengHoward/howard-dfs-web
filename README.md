# howard-dfs-web
统一文件管理平台(附定时任务管理模块)
### 背景
> 公司需要对分布式项目进行文件统一管理。FTP是首选，但实用性、安全性、便捷性都不达标，所以决定自行开发一款实用方便且便捷的文件管理平台。

### 功能
1.后台管理
- [x] 文件分区管理
- [x] 分区key管理
- [x] key权限管理
- [x] 定时任务管理
- [x] 查看分区文件

2.文件上传
- [x] 通过分区ID和Key上传

3.文件下载
- [x] 通过分区ID和Key下载

3.文件查询
- [x] 通过分区ID和Key对文件分区进行查询
- [x] 通过分区ID和Key以及索引对文件进行查询

3.文件删除
- [x] 通过分区ID和Key对文件进行删除操作

### 运行
``` cmd
# Windows Cmd
# 安装virtualenv模块
pip3 install virtualenv
# 创建虚拟环境
virtualenv env_dfs
# 打开虚拟环境
"./env_dfs/Scripts/activate"
# 安装项目模块
pip3 install -r requirements.txt
# 启动项目
python app.py
```

### 提示
SQLAlchemy会自动生成表结构，请自行创建数据库和足够权限的用户
数据库连接地址在[config.conf](https://github.com/tt20050510/howard-dfs-web/blob/main/config.conf)文件`[db]`中配置


### 环境
[Python 3.6.x](https://www.python.org/)
Mysql8 (可以切换其它版本或数据库)

### 前端
|[Layui](https://github.com/sentsin/layui)|
|[Jquery](https://github.com/jquery/jquery)|
|[Vue](https://github.com/vuejs/vue)|
|videojs|

### 后端
|[Flask](https://github.com/pallets/flask)|
|[sqlalchemy](https://github.com/zzzeek/sqlalchemy)|
|[sqlacodegen](https://github.com/agronholm/sqlacodegen)|

# API
[Java-API](https://github.com/tt20050510/dfs-java-api)