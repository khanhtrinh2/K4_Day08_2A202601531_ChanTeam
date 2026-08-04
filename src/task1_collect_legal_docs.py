"""
Task 1 — Thu thập văn bản chính sách thương mại điện tử / hỗ trợ khách hàng.

Hướng dẫn:
    1. Tạo 3 văn bản chính sách PDF trong data/landing/legal/
    2. Đặt tên file rõ ràng:
       - chinh-sach-tra-hang-hoan-tien.pdf (buyer focused)
       - phuong-thuc-thanh-toan.pdf (both buyer & seller)
       - quy-dinh-dang-ban-san-pham.pdf (seller focused)
    3. Đảm bảo kích thước mỗi file >1KB.
"""

from pathlib import Path
from fpdf import FPDF

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory():
    """Tạo thư mục data/landing/legal/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Thư mục đã sẵn sàng: {DATA_DIR}")


class PolicyPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "SHOPEE VIETNAM - E-COMMERCE LEGAL & POLICY DOCUMENTS", border=False, align="C")
        self.ln(6)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} - Shopee Legal & Compliance Department", border=False, align="C")


def create_pdf(filename: str, title: str, customer_role: str, content_sections: list):
    pdf = PolicyPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Header metadata
    pdf.set_font("Helvetica", "B", 14)
    pdf.multi_cell(0, 8, title)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 6, f"Target Role / Metadata: customer_role={customer_role}", border=False)
    pdf.ln(5)
    pdf.cell(0, 6, f"Document Identifier: {filename.replace('.pdf', '')}", border=False)
    pdf.ln(5)
    pdf.cell(0, 6, "Effective Date: 2026-01-01 | Version: 2.4 | Status: Active", border=False)
    pdf.ln(8)
    
    # Sections
    for sec_title, sec_body in content_sections:
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, sec_title)
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 9.5)
        pdf.multi_cell(0, 5.5, sec_body)
        pdf.ln(4)

    filepath = DATA_DIR / filename
    pdf.output(str(filepath))
    size = filepath.stat().st_size
    print(f"✓ Created: {filepath.name} ({size} bytes)")
    return filepath


def generate_legal_docs():
    """Tạo 3 file PDF chính sách Shopee trong data/landing/legal/"""
    setup_directory()

    # Document 1: Return and Refund Policy (buyer focused)
    doc1_sections = [
        (
            "1. OVERVIEW AND SCOPE OF RETURN AND REFUND POLICY (TONG QUAN CHINH SACH TRA HANG)",
            "Chinh sach Tra hang va Hoan tien nay quy dinh cac dieu kien, quy trinh va thu tuc "
            "danh cho Nguoi mua (Buyer) khi thuc hien yeu cau tra hang hoac hoan tien cho cac "
            "don hang mua sam tren san thuong mai dien tu Shopee Vietnam. Shopee cam ket "
            "bao ve quyen loi hop phap cua Nguoi mua va dam bao giao dich an toan, minh bach. "
            "Tat ca cac giao dich tren Shopee deu duoc bao ve boi chinh sach Shopee Guarantee "
            "(Dam bao Shopee). So tien thanh toan cua Nguoi mua se duoc Shopee giu an toan "
            "va chi chuyen cho Nguoi ban sau khi Nguoi mua xac nhan da nhan duoc hang va "
            "khong co bat ky khieu nai nao trong thoi gian quy dinh."
        ),
        (
            "2. ELIGIBILITY CONDITIONS FOR RETURN AND REFUND (DIEU KIEN YEU CAU TRA HANG)",
            "Nguoi mua co the yeu cau Tra hang va Hoan tien trong cac truong hop sau đây:\n"
            "a) Nguoi mua da thanh toan nhung khong nhan duoc san pham hoac san pham bi thai lac "
            "trong qua trinh van chuyen cua đơn vi van chuyen.\n"
            "b) San pham bi loi, bi dam hai, móp meo hoac vỡ nhat trong qua trinh van chuyen. "
            "Nguoi mua can cung cap video unboxing (mo hop hang) va hinh anh ro rang lam bang chung.\n"
            "c) Shopee hoac Nguoi ban giao sai san pham cho Nguoi mua, bao gom sai kich thuoc, "
            "sai mau sac, sai phien ban hoac thieu phu kien di kem.\n"
            "d) San pham Nguoi mua nhan duoc khac bien ro ret so voi thong tin mo ta, hinh anh "
            "hoac thong so ky thuat ma Nguoi ban da dang tai tren gian hang.\n"
            "e) San pham la hang gia, hang nhai, hang khong chinh hang hoac vi pham quyen so huu tri tue.\n"
            "f) Nguoi ban va Nguoi mua da tu thoa thuan va dong y cho phap tra hang."
        ),
        (
            "3. TIMEFRAME FOR SUBMITTING RETURN REQUESTS (THOI GIAN YEU CAU TRA HANG)",
            "Thoi gian Nguoi mua co the gui yeu cau Tra hang va Hoan tien duoc quy dinh nhu sau:\n"
            "- Doi voi don hang thong thuong (Shopee Standard): Trong vong 07 ngay ke tu ngay don hang "
            "duoc cap nhat trang thai Giao hang thanh cong.\n"
            "- Doi voi don hang Shopee Mall: Trong vong 15 ngay ke tu ngay don hang duoc cap nhat trang thai "
            "Giao hang thanh cong.\n"
            "- Sau khi het thoi han tren, Shopee Guarantee se het hieu luc. So tien thanh toan se duoc "
            "tu dong chuyen cho Nguoi ban va Shopee se khong the ho tro quyet dinh khieu nai tra hang."
        ),
        (
            "4. STEP-BY-STEP RETURN PROCESS (QUY TRINH THUC HIEN TRA HANG)",
            "Quy trinh thuc hien tra hang duoc tien hanh qua 4 buoc chinh:\n"
            "Buoc 1: Gui yeu cau tren ung dung Shopee. Nguoi mua vao muc Don hang cua toi -> Chon don hang -> "
            "Bấm Tra hang/Hoan tien -> Chon ly do va tai len hinh anh/video bang chung.\n"
            "Buoc 2: Xem xet va phan hoi tu Nguoi ban. Nguoi ban co 48 gio de dong y hoac khieu nai yeu cau. "
            "Neu Nguoi ban khong phan hoi trong 48h, he thong se tu dong chieu theo yeu cau cua Nguoi mua.\n"
            "Buoc 3: Dong goi va gui hang tra. Nguoi mua dong goi san pham nguyen ven phu kien, tem nhan, "
            "su dung ma van don tra hang mien phi do Shopee cung cap de gui hang qua bưu cục.\n"
            "Buoc 4: Kiem tra va Hoan tien. Sau khi kho Shopee hoac Nguoi ban nhan duoc hang va kiem tra "
            "tinh trang, so tien hoan se duoc chuyen ve tai khoan cua Nguoi mua."
        ),
        (
            "5. RETURN SHIPPING FEES AND COVERAGE (CHI PHI VAN CHUYEN TRA HANG)",
            "Shopee ho tro mien phi 100% chi phi van chuyen tra hang neu Nguoi mua su dung dung ma van don "
            "tra hang (Return Shipping Label) duoc tao truc tiep tren ung dung Shopee. Trong truong hop "
            "Nguoi mua tu gui hang qua cac don vi van chuyen ngoai ma khong dung ma cua Shopee, Nguoi mua "
            "se phai tu chi tra phi van chuyen ban dau. Shopee se xem xet hoan lai chi phi van chuyen duoi "
            "dang Shopee Xu neu khieu nai cua Nguoi mua duoc xac dinh la hop le va co hoa don van chuyen."
        ),
        (
            "6. NON-RETURNABLE PRODUCTS AND EXCEPTIONS (CAC SAN PHAM KHONG DUOC TRA HANG)",
            "Cac danh muc san pham va truong hop khong ap dung chinh sach tra hang hoan tien bao gom:\n"
            "- Cac san pham ky thuat so, voucher dien tu, e-voucher, nạp tien dien thoai, the game.\n"
            "- San pham thuoc danh muc thuc pham tuoi song, do an nhanh, hang hoa co han su dung duoi 07 ngay.\n"
            "- San pham do lot, do tap, my pham da mo seal hoac da qua su dung vi ly do an toan ve sinh.\n"
            "- San pham bi hu hong, bien dang, mat tem nhan do loi co y hoac khong la tu phia Nguoi mua."
        ),
        (
            "7. REFUND METHODS AND PROCESSING TIMELINE (PHUONG THUC VA THOI GIAN HOAN TIEN)",
            "Thoi gian Nguoi mua nhan duoc tien hoan phu thuoc vao phuong thuc thanh toan ban dau:\n"
            "- Vi ShopeePay: Hoan tien trong vong 24 gio lam viec sau khi yeu cau duoc phiet duyet.\n"
            "- Tai khoan Ngan hang lien ket / Chuyen khoan: Hoan tien trong vong 24-48 gio lam viec.\n"
            "- The Tin dung / The Ghi no (Credit/Debit Card): Hoan tien trong vong 07 den 14 ngay lam viec "
            "tuy theo quy dinh va chu ky doi soat cua ngan hang phat hanh the.\n"
            "- Thanh toan COD: Hoan tien vao Vi ShopeePay hoac Tai khoan Ngan hang da dang ky tren Shopee."
        ),
    ]

    create_pdf(
        filename="chinh-sach-tra-hang-hoan-tien.pdf",
        title="CHINH SACH TRA HANG VA HOAN TIEN SHOPEE (BUYER RETURN & REFUND POLICY)",
        customer_role="buyer",
        content_sections=doc1_sections,
    )

    # Document 2: Payment Methods Policy (both buyer & seller)
    doc2_sections = [
        (
            "1. GENERAL PROVISIONS ON PAYMENT METHODS (TONG QUAN PHUONG THUC THANH TOAN)",
            "Văn ban nay quy dinh tat ca cac phuong thuc thanh toan hop le, quy trinh xu ly giao dich "
            "va quy dinh bao mat tai chinh cho ca Nguoi mua (Buyer) va Nguoi ban (Seller) khi giao dich "
            "tren nen tang thương mai dien tu Shopee Vietnam. Tat ca cac giao dich thanh toan tren Shopee "
            "deu phai thuc hien thong qua he thong thanh toan chinh thuc cua Shopee de dam bao an toan "
            "va duoc bao ve boi Shopee Guarantee. Nghiem cam moi hanh vi thoa thuan thanh toan ngoai "
            "nen tang (off-platform payment)."
        ),
        (
            "2. PAYMENT OPTIONS AVAILABLE FOR BUYERS (CAC PHUONG THUC THANH TOAN CHO NGUOI MUA)",
            "Shopee ho tro nhieu phuong thuc thanh toan linh hoat va an toan cho Nguoi mua bao gom:\n"
            "a) Thanh toan khi nhan hang (COD - Cash On Delivery): Nguoi mua thanh toan tien mat cho "
            "nhan vien giao hang khi nhan kien hang. Ap dung cho hau het cac khu vuc va danh muc hang hoa.\n"
            "b) Vi dien tu ShopeePay: Phuong thuc thanh toan dien tu nhan uu dai ma giam gia, mieng phi "
            "van chuyen va hoan tien nhanh. Yeu cau nạp tien tu tai khoan ngan hang lien ket.\n"
            "c) The Tin dung / The Ghi no (Credit / Debit Card): Ho tro cac the Visa, Mastercard, JCB, "
            "American Express phat hanh boi cac ngan hang hop phap. Giao dich duoc ma hoa 3D-Secure.\n"
            "d) Chuyen khoan Ngan hang / QR Code: Nguoi mua quet ma VietQR hoac chuyen khoan den tai khoan "
            "dinh danh cua Shopee de xac nhan don hang tu dong trong vong 5 phut.\n"
            "e) SPayLater (Mua truoc tra sau): Dich vu tin dung duoc cung cap boi doi tac ngan hang cua "
            "Shopee, cho phep Nguoi mua chia nho khoan thanh toan thanh 1, 3, 6 hoac 12 ky han."
        ),
        (
            "3. SELLER BALANCE MANAGEMENT & WITHDRAWALS (QUAN LY SO DU THU NHAP CUA NGUOI BAN)",
            "Quy dinh ve thanh toan va thu nhap danh cho Nguoi ban tren Shopee:\n"
            "- So du Tai khoan Shopee (Shopee Balance): So tien tu cac don hang hoan tat se duoc ghi co "
            "vao So du Tai khoan Shopee cua Nguoi ban sau khi tru cac khoan phi dich vu va phi giao dich.\n"
            "- Rut tien tu dong (Auto Withdrawal): Nguoi ban co the thiet lap lich rut tien tu dong hang "
            "tuan (vao thu 3) hoac hang thang (ngay 1 va 15) ve tai khoan ngan hang chinh thuc.\n"
            "- Rut tien thu cong (Manual Withdrawal): Nguoi ban co the gui yeu cau rut tien bat ky luc nao. "
            "Thoi gian xu ly chuyen tien tu 24h den 48h lam viec (khong tinh thu 7, chu nhat va ngay le).\n"
            "- Han muc rut tien: Moi tai khoan Nguoi ban duoc mien phi 01 lan rut tien thu cong moi ngay."
        ),
        (
            "4. TRANSACTION FEES AND PLATFORM COMMISSIONS (BIEU PHI GIAO DICH VA PHI NEN TANG)",
            "Nguoi ban va Nguoi mua phai tuan thu quy dinh ve cac khoan phi giao dich va phi nen tang:\n"
            "a) Phi giao dich (Transaction Fee): Phi tinh tren tong so tien thanh toan cua don hang "
            "(bao gom tien hang va phi van chuyen). Muc phi hien tai la 3.0% - 4.0% tuy theo phuong thuc.\n"
            "b) Phi co dinh (Fixed Fee): Phi hoa hong nen tang ap dung cho tat ca cac don hang thanh cong "
            "cua Nguoi ban Shopee Mall va Nguoi ban thong thuong (tu 2.5% den 8.0% tuy danh muc ngành hang).\n"
            "c) Phi Dich vu (Service Fee): Ap dung cho Nguoi ban tham gia cac chuong trinh uu dai nhu "
            "Goi Freeship Xtra, Goi Voucher Xtra, hoac Chuong trinh Hoan Xu Xtra."
        ),
        (
            "5. TRANSACTION SECURITY AND ANTI-FRAUD MEASURES (BAO MAT VA PHONG CHONG GIAN LAU)",
            "Doi voi an toan thanh toan va phong chong gian luan:\n"
            "- Shopee su dung he thong quan ly rui ro tu dong de phat hien cac giao dich bat thuong, "
            "su dung the tin dung gia, hoac co hanh vi spaming ma giam gia.\n"
            "- Moi hanh vi co tinh thuc hien giao dich khong hop le, rửa tien, hoac gian lận thanh toan "
            "se bi khoa tai khoan vinh vien va chuyen ho so sang co quan chuc nang xu ly theo phap luat.\n"
            "- Shopee khong bao gio yeu cau Nguoi dung cung cap ma OTP, mat khau vi hoac so the tin dung "
            "qua dien thoai hay tin nhan ca nhan."
        ),
    ]

    create_pdf(
        filename="phuong-thuc-thanh-toan.pdf",
        title="QUY DINH PHUONG THUC THANH TOAN SHOPEE (BUYER & SELLER PAYMENT POLICY)",
        customer_role="both",
        content_sections=doc2_sections,
    )

    # Document 3: Seller Listing Regulations (seller focused)
    doc3_sections = [
        (
            "1. OVERVIEW OF SELLER LISTING REGULATIONS (TONG QUAN QUY DINH DANG BAN)",
            "Văn ban nay quy dinh cac tieu chuan, dieu kien va quy dinh bat buoc danh cho Nguoi ban "
            "(Seller) khi dang tai, quan ly va kinh doanh san pham tren san thuong mai dien tu Shopee "
            "Vietnam. Tat ca Nguoi ban phai tuan thu Luat Thuong mai dien tu, Luat Bao ve quyen loi "
            "nguoi tieu dung va cac quy dinh phap luat hien hanh cua Nuoc Cong hoa Xa hoi Chu nghia Viet Nam. "
            "Viec dang ban san pham vi pham se giet den cac hinh thuc xu phat tu xoa san pham, cong diem "
            "sao qua ta den khoa tai khoan kinh doanh."
        ),
        (
            "2. PROHIBITED AND RESTRICTED PRODUCT LISTINGS (DANH MUC SAN PHAM CAM DANG BAN)",
            "Nguoi ban khong duoc phep dang ban cac san pham thuoc danh muc cam hoac han che sau đây:\n"
            "a) Hang hoa cam theo quy dinh phap luat: Vu khi, quoc phong, ma tuy, phao hoa, thuc pham "
            "khong an toan ve sinh, dong vat hoang da nguy cap, bang dia co noi dung doc hai hoac phan dong.\n"
            "b) Hang gia, hang nhai va vi pham thuong hieu (Counterfeit & Infringing Goods): San pham "
            "sao chep kieu dang, logo, ten thuong hieu cua cac nhan hang da duoc bảo ho ma khong co "
            "van ban uo quyền hop le.\n"
            "c) San pham cam theo quy dinh Shopee: Ve so, dich vu tai chinh, vay tien, thuoc va thiet bi "
            "y te chuyen dung, hoa don, e-voucher khong hop le, tai khoan game/phan mem ban quyen.\n"
            "d) San pham can giay phep dac biet: My pham, thuc pham chuc nang, thuc pham bao ve sức khoe, "
            "sua va san pham dinh duong cho tre em duoi 24 thang tuoi can tai len day du Giay cong bo "
            "san pham va Giay phep quang cao truoc khi dang ban."
        ),
        (
            "3. PRODUCT TITLE, IMAGES AND DESCRIPTION STANDARDS (TIEU CHUAN THONG TIN SAN PHAM)",
            "Quy dinh chi tiet ve thong tin dang tai san pham:\n"
            "- Tieu de san pham (Product Title): Phai bat dau bang Ten san pham + Thương hieu + Thong so "
            "ky thuat. Tieu de phai viet bang tieng Viet co dau hoac tieng Anh. Khong chua tu khoa rác, "
            "khong chua ky tu dac biet va khong gia danh thuong hieu khac (vi du: 'Ao khoac phong cach Zara' "
            "la vi pham quy dinh).\n"
            "- Hinh anh va Video san pham (Images & Video): Hinh anh phai sac net, phan anh chinh xac san pham "
            "thuc te. Khong duoc dung hinh anh phan cam, khong chua thong tin/logo cua cac san TMDT doi thu, "
            "khong chèn so dien thoai hay dia chi ca nhan len anh san pham.\n"
            "- Mo ta san pham (Product Description): Cung cap thong tin chi tiet ve chat lieu, kich thuoc, "
            "xuat xu, huong dan su dung, che do bao hanh va cac canh bao an toan."
        ),
        (
            "4. PRICE SETTING AND INVENTORY MANAGEMENT RULES (QUY DINH GIA VA TON KHO)",
            "Nguoi ban phai tuan thu cac quy dinh ve gia va quan ly ton kho:\n"
            "- Niem yet gia minh bach: Gia san pham phai niem yet bang Dong Viet Nam (VND), bao gom "
            "tat ca cac khoản thue ap dung. Nghiem cam dang gia 0 dong, gia ao hoac gia khac xa gia tri thuc.\n"
            "- Hanh vi tang gia roi giam gia (Spam Discount): Nghiem cam hanh vi tang gia san pham len cao "
            "ngay truoc khi tham gia cac chuong trinh khuyen mai roi thuc hien giam gia ao de luoi kien "
            "nguoi mua hang.\n"
            "- Cập nhat ton kho chinh xac: Nguoi ban phai thuong xuyen cap nhat so luong ton kho thuc te. "
            "Viec de xay ra tinh trang het hang dan den huy don se bi tinh vao Ty le Don hang Khong hoan thanh."
        ),
        (
            "5. PENALTY POINTS SYSTEM AND ENFORCEMENT MEASURES (HE THONG SAO QUA TA VA XU PHAT)",
            "Shopee ap dung He thong Diem Sao Qua Ta (Penalty Points System) de quan ly vi pham cua Nguoi ban:\n"
            "- Ty le don hang giao tre (Late Shipment Rate) va Ty le don khong hoan thanh (Non-fulfilment Rate): "
            "Neu vuot qua muc quy dinh 10%, Nguoi ban se bi cộng tu 1 den 2 diem sao qua ta moi tuan.\n"
            "- Dang ban san pham vi pham: Moi san pham vi pham danh muc cam hoac hang gia se bi xoa va "
            "Nguoi ban bi cộng 2 den 4 diem sao qua ta.\n"
            "- Cac muc do xu phat theo Sao Qua Ta:\n"
            "  + 3 diem: Tam dung tham gia cac chuong trinh khuyen mai trong 28 ngay.\n"
            "  + 6 diem: Tuoc danh hieu Shopee Mall / Shop Yeu thich va han che hien thi san pham.\n"
            "  + 9 diem: Ban quyen dang ban san pham moi.\n"
            "  + 12 diem tro len: Tước quyen truy cap va khoa tai khoan kinh doanh tam thoi hoac vinh vien."
        ),
    ]

    create_pdf(
        filename="quy-dinh-dang-ban-san-pham.pdf",
        title="QUY DINH DANG BAN SAN PHAM CHO NGUOI BAN (SELLER LISTING REGULATIONS)",
        customer_role="seller",
        content_sections=doc3_sections,
    )

    print("\n✓ Hoàn tất tạo 3 file PDF chính sách Shopee!")


if __name__ == "__main__":
    generate_legal_docs()

