import asyncio
from bs4 import BeautifulSoup
import os
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer, guess_lexer
from pygments.util import ClassNotFound
import subprocess
from weasyprint import HTML
import tempfile
import re
import time
import toml
from datetime import datetime
import hashlib
import shutil
import sys

# 异步函数：生成目录
async def generate_toc(soup):
    """生成目录"""
    # 获取内容div
    content_div = soup.find('div', id='content')
    if not content_div:
        return

    # 创建目录容器
    toc = soup.new_tag('article')
    toc['id'] = 'contents'

    # 添加目录标题
    title = soup.new_tag('h2')
    title.string = '目录'
    toc.append(title)

    # 创建部分标题和列表
    headers = content_div.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    # 用于跟踪每个级别的索引
    current_indices = [0] * 6

    for header in headers:
        # 为每个标题生成唯一ID（如果没有的话）
        if not header.get('id'):
            header['id'] = f'header-{hash(header.get_text())}'

        # 根据标题级别组织部分
        level = int(header.name[1])  # h1=1, h2=2, ...

        # 更新当前级别的索引
        current_indices[level - 1] += 1

        # 重置下级别的索引
        for i in range(level, 6):
            current_indices[i] = 0

        # 生成前缀
        prefix = '.'.join(str(i) for i in current_indices if i > 0)

        # 处理 h1 标签
        if level == 1:
            # 处理 h1 标签
            current_h1 = soup.new_tag('a')
            current_h1['href'] = f'#{header["id"]}'
            current_h1['class'] = 'toc_section'
            current_h1.string = f'{prefix} {header.get_text()}'
            toc.append(current_h1)

            # 创建一个新的列表
            ul = soup.new_tag('ul')
            toc.append(ul)
        else:
            # 处理 h2-h6 标签
            li = soup.new_tag('li')
            link = soup.new_tag('a')
            link['href'] = f'#{header["id"]}'
            link.string = f'{prefix} {header.get_text()}'
            li.append(link)
            ul.append(li)  # 将链接添加到当前 h1 的列表中

# 添加目录样式
    style = soup.find('style')
    if not style:
        style = soup.new_tag('style')
        soup.head.append(style)
        style.string = ""

    # 添加目录样式
    toc_style = """
h2,
h3,
h4,
h5,
h6 {
  page-break-before: always;
  page-break-after: avoid;
}

a.toc_section::before {
  background: #fbc847;
  display: block;
  content: '';
  height: .08cm;
  margin-bottom: .25cm;
  width: 100%;
}

a.toc_section {
  font-weight: 500;
  margin: 3em 0 1em;
}

#contents {
    break-before: right;
    break-after: left;
    page: no-chapter;
}

#contents h2 {
    font-size: 20pt;
    font-weight: 400;
    margin-bottom: 3cm;
}

#contents a {
    font-weight: 500;
    display: block;  /* 使a表现得像块元素 */
    margin: 1em 0;  /* 添加间距 */
}

#contents ul {
    list-style: none;
    padding-left: 0;
}

#contents ul li {
    border-top: .25pt solid #c1c1c1;
    margin: .25cm 0;
    padding-top: .25cm;
}

#contents ul li a::before {
    color: #fbc847;
    content: '• ';
    font-size: 40pt;
    line-height: 16pt;
    vertical-align: bottom;
}

#contents ul li a {
    color: inherit;
    text-decoration-line: inherit;
}

#contents ul li a::after {
    color: #fbc847;
    content: target-counter(attr(href), page);
    float: right;
}
"""

    if style.string is None:
        style.string = toc_style
    else:
        style.string += toc_style

    return toc

# 异步函数：处理代码高亮
async def process_code_block(code_block, soup):
    """处理代码高亮"""
    try:
        code = code_block.get_text()

        # 获取语言类型
        language = None
        if code_block.get('class'):
            for cls in code_block.get('class'):
                if cls.startswith('language-'):
                    language = cls.replace('language-', '')
                    break

        # 确定使用的样式 - 使用更适合打印的主题
        style_name = 'vs'  # 改为 vs 主题，更适合打印

        try:
            if language:
                lexer = get_lexer_by_name(language)
            else:
                lexer = guess_lexer(code)
        except ClassNotFound as e:
            print(f"无法找到语言解析器: {e}")
            lexer = TextLexer()

        # 检查是否为块级元素
        is_block = code_block.parent.name == 'pre'

        # 使用特定的格式化选项
        formatter = HtmlFormatter(
            style=style_name,
            cssclass='highlight',  # 使用统一的基础类名
            nowrap=False if is_block else True,
            linenos=False,
            noclasses=False,  # 确保生成类名
        )

        highlighted = highlight(code, lexer, formatter)

        # 创建包装元素
        new_div = soup.new_tag('div' if is_block else 'span')
        new_div['class'] = f'highlight' if is_block else 'highlight-inline'

        # 直接使用 HTML 字符串创建新的标签
        new_code = BeautifulSoup(highlighted, 'html.parser')
        if new_code.contents:
            new_div.extend(new_code.contents)

        code_block.replace_with(new_div)

        # 添加样式（只添加一次）
        if not soup.find('style', class_='pygments-style'):
            style_tag = soup.new_tag('style')
            style_tag['class'] = 'pygments-style'

            # 生成基础高亮样式
            base_style = formatter.get_style_defs('.highlight')

            # 添加优化的容器样式
            container_style = """
            /* 代码块容器样式 */
            .highlight {
                break-inside: avoid;
                display: block;
                padding: 1em;
                font-size: 8pt;
                border-radius: 4px;
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                overflow-x: auto;
                margin: 1em 0;
                font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            }

            /* 行内代码样式 */
            .highlight-inline {
                display: inline;
                border-radius: 3px;
                background-color: #f6f8fa;
                color: #24292e;
                border: 1px solid #e1e4e8;
                font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
                font-size: 85%;
            }

            /* 代码块内部样式 */
            .highlight pre {
                margin: 0;
                padding: 0;
                background: transparent;
            }

            .highlight span {
                white-space: pre;
                word-wrap: normal;
                word-break: keep-all;
            }

            /* 确保语法高亮颜色在PDF中正确显示 */
            .highlight .hll { background-color: #ffffcc }
            .highlight .c { color: #6a737d; font-style: italic } /* Comment */
            .highlight .err { color: #d73a49; background-color: #ffeef0 } /* Error */
            .highlight .k { color: #d73a49; font-weight: bold } /* Keyword */
            .highlight .o { color: #24292e; font-weight: bold } /* Operator */
            .highlight .ch { color: #6a737d; font-style: italic } /* Comment.Hashbang */
            .highlight .cm { color: #6a737d; font-style: italic } /* Comment.Multiline */
            .highlight .cp { color: #6a737d; font-style: italic } /* Comment.Preproc */
            .highlight .cpf { color: #6a737d; font-style: italic } /* Comment.PreprocFile */
            .highlight .c1 { color: #6a737d; font-style: italic } /* Comment.Single */
            .highlight .cs { color: #6a737d; font-style: italic } /* Comment.Special */
            .highlight .gd { color: #24292e; background-color: #ffeef0 } /* Generic.Deleted */
            .highlight .ge { color: #24292e; font-style: italic } /* Generic.Emph */
            .highlight .gi { color: #24292e; background-color: #f0fff4 } /* Generic.Inserted */
            .highlight .gs { color: #24292e; font-weight: bold } /* Generic.Strong */
            .highlight .gu { color: #6f42c1; font-weight: bold } /* Generic.Subheading */
            .highlight .kc { color: #d73a49; font-weight: bold } /* Keyword.Constant */
            .highlight .kd { color: #d73a49; font-weight: bold } /* Keyword.Declaration */
            .highlight .kn { color: #d73a49; font-weight: bold } /* Keyword.Namespace */
            .highlight .kp { color: #d73a49; font-weight: bold } /* Keyword.Pseudo */
            .highlight .kr { color: #d73a49; font-weight: bold } /* Keyword.Reserved */
            .highlight .kt { color: #d73a49; font-weight: bold } /* Keyword.Type */
            .highlight .m { color: #005cc5 } /* Literal.Number */
            .highlight .s { color: #032f62 } /* Literal.String */
            .highlight .na { color: #6f42c1 } /* Name.Attribute */
            .highlight .nb { color: #005cc5 } /* Name.Builtin */
            .highlight .nc { color: #6f42c1; font-weight: bold } /* Name.Class */
            .highlight .no { color: #005cc5 } /* Name.Constant */
            .highlight .nd { color: #6f42c1; font-weight: bold } /* Name.Decorator */
            .highlight .ni { color: #005cc5 } /* Name.Entity */
            .highlight .ne { color: #d73a49; font-weight: bold } /* Name.Exception */
            .highlight .nf { color: #6f42c1; font-weight: bold } /* Name.Function */
            .highlight .nl { color: #005cc5 } /* Name.Label */
            .highlight .nn { color: #6f42c1; font-weight: bold } /* Name.Namespace */
            .highlight .nx { color: #6f42c1 } /* Name.Other */
            .highlight .py { color: #005cc5 } /* Name.Property */
            .highlight .nt { color: #d73a49; font-weight: bold } /* Name.Tag */
            .highlight .nv { color: #005cc5 } /* Name.Variable */
            .highlight .ow { color: #d73a49; font-weight: bold } /* Operator.Word */
            .highlight .w { color: #24292e } /* Text.Whitespace */
            .highlight .mb { color: #005cc5 } /* Literal.Number.Bin */
            .highlight .mf { color: #005cc5 } /* Literal.Number.Float */
            .highlight .mh { color: #005cc5 } /* Literal.Number.Hex */
            .highlight .mi { color: #005cc5 } /* Literal.Number.Integer */
            .highlight .mo { color: #005cc5 } /* Literal.Number.Oct */
            .highlight .sa { color: #032f62 } /* Literal.String.Affix */
            .highlight .sb { color: #032f62 } /* Literal.String.Backtick */
            .highlight .sc { color: #032f62 } /* Literal.String.Char */
            .highlight .dl { color: #032f62 } /* Literal.String.Delimiter */
            .highlight .sd { color: #6a737d; font-style: italic } /* Literal.String.Doc */
            .highlight .s2 { color: #032f62 } /* Literal.String.Double */
            .highlight .se { color: #032f62 } /* Literal.String.Escape */
            .highlight .sh { color: #032f62 } /* Literal.String.Heredoc */
            .highlight .si { color: #032f62 } /* Literal.String.Interpol */
            .highlight .sx { color: #032f62 } /* Literal.String.Other */
            .highlight .sr { color: #032f62 } /* Literal.String.Regex */
            .highlight .s1 { color: #032f62 } /* Literal.String.Single */
            .highlight .ss { color: #032f62 } /* Literal.String.Symbol */
            .highlight .bp { color: #005cc5 } /* Name.Builtin.Pseudo */
            .highlight .fm { color: #6f42c1; font-weight: bold } /* Name.Function.Magic */
            .highlight .vc { color: #005cc5 } /* Name.Variable.Class */
            .highlight .vg { color: #005cc5 } /* Name.Variable.Global */
            .highlight .vi { color: #005cc5 } /* Name.Variable.Instance */
            .highlight .vm { color: #005cc5 } /* Name.Variable.Magic */
            .highlight .il { color: #005cc5 } /* Literal.Number.Integer.Long */
            """

            style_tag.string = base_style + container_style
            if soup.head:
                soup.head.append(style_tag)
            else:
                print("文档没有 <head> 标签，无法插入样式")

    except Exception as e:
        import traceback
        print(f"代码高亮处理失败: {e}")
        print(traceback.format_exc())

# 异步函数：处理mermaid图表
async def process_mermaid(mermaid_block, soup, index, output_dir):
    """处理mermaid图表"""
    mermaid_content = mermaid_block.get_text().strip()

    # 检查mermaid内容是否为空
    if not mermaid_content:
        print(f"警告: 空的mermaid块 #{index}")
        return

    # 使用MD5生成唯一的文件名
    content_hash = hashlib.md5(mermaid_content.encode('utf-8')).hexdigest()
    output_file = os.path.join(output_dir, f'mermaid_{content_hash}.png')

    # 检查文件是否已存在
    print('检查文件是否存在:', output_file)
    if os.path.exists(output_file):
        print(f"使用缓存的mermaid图片 #{index}: {os.path.basename(output_file)}")
        # 直接使用已存在的图片
        img = soup.new_tag('img')
        img['src'] = f'{output_dir}/mermaid_{content_hash}.png'
        img['class'] = 'mermaid'
        mermaid_block.replace_with(img)
        return

    # 创建临时文件存储mermaid内容
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
        f.write(mermaid_content)
        mmd_file = f.name

    try:
        # 使用python subprocess调用mmdc命令，添加超时设置
        process = await asyncio.create_subprocess_exec(
            'mmdc',
            '-i', mmd_file,
            '-o', output_file,
            '-t', 'default',  # 使用默认主题
            '-b', 'transparent',  # 透明背景
            '-q', '4',  # 设置质量为4（最高质量）
            '-w', '2048',  # 设置宽度（可以根据需要调整）
            '-s', '2',  # 设置缩放比例为2（提高清晰度）
            '--pdfFit',  # 适应PDF大小
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)

            if process.returncode == 0 and os.path.exists(output_file):
                print(f"生成新的mermaid图片 #{index}: {os.path.basename(output_file)}")
                # 创建新的img标签，使用相对路径
                img = soup.new_tag('img')
                img['src'] = f'{output_dir}/mermaid_{content_hash}.png'
                img['class'] = 'mermaid'
                mermaid_block.replace_with(img)
            else:
                print(f"Mermaid转换失败 #{index}: {stderr.decode()}")
                # 保留原始mermaid块
                print(f"原始内容: {mermaid_content[:100]}...")
        except asyncio.TimeoutError:
            print(f"Mermaid转换超时 #{index}")
            process.kill()

    except Exception as e:
        print(f"处理Mermaid图表时出错 #{index}: {e}")
    finally:
        # 清理临时文件
        try:
            os.unlink(mmd_file)
        except:
            pass

# 异步函数：生成PDF封面
async def generate_cover(book_toml_path: str, soup: BeautifulSoup) -> None:
    """生成PDF封面"""
    try:
        # 读取book.toml文件
        with open(book_toml_path, 'r', encoding='utf-8') as f:
            book_config = toml.load(f)

        # 统计字数
        content_div = soup.find('div', id='content')
        word_count = 0
        if content_div:
            word_count = len(''.join(content_div.stripped_strings))

        # 创建封面容器
        cover_container = soup.new_tag('div')
        cover_container['class'] = 'cover-container'

        # 添加装饰元素
        corner_decoration = soup.new_tag('div')
        corner_decoration['class'] = 'corner-decoration'
        cover_container.append(corner_decoration)

        # 添加书名
        book_title = soup.new_tag('div')
        book_title['class'] = 'book-title'
        # 处理书名，如果包含换行符则分割
        title_text = book_config['book']['title']
        title_text = title_text.capitalize()
        if '\n' in title_text:
            title_lines = title_text.split('\n')
            for i, line in enumerate(title_lines):
                if i > 0:
                    book_title.append(soup.new_tag('br'))
                book_title.append(line)
        else:
            book_title.string = title_text
        cover_container.append(book_title)

        # 添加作者
        author = soup.new_tag('div')
        author['class'] = 'author'
        author.string = f"作者 · {', '.join(book_config['book']['authors'])}"
        cover_container.append(author)

        # 添加元信息容器
        meta_info = soup.new_tag('div')
        meta_info['class'] = 'meta-info'

        # 更新时间
        update_time = soup.new_tag('div')
        update_time['class'] = 'update-time'
        update_time.string = f"最后更新于 {datetime.now().strftime('%Y年%m月%d日')}"
        meta_info.append(update_time)

        # 字数统计
        word_count_div = soup.new_tag('div')
        word_count_div['class'] = 'word-count'
        word_count_div.string = f"全书共计 {word_count:,} 字"
        meta_info.append(word_count_div)

        cover_container.append(meta_info)

        # 在内容最前面插入封面
        content_div = soup.find('div', id='content')
        if content_div:
            content_div.insert(0, cover_container)

        # 添加封面样式
        cover_style = soup.new_tag('style')
        cover_style['class'] = 'cover-style'
        cover_style.string = """
        /* 封面样式 */
        .cover-container {
            width: 186mm;
            height: 263mm;
            background: white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 30px;
            position: relative;
            overflow: hidden;
            border-radius: 2px;
            margin: 0 auto;
            page-break-after: always;
        }
        
        /* 装饰性渐变条 */
        .cover-container::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 8px;
            background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        }
        
        .book-title {
            font-size: 42pt;
            font-weight: 600;
            margin: 40px 0;
            color: #2c3e50;
            line-height: 1.3;
            letter-spacing: 2px;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.05);
            font-family: "Noto Serif SC", "SimSun", serif;
            text-align: center;
        }
        
        .author {
            font-size: 20pt;
            margin: 60px 0;
            color: #7f8c8d;
            letter-spacing: 3px;
            position: relative;
            display: inline-block;
            text-align: center;
        }
        
        .author::after {
            content: "";
            position: absolute;
            bottom: -15px;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 2px;
            background: linear-gradient(90deg, transparent 0%, #3498db 50%, transparent 100%);
        }
        
        .meta-info {
            margin-top: 80px;
            font-size: 13pt;
            color: #95a5a6;
            line-height: 1.8;
            text-align: center;
        }
        
        .update-time {
            font-weight: 300;
        }
        
        .word-count {
            font-style: italic;
            letter-spacing: 1px;
        }
        
        /* 右下角装饰元素 */
        .corner-decoration {
            position: absolute;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            opacity: 0.1;
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            clip-path: polygon(0 40%, 40% 40%, 40% 0, 100% 0, 100% 100%, 0 100%);
        }
        
        /* 封面页面设置 */
        @page cover {
            size: A4;
            margin: 0;
        }
        
        .cover-container {
            page: cover;
        }
        """

        if soup.head:
            soup.head.append(cover_style)
        else:
            print("文档没有 <head> 标签，无法插入封面样式")

    except Exception as e:
        print(f"生成封面时出错: {e}")
        import traceback
        print(traceback.format_exc())

# 异步函数：检查是否安装了mermaid-cli工具
async def check_mermaid_cli():
    """检查是否安装了mermaid-cli工具"""
    if not shutil.which('mmdc'):
        return False
    return True

# 异步函数：处理HTML文件
async def process_html_file(html_file):
    start_time = time.time()

    # 获取book.toml路径
    book_toml_path = os.path.join(os.path.dirname(html_file), '..', 'book.toml')

    # 获取输入文件的目录
    output_dir = os.path.dirname(os.path.abspath(html_file))
    mermaid_dir = os.path.join(output_dir, 'mermaid_images')
    os.makedirs(mermaid_dir, exist_ok=True)  # 提前创建mermaid目录

    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    parse_time = time.time() - start_time
    print(f"HTML解析耗时: {parse_time:.2f}秒")

    # 检查是否存在mermaid图表
    mermaid_blocks = soup.find_all('pre', class_='mermaid')
    if mermaid_blocks:
        # 如果存在mermaid图表，检查是否安装了mermaid-cli
        if not await check_mermaid_cli():
            print("\n错误: 检测到文档中包含 Mermaid 图表，但未安装 mermaid-cli 工具")
            print("请按照以下步骤安装 mermaid-cli:")
            print("\n1. 首先确保已安装 Node.js 和 npm")
            print("2. 然后运行以下命令安装 mermaid-cli:")
            print("\n   npm install -g @mermaid-js/mermaid-cli")
            print("\n安装完成后重新运行本程序")
            sys.exit(1)

    # 获取或创建content div
    content_div = soup.find('div', id='content')
    if not content_div:
        content_div = soup.new_tag('div')
        content_div['id'] = 'content'
        if soup.body:
            soup.body.append(content_div)

    # 先生成目录
    toc_start = time.time()
    toc = await generate_toc(soup)
    if toc:  # 确保目录生成成功
        content_div.insert(0, toc)  # 先插入目录
    toc_time = time.time() - toc_start
    print(f"目录生成耗时: {toc_time:.2f}秒")

    # 再生成封面（在目录之前）
    cover_time = 0
    if os.path.exists(book_toml_path):
        cover_start = time.time()
        await generate_cover(book_toml_path, soup)
        cover_time = time.time() - cover_start
        print(f"封面生成耗时: {cover_time:.2f}秒")

    # 处理代码高亮
    code_start = time.time()
    code_blocks = soup.find_all('code')
    code_tasks = [process_code_block(block, soup) for block in code_blocks]
    await asyncio.gather(*code_tasks)
    code_time = time.time() - code_start
    print(f"代码高亮处理耗时: {code_time:.2f}秒 (处理了{len(code_blocks)}个代码块)")

    # 处理mermaid图表
    mermaid_time = 0
    if mermaid_blocks:
        mermaid_start = time.time()
        semaphore = asyncio.Semaphore(2)
        async def process_mermaid_with_semaphore(block, soup, i, mermaid_dir):
            async with semaphore:
                return await process_mermaid(block, soup, i, mermaid_dir)

        mermaid_tasks = [process_mermaid_with_semaphore(block, soup, i, mermaid_dir) for i, block in enumerate(mermaid_blocks)]
        await asyncio.gather(*mermaid_tasks)
        mermaid_time = time.time() - mermaid_start
        print(f"Mermaid图表处理耗时: {mermaid_time:.2f}秒 (处理了{len(mermaid_blocks)}个图表)")

    # 添加CSS样式和保存HTML
    save_start = time.time()
    style = soup.new_tag('style')
    style.string = """
    @page {
        @bottom-right {
            background: #fbc847;
            content: counter(page);
            height: 1cm;
            text-align: center;
            width: 1cm;
        }
        @top-center {
            background: #fbc847;
            content: '';
            display: block;
            height: .05cm;
            opacity: .5;
            width: 100%;
            margin-bottom: 7pt;
        }
        @top-right {
            content: string(chapter);
            font-size: 9pt;
            height: 1cm;
            vertical-align: middle;
            width: 100%;
            margin-bottom: 7pt;
        }
    }

    html {
        color: #393939;
        font-family: Fira Sans;
        font-size: 11pt;
        font-weight: 300;
        line-height: 1.5;
    }

    /* 封面页面设置已在封面生成函数中处理 */

    /* 修改mermaid图片样式 */
    .mermaid {
        max-width: 100%;
        break-inside: avoid;
        width: auto;
        height: auto;
        image-rendering: high-quality;  /* 添加图片渲染质量设置 */
        -webkit-image-rendering: high-quality;
        -ms-image-rendering: high-quality;
    }

    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
        string-set: chapter content();
    }

    @media print {
        table {
            page-break-after: auto
        }

        tr {
            page-break-inside: avoid;
            page-break-after: auto
        }

        td {
            page-break-inside: avoid;
            page-break-after: auto
        }

        thead {
            display: table-header-group
        }

        tfoot {
            display: table-footer-group
        }
    }
    """
    soup.head.append(style)

    output_html = html_file.replace('.html', '_processed.html')
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    save_time = time.time() - save_start
    print(f"HTML保存耗时: {save_time:.2f}秒")

    # 生成PDF并统计页数
    pdf_start = time.time()
    pdf_path = html_file.replace('.html', '.pdf')
    html = HTML(output_html)
    pdf_document = html.write_pdf(pdf_path)

    # 使用WeasyPrint计算页数
    total_pages = len(html.render().pages)
    pdf_time = time.time() - pdf_start

    print(f"PDF生成耗时: {pdf_time:.2f}秒")
    print(f"PDF总页数: {total_pages}页")
    print(f"平均每页处理时间: {pdf_time/total_pages:.2f}秒")
    print(f"\nPDF文件已生成: {os.path.abspath(pdf_path)}")

    total_time = time.time() - start_time
    print(f"\n总耗时统计:")
    print(f"{'处理步骤':<15} {'耗时(秒)':<10} {'占比':<10}")
    print("-" * 35)
    print(f"{'HTML解析':<15} {parse_time:>10.2f} {parse_time/total_time*100:>9.1f}%")
    print(f"{'封面生成':<15} {cover_time:>10.2f} {cover_time/total_time*100:>9.1f}%")
    print(f"{'目录生成':<15} {toc_time:>10.2f} {toc_time/total_time*100:>9.1f}%")
    print(f"{'代码高亮':<15} {code_time:>10.2f} {code_time/total_time*100:>9.1f}%")
    print(f"{'Mermaid处理':<15} {mermaid_time:>10.2f} {mermaid_time/total_time*100:>9.1f}%")
    print(f"{'HTML保存':<15} {save_time:>10.2f} {save_time/total_time*100:>9.1f}%")
    print(f"{'PDF生成':<15} {pdf_time:>10.2f} {pdf_time/total_time*100:>9.1f}%")
    print("-" * 35)
    print(f"{'总计':<15} {total_time:>10.2f} {'100.0':>9}%")
    print(f"平均每页耗时: {total_time/total_pages:.2f}秒")

# 主函数
def main():
    import sys
    # 检查命令行参数个数
    if len(sys.argv) != 2:
        print("使用方法: python script.py <html文件>")  # 打印使用方法
        sys.exit(1)  # 退出脚本并返回错误代码

    html_file = sys.argv[1]  # 获取HTML文件名
    asyncio.run(process_html_file(html_file))  # 运行异步函数处理HTML文件

if __name__ == "__main__":
    main()  # 调用主函数执行脚本
