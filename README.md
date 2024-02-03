1.	Giới thiệu
Tool được xây dựng để mine và extract các thông tin về các commit và thay đổi về code trong commit đó trong một repository.
Tool sử dụng công cụ PyDriller và Rest API của Github.
2.	Cách sử dụng
Chạy chương trình main.py với tham số đầu vào là link github của repo để mine và extract.
3.	Đầu ra
Kết quả sau cùng là 2 file json:
•	File {tên repo}_raw.json: dữ liệu mine được
•	File {tên repo}_ext.json: dữ liệu extract
4.	File raw
Chứa các thông tin:
•	Ngôn ngữ lập trình
•	Domain
•	Tác giả
•	Danh sách người tham gia
•	Issues: STT, tên issues, người raise issue.
•	Commits
Thông tin một commit:
•	Sha
•	Tên tác giả
•	Lời nhắn
•	Ngày giờ commit
•	Sha các commit cha
•	Tổng số dòng thêm
•	Tổng số dòng xóa
•	Các file thay đổi: tên file, loại thay đổi, số dòng thêm, số dòng xóa, số dòng code, nội dung file, diff.
5.	File ext
Chứa các thông tin được extract tại mỗi commit:
•	Tổng số dòng thêm trong commit
•	Tổng số dòng xóa trong commit
•	EXP: Kinh nghiệm của tác giả: tính bằng số commit khác nhau tác giả đã thực hiện trước đây.
•	NUC: số unique change: tính bằng số commit khác nhau trước đây đã từng chỉnh sửa các file trong commit
•	Tổng số dev đã chỉnh sửa các file trong commit
•	Trung bình thời gian các file bị sửa đổi tính từ lần cuối trong commit
•	Thông tin các file: LT: số dòng code trước đây, NDEV: số lượng dev đã chỉnh sửa file này.
6.	Hạn chế
Tool sử dụng công cụ Pydriller nên sẽ không kiểm tra được số dòng code trong các file có ngôn ngữ không được hỗ trợ bởi thư viện lizard
