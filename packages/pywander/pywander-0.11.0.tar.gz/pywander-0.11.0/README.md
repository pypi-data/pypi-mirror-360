# pywander
a general purpose python module.


## USAGE
user just ust the package.
```
pip install pywander
```

## Console Scripts
### pywander_file
扫描该文件夹下的某种类型文件
```
pywander_file scan --help
```
```text
pywander_file scan --filetype=py$ pywander
```
扫描当前文件夹下的pywander文件夹下的所有py结尾的python脚本文件。


执行该文件夹下的所有python脚本
```
pywander_file run --help
```

```text
pywander_file run scripts
```
执行当前文件夹下的scripts文件夹下的所有python脚本文件，有文件hash跟踪改动的优化设计，假设某个python脚本为test.py，输出内容在test.py.out文件那里，可能的错误信息在test.py.err文件那里。

### pywander_image
convert image
```
pywander_image convert --help
```

将某个pdf图片文件转成png格式
```text
pywander_image.exe convert .\book_cover.pdf   
```

将某个svgz通过inkscape转成pdf格式
```
pywander_image.exe convert --imgformat pdf .\f11-08_tc_big.svgz 
```

建议安装inkscape到默认的 `C:\\Program Files` 那里，那样命令行工具将可以直接调用，否则你可能需要配置PATH环境变量。 


resize image

```text
pywander_image resize --help
```

## TEST
local environment run 
```
pip install -e .
```
and run 

```
pytest
```
