from flask import Flask, render_template, request, jsonify
from ultralytics import YOLO
import cv2
import numpy as np
import base64
from PIL import Image, ImageFont
import io
import os
from paddleocr import PaddleOCR

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

app = Flask(__name__)

# 加载YOLOv8车牌检测模型
model = YOLO("models/best.pt")
print("YOLO模型加载成功")

# 初始化 PaddleOCR
cls_model_dir = 'paddleModels/whl/cls/ch_ppocr_mobile_v2.0_cls_infer'
rec_model_dir = 'paddleModels/whl/rec/ch/ch_PP-OCRv4_rec_infer'
ocr = PaddleOCR(use_angle_cls=False, lang="ch", det=False, 
                cls_model_dir=cls_model_dir, 
                rec_model_dir=rec_model_dir)
print("OCR模型加载成功")

# 加载字体
fontC = ImageFont.truetype("Font/platech.ttf", 50, 0)

def get_license_result(ocr, image):
    """获取车牌识别结果"""
    result = ocr.ocr(image, cls=True)[0]
    if result:
        license_name, conf = result[0][1]
        if '·' in license_name:
            license_name = license_name.replace('·', '')
        return license_name, conf
    else:
        return None, None

def process_image(image_file):
    # 读取上传的图片
    image = Image.open(image_file)
    # 转换为OpenCV格式
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    original_image = image_cv.copy()

    print("开始执行目标检测...")
    # 运行车牌检测推理
    results = model(image_cv)[0]
    print(f"检测结果: {results}")

    detection_results = []
    location_list = results.boxes.xyxy.tolist()
    
    if len(location_list) >= 1:
        location_list = [list(map(int, e)) for e in location_list]
        # 截取每个车牌区域的照片
        license_imgs = []
        for box in location_list:
            x1, y1, x2, y2 = box
            cropImg = original_image[y1:y2, x1:x2]
            license_imgs.append(cropImg)
            print(f"裁剪车牌区域: ({x1}, {y1}, {x2}, {y2})")

        # 对每个检测到的区域进行OCR识别
        for i, (box, img) in enumerate(zip(location_list, license_imgs)):
            x1, y1, x2, y2 = box
            conf = float(results.boxes.conf[i])
            cls = int(results.boxes.cls[i])

            # OCR识别
            license_num, ocr_conf = get_license_result(ocr, img)
            if not license_num:
                license_num = "未识别"
                ocr_conf = 0.0

            print(f"车牌号: {license_num}, 置信度: {ocr_conf}")

            # 在图像上绘制边界框和文字
            cv2.rectangle(
                image_cv, 
                (x1, y1), 
                (x2, y2), 
                (0, 255, 0), 
                2
            )
            
            # 在边界框上方显示识别结果
            cv2.putText(
                image_cv,
                f"{license_num} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
            )

            # 添加检测和识别结果
            detection_results.append({
                "class": model.names[cls],
                "confidence": conf,
                "bbox": [x1, y1, x2, y2],
                "plate_number": license_num,
                "ocr_confidence": float(ocr_conf)
            })

    print(f"处理完成，检测结果: {detection_results}")

    # 将处理后的图片转换为base64
    _, buffer = cv2.imencode(".jpg", image_cv)
    img_str = base64.b64encode(buffer).decode()

    return img_str, detection_results

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/detect", methods=["POST"])
def detect():
    if "file" not in request.files:
        return jsonify({"error": "没有文件上传"})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "没有选择文件"})

    if file:
        try:
            print(f"接收到文件: {file.filename}")
            processed_image, detection_results = process_image(file)
            print("图像处理完成")

            return jsonify({
                "success": True,
                "image": processed_image,
                "results": detection_results,
            })

        except Exception as e:
            print(f"处理过程中出现错误: {str(e)}")
            return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
