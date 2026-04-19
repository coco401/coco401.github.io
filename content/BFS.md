---
title: BFS,DFS,拓扑排序
date: '2020-06-27'
tags:
- 算法
aliases:
- posts/BFS
---

## 宽度优先搜索

通常使用queue来实现BFS，在python中是collections中的deque

### 什么时候用BFS

#### 图的遍历 traversal in graph

- 层级遍历 level order traversal （树）

  - [102.二叉树层序遍历](https://leetcode.com/problems/binary-tree-level-order-traversal/)
  - [103.二叉树的锯齿层遍历](https://leetcode.com/problems/binary-tree-zigzag-level-order-traversal/)
  - [107.二叉树的层次遍历 II](https://leetcode-cn.com/problems/binary-tree-level-order-traversal-ii/description/)
  - 114.
  - [297.Serialize and Deserialize Binary Tree](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/)

- 由点及面 connected component （图，矩阵）
- 拓扑排序 topological sorting

#### 简单图的最短路径 shortest path in simple graph

复杂图应该用→ Dijkstra, SPFA, Floyd.最长路径的话如果图能分层用DP，不能用DFS

分为：求具体的path 或者 求最短的值

- [111.二叉树的最小深度](https://leetcode-cn.com/problems/minimum-depth-of-binary-tree/description/)
- [542.01 矩阵](https://leetcode-cn.com/problems/01-matrix/description/)
- [1091. Shortest Path in Binary Matrix](https://leetcode.com/problems/shortest-path-in-binary-matrix/)
- [Web Crawler Multithreaded](https://leetcode.com/problems/web-crawler-multithreaded/)
- [Web Crawler](https://leetcode.com/problems/web-crawler/)

#### 非递归的方式找所有方案Iteration solution for all possible results

### BFS可以用来做序列化

#### 什么是序列化？

将“内存”中结构化的数据变成“字符串”的过程

序列化：object to string 反序列化：string to object

#### 什么时候序列化？

1. 将内存中的数据持久化存储时： 内存中重要的数据不能只是呆在内存里，这样断电就没有了，所需需要用一种方式写入硬盘，在需要 的时候，能否再从硬盘中读出来在内存中重新创建
2. 网络传输时：机器与机器之间交换数据的时候，不可能互相去读对方的内存。只能讲数据变成字符流数据（字符串） 后通过网络传输过去。接受的一方再将字符串解析后到内存中。

#### 序列化的手段

- XML
- Json

### 不同数据结构做BFS的注意点

## 拓扑排序

当图中存在依赖关系时往往会用到拓扑排序。拓扑排序能用BFS也能用DFS。不过一般能用BFS解决就用BFS解决

- 求任意1个拓扑序（Topological Order）
- 问是否存在拓扑序（是否可以被拓扑排序）
- 求所有的拓扑序 （需要使用DFS）
- 求是否存在且仅存在一个拓扑序 Queue中最多同时只有1个节点
