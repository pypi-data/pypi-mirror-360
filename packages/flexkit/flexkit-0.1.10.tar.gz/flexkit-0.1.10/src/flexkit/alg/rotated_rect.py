import cv2
import pandas as pd
import numpy as np
from typing import Tuple, Optional

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


class RotatedRect:
    class AssertInfo:
        @staticmethod
        def assert_points_shape(points: np.ndarray):
            """
            检查输入点的形状是否符合要求

            参数:
                points: 待检测的点集
            """
            assert len(points.shape) == 2 and points.shape[1] == 2, (
                "输入点集必须是(N,2)形状"
            )

    def __init__(self, points: np.ndarray):
        """
        初始化旋转矩形类

        参数:
            points: 输入点集，形状为(N,2)的numpy数组
        """
        self.AssertInfo.assert_points_shape(points)
        self.points = points

    def min_bounding_rect(self) -> Tuple[np.ndarray, Tuple[float, float, float]]:
        """
        计算当前点集的最小外接矩形

        返回:
            box: 矩形的四个顶点坐标，形状为(4,2)的numpy数组
            rect: 包含(中心(x,y), (宽度,高度), 旋转角度)的元组
        """
        rect = cv2.minAreaRect(self.points)
        box = cv2.boxPoints(rect)
        return box, rect

    def rotate(
        self, angle: float, center: Optional[Tuple[float, float]] = None
    ) -> np.ndarray:
        """
        旋转点集

        参数:
            angle: 旋转角度(度)，正值为逆时针
            center: 旋转中心点(x,y)，默认为矩形中心

        返回:
            旋转后的点集
        """
        if center is None:
            center = (0, 0)

        # 构建旋转矩阵
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        # 应用旋转
        rotated_points = cv2.transform(np.array([self.points]), rotation_matrix)[0]
        self.points = rotated_points

    def re_rotate(
        self, angle: float, center: Optional[Tuple[float, float]] = None
    ) -> np.ndarray:
        """
        将点集旋转回原始方向

        返回:
            旋转回原始方向的点集
        """
        if angle == 0:
            return self.points

        if center is None:
            center = (0, 0)

        # 反向旋转
        rotation_matrix = cv2.getRotationMatrix2D(center, -angle, 1.0)
        original_points = cv2.transform(np.array([self.points]), rotation_matrix)[0]

        self.points = original_points

    def filter(self, box: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        rect_contour = box.reshape((-1, 1, 2)).astype(np.int32)
        mask = []
        for pt in self.points:
            if cv2.pointPolygonTest(rect_contour, tuple(pt), False) >= 0:
                mask.append(True)
            else:
                mask.append(False)
        mask = np.array(mask)
        return self.points[mask], mask

    def draw(self, rect: Tuple[float, float, float], box: np.ndarray) -> None:
        # 绘制点集和旋转矩形
        plt.figure(figsize=(8, 6))
        plt.scatter(
            self.points[:, 0], self.points[:, 1], c="blue", label="Input Points"
        )  # 原始点集

        # 绘制旋转矩形（填充半透明绿色）
        rect_patch = Polygon(
            box, closed=True, fill=True, alpha=0.3, color="green", label="Rotated Rect"
        )
        plt.gca().add_patch(rect_patch)

        # 标记中心点和参数
        plt.scatter(rect[0][0], rect[0][1], c="red", marker="x", label="Center")
        plt.title(
            f"Rotation  Angle: {rect[2]:.1f}°\nWidth/Height: {rect[1][0]:.1f}, {rect[1][1]:.1f}"
        )
        plt.legend()
        plt.grid(True)
        plt.axis("equal")
        plt.show()

    @staticmethod
    def test_min_bounding_rect():
        data = pd.read_csv("test_data.csv", encoding="gbk")
        JD = data[["JD1_X", "JD1_Y"]].dropna()
        print(JD.values)
        rotate_rect = RotatedRect(JD.values.astype(np.float32))
        box, rect = rotate_rect.min_bounding_rect()
        print(box, rect)
        rotate_rect.draw(rect, box)

    @staticmethod
    def test_rotate():
        data = pd.read_csv("test_data.csv", encoding="gbk")
        JD = data[["JD1_X", "JD1_Y"]].dropna()
        print(JD.values)
        rotate_rect = RotatedRect(JD.values.astype(np.float32))
        box, rect = rotate_rect.min_bounding_rect()
        rotate_rect.rotate(rect[2], rect[0])
        rotate_rect.draw(rect, box)
        return rotate_rect, box, rect

    @staticmethod
    def test_re_rotate():
        data = pd.read_csv("data/test_data.csv", encoding="gbk")
        JD = data[["JD1_X", "JD1_Y"]].dropna()
        print(JD.values)
        rotate_rect = RotatedRect(JD.values.astype(np.float32))
        box, rect = rotate_rect.min_bounding_rect()
        rotate_rect.rotate(rect[2], rect[0])
        rotate_rect.re_rotate(rect[2], rect[0])
        rotate_rect.draw(rect, box)

    @staticmethod
    def test_filter():
        data = pd.read_csv("data/test_data.csv", encoding="gbk")
        JD = data[["JD1_X", "JD1_Y"]].dropna()
        print(JD.values)
        rotate_rect = RotatedRect(JD.values.astype(np.float32))
        box, rect = rotate_rect.min_bounding_rect()
        rotate_rect.rotate(rect[2], rect[0])
        rotate_rect.points, _ = rotate_rect.filter(box)
        rotate_rect.draw(rect, box)


if __name__ == "__main__":
    RotatedRect.test_min_bounding_rect()
