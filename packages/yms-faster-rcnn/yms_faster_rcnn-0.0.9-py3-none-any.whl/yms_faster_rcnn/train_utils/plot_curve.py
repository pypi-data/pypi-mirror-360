import datetime
import matplotlib.pyplot as plt


def plot_loss_and_lr(train_loss, learning_rate,
                     path='./loss_and_lr.png'
                     ):
    try:
        x = list(range(len(train_loss)))
        fig, ax1 = plt.subplots(1, 1)
        ax1.plot(x, train_loss, 'r', label='loss')
        ax1.set_xlabel("step")
        ax1.set_ylabel("loss")
        ax1.set_title("Train Loss and lr")
        plt.legend(loc='best')

        ax2 = ax1.twinx()
        ax2.plot(x, learning_rate, label='lr')
        ax2.set_ylabel("learning rate")
        ax2.set_xlim(0, len(train_loss))  # 设置横坐标整数间隔
        plt.legend(loc='best')

        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        plt.legend(handles1 + handles2, labels1 + labels2, loc='upper right')

        fig.subplots_adjust(right=0.8)  # 防止出现保存图片显示不全的情况
        fig.savefig(path)
        plt.close()
        print("successful save loss curve! ")
    except Exception as e:
        print(e)


def plot_map(mAP, path='./save_weights/mAP.png'):
    try:
        x = list(range(len(mAP)))
        plt.plot(x, mAP, label='mAp')
        plt.xlabel('epoch')
        plt.ylabel('mAP')
        plt.title('Eval mAP')
        plt.xlim(0, len(mAP))
        plt.legend(loc='best')
        plt.savefig(path)
        plt.close()
        print("successful save mAP curve!")
    except Exception as e:
        print(e)


def plot_single(met, name, path):
    try:
        x = list(range(len(met)))
        plt.plot(x, met, label='{}'.format(name))
        plt.xlabel('epoch')
        plt.ylabel('{}'.format(name))
        plt.title('Eval {}'.format(name))
        plt.xlim(0, len(met))
        plt.legend(loc='best')
        plt.savefig(path)
        plt.close()
        print("successful save {} curve!".format(name))
    except Exception as e:
        print(e)


def plot_metrics(metrics_dict,
                 path='./save_weights/metrics_{}.png'.format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))):
    try:
        fig, axs = plt.subplots(2, 5, figsize=(1920 / 96, 960 / 96), dpi=96)
        train_box = metrics_dict.get("train_box", [])
        train_obj = metrics_dict.get("train_obj", [])
        train_cla = metrics_dict.get("train_cla", [])
        map_05 = metrics_dict.get("mAP@0.5", [])
        map_0595 = metrics_dict.get("mAP@0.5:0.95", [])
        val_box = metrics_dict.get("val_box", [])
        val_obj = metrics_dict.get("val_obj", [])
        val_cla = metrics_dict.get("val_cla", [])
        precision = metrics_dict.get("precision", [])
        recall = metrics_dict.get("recall", [])

        # 第1个子图：Box
        axs[0, 0].plot(list(range(len(train_box))), train_box)
        axs[0, 0].set_title('Box')
        # axs[0, 0].legend(loc='best')

        # 第2个子图：Objectness
        axs[0, 1].plot(list(range(len(train_obj))), train_obj)
        axs[0, 1].set_title('Objectness')

        # 第3个子图：Classification
        axs[0, 2].plot(list(range(len(train_cla))), train_cla)
        axs[0, 2].set_title('Classification')

        # 第4个子图：precision
        axs[0, 3].plot(list(range(len(precision))), precision)
        axs[0, 3].set_title('Precision')

        # 第5个子图：recall
        axs[0, 4].plot(list(range(len(recall))), recall)
        axs[0, 4].set_title('Recall')

        # 第6个子图：val Box
        axs[1, 0].plot(list(range(len(val_box))), val_box)
        axs[1, 0].set_title('Val Box')

        # 第7个子图：val Objectness
        axs[1, 1].plot(list(range(len(val_obj))), val_obj)
        axs[1, 1].set_title('Val Objectness')

        # 第8个子图：val Classification
        axs[1, 2].plot(list(range(len(val_cla))), val_cla)
        axs[1, 2].set_title('Val Classification')

        # 第9个子图：mAP@0.5
        axs[1, 3].plot(list(range(len(map_05))), map_05)
        axs[1, 3].set_title('mAP@0.5')

        # 第10个子图：mAP@0.5:0.95
        axs[1, 4].plot(list(range(len(map_0595))), map_0595)
        axs[1, 4].set_title('mAP@0.5:0.95')

        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        print("successful save metrics curve!")

    except Exception as e:
        print(e)
