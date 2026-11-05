#!/usr/bin/env python3
"""Đọc nhật ký Messenger Vdk → dòng thời gian lúc đăng nhập + chỗ nghi lỗi (⚠️) + kết luận.

Cách dùng:
  python3 chan-doan/doc-nhat-ky.py "<gói chẩn đoán .zip | messenger.log | thư mục>" [--het]
  --het : in mọi lần mở app và mọi dòng (mặc định chỉ in lần mở app có đăng nhập / có lỗi, bỏ bớt dòng mạng)

Nguồn: gói chẩn đoán tạo bằng Trợ giúp → Tạo gói chẩn đoán… (app 0.6.6+). Nhật ký bản cũ (0.6.3) vẫn đọc được
nhưng thiếu dòng «CĐ» (khung con, link bị đẩy ra trình duyệt, mã server).
"""
import io
import os
import re
import sys
import zipfile
from collections import Counter

DONG = re.compile(r'^(\d{4}-\d\d-\d\d) (\d\d:\d\d:\d\d)\.\d+ \S+\[(\d+):\d+\] VM: (.*)$')
KIEM_TRA = re.compile(r'arkoselabs|funcaptcha|captcha|hcaptcha|recaptcha', re.I)   # tên miền ô kiểm tra bảo mật
TRANG_DN = re.compile(r'/(login|checkpoint|two_step|two_factor|auth_platform|recover|device-based|security|arkose|captcha)', re.I)
COOKIE_DN = ('c_user ', 'xs ')


def giay(gio):
    h, m, s = gio.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


def doc_nguon(p):
    """→ (danh sách dòng nhật ký theo thứ tự thời gian, nội dung thong-tin.txt hoặc '')"""
    tep = {}
    if os.path.isdir(p):
        for goc, _, ds in os.walk(p):
            for t in ds:
                if not t.startswith('._'):
                    tep[t] = open(os.path.join(goc, t), encoding='utf-8', errors='replace').read()
    elif p.lower().endswith('.zip'):
        with zipfile.ZipFile(p) as z:
            for t in z.namelist():
                ten = os.path.basename(t)
                if ten and not ten.startswith('._'):
                    tep[ten] = io.TextIOWrapper(z.open(t), encoding='utf-8', errors='replace').read()
    else:
        tep[os.path.basename(p)] = open(p, encoding='utf-8', errors='replace').read()
    if 'messenger.log' in tep or 'messenger.1.log' in tep:   # cũ trước, mới sau
        dong = (tep.get('messenger.1.log', '') + '\n' + tep.get('messenger.log', '')).splitlines()
    else:                                                     # file log tên khác (vd. anh lưu bằng «Lưu nhật ký…»)
        dong = '\n'.join(v for k, v in tep.items() if k != 'thong-tin.txt').splitlines()
    return dong, tep.get('thong-tin.txt', '')


def tach_lan_mo(dong):
    """Gom theo lần mở app (pid) → [(pid, [(ngày, giờ, nội dung)])]"""
    lan, theo_pid = [], {}
    for d in dong:
        m = DONG.match(d)
        if not m:
            continue
        ngay, gio, pid, nd = m.groups()
        if pid not in theo_pid:
            theo_pid[pid] = []
            lan.append((pid, theo_pid[pid]))
        theo_pid[pid].append((ngay, gio, nd))
    return lan


def phan_tich(su_kien, het=False):
    """→ (dòng để in, danh sách cảnh báo, có hoạt động đăng nhập không)"""
    ra, canh_bao = [], []
    mang = Counter()
    khung_da_thay = set()
    xoa_luc = {}            # tên cookie → giờ bị xoá (tìm app dựng lại cookie vừa bị xoá)
    dang_nhap = False       # có thấy trang đăng nhập / bấm Đăng nhập
    da_bam = False
    buoc_cuoi = ''          # trang không-phải-đăng-nhập cuối cùng sau khi bấm (vd. trang kiểm tra bảo mật)
    vao_chat = None

    def cb(gio, s):
        canh_bao.append(f'{gio}  {s}')
        ra.append(f'  ⚠️ {gio}  {s}')

    for ngay, gio, nd in su_kien:
        cd = nd[3:] if nd.startswith('CĐ ') else None
        if cd is not None:
            if cd.startswith('MÁY '):
                ra.append(f'  {gio}  Máy: {cd[4:]}')
            elif cd.startswith('COOKIE lúc mở app'):
                ra.append(f'  {gio}  {cd}')
            elif cd.startswith('COOKIE + ') or cd.startswith('COOKIE − '):
                ten = cd[9:]
                if cd.startswith('COOKIE − '):
                    xoa_luc[ten.split(' ')[0]] = gio
                if ten.startswith(COOKIE_DN) or het:
                    them = ' (cookie đăng nhập)' if ten.startswith(COOKIE_DN) else ''
                    ra.append(f'  {gio}  {"Có" if "+" in cd[:8] else "MẤT"} cookie {ten}{them}')
            elif cd.startswith('ĐH '):
                p = cd.split(' ')
                khung = p[1]
                if 'MỞ TRÌNH DUYỆT' in cd:
                    dich = cd.split(' ')[3] if len(p) > 3 else '?'
                    if vao_chat is None:
                        cb(gio, f'App ĐẨY RA TRÌNH DUYỆT lúc chưa vào chat: {dich} → trang trong app không đi tiếp được ({cd})')
                    else:
                        ra.append(f'  {gio}  Mở trình duyệt: {cd}')
                elif khung == 'chính' or het:
                    ra.append(f'  {gio}  → {cd[3:]}')
                elif khung == 'con':
                    host = p[3].split('/')[0] if len(p) > 3 else '?'
                    if host not in khung_da_thay:
                        khung_da_thay.add(host)
                        ra.append(f'  {gio}  khung con mở {host}')
            elif cd.startswith('PH '):
                p = cd.split(' ')
                ma = int(p[2]) if len(p) > 2 and p[2].isdigit() else 0
                if ma >= 400:
                    if p[1] == 'chính':
                        cb(gio, f'Server trả lỗi {ma} cho trang chính {p[3]}')
                    elif KIEM_TRA.search(cd):
                        cb(gio, f'Khung kiểm tra bảo mật bị server trả lỗi {ma}: {p[3]}')
                    elif het:
                        ra.append(f'  {gio}  {cd}')
                elif p[1] == 'chính' or het:
                    ra.append(f'  {gio}    (server {ma} {p[3] if len(p) > 3 else ""})')
            elif cd.startswith('CHUYỂN HƯỚNG'):
                ra.append(f'  {gio}    {cd}')
            elif cd.startswith('CỬA SỔ MỚI'):
                if 'MỞ TRÌNH DUYỆT' in cd and vao_chat is None:
                    cb(gio, f'Trang xin mở cửa sổ mới, app ĐẨY RA TRÌNH DUYỆT lúc chưa vào chat: {cd[11:]}')
                else:
                    ra.append(f'  {gio}  {cd}')
            elif cd.startswith('TRANG: '):
                s = cd[7:]
                if s.startswith('MẠNG '):
                    host = s.split(' ')[2].split('/')[0] if len(s.split(' ')) > 2 else '?'
                    mang[host] += 1
                    if KIEM_TRA.search(s) or het:
                        ra.append(f'  {gio}    {s}')
                elif s.startswith('THẤY '):
                    co_mk = 'ô mật khẩu có' in s
                    if co_mk:
                        dang_nhap = True
                        if da_bam and buoc_cuoi:
                            cb(gio, f'VĂNG VỀ TRANG ĐĂNG NHẬP sau bước: {buoc_cuoi}')
                            buoc_cuoi = ''
                    elif da_bam:
                        buoc_cuoi = s[5:]
                    ra.append(f'  {gio}  Trang hiện: {s[5:]}')
                elif s.startswith('BẤM ') or s.startswith('GỬI FORM'):
                    if 'Đăng nhập' in s or 'Log in' in s or 'Log In' in s or s.startswith('GỬI FORM'):
                        da_bam = True
                    ra.append(f'  {gio}  👆 {s}')
                elif s.startswith('CSP') or s.startswith('LỖI'):
                    if KIEM_TRA.search(s):
                        cb(gio, f'Trang không tải được phần kiểm tra bảo mật: {s}')
                    else:
                        ra.append(f'  {gio}    {s}')
                else:
                    ra.append(f'  {gio}  {s}')
            elif cd.startswith('KHUNG CON '):
                s = cd[10:]
                host = s.split(':')[0]
                if 'storage access=false' in s and KIEM_TRA.search(host):
                    cb(gio, f'Khung kiểm tra bảo mật {host} KHÔNG được dùng cookie (storage access=false) – WebKit chặn cookie bên thứ ba')
                elif ('LỖI' in s or 'CSP' in s) and KIEM_TRA.search(host):
                    cb(gio, f'Khung kiểm tra bảo mật {host} báo lỗi: {s[len(host) + 2:]}')
                elif KIEM_TRA.search(host) or het or 'LỖI' in s:
                    if 'MẠNG' in s and not het and not KIEM_TRA.search(host):
                        continue
                    ra.append(f'  {gio}    khung {s}')
            elif cd.startswith('đã vào màn chat'):
                vao_chat = gio
                ra.append(f'  ✅ {gio}  Đã vào màn chat (đăng nhập thành công)')
            elif cd.startswith('trang chính về trang đăng nhập'):
                vao_chat = None
                ra.append(f'  {gio}  {cd}')
            elif cd.startswith('THỬ '):
                continue
            else:
                ra.append(f'  {gio}  {cd}')
            if cd.startswith('ĐH chính') and TRANG_DN.search(cd):
                dang_nhap = True
            continue
        # Dòng thường (có cả ở bản 0.6.3)
        if nd.startswith('giữ đăng nhập – cookie '):
            ten = nd.split(' ')[4]
            if ten in xoa_luc and 0 <= giay(gio) - giay(xoa_luc[ten]) <= 3:
                cb(gio, f'App DỰNG LẠI cookie «{ten}» vừa bị server xoá lúc {xoa_luc[ten]} (lỗi lớp giữ đăng nhập)')
            elif het or ten in ('c_user', 'xs'):
                ra.append(f'  {gio}  App gia hạn cookie {ten} → 1 năm')
        elif nd.startswith('lỗi mở trang') or nd.startswith('lỗi tải'):
            if '-999' in nd:
                ra.append(f'  {gio}    {nd} (huỷ – thường do app chặn / đẩy link ra ngoài)')
            else:
                cb(gio, nd)
        elif nd.startswith('nhân web bị sập'):
            cb(gio, 'Nhân web bị sập (hết RAM / lỗi WebKit) → app tự tải lại')
        elif nd.startswith('tải xong'):
            if TRANG_DN.search(nd):
                dang_nhap = True
            ra.append(f'  {gio}  {nd}')
        elif nd.startswith('MỞ TRANG') or nd.startswith('LỖI TRANG'):
            if het:
                ra.append(f'  {gio}    {nd}')
        elif het:
            ra.append(f'  {gio}    {nd}')
    if mang and not het:
        ra.append('  Mạng (số yêu cầu theo tên miền): ' + ', '.join(f'{h} {n}' for h, n in mang.most_common(8)))
    return ra, canh_bao, dang_nhap or da_bam, vao_chat


def ket_luan(tat_ca_cb, co_cd):
    k = []
    noi = '\n'.join(tat_ca_cb)
    if 'ĐẨY RA TRÌNH DUYỆT' in noi:
        k.append('App đẩy một trang của bước đăng nhập ra trình duyệt → thêm tên miền đó vào danh sách mở trong app (tenMienTrongApp).')
    if 'KHÔNG được dùng cookie' in noi:
        k.append('Ô kiểm tra bảo mật (Arkose…) nằm trong khung con bị WebKit chặn cookie bên thứ ba → Facebook coi như trượt kiểm tra. '
                 'Hướng sửa: mở bước kiểm tra ở trang chính / cửa sổ riêng, hoặc xin quyền dùng cookie cho khung đó.')
    if 'không tải được phần kiểm tra' in noi or 'Khung kiểm tra bảo mật' in noi and 'lỗi' in noi:
        k.append('Phần kiểm tra bảo mật không tải được (lỗi / bị chặn) → xem dòng ⚠️ để biết tài nguyên nào.')
    if 'DỰNG LẠI cookie' in noi:
        k.append('Lớp «giữ đăng nhập» dựng lại cookie server vừa xoá → bỏ / sửa lớp này.')
    if 'Server trả lỗi' in noi:
        k.append('Server Facebook trả lỗi ở trang chính → có thể tài khoản / thiết bị bị giới hạn.')
    if 'VĂNG VỀ TRANG ĐĂNG NHẬP' in noi and not k:
        k.append('Văng về trang đăng nhập mà không thấy lỗi phía app (không chặn link, không lỗi tải) → nhiều khả năng Facebook '
                 'từ chối (bài kiểm tra trượt, tài khoản / thiết bị bị nghi). Thử đăng nhập bằng Safari trên cùng máy để so sánh.')
    if 'lỗi mở trang' in noi or 'lỗi tải' in noi:
        k.append('Có lỗi mở / tải trang (mất mạng, server không trả lời…) – xem dòng ⚠️ để biết lúc nào, trang nào.')
    if 'Nhân web bị sập' in noi:
        k.append('Nhân web bị sập – máy thiếu RAM hoặc lỗi WebKit.')
    if not k:
        k.append(f'Có {len(tat_ca_cb)} chỗ nghi lỗi – xem dòng ⚠️.' if tat_ca_cb else 'Không thấy dấu hiệu lỗi.')
    if not co_cd:
        k.append('Nhật ký này là bản cũ (không có dòng «CĐ») – thiếu khung con, link bị đẩy ra trình duyệt, mã server. Cần app 0.6.6+ để đọc đủ.')
    return k


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    het = '--het' in sys.argv
    nguon = [a for a in sys.argv[1:] if a != '--het'][0]
    dong, thong_tin = doc_nguon(nguon)
    print(f'== Nguồn: {os.path.basename(nguon)} ({len(dong)} dòng nhật ký)')
    if thong_tin:
        print('== thong-tin.txt:\n' + '\n'.join('  ' + d for d in thong_tin.strip().splitlines()[:8]))
    co_cd = any(' VM: CĐ ' in d for d in dong)
    tat_ca_cb = []
    lan = tach_lan_mo(dong)
    in_ra = 0
    for i, (pid, sk) in enumerate(lan, 1):
        ra, cbao, dn, vao = phan_tich(sk, het)
        tat_ca_cb += cbao
        if not (het or cbao or dn):
            continue
        in_ra += 1
        print(f'\n== Lần mở app {i}/{len(lan)} (pid {pid}) {sk[0][0]} {sk[0][1]} → {sk[-1][1]}'
              + (f' · vào chat lúc {vao}' if vao else ' · CHƯA vào chat'))
        print('\n'.join(ra) if ra else '  (không có dòng liên quan)')
    if not in_ra:
        print(f'\n(Không lần mở app nào có đăng nhập hay lỗi trong {len(lan)} lần – thêm --het để in hết)')
    print('\n== KẾT LUẬN')
    if tat_ca_cb:
        print(f'  {len(tat_ca_cb)} chỗ nghi lỗi (⚠️ ở trên).')
    for d in ket_luan(tat_ca_cb, co_cd):
        print('  • ' + d)


if __name__ == '__main__':
    main()
