# Messenger Vdk

App Messenger gọn nhẹ cho macOS (chip Apple), viết bằng Swift + WKWebView. Chỉ **~1,2 MB** (bản Electron gốc ~241 MB).

> ⚠️ App **không chính thức**, không liên quan tới Meta. App chỉ mở trang **messenger.com** chính thức trong một cửa sổ riêng – đăng nhập, tin nhắn, cuộc gọi đi thẳng tới máy chủ Meta như khi dùng trình duyệt. App **không gửi dữ liệu đi đâu khác**, không thu thập thông tin người dùng.

## Tính năng
- **Thông báo tin nhắn** khi bạn ở app khác (cả tin nhóm). Dock chỉ nảy khi có cuộc gọi.
- **Bảng nổi cuộc gọi đến**: phân biệt gọi thoại / video / gọi nhóm (kèm tên nhóm), bấm Từ chối / Chấp nhận ngay trên bảng. Gác máy là tắt chuông.
- **Cuộc gọi**: chia sẻ màn hình, tự thu nhỏ thành cửa sổ nổi (PiP) khi chuyển app, ⇧⌘P.
- **Tải ảnh / file**: hỏi lưu vào đâu (hoặc lưu thẳng một thư mục), giữ độ phân giải gốc.
- **Phím tắt**: ⌘N tin nhắn mới · ⌘1–9 mở đoạn chat · ⌘F / ⇧⌘F tìm · ⌘S ẩn/hiện thông tin cuộc trò chuyện · ⇧⌘S ẩn/hiện thanh bên · ⌘/ bảng phím tắt.
- **Cài đặt (⌘,)**: thông báo, cuộc gọi, tải file, mở cùng máy, nhật ký gỡ lỗi.
- **Cập nhật trong app**: Cài đặt → Chung → *Kiểm tra cập nhật* – bản mới được kiểm chữ ký số (Ed25519) rồi tự cài. App không tự hỏi, chỉ kết nối GitHub khi bạn bấm.
- **Đăng xuất và xoá dữ liệu** (Cài đặt → Chung) cho máy dùng chung.
- **Gói chẩn đoán** (Trợ giúp → Tạo gói chẩn đoán…) để báo lỗi – không chứa mật khẩu hay tin nhắn.
- Giữ đăng nhập, chỉ chạy 1 bản, giao diện tiếng Việt.

## Cài đặt
Yêu cầu: macOS 14 trở lên, chip Apple (M1/M2/M3…).

1. Tải file **`.dmg`** mới nhất ở mục **[Releases](../../releases/latest)**.
2. Bấm đúp file DMG → kéo **Messenger Vdk** vào **Applications**.

   <img src="anh/cua-so-dmg.png" width="460" alt="Cửa sổ DMG">

3. Mở lần đầu: app chưa được Apple công chứng nên macOS sẽ chặn → **Cài đặt hệ thống → Quyền riêng tư & Bảo mật → Bảo mật → Vẫn mở**.

👉 **Hướng dẫn chi tiết từng trường hợp (có ảnh): [HUONG-DAN-CAI.md](HUONG-DAN-CAI.md)** – file này cũng có sẵn trong DMG («Hướng dẫn mở lần đầu»).

### Gõ tiếng Việt bị lỗi dấu (lặp dấu, mất chữ)?
- **Bộ gõ Apple** (Telex/VNI): dùng được ngay, không cần chỉnh.
- **VietTelex**:
  1. Cập nhật VietTelex lên bản mới nhất.
  2. Mở Cài đặt VietTelex → mục **Cách gõ trực tiếp** → tích 2 ô:
     - ☑ *Dùng cách gõ an toàn cho ứng dụng chưa nhận diện*
     - ☑ *Giữ VietTelex khi macOS tự đổi bộ gõ*
  3. Vẫn lỗi → Cài đặt → tắt «Ẩn tính năng nâng cao» → tab **Bảng cơ chế gõ** → Thêm app → dán `com.vduck.messenger` → chọn **Gõ trực tiếp**.
- **OpenKey**: mở cài đặt OpenKey → bật **Sửa lỗi gợi ý trình duyệt** (mặc định đã bật).
- **Bộ gõ khác** (EVKey, GoTiengViet…) mà vẫn lỗi: chụp màn hình chữ bị sai, gửi cho mình.

### Gặp lỗi khác (không đăng nhập được, trang không tải…)?
1. Làm lại thao tác bị lỗi 1 lần.
2. Menu **Trợ giúp → Tạo gói chẩn đoán…** (hoặc Cài đặt → Chung → *Chẩn đoán*) → lưu file `.zip`.
3. Gửi file đó cho mình. Trong gói chỉ có đường đi của trang + thông tin máy (macOS, bản app), **không có** mật khẩu, email, cookie hay nội dung tin nhắn.

Người hỗ trợ đọc gói bằng: `python3 chan-doan/doc-nhat-ky.py "<file zip>"` – in dòng thời gian lúc đăng nhập và đánh dấu ⚠️ chỗ nghi lỗi.

## Tự build
```bash
bash build.sh
```
Ra `Messenger Vdk.app` trong `$TMPDIR/vduck-messenger-build`. Cần Xcode Command Line Tools. Ký app: đặt mã chứng chỉ vào biến `KY_APP` hoặc file `.ky-app`; không có thì ký tạm (ad-hoc).

Mã nguồn: `Ma nguon/main.swift` (toàn bộ app, chú thích tiếng Việt).

## Ghi công
Ý tưởng từ **MessengerApp** của Stefan – [stefanminch/messenger-mac](https://github.com/stefanminch/messenger-mac) (MIT). Bản này viết lại từ đầu bằng Swift.

Giấy phép: [CC BY-NC 4.0](LICENSE) – được dùng, chia sẻ, sửa lại nếu ghi nguồn, **không dùng vào mục đích thương mại**. (Bản 0.6.0 và 0.6.1 phát hành trước đó theo MIT.)

© 2026 by Vduck
