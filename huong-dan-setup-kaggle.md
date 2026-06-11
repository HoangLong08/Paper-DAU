Bước 1: Nén thư mục code lại
Mở File Explorer, đi tới:

d:\HoangLong\Personal\paper\3-\
Bạn sẽ thấy thư mục qigoa. Click chuột phải vào nó → Send to → Compressed (zipped) folder.

Kết quả: bạn sẽ có file qigoa.zip ở cùng thư mục.

🌐 Bước 2: Lên Kaggle, đăng nhập
Mở trình duyệt → vào https://www.kaggle.com
Đăng nhập (nếu chưa có tài khoản thì đăng ký bằng Google, miễn phí).
Xác thực số điện thoại (Phone Verify) — bắt buộc để dùng được GPU/CPU. Vào: Settings → Phone verification.
📤 Bước 3: Upload code lên Kaggle dưới dạng Dataset
Trên Kaggle, click "+ Create" (góc trên trái) → chọn "New Dataset".
Cửa sổ upload hiện ra → kéo thả file qigoa.zip vào.
Đặt tên Dataset: gõ qigoa-code.
Click "Create" (góc dưới phải).
Đợi ~1 phút, Kaggle sẽ tự giải nén.
🧠 Bước 4: Thêm BraTS Dataset (không cần upload, có sẵn)
Vẫn ở Kaggle, vào ô search trên cùng, gõ: brats20 dataset training validation
Click vào kết quả "BraTS20 Dataset (Training + Validation)" của user awsaf49.
Click nút "..." (góc phải, gần "Download") → chọn "New Notebook".
Kaggle sẽ tự tạo một notebook mới với BraTS đã được mount sẵn. ✅

🚀 Bước 5: Chạy notebook QIGOA
Ở notebook vừa tạo:

5.1. Thêm code QIGOA của mình vào notebook
Bên phải có panel "Input" → click "+ Add Input".
Search: qigoa-code (tên Dataset bạn vừa upload).
Click "Add" bên cạnh nó.
Bây giờ notebook có 2 input:

/kaggle/input/brats20-dataset-training-validation/... (BraTS)
/kaggle/input/qigoa-code/... (code của bạn)
5.2. Copy nội dung notebook tôi viết sẵn vào
Notebook tôi đã viết sẵn ở: qigoa/notebooks/qigoa_kaggle.ipynb

Cách dùng:

Mở file qigoa_kaggle.ipynb bằng VS Code (chính cửa sổ này).
Trên Kaggle, click File → Import Notebook → File → chọn file .ipynb đó từ máy.
