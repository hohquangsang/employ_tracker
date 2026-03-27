import cv2
import json
import numpy as np

zones = {}
points = []
zone_counter = 1
current_zone_name = ""
done = False  # ✅ Flag để kết thúc khi nhấn D

def click_event(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(f"Chọn điểm: ({x}, {y})")
    elif event == cv2.EVENT_RBUTTONDOWN and points:
        zones[current_zone_name] = points.copy()
        print(f"✅ Đã lưu {current_zone_name} với {len(points)} điểm.")
        points.clear()

def main():
    global current_zone_name, zone_counter, done

    cap = cv2.VideoCapture("demo.mp4")
    ret, frame = cap.read()
    if not ret:
        print("❌ Không đọc được frame từ video.")
        return

    clone = frame.copy()
    print("📌 Hướng dẫn:")
    print("🖱 Chuột trái: chọn điểm")
    print("🖱 Chuột phải: lưu vùng")
    print("⎋ ESC: xóa điểm đang vẽ")
    print("⏎ ENTER: vẽ vùng tiếp theo")
    print("▶ D: kết thúc và lưu file")

    while not done:
        current_zone_name = input(f"Nhập tên zone (Cabin {zone_counter}): ").strip()
        if not current_zone_name:
            print("⚠️ Tên zone không được để trống.")
            continue

        cv2.namedWindow("Vẽ cabin")
        cv2.setMouseCallback("Vẽ cabin", click_event)

        while True:
            temp = clone.copy()
            for pt in points:
                cv2.circle(temp, pt, 3, (0, 0, 255), -1)
            if len(points) >= 2:
                cv2.polylines(temp, [np.array(points)], isClosed=False, color=(255, 0, 0), thickness=2)

            cv2.imshow("Vẽ cabin", temp)
            key = cv2.waitKey(1) & 0xFF

            if key == 27:  # ESC → xóa
                points.clear()
                print("⛔ Đã xóa điểm đang vẽ.")
            elif key == 13:  # ENTER → chuyển vùng tiếp theo
                break
            elif key == ord('d') or key == ord('D'):  # ✅ nhấn D để kết thúc
                done = True
                break
        zone_counter += 1

    cv2.destroyAllWindows()
    with open("zones.json", "w") as f:
        json.dump(zones, f)
    print("✅ Đã lưu vào zones.json")

if __name__ == "__main__":
    main()
