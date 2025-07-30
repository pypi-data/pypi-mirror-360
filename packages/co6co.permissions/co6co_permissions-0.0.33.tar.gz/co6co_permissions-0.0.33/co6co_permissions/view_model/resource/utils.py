from co6co.utils import log
import os
import datetime
import cv2
from cv2.typing import MatLike
from websockets.sync.client import connect
import numpy as np
from co6co.utils.File import File


def showImage(wsUrl: str):
    first = None
    t: int = 100
    with connect(wsUrl) as ws:
        all: bytes = None
        while t > 0:
            # 接收消息
            result = ws.recv()
            if all == None:
                all = result
            else:
                all = all+result
            # 解析消息为图像数据

            # img_data = np.fromstring(result, dtype='uint8')
            # img_data = np.asarray( bytearray( result[3:]), dtype="uint8")
            # img = base64.b64decode(all)
            img = cv2.imdecode(np.frombuffer(
                all, dtype='uint8'), cv2.IMREAD_COLOR)
            if img == None:
                print("is None")
            else:  # 显示图像
                cv2.imshow('WebSocket Image', img)
                break
            cv2.waitKey(1)
    ws.close()


def getVideoFragment(wsUrl: str):
    try:
        with connect(wsUrl) as ws:
            # 接收消息
            result = ws.recv()
            s = getTempFileName("t.mp4")
            File.writeFile(s, result)
            return s
    except Exception as e:
        return None


def getTempFileName(ext: str = "jpg"):
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    s = f"tmp/frame_{datetime.datetime.now().strftime('%H%M%S%f')}.{ext}"
    return s


class VideoCamera(object):
    """
    摄像头
    """
    video: cv2.VideoCapture

    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()


def resize_image(imreadImage: MatLike, height: int = 208, width: int = 117) -> MatLike:
    """
    按指定图像大小调整尺寸
    """
    top, bottom, left, right = (0, 0, 0, 0)
    # 获取图片尺寸
    h, w, _ = imreadImage.shape

    # 对于长宽不等的图片，找到最长的一边
    longest_edge = max(h, w)

    # 计算短边需要增加多少像素宽度才能与长边等长(相当于padding，长边的padding为0，短边才会有padding)
    if h < longest_edge:
        dh = longest_edge - h
        top = dh // 2
        bottom = dh - top
    elif w < longest_edge:
        dw = longest_edge - w
        left = dw // 2
        right = dw - left
    else:
        pass  # pass是空语句，是为了保持程序结构的完整性。pass不做任何事情，一般用做占位语句。

    # RGB颜色
    BLACK = [0, 0, 0]
    # 给图片增加padding，使图片长、宽相等
    # top, bottom, left, right分别是各个边界的宽度，cv2.BORDER_CONSTANT是一种border type，表示用相同的颜色填充
    constant = cv2.copyMakeBorder(
        imreadImage, top, bottom, left, right, cv2.BORDER_CONSTANT, value=BLACK)
    # 调整图像大小并返回图像，目的是减少计算量和内存占用，提升训练速度
    return cv2.resize(constant, (height, width))


async def screenshot(videoPathOrStreamUrl: str, w: int = 208, h: int = 117, isFile: bool = True, useBytes: bool = False) -> str | bytes | None:
    """
    视频截图
    视频第一帧作为 poster
    """

    if (isFile and os.path.exists(videoPathOrStreamUrl)) or videoPathOrStreamUrl:
        try:
            userVideoFragment = False
            if 'wss://' in videoPathOrStreamUrl or 'wss://' in videoPathOrStreamUrl:
                videoPathOrStreamUrl = getVideoFragment(videoPathOrStreamUrl)
                userVideoFragment = True
            cap = cv2.VideoCapture(videoPathOrStreamUrl,
                                   cv2.CAP_FFMPEG)  # 打开视频
            if not cap.isOpened():
                log.warn(f"未能打开：{videoPathOrStreamUrl}")
                return None

            '''
            # 视频信息
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            # 创建输出视频文件对象，参数为输出文件名、编解码器、帧率、宽度和高度信息
            out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))

            cap.set(cv2.CAP_PROP_FPS, 30)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080) 
            '''
            # cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC , 5)
            ret, fram = cap.read()
            if not ret:
                return None
            if useBytes:
                fram = resize_image(fram, w, h)
                ret, jpeg = cv2.imencode('.jpg', fram)
                return jpeg.tobytes()
            s = None
            if type(fram) == np.ndarray:
                s = getTempFileName()
                fram = resize_image(fram, w, h)
                cv2.imwrite(s, fram)
                return s
        finally:
            cap.release()
            if userVideoFragment:
                os.remove(videoPathOrStreamUrl)
    return None
