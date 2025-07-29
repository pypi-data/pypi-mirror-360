import os
import time
import json

import torch
from PIL import Image
import matplotlib.pyplot as plt

from torchvision import transforms
from yms_faster_rcnn.train.draw_box_utils import my_draw_objs
from yms_faster_rcnn.train import create_model


def time_synchronized():
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    return time.time()


def main():
    # get devices
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("using {} device.".format(device))

    # create model
    model = create_model(num_classes=4)

    # load train weights
    weights_path = r"E:\目标检测\10月26\第一次efficientnet_v2_s\best_model.pth"
    assert os.path.exists(weights_path), "{} file dose not exist.".format(weights_path)
    weights_dict = torch.load(weights_path, map_location='cpu')
    weights_dict = weights_dict["model"] if "model" in weights_dict else weights_dict
    model.load_state_dict(weights_dict)
    model.to(device)
    # torch.save(model.state_dict(), r'E:\目标检测\10月26\第一次efficientnet_v2_s\only-model.pth')

    # read class_indict
    # label_json_path = 'classes.json'
    label_json_path = 'classes.json'
    assert os.path.exists(label_json_path), "json file {} dose not exist.".format(label_json_path)
    with open(label_json_path, 'r') as f:
        class_dict = json.load(f)

    category_index = {str(v): str(k) for k, v in class_dict.items()}
    # 图片文件夹路径
    image_folder = r"D:\Code\data\齿轮检测数据集\VOC\VOCdevkit\VOC2012\JPEGImages"
    # image_folder = '/kaggle/input/xingzhicupgeardataset/VOCdevkit/VOC2012/JPEGImages'
    image_files = os.listdir(image_folder)
    data_transform = transforms.Compose([transforms.ToTensor()])

    for image_file in image_files:
        # 加载图片
        original_img = Image.open(os.path.join(image_folder, image_file))

        # 将PIL图片转换为张量
        img = data_transform(original_img)
        # 扩展批次维度
        img = torch.unsqueeze(img, dim=0)

        model.eval()  # 进入验证模式
        with torch.no_grad():
            # init
            img_height, img_width = img.shape[-2:]
            init_img = torch.zeros((1, 3, img_height, img_width), device=device)
            model(init_img)

            t_start = time_synchronized()
            predictions = model(img.to(device))[0]
            t_end = time_synchronized()
            print("inference+NMS time: {}".format(t_end - t_start))

            predict_boxes = predictions["boxes"].to("cpu").numpy()
            predict_classes = predictions["labels"].to("cpu").numpy()
            predict_scores = predictions["scores"].to("cpu").numpy()

            if len(predict_boxes) == 0:
                print("没有检测到任何目标!")

            plot_img = my_draw_objs(original_img,
                                    predict_boxes,
                                    predict_classes,
                                    predict_scores,
                                    category_index=category_index,
                                    box_thresh=0.5,
                                    line_thickness=3,
                                    image_name=image_file,
                                    font='Arial.ttf',
                                    font_size=20)
            plt.imshow(plot_img)
        # plt.show()
        # 保存预测的图片结果
        #     plot_img.save("test_result.jpg")
        plot_img.save(os.path.join(r"D:\Code\data\齿轮检测数据集\predicted", image_file))


if __name__ == '__main__':
    main()
