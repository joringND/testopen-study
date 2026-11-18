import io
import requests
import pytest

BASE="http://127.0.0.1:8000"

def test_upload_file():
    #files=三元组：(文件名，内容（字节），类型)
    files={"file":("hello.txt",io.BytesIO(b"hello world"),"text/plain")}
    resp=requests.post(f"{BASE}/upload",files=files,timeout=5)
    data=resp.json()
    assert data["code"]==0,f"上传失败，{data}"
    assert data["filename"]=="hello.txt"
    assert data["size"]==11 # b"hello world" = 11 字节

def test_download_file():
    resp=requests.get(f'{BASE}/download',timeout=5)
    assert resp.status_code==200
    assert len(resp.content)>0
    with open("data/downloaded.txt","wb") as f: # 保存到 data/（没有就先建目录）
        f.write(resp.content)
    assert resp.content.startswith(b"hello")

def test_download_stream():
    #大文件版：流式分块，不一次性进内存
    resp=requests.get(f"{BASE}/download",timeout=5,stream=True)
    assert resp.status_code==200
    chunks=[chunk for chunk in resp.iter_content(1024)]
    content=b"".join(chunks)
    assert content.startswith(b"hello")

# 按示例跑通 test_upload_file / test_download_file / test_download_stream，发我运行结果（预期 3 passed）
print("已跑完并提交给ai查看")
# 三步法问答：上传用例里 Q2（调哪个接口、传什么参数）怎么答？
print('上传用例 Q2 = 调 POST /upload，关键参数 files={"file": ("hello.txt", io.BytesIO(b"hello world"), \
      "text/plain")}\
      下载用例 Q2 = 调 GET /download，关键参数 stream=True（+ iter_content 分块）')
# 想一想：data/size == 11 为什么是 11？（字节数）
print('data[size]之所以为11，因为“hello world”包含10个字母和一个空格')

# AI 自测 5 题（一起发了批改）
# 上传文件用 requests 的哪个参数？它自动转成什么格式？
print('使用files=参数，requests 自动转 multipart/form-data')
# 下载大文件为什么用 stream=True？iter_content 是干嘛的？
print('使用流式读，大文件不占内存，iter_content代表每块多少字节')
# mock 端用什么解析上传的 multipart？（模块名）
print('使用cgi模块，cgi.FieldStorage.fp=io.BytesIO(raw) 喂给 FieldStorage 解析。\
      上传解析三件套：cgi.FieldStorage + io.BytesIO + form ["file"]。')
# 上传后断言哪三个点？
print('断言文件是否上传成功、文件名和文件内容是否正确')
# 写代码：用 io.BytesIO 上传 fake.txt（内容 b"abc"）到 /upload，断言 code==0
def test_upload_homework():
    files={"file":("fake.txt",io.BytesIO(b"abc"),"text/plain")}
    resp=requests.post(f"{BASE}/upload",files=files,timeout=5)
    data=resp.json()
    assert data["code"]==0
