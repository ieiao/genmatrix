# genmatrix

genmatrix是一个使用python实现的单色位图及点阵字体取模工具。

之所以编写该工具，是因为在把玩墨水屏时发现在Linux操作系统中找不到像Windows系统下类似的取模工具，同时[xbm](https://www.fileformat.info/format/xbm/egff.htm#:~:text=XBM%20is%20a%20monochrome%20bitmap%20format%20in%20which,being%20stored%20as%20binary%20information%20in%20a%20file.)图像格式并不能很好的满足一些奇奇怪怪的取模需求，便有了genmatrix。

运行脚本前确保已经安装了`pillow`库，随后执行`./genmatrix`即可查看使用说明。

以墨水屏demo项目[github](https://hub.fastgit.org/ieiao/hanshow-2in9-epaper)|[gitee](https://gitee.com/ieiao/hanshow-2in9-epaper)为例，该墨水屏取模时的参数为：垂直扫描、大端序、图像水平翻转，执行如下命令便可以得到对应图片的点阵数据了。

```shell
./genmatrix.py -O mono -S V -E B -F X ../temp/aaa.bmp
```

而执行以下命令可以得到字符串参数的点阵数据了

```shell
./genmatrix.py -O str -F X -S V -E B '中华人民共和国'
```

最终叠加后可以得到如下的显示效果

![pic](https://gitee.com/ieiao/genmatrix/raw/master/pics/pic.jpg)
