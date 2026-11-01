# Day32 学习笔记：文件上传/下载接口测试（第 6 周 Day1）

> 日期：2026-11-01
> 计划阶段：18个月测开计划 · 阶段1 筑基期 · 第 6 周 · Day32
> 状态：✅ 3 passed（上传/下载/流式）；自测 2/5，错题回顾后过
> 里程碑：第一次接触"非 JSON"接口形态——文件接口测试

---

## 一、今日目标

给 mock 升级 /upload、/download 两个文件接口，用 requests 写文件上传/下载用例，三步法用于文件接口。

## 二、今日涉及文件

| 操作 | 文件 | 改动 |
|---|---|---|
| 【修改】 | `mock_server.py` | import cgi/io；do_POST 分流；do_GET 加 /download |
| 【新建】 | `day32_homework.py` | 上传/下载/流式 3 用例 |

## 三、知识点：文件接口三板斧

```python
# ① 上传：files= 参数（自动转 multipart/form-data）
files = {"file": ("hello.txt", io.BytesIO(b"hello world"), "text/plain")}
resp = requests.post(url, files=files)
#                  ^^^^^ files= 是 requests 参数名（复数，固定）
#            {"file": ...} 里 file 是表单字段名（mock 用 form["file"] 读）

# ② 下载：stream=True 流式（大文件不一次性进内存）
resp = requests.get(url, stream=True)
for chunk in resp.iter_content(1024):    # 按块迭代，每块 1024 字节
    f.write(chunk)

# ③ 等价写法（chunk vs chunks 别混）
chunks = [chunk for chunk in resp.iter_content(1024)]
#         ^^^^^                    ^^^^^
#         结果列表                   迭代变量
```

**关键差异**：JSON 接口用 `json={...}`；文件接口用 `files={...}`（multipart）；下载用 `stream=True`。

## 四、mock 侧：do_POST 分流（今日核心坑）

**坑**：do_POST 开头 `body = json.loads(self.rfile.read(length))` 一刀切——multipart 不是 JSON → JSONDecodeError；且 body 被读走，FieldStorage 读空流。

**修法**：先读原始字节，按接口类型分流：

```python
raw = self.rfile.read(length) if length else b""   # ① 先读原始字节

if self.path == "/login":
    body = json.loads(raw) if raw else {}          # ② JSON 接口才 json.loads
elif self.path == "/echo":
    body = json.loads(raw) if raw else {}
elif self.path == "/upload":                       # ③ multipart 接口给 cgi
    form = cgi.FieldStorage(fp=io.BytesIO(raw), headers=self.headers,
                            environ={"REQUEST_METHOD": "POST",
                                     "CONTENT_TYPE": self.headers.get("Content-Type", "")})
    file_item = form["file"]
    raw_content = file_item.file.read()
    self._send(200, {"code": 0, "filename": file_item.filename,
                     "size": len(raw_content), "msg": "上传成功"})
```

**口诀**：先读字节，JSON 才 json.loads，multipart 给 cgi。

## 五、今日改动代码走读（逐行）

### 5.1 顶部 import（2 行）

```python
import io   # 提供 BytesIO：把读到的字节"包成内存文件对象"喂给 cgi
import cgi  # 标准库 multipart 解析器：FieldStorage 能拆解 multipart 表单
```

**为什么需要这俩**：requests 上传时把文件转成 multipart 二进制；mock 收到的是"一堆字节 + 一个 Content-Type 头（带 boundary）"。`cgi.FieldStorage` 负责从字节里拆出文件名、内容；但它要"能定位的文件对象"而不是裸字节，所以用 `io.BytesIO(raw)` 包一层。

### 5.2 do_GET 加 /download（逐行）

```python
if self.path == "/download":
    content = b"hello,this is a test file" * 20      # ① 造内容：一段字节×20 ≈ 460 字节
    self.send_response(200)                          # ② 状态行：200 OK
    self.send_header("Content-Type", "application/octet-stream")              # ③ 声明"我是二进制流"
    self.send_header("Content-Disposition", 'attachment; filename="demo.txt"') # ④ 附件头：当文件存，叫 demo.txt
    self.send_header("Content-Length", str(len(content)))                     # ⑤ 告诉客户端"读 460 字节就完"
    self.end_headers()                               # ⑥ 头部结束（空行）
    self.wfile.write(content)                        # ⑦ 写响应体：文件内容
    return
```

**三个头各管什么**：
- `Content-Type: application/octet-stream` → 不是 JSON，是原始字节流
- `Content-Disposition: attachment; filename="demo.txt"` → **当附件下载** + 给文件名（拼错 Dispositon 会让它失效）
- `Content-Length` → 客户端读多少字节算完（没有它可能等不到结束）

### 5.3 do_POST 重构（核心）

```python
def do_POST(self):
    global LATEST_TOKEN, COUNTER                     # ① 声明要改全局
    length = int(self.headers.get("Content-Length", 0))   # ② 请求头里的"body 长度"
    raw = self.rfile.read(length) if length else b""      # ③ 读原始字节——不解析！
```

**②③ 是灵魂**。以前 `json.loads(self.rfile.read(length))` 一步到位，现在拆成"只读字节、先不解析"。为什么？
- `json.loads(multipart二进制)` 必崩（multipart 不是 JSON）
- **rfile 是流，读一遍就没了**——开头被 json.loads 读走，后面 FieldStorage 再读就是空流

```python
    if self.path == "/login":                        # ④ 分支1：JSON 接口
        body = json.loads(raw) if raw else {}        #    只有走到这里才 json.loads
        # （登录逻辑不变）
    elif self.path == "/echo":                       # ⑤ 分支2：JSON 接口
        body = json.loads(raw) if raw else {}
        self._send(200, {"code": 0, "echo": body})
    elif self.path == "/upload":                     # ⑥ 分支3：multipart 接口
        form = cgi.FieldStorage(
            fp=io.BytesIO(raw),                      # 把字节包成内存文件对象
            headers=self.headers,                    # FieldStorage 靠 Content-Type 找 boundary
            environ={"REQUEST_METHOD": "POST",       # cgi 需要的"环境变量"
                     "CONTENT_TYPE": self.headers.get("Content-Type", "")})
        file_item = form["file"]                     # 按字段名取文件
        raw_content = file_item.file.read()          # 读文件内容字节
        self._send(200, {"code": 0, "filename": file_item.filename,
                         "size": len(raw_content), "msg": "上传成功"})
        return
    else:                                            # ⑦ 兜底
        self._send(404, {"code": 404, "msg": "not found"})
```

**FieldStorage 三个参数为什么这么传**：
- `fp=io.BytesIO(raw)` → 要"能 seek 的文件对象"，BytesIO 把字节变内存文件
- `headers=self.headers` → multipart 的 boundary 藏在 `Content-Type: multipart/form-data; boundary=xxx`，拆包必须知道它
- `environ=...` → cgi 模块按"CGI 环境"工作，REQUEST_METHOD / CONTENT_TYPE 是最小两个键

**`form["file"]` 的 `"file"` 哪来的**：和 requests 端 `files={"file": ("hello.txt", ...)}` **表单字段名一一对应**——发 `file` 字段，mock 就 `form["file"]` 取。这是两端约定的"接头暗号"。

**走读结论**：改动核心一句话——**"JSON 接口和 multipart 接口不能在入口共用同一种解析方式"**，先读字节、按 path 分流。以后加接口：先想清楚 JSON 还是 multipart，再决定放哪个分支、用什么解析。

## 六、今日其他坑

1. **`_send_json` 不存在** → 用 mock 自己的 `_send`
2. **Content-Dispositon 拼错**（少 i）→ `Content-Disposition`（附件名才生效）
3. **chunks = [chunks for ...]** → 迭代变量写错，NameError；应为 `chunk`

## 七、自测批改记录（2/5，错题已回顾）

| 题 | 判定 | 要点 |
|---|---|---|
| 1 files 参数 | ⚠️ | 格式对；参数名是 **files** 不是 file |
| 2 stream | ✅ | 流式不占内存；iter_content 按块 |
| 3 mock 解析模块 | ❌ | **cgi**（FieldStorage）不是 request |
| 4 三断言 | ⚠️ | code / filename / **size** |
| 5 上传代码 | ❌ | `file=files` → TypeError；应为 `files={"file": ...}` |

**错题核心记忆**：
- 外层 `files=`（requests 参数） vs 内层 `"file"`（表单字段名）
- 上传 `files=` / 下载 `stream=`，不混用
- multipart 解析 = cgi.FieldStorage + io.BytesIO

## 八、明日预告（Day33）

接口框架进阶 Day2：**会话与超时控制**——Session 复用、超时设置、重试机制（接口测试的稳定性三件套）。

---

*笔记由 AI 根据当日学习内容整理。*
