// Xuất 10 logo trong «Xem thử logo Messenger.html» ra PNG 512×512 (vẽ bằng WebKit, có bóng đổ như icon macOS).
// Cách dùng: swift xuat-png.swift "<file html>" "<thư mục ra>"
import Cocoa
import WebKit

let tenFile = ["but-chi", "no-hong", "gau", "thach-kinh", "anh-dao", "thien-ha", "neon", "8bit", "chrome", "den-nham"]
let args = CommandLine.arguments
let html = URL(fileURLWithPath: args[1]), ra = URL(fileURLWithPath: args[2])
try? FileManager.default.createDirectory(at: ra, withIntermediateDirectories: true)

final class XuLy: NSObject, WKNavigationDelegate {
    func webView(_ w: WKWebView, didFinish _: WKNavigation!) {
        w.callAsyncJavaScript("""
          const ds = [...document.querySelectorAll('.the:not(.hientai) .to svg')], kq = [];
          for (const s0 of ds) {
            const s = s0.cloneNode(true); s.setAttribute('width', 512); s.setAttribute('height', 512);  // vẽ thẳng 512 px, không phóng ảnh nhỏ
            const c = document.createElement('canvas'); c.width = c.height = 512; const x = c.getContext('2d');
            const im = new Image(); im.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(new XMLSerializer().serializeToString(s));
            await im.decode();
            x.shadowColor = 'rgba(0,0,0,0.28)'; x.shadowBlur = 14; x.shadowOffsetY = 7;
            x.drawImage(im, 0, 0, 512, 512);
            kq.push(c.toDataURL('image/png').split(',')[1]);
          }
          return kq;
        """, arguments: [:], in: nil, in: .page) { r in
            guard case .success(let v) = r, let ds = v as? [String] else { print("⛔", r); exit(1) }
            guard ds.count == tenFile.count else { print("⛔ có \(ds.count) logo, cần \(tenFile.count)"); exit(1) }
            for (i, b) in ds.enumerated() {
                try! Data(base64Encoded: b)!.write(to: ra.appendingPathComponent(tenFile[i] + ".png"))
            }
            print("✅ \(ds.count) logo → \(ra.path)"); exit(0)
        }
    }
}
let app = NSApplication.shared
let w = WKWebView(frame: NSRect(x: 0, y: 0, width: 1280, height: 1000))
let xl = XuLy(); w.navigationDelegate = xl
w.loadFileURL(html, allowingReadAccessTo: html.deletingLastPathComponent())
DispatchQueue.main.asyncAfter(deadline: .now() + 30) { print("⛔ quá 30 giây"); exit(1) }
app.run()
