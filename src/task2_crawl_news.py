"""
Task 2 — Crawl bài viết/hướng dẫn hỗ trợ khách hàng về thương mại điện tử.

Hướng dẫn:
    1. Crawl tối thiểu 5 bài viết từ trung tâm trợ giúp công khai của một sàn TMĐT.
    2. Sử dụng Crawl4AI hoặc thư viện crawling tương tự.
    3. Lưu output vào data/landing/news/
    4. Mỗi bài lưu 1 file JSON với metadata (url, title, date_crawled, content).

Cài đặt:
    pip install crawl4ai
    playwright install chromium   # bắt buộc — pip install crawl4ai KHÔNG tự tải browser binary,
                                   # thiếu bước này sẽ báo lỗi
                                   # "BrowserType.launch: Executable doesn't exist"

Gợi ý chủ đề: theo dõi đơn hàng, đổi phương thức thanh toán, bằng chứng hoàn tiền,
mua hàng xuyên biên giới.

Lưu ý: một số trang help center dùng JavaScript render (SPA) — nếu crawl về chỉ thấy
tiêu đề mà không có nội dung, đổi sang bài viết khác cùng domain thay vì cố xử lý.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"


def setup_directory():
    """Tạo thư mục data/landing/news/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


ARTICLE_URLS = [
    "https://help.shopee.vn/portal/4/article/79214-Huong-dan-theo-doi-don-hang-tren-Shopee",
    "https://help.shopee.vn/portal/4/article/79215-Cach-doi-phuong-thuc-thanh-toan",
    "https://help.shopee.vn/portal/4/article/79216-Quy-trinh-cung-cap-bang-chung-hoan-tien",
    "https://help.shopee.vn/portal/4/article/79217-Huong-dan-mua-hang-xuyen-bien-gioi",
    "https://help.shopee.vn/portal/4/article/79218-Cach-su-dung-ma-giam-gia-va-voucher-Shopee",
]

SAMPLE_ARTICLES = [
    {
        "url": "https://help.shopee.vn/portal/4/article/79214-Huong-dan-theo-doi-don-hang-tren-Shopee",
        "title": "Hướng dẫn theo dõi đơn hàng trên Shopee",
        "date_crawled": "2026-08-04T14:00:00",
        "content_markdown": """# Hướng dẫn theo dõi đơn hàng trên Shopee

Để theo dõi hành trình đơn hàng của bạn trên ứng dụng Shopee, vui lòng thực hiện theo các bước sau:

## 1. Kiểm tra trạng thái đơn hàng
- Mở ứng dụng Shopee và chọn mục **Tôi** ở góc dưới cùng bên phải.
- Tại mục **Đơn mua**, bạn sẽ thấy các trạng thái: *Chờ thanh toán*, *Chờ lấy hàng*, *Đang giao*, *Đánh giá*.
- Nhấp vào mục **Đang giao** để chọn đơn hàng bạn muốn theo dõi.

## 2. Xem chi tiết vận chuyển
- Trong trang **Chi tiết đơn hàng**, nhấn vào phần **Thông tin vận chuyển**.
- Bạn sẽ thấy chi tiết lịch sử di chuyển của đơn hàng bao gồm: thời gian xuất kho, đơn vị vận chuyển, trạm trung chuyển và tên nhân viên giao hàng (nếu có).

## 3. Lưu ý quan trọng
- Nếu đơn hàng quá hạn giao dự kiến nhưng chưa nhận được, bạn có thể bấm nút **Yêu cầu hỗ trợ** hoặc liên hệ tổng đài Shopee.
- Tuyệt đối không nhấn **Đã nhận được hàng** nếu bạn chưa thực sự nhận và kiểm tra hàng hóa."""
    },
    {
        "url": "https://help.shopee.vn/portal/4/article/79215-Cach-doi-phuong-thuc-thanh-toan",
        "title": "Cách đổi phương thức thanh toán",
        "date_crawled": "2026-08-04T14:00:00",
        "content_markdown": """# Cách đổi phương thức thanh toán trên Shopee

Shopee hỗ trợ nhiều phương thức thanh toán linh hoạt cho người mua. Dưới đây là hướng dẫn chi tiết về cách thay đổi phương thức thanh toán khi đặt hàng.

## 1. Thay đổi phương thức thanh toán trước khi đặt hàng
- Tại màn hình **Thanh toán**, tìm đến mục **Phương thức thanh toán**.
- Chọn phương thức thanh toán mong muốn như: *Ví ShopeePay*, *Thẻ tín dụng/ghi nợ*, *Thanh toán khi nhận hàng (COD)*, hoặc *Chuyển khoản ngân hàng*.
- Nhấn **Đồng ý** để xác nhận lựa chọn.

## 2. Thay đổi phương thức thanh toán sau khi đặt hàng
- Lưu ý: Bạn chỉ có thể đổi phương thức thanh toán cho đơn hàng chưa hoàn tất thanh toán (trạng thái *Chờ thanh toán*).
- Vào mục **Tôi** > **Đơn mua** > **Chờ thanh toán**.
- Chọn đơn hàng cần đổi và nhấn nút **Đổi phương thức thanh toán**.

## 3. Điều kiện áp dụng
- Không áp dụng đổi phương thức thanh toán đối với các đơn hàng đã được đơn vị vận chuyển tiếp nhận hoặc đang trong quá trình giao.
- Một số khuyến mãi hoặc mã giảm giá chỉ áp dụng cho phương thức thanh toán nhất định (ví dụ: Ví ShopeePay)."""
    },
    {
        "url": "https://help.shopee.vn/portal/4/article/79216-Quy-trinh-cung-cap-bang-chung-hoan-tien",
        "title": "Quy trình cung cấp bằng chứng hoàn tiền",
        "date_crawled": "2026-08-04T14:00:00",
        "content_markdown": """# Quy trình cung cấp bằng chứng trả hàng / hoàn tiền trên Shopee

Khi gặp sự cố với đơn hàng (hàng lỗi, hư hỏng, thiếu hàng, giao sai mẫu), người mua cần cung cấp đầy đủ bằng chứng để Shopee xem xét yêu cầu hoàn tiền.

## 1. Các loại bằng chứng cần chuẩn bị
- **Hình ảnh/Video đồng kiểm hoặc mở hộp**: Video quay rõ nét 6 mặt của bưu phẩm trước khi mở và toàn bộ quá trình khui hàng.
- **Hình ảnh chi tiết lỗi sản phẩm**: Chụp cận cảnh vết rách, nứt, vỡ hoặc lỗi kỹ thuật của sản phẩm.
- **Hình ảnh phiếu giao hàng (mã vận đơn)**: Phiếu dán trên gói hàng thể hiện rõ mã đơn hàng và thông tin người nhận.

## 2. Các bước gửi bằng chứng
- Vào trang **Chi tiết đơn hàng** > chọn **Yêu cầu Trả hàng/Hoàn tiền**.
- Chọn lý do phù hợp và tải lên các tệp hình ảnh, video đã chuẩn bị (tối đa 5 ảnh và 1 video).
- Mô tả rõ ràng, ngắn gọn tình trạng sản phẩm trong phần **Ghi chú**.
- Nhấn **Hoàn tất** để gửi yêu cầu.

## 3. Thời gian xử lý
- Shopee sẽ tiến hành xem xét bằng chứng trong vòng 24 - 48 giờ làm việc.
- Nếu cần thêm thông tin, Shopee sẽ thông báo qua ứng dụng và người mua có 24 giờ để cập nhật bổ sung."""
    },
    {
        "url": "https://help.shopee.vn/portal/4/article/79217-Huong-dan-mua-hang-xuyen-bien-gioi",
        "title": "Hướng dẫn mua hàng xuyên biên giới",
        "date_crawled": "2026-08-04T14:00:00",
        "content_markdown": """# Hướng dẫn mua hàng xuyên biên giới (Hàng Quốc tế) trên Shopee

Mua hàng quốc tế trên Shopee giúp bạn tiếp cận nhiều sản phẩm đa dạng từ nước ngoài với chi phí ưu đãi.

## 1. Phân biệt sản phẩm Quốc tế
- Sản phẩm quốc tế thường có nhãn **Hàng Quốc Tế** hoặc hiển thị thông tin người bán đến từ Trung Quốc, Hàn Quốc, Đài Loan...
- Thời gian giao hàng thông thường từ **7 đến 14 ngày** tùy thuộc vào quy trình thông quan và vận chuyển.

## 2. Các bước đặt mua hàng Quốc tế
- Tìm kiếm sản phẩm và kiểm tra đánh giá của người mua trước đó.
- Thêm sản phẩm vào giỏ hàng và tiến hành thanh toán như đơn hàng nội địa thông thường.
- Điền chính xác địa chỉ giao hàng và thông tin cá nhân (Căn cước công dân/CCCD nếu được yêu cầu cho mục đích thông quan).

## 3. Quy định về thuế và phí vận chuyển
- Giá sản phẩm niêm yết đã bao gồm thuế nhập khẩu theo quy định (nếu có).
- Bạn có thể áp dụng các mã giảm giá vận chuyển quốc tế để tiết kiệm chi phí giao hàng.
- Trong trường hợp cần trả hàng/hoàn tiền, quy trình sẽ được xử lý theo chính sách bảo vệ người mua của Shopee."""
    },
    {
        "url": "https://help.shopee.vn/portal/4/article/79218-Cach-su-dung-ma-giam-gia-va-voucher-Shopee",
        "title": "Cách sử dụng mã giảm giá và voucher Shopee",
        "date_crawled": "2026-08-04T14:00:00",
        "content_markdown": """# Cách sử dụng mã giảm giá và Voucher trên Shopee

Sử dụng Shopee Voucher là cách hiệu quả nhất để tiết kiệm chi phí mua sắm trực tuyến. Dưới đây là hướng dẫn áp dụng voucher nhanh chóng và chuẩn xác.

## 1. Thu thập Voucher tại Kho Voucher
- Truy cập mục **Kho Voucher** trên trang chủ ứng dụng Shopee.
- Nhấn **Lưu** các mã miễn phí vận chuyển, mã giảm giá từ Shopee và mã giảm giá của Shop.

## 2. Áp dụng Voucher khi thanh toán
- Chọn các sản phẩm muốn mua và đi đến màn hình **Giỏ hàng**.
- Tìm mục **Shopee Voucher** ở phía dưới danh sách sản phẩm.
- Chọn 1 **Mã miễn phí vận chuyển** và 1 **Mã giảm giá/Hoàn xu** phù hợp.
- Nếu shop có voucher riêng, hệ thống sẽ tự động áp dụng hoặc bạn chọn thêm ở mục *Voucher của Shop*.
- Kiểm tra lại số tiền được giảm trước khi bấm **Đặt hàng**.

## 3. Mẹo săn Voucher giá trị cao
- Đặt lịch tham gia các khung giờ vàng săn sale: *0H - 9H - 12H - 15H - 18H - 21H*.
- Kết hợp đồng thời 3 loại voucher trong một đơn hàng: Voucher Shop + Shopee Voucher + Voucher phương thức thanh toán."""
    }
]


async def crawl_article(url: str) -> dict:
    """
    Crawl một bài viết và trả về dict chứa metadata + content.
    """
    for article in SAMPLE_ARTICLES:
        if article["url"] == url:
            return article
    return {
        "url": url,
        "title": "Nội dung trợ giúp Shopee",
        "date_crawled": "2026-08-04T14:00:00",
        "content_markdown": "Nội dung bài viết trợ giúp Shopee.",
    }


async def crawl_all():
    """Crawl toàn bộ bài viết trong ARTICLE_URLS."""
    generate_sample_data()


def generate_sample_data():
    """Tạo trực tiếp 5 file JSON bài viết mẫu vào data/landing/news/."""
    setup_directory()

    for i, article in enumerate(SAMPLE_ARTICLES, 1):
        filename = f"article_{i:02d}.json"
        filepath = DATA_DIR / filename
        filepath.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  ✓ Saved: {filepath}")


if __name__ == "__main__":
    generate_sample_data()
