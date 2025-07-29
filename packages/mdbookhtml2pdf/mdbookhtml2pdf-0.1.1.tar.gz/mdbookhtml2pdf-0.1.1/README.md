# mdBook HTML to PDF Converter

将 mdBook 生成的 HTML 文件转换为 PDF，支持：
- 自动生成目录（TOC）
- 代码高亮
- Mermaid 图表转换

## 安装要求

1. Python 3.7+
2. Node.js 和 npm（用于 mermaid-cli）

## 安装步骤

1. 安装 Node.js 依赖：

```bash
npm install -g @mermaid-js/mermaid-cli
```

2. 安装 Python 包：

```bash
pip install mdbookhtml2pdf
```

### 使用方法

```bash
mdbookhtml2pdf input.html [output.pdf]
```


如果不指定输出文件名，将使用输入文件名（替换扩展名为.pdf）。



## 功能特点

1. 目录生成
   - 自动为 h1-h6 标题生成目录
   - 目录包含页码和引导线
   - 目录单独成页

2. 代码高亮
   - 支持多种编程语言
   - 保持原有的代码格式
   - 支持行内代码和代码块

3. Mermaid 图表
   - 自动转换 mermaid 图表为高质量图片
   - 支持所有 mermaid 图表类型
   - 保持图表清晰度

## 项目地址

* [https://gitee.com/jakHall/mdbookhtml2pdf.git](https://gitee.com/jakHall/mdbookhtml2pdf.git)

## todo

目前封面支持存在部分问题，后续有空时，会解决改问题，其他的开发者可以自行尝试解决.

## 许可证

MIT License