# The PureTime · 每日 Instagram Story 自动发布

每天自动:抓取预约空档 → 生成故事图片 → 发布到 Instagram Story。

---

## 一、部署前必读

**这个 GitHub 仓库必须设为 Public(公开)。**
因为 Instagram 服务器需要能直接访问到生成的图片地址(raw.githubusercontent.com),
私有仓库的文件它读不到。仓库里不会有任何顾客隐私信息，只有店铺logo、背景照片和"预约时段"这种本来就会公开发在社交媒体上的内容，公开仓库是安全的。

---

## 二、需要准备的 4 个 GitHub Secrets

进入你的仓库 → **Settings → Secrets and variables → Actions → New repository secret**，依次添加:

| Secret 名称 | 值 | 说明 |
|---|---|---|
| `BOOKING_AUTH_HEADER` | `Basic QBlek+j7a55AKQ7...`(你之前给我的那一串) | 预约网站接口需要的授权头 |
| `BOOKING_SERVICE_ID` | `200` | Luxury Head Spa 对应的服务ID，以后想换服务改这里就行 |
| `IG_USER_ID` | `17841447945876531` | the.puretime.headspa 对应的 Instagram Business Account ID |
| `IG_ACCESS_TOKEN` | (在 App 后台 "API setup with Instagram login" 页面生成) | Instagram 长期访问令牌 |

---

## 三、获取 IG_USER_ID 和 IG_ACCESS_TOKEN(Instagram Login 方式，2026年新版流程)

Meta 已经把 Instagram 发布接口升级成了 **"Instagram API with Instagram Login"**，
不再需要绑定 Facebook Page，流程比旧版简单。

### 已经拿到的信息
- **IG_USER_ID**: `17841447945876531` (the.puretime.headspa 账号)

### 步骤(已完成，供以后参考/token过期后重新生成用)

1. **创建 Meta App** → developers.facebook.com/apps → Create App → Business 类型
2. **添加 "Manage messaging & content on Instagram" 这个 use case**
3. App 后台左侧菜单 → **Instagram → API setup with Instagram login**
4. 第 1 步区块 "Add required messaging permissions" → 点 "Go to permissions and features"，
   确认以下权限都已启用(**尤其是 `instagram_business_content_publish`，这是发布内容必需的**)：
   - `instagram_business_basic`
   - `instagram_business_content_publish`
   - `instagram_business_manage_comments`(可选)
   - `instagram_business_manage_messages`(可选)
5. **App roles → Roles → Add People** → 角色选 "Instagram Tester" → 填入 Instagram 账号用户名
6. 手机 Instagram App 里 → 设置 → Apps and websites → Tester Invites → Accept
7. 回到 "API setup with Instagram login" 页面 → 第 2 步区块 "Generate access tokens" →
   找到账号 the.puretime.headspa 那一行 → 点 "Generate token" → 登录并 Allow 授权
8. 弹窗里显示的长长一串字符就是 `IG_ACCESS_TOKEN`，**只显示一次**，立即复制保存

   ⚠️ **这个 token 有效期通常是 60 天左右**，到期前需要重复第 7-8 步重新生成一次，更新到 GitHub Secret 里。

   ⚠️ **调用的 API 地址是 `graph.instagram.com`**，不是旧版的 `graph.facebook.com`(代码里已经改好了，这里只是记录一下原因，避免以后debug困惑)。

---

## 四、本地测试(可选)

如果你想在正式接入 GitHub Actions 之前，先在自己电脑上跑一次确认没问题:

```bash
pip install -r requirements.txt
playwright install chromium

export BOOKING_AUTH_HEADER="Basic ...."
export IG_USER_ID="1234567890"
export IG_ACCESS_TOKEN="EAAxxxxx"

python3 main.py
```

---

## 五、上线

把以上 4 个 Secrets 填好后，工作流会**每天 UTC 12:00(对应美东夏令时早上8点)自动运行**。

也可以手动测试：进入仓库 → **Actions** 标签页 → 左侧选择 "Daily Instagram Story" → 右上角 **"Run workflow"** 按钮，立即触发一次，方便验证效果。

如果之后想改发布时间，编辑 `.github/workflows/daily_story.yml` 里的 `cron` 那一行即可（时间是 UTC，需要自己换算）。
