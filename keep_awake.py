"""Giu app Streamlit Community Cloud luon thuc VA kiem app that su hien giao dien.

1. Mo trang bang trinh duyet that; neu app dang ngu (nut 'Yes, get this app back up') thi bam danh thuc.
2. Kiem giao dien da hien du: co chu tieu de app (code app da chay) + o chon da ve xong
   (file JS cua o nhap da tai) + khong co loi Python mau do.
   Bai hoc 04/11/2026: Hiep Ky treo nua ngay (vong quay mai, roi o nhap xam) ma ban cu van bao
   "thanh cong" vi chi kiem nut danh thuc.
3. Khong dat -> tai lai trang thu them 1 lan (tranh bao dong nham) -> van khong dat thi chup man hinh,
   thoat ma 1: workflow FAIL, GitHub gui email cho nguoi tao lich chay (cron).

Bien moi truong: STREAMLIT_APP_URL, EXPECT_TEXT (chu tren header app, khong phan biet hoa thuong).
"""
import os
import re
import sys
import time

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

URL = os.environ.get("STREAMLIT_APP_URL", "https://bacsirobot.streamlit.app/")
EXPECT_TEXT = os.environ.get("EXPECT_TEXT", "BÁC SĨ ROBOT")
WAKE_TEXT = "get this app back up"
RENDER_TIMEOUT = int(os.environ.get("RENDER_TIMEOUT", "120"))  # giay cho giao dien hien du
SCREENSHOT = "keep_awake_loi.png"


def _co(frame, selector):
    try:
        return frame.locator(selector).count() > 0
    except Exception:  # frame dang tai lai / da dong
        return False


def trang_thai(page):
    """(ok, ly_do) tai thoi diem hien tai, xet moi frame (Streamlit Cloud boc app trong iframe)."""
    ly_do = "Chua thay chu '%s': app chua chay xong (trang trang / vong quay mai)" % EXPECT_TEXT
    for fr in page.frames:
        if _co(fr, '[data-testid="stException"]'):
            try:
                msg = fr.locator('[data-testid="stException"]').first.inner_text(timeout=2000)[:300]
            except Exception:
                msg = ""
            return False, "App bao loi Python: " + msg.replace("\n", " ")
        if _co(fr, 'text="Failed to fetch dynamically imported module"') or _co(fr, "text=/Failed to fetch dynamically/"):
            return False, "Trinh duyet khong tai duoc file JS cua o nhap (Failed to fetch)"
        if _co(fr, "text=/%s/i" % re.escape(EXPECT_TEXT)):
            # Do tren Streamlit 1.66: o nhap chua tai xong JS thi hien khoi xam stSkeleton thay cho stSelectbox
            if _co(fr, '[data-testid="stSelectbox"]') and not _co(fr, '[data-testid="stSkeleton"]'):
                return True, "Giao dien hien du (tieu de + o chon)"
            ly_do = "Co tieu de nhung o nhap chua ve xong (khoi xam): file JS cua o nhap bi treo"
    return False, ly_do


def cho_giao_dien(page, timeout_s):
    han = time.time() + timeout_s
    ok, ly_do = trang_thai(page)
    while not ok and time.time() < han:
        time.sleep(3)
        ok, ly_do = trang_thai(page)
    return ok, ly_do


def danh_thuc(page):
    btn = page.get_by_role("button", name=WAKE_TEXT, exact=False)
    if btn.count() == 0:
        print("Khong thay nut danh thuc -> app dang thuc")
        return True, ""
    print("App dang ngu -> bam nut danh thuc")
    btn.first.click()
    try:
        btn.first.wait_for(state="detached", timeout=180_000)
        print("Da danh thuc xong")
        return True, ""
    except PWTimeout:
        return False, "Bam danh thuc roi nhung app chua day sau 3 phut"


def bao_loi(page, ly_do):
    print("::error title=App khong hien giao dien::%s (%s)" % (ly_do, URL))
    try:
        page.screenshot(path=SCREENSHOT, full_page=True)
        print("Da chup man hinh:", SCREENSHOT)
    except Exception as e:
        print("Khong chup duoc man hinh:", e)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("### ❌ App không hiện giao diện\n\n- Trang: %s\n- Lý do: %s\n- Ảnh chụp: mục Artifacts của lần chạy này\n"
                    "- Cách xử lý: share.streamlit.io → app → ⋮ → Reboot; vẫn lỗi thì xem Manage app → log\n"
                    % (URL, ly_do))


def kiem_tra(page, render_timeout=RENDER_TIMEOUT):
    """Danh thuc + kiem giao dien, tai lai trang thu them 1 lan. Tra ve (ok, ly_do)."""
    print("Mo:", URL)
    page.goto(URL, wait_until="commit", timeout=90_000)  # JS chinh treo thi domcontentloaded cung treo
    time.sleep(8)
    ok, ly_do = danh_thuc(page)
    if not ok:
        return ok, ly_do
    ok, ly_do = cho_giao_dien(page, render_timeout)
    if not ok:
        print("Lan 1 chua dat (%s) -> tai lai trang thu lan nua" % ly_do)
        page.reload(wait_until="commit", timeout=90_000)
        ok, ly_do = cho_giao_dien(page, max(30, render_timeout // 2))
    return ok, ly_do


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        try:
            ok, ly_do = kiem_tra(page)
        except Exception as e:  # mat mang, trang khong mo duoc...
            ok, ly_do = False, "Khong mo duoc trang: %s" % e
        print(("OK: " if ok else "LOI: ") + ly_do)
        print("Tieu de trang:", page.title())
        if ok:
            time.sleep(20)  # o lai mot luc de Streamlit ghi nhan co phien truy cap that
        else:
            bao_loi(page, ly_do)
        browser.close()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
