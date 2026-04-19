---
title: 【hexo施工中】添加live2d、评论系统、文章阅读量显示
date: '2020-06-25'
tags:
- hexo
aliases:
- posts/【hexo施工中】添加live2d和评论系统
---

## live2d

live2d是一种将静态2d图片，通过将一系列的2D图像进行平移、旋转和变形等操作，生成一个具有自然动画效果的可动人物模型。

在hexo配置live2d，使用了这个[教程](https://github.com/EYHN/hexo-helper-live2d/blob/master/README.zh-CN.md)。

根据教程的说法，完全可以自己创建一个live2d model。不过为了省时间，这里就直接npm安装现有的一个叫wanko的模型。

![wanko](https://github.com/xiazeyu/live2d-widget-models/blob/master/packages/live2d-widget-model-wanko/assets/moc/wanko.1024/texture_00.png?raw=true)

![wankolive2d](https://res.cloudinary.com/da0mfx0pn/image/upload/v1593124363/%E5%BE%AE%E4%BF%A1%E6%88%AA%E5%9B%BE_20200625150350_knv8ym.png)

## vasline 评论系统

之前使用了gittalk作为评论系统，可惜bug很多而且评论需要注册github账户。所以转用vasline，不需要账户就能评论还支持markdown。需要注意的是，hexo自带了vasline，所以不需要再用npm安装包了。不过由于vasline使用了leanclud的服务。要使用vasline，还是需要先注册LeanCloud的账号来[获得id和key](https://valine.js.org/quickstart.html)。并把得到的id和key设置在\_config.yml 里。

vasline也支持[文章阅读量统计](https://valine.js.org/visitor.html)。 在hexo中只需要在\_config.yml 里的vasline项把visitor设置为true即可。
