写在最前，如果要使用此python脚本，确保本机python环境中安装了docx库文件，若没有安装，可以按以下步骤进行安装

1.打开终端

2.输入 pip install python-docx

如果使用的是python3环境，则输入 pip3 install python-docx

在当前环境下输入from docx import Document 若没报错则安装docx成功
（建议使用conda创建一个与本机环境相同的测试环境，本机测试的python版本为3.11.13）

2025.6.9
目前只做了两部分，可以视作一个论文检测的demo
其中 CoverPage.py 是检测论文封面是否符合规范，此规范是参考文件夹中的《论文格式.docx》，也就是《2 信息学院本科毕业设计 附件 格式 2025修订版.docx》这个文件，如果要进行检测
只需要把待检测的论文放入此文件夹，并将代码最后的 docx_path='毕业论文-陈耿洋.docx' 这一部分中的文件名改成待检测的论文即可。
其中 RefCheck.py 是检测最后参考文献的引用是否规范，规范同上，使用方式也同上。

2025.6.11
修改了参考文献检测方法，现在可以检测格式规范和是否使用全角字符，具体使用方法如下：
  1.打开transfer.py文件，将要检测的论文路径填入 docx_path = '3.docx' 替换 3.docx 的位置，运行代码后会在目录得到一个 references.txt的文件
  2.不修改 ref_finalver.py的参数，直接运行得到结果。（若在上一个 transfer.py中修改过生成的references.txt文件名，则在 ref_finalver中填入自己修改的 txt 文件名）

2025.7.20
新增了承诺书的检测

2025.7.24
新增了中英文摘要的检测

2025.8.11
新增了目录格式的检测
  
