---
title: "博客迁移至Hugo"
date: 2020-05-30T07:25:48+08:00
categories:
  - blog
---


作为一个Gopher, 今天终于将博客从Jeklly迁移到了Hugo. 并不是一帆风顺, 折腾了大半天.

首先, Hugo同Jeklly Markdown文件的元数据有区别. 为了转为Hugo格式, 使用了一个工具[ConvertToHugo](https://github.com/coderzh/ConvertToHugo), 是Python 2写的. 转换后的文件, date字段缺失. 因为之前时间是从文件名截取的(如: `2019-03-02`-go-http-timeout.md),  所以自己写了个[脚本](https://gist.github.com/bopjiang/b47132a97fd32ff99f73174de5bace89)解决.

其次, 还有git submodule这快碰到些问题, 特别是删除submodule, 最后在stackoverflow找到的[答案](https://stackoverflow.com/questions/29850029/what-is-the-current-way-to-remove-a-git-submodule).
```bash
git submodule deinit <asubmodule>    
git rm <asubmodule>
# Note: asubmodule (no trailing slash)
# or, if you want to leave it in your working tree
git rm --cached <asubmodule>
rm -rf .git/modules/<asubmodule>
```

还有, 为了提交.md代码后, 博客能自动渲染, 使用Github Action建立了个CD流程. 

最后, 建立两个代码仓库:
 - [blog](https://github.com/bopjiang/blog), 存放.md文件
 - [bopjiang.github.io](https://github.com/bopjiang/bopjiang.github.io), 存放生成的静态HTML文件.

做完的效果就是, Markdown格式的博客文件提交后, 1分钟内网站上[bopjiang.github.io](https://bopjiang.github.io)就能看到效果. 整个流程在github上就搞定, 没有其他依赖.


## 参考
- [hugo-ivy](https://github.com/yihui/hugo-ivy), 博客使用的模版
- [谢益辉Yihui's Blog](https://yihui.org/cn/)
- https://www.jameswright.xyz/post/deploy-hugo-academic-using-githubio/
- https://gohugo.io/hosting-and-deployment/hosting-on-github/, 这篇文章中的脚本deploy.sh和将public目录设置为submodule在CD流程中没采用.