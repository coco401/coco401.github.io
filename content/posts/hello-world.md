---
title: Hello World
date: '2020-06-20'
tags:
- hexo
---

这是我得用[Hexo](https://hexo.io/)写的第一篇博客，感谢[Hexo官网的教程](https://hexo.io/docs/)。下面是一些简单使用Hexo的方法。会随着我对Hexo的了解不断更新。

## 快速开始

### 创建一篇新文章

```
$ hexo new "Hello-world"
```

### 运行服务器

```
$ hexo server
```

### 生成静态文件

```
$ hexo generate
```

### 部署网站

```
$ hexo deploy
```

## 使用数学公式

Hexo并不原生支持数学公式，需要安装插件mathjax。

```
$ npm install hexo-math --save
```

在站点配置文件 \_config.yml 中添加：

```
math:
  engine: 'mathjax' # or 'katex'
  mathjax:
    # src: custom_mathjax_source
    config:
      # MathJax config
```
