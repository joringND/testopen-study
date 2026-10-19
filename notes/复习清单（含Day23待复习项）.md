# 复习清单（待办）

> 学习过程中标记为"暂理解、后复习"的知识点，学到对应主题时回来补。

---

## 待复习

### 1. Day23：`_request` 自动认证逻辑 + mock v3 的 token 机制
- 状态：⏳ 待复习（2026-10-20 标记）
- 标记原因：当时没细看新版 mock_server.py，对"每次登录发新 token / 只有最新 token 有效 / 401 重试"的完整闭环缺 mock 侧视角
- 现在理解程度：`_request` 逐行已懂（懒登录 / 自动带 headers / 401 重新登录重试）；缺 mock 侧：COUNTER/LATEST_TOKEN 全局变量、Set-Cookie、Bearer 校验
- **复习触发点**：学到 mock 深入 / 接口框架 mock 专题时，回看：
  - mock v3 的 `do_POST /login`（COUNTER 递增 → LATEST_TOKEN 更新）
  - mock v3 的 `do_GET /get_user`（Bearer == 最新 token 才 200）
  - `_request` 在 401 时的重试链路（旧 token → 401 → login() 换新 → 重发）
  - 用练习5 的方式亲眼验证：打印第一次状态码（401）和最终状态码（200）

## 已复习

（暂无）
