# toolkits
## 迁移PDM项目
1, Create virtual env 
pdm venv create

2, Install dependency
pdm install 

3, basic python libs 
pdm add arrow toolkits requests dingtalkchatbot exchangelib redis PyYAML sqlalchemy kafka-python-ng urllib3==1.26.15 wheel jmespath log4python PyMySQL pytest crython icecream

## 使用包中的Python脚本 
### 设置Python环境变量 
      export PYTHONPATH="/home/pythonDemo/toolkits/src/:$PYTHONPATH"
### 源码目录中不要有[与包名一致的Python脚本文件] 
### 直接调用Python脚本 
      python toolkits/db_query_demo.py --config_path="/home/pythonDemo/toolkits/src/toolkits/config/config_demo.py" worker test_01.txt 
