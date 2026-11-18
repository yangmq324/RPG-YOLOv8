# # -*- coding: utf-8 -*-
# """
# split_half_dataset_even.py

# 功能：
#     将原始 YOLO 数据集 datasets 中的 train / val / test 各自抽取一半样本，
#     按文件排序后保留第 2、4、6、8... 个样本，并同步复制对应 labels，
#     另存为新的 dataset 文件夹。

# 原始结构示例：
#     datasets/
#     ├── train/
#     │   ├── images/
#     │   └── labels/
#     ├── val/
#     │   ├── images/
#     │   └── labels/
#     └── test/
#         ├── images/
#         └── labels/

# 输出结构：
#     dataset/
#     ├── train/
#     │   ├── images/
#     │   └── labels/
#     ├── val/
#     │   ├── images/
#     │   └── labels/
#     └── test/
#         ├── images/
#         └── labels/

# 筛选规则：
#     对每个子集 images 文件按文件名排序：
#     第 1 个不保留，第 2 个保留，第 3 个不保留，第 4 个保留 ...
#     即保留排序后索引为 2,4,6,8... 的样本。
# """

# import argparse
# import shutil
# from pathlib import Path


# IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


# def find_images(image_dir: Path):
#     """查找 images 文件夹下的所有图像文件，并按文件名排序。"""
#     if not image_dir.exists():
#         return []

#     image_files = [
#         p for p in image_dir.iterdir()
#         if p.is_file() and p.suffix.lower() in IMG_EXTS
#     ]

#     return sorted(image_files, key=lambda x: x.name)


# def copy_one_subset(src_root: Path, dst_root: Path, subset: str, keep_mode: str = "even"):
#     """
#     复制单个子集 train / val / test。

#     keep_mode:
#         even: 保留第 2、4、6、8... 个样本
#         odd:  保留第 1、3、5、7... 个样本
#     """
#     src_img_dir = src_root / subset / "images"
#     src_label_dir = src_root / subset / "labels"

#     dst_img_dir = dst_root / subset / "images"
#     dst_label_dir = dst_root / subset / "labels"

#     dst_img_dir.mkdir(parents=True, exist_ok=True)
#     dst_label_dir.mkdir(parents=True, exist_ok=True)

#     image_files = find_images(src_img_dir)

#     if not image_files:
#         print(f"[Warning] No images found in: {src_img_dir}")
#         return {
#             "subset": subset,
#             "total_images": 0,
#             "copied_images": 0,
#             "copied_labels": 0,
#             "missing_labels": 0
#         }

#     copied_images = 0
#     copied_labels = 0
#     missing_labels = 0

#     for idx, img_path in enumerate(image_files, start=1):
#         if keep_mode == "even":
#             keep = (idx % 2 == 0)
#         elif keep_mode == "odd":
#             keep = (idx % 2 == 1)
#         else:
#             raise ValueError("keep_mode must be 'even' or 'odd'.")

#         if not keep:
#             continue

#         dst_img_path = dst_img_dir / img_path.name
#         shutil.copy2(img_path, dst_img_path)
#         copied_images += 1

#         label_path = src_label_dir / f"{img_path.stem}.txt"
#         dst_label_path = dst_label_dir / f"{img_path.stem}.txt"

#         if label_path.exists():
#             shutil.copy2(label_path, dst_label_path)
#             copied_labels += 1
#         else:
#             dst_label_path.write_text("", encoding="utf-8")
#             missing_labels += 1
#             print(f"[Warning] Missing label, created empty txt: {label_path}")

#     return {
#         "subset": subset,
#         "total_images": len(image_files),
#         "copied_images": copied_images,
#         "copied_labels": copied_labels,
#         "missing_labels": missing_labels
#     }


# def write_data_yaml(dst_root: Path, nc: int, names: list[str]):
#     """为新数据集生成 data.yaml。"""
#     yaml_path = dst_root / "data.yaml"

#     lines = [
#         f"path: {dst_root.as_posix()}",
#         "",
#         "train: train/images",
#         "val: val/images",
#         "test: test/images",
#         "",
#         f"nc: {nc}",
#         "names:"
#     ]

#     for i, name in enumerate(names):
#         lines.append(f"  {i}: {name}")

#     yaml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
#     return yaml_path


# def main():
#     parser = argparse.ArgumentParser(description="Keep half of YOLO dataset samples and copy to a new dataset folder.")

#     parser.add_argument(
#         "--src",
#         type=str,
#         default=r"F:\workspace\ultralytics-main\datasets",
#         help="原始数据集根目录，例如 F:/workspace/ultralytics-main/datasets"
#     )

#     parser.add_argument(
#         "--dst",
#         type=str,
#         default=r"F:\workspace\ultralytics-main\datasets1",
#         help="输出数据集根目录，例如 F:/workspace/ultralytics-main/datasets1"
#     )

#     parser.add_argument(
#         "--keep",
#         type=str,
#         default="even",
#         choices=["even", "odd"],
#         help="even 表示保留第 2、4、6... 个样本；odd 表示保留第 1、3、5... 个样本"
#     )

#     parser.add_argument(
#         "--overwrite",
#         action="store_true",
#         help="如果输出目录已存在，是否先删除后重建"
#     )

#     parser.add_argument(
#         "--nc",
#         type=int,
#         default=4,
#         help="类别数"
#     )

#     parser.add_argument(
#         "--names",
#         type=str,
#         default="lightVehicle,heavyVehicle,pedestrian,rider",
#         help="类别名称，用英文逗号分隔"
#     )

#     args = parser.parse_args()

#     src_root = Path(args.src)
#     dst_root = Path(args.dst)

#     if not src_root.exists():
#         raise FileNotFoundError(f"Source dataset does not exist: {src_root}")

#     if dst_root.exists() and args.overwrite:
#         print(f"[Info] Removing existing output directory: {dst_root}")
#         shutil.rmtree(dst_root)

#     dst_root.mkdir(parents=True, exist_ok=True)

#     print(f"Source dataset: {src_root}")
#     print(f"Output dataset: {dst_root}")
#     print(f"Keep mode: {args.keep}")
#     print("-" * 60)

#     for subset in ["train", "val", "test"]:
#         summary = copy_one_subset(src_root, dst_root, subset, keep_mode=args.keep)
#         print(
#             f"{subset}: total={summary['total_images']}, "
#             f"copied_images={summary['copied_images']}, "
#             f"copied_labels={summary['copied_labels']}, "
#             f"missing_labels={summary['missing_labels']}"
#         )

#     names = [x.strip() for x in args.names.split(",") if x.strip()]
#     if len(names) != args.nc:
#         print(f"[Warning] nc={args.nc}, but names has {len(names)} items.")

#     yaml_path = write_data_yaml(dst_root, args.nc, names)

#     print("-" * 60)
#     print("Done.")
#     print(f"New data.yaml: {yaml_path}")
#     print("\nYou can train with:")



# if __name__ == "__main__":
#     main()
# -*- coding: utf-8 -*-
"""
split_dataset_keep_every_three.py

功能：
    将原始 YOLO 数据集 datasets 中的 train / val / test 各自按文件名排序，
    每 3 个样本保留 1 个，并同步复制对应 labels，
    另存为新的 dataset 文件夹。

原始结构示例：
    datasets/
    ├── train/
    │   ├── images/
    │   └── labels/
    ├── val/
    │   ├── images/
    │   └── labels/
    └── test/
        ├── images/
        └── labels/

输出结构：
    datasets1/
    ├── train/
    │   ├── images/
    │   └── labels/
    ├── val/
    │   ├── images/
    │   └── labels/
    └── test/
        ├── images/
        └── labels/

筛选规则：
    对每个子集 images 文件按文件名排序：
    默认保留第 3、6、9、12... 个样本。
"""

import argparse
import shutil
from pathlib import Path


IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def find_images(image_dir: Path):
    """查找 images 文件夹下的所有图像文件，并按文件名排序。"""
    if not image_dir.exists():
        return []

    image_files = [
        p for p in image_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMG_EXTS
    ]

    return sorted(image_files, key=lambda x: x.name)


def copy_one_subset(src_root: Path, dst_root: Path, subset: str, interval: int = 3, offset: int = 0):
    """
    复制单个子集 train / val / test。

    interval:
        每隔多少个样本保留 1 个。
        interval=3 表示每 3 个样本保留 1 个。

    offset:
        控制保留位置。

        offset=0：保留第 3、6、9、12... 个样本
        offset=1：保留第 1、4、7、10... 个样本
        offset=2：保留第 2、5、8、11... 个样本
    """
    src_img_dir = src_root / subset / "images"
    src_label_dir = src_root / subset / "labels"

    dst_img_dir = dst_root / subset / "images"
    dst_label_dir = dst_root / subset / "labels"

    dst_img_dir.mkdir(parents=True, exist_ok=True)
    dst_label_dir.mkdir(parents=True, exist_ok=True)

    image_files = find_images(src_img_dir)

    if not image_files:
        print(f"[Warning] No images found in: {src_img_dir}")
        return {
            "subset": subset,
            "total_images": 0,
            "copied_images": 0,
            "copied_labels": 0,
            "missing_labels": 0
        }

    copied_images = 0
    copied_labels = 0
    missing_labels = 0

    for idx, img_path in enumerate(image_files, start=1):
        keep = (idx % interval == offset)

        if not keep:
            continue

        dst_img_path = dst_img_dir / img_path.name
        shutil.copy2(img_path, dst_img_path)
        copied_images += 1

        label_path = src_label_dir / f"{img_path.stem}.txt"
        dst_label_path = dst_label_dir / f"{img_path.stem}.txt"

        if label_path.exists():
            shutil.copy2(label_path, dst_label_path)
            copied_labels += 1
        else:
            dst_label_path.write_text("", encoding="utf-8")
            missing_labels += 1
            print(f"[Warning] Missing label, created empty txt: {label_path}")

    return {
        "subset": subset,
        "total_images": len(image_files),
        "copied_images": copied_images,
        "copied_labels": copied_labels,
        "missing_labels": missing_labels
    }


def write_data_yaml(dst_root: Path, nc: int, names: list[str]):
    """为新数据集生成 data.yaml。"""
    yaml_path = dst_root / "data.yaml"

    lines = [
        f"path: {dst_root.as_posix()}",
        "",
        "train: train/images",
        "val: val/images",
        "test: test/images",
        "",
        f"nc: {nc}",
        "names:"
    ]

    for i, name in enumerate(names):
        lines.append(f"  {i}: {name}")

    yaml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return yaml_path


def main():
    parser = argparse.ArgumentParser(
        description="Keep one sample every three YOLO dataset samples and copy to a new dataset folder."
    )

    parser.add_argument(
        "--src",
        type=str,
        default=r"F:\workspace\ultralytics-main\datasets",
        help="原始数据集根目录，例如 F:/workspace/ultralytics-main/datasets"
    )

    parser.add_argument(
        "--dst",
        type=str,
        default=r"F:\workspace\ultralytics-main\datasets3",
        help="输出数据集根目录，例如 F:/workspace/ultralytics-main/datasets3"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=3,
        help="每隔多少个样本保留 1 个，默认 3 表示每三个保留一个"
    )

    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        choices=[0, 1, 2],
        help=(
            "保留位置："
            "0 表示保留第 3、6、9... 个；"
            "1 表示保留第 1、4、7... 个；"
            "2 表示保留第 2、5、8... 个"
        )
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="如果输出目录已存在，是否先删除后重建"
    )

    parser.add_argument(
        "--nc",
        type=int,
        default=4,
        help="类别数"
    )

    parser.add_argument(
        "--names",
        type=str,
        default="lightVehicle,heavyVehicle,pedestrian,rider",
        help="类别名称，用英文逗号分隔"
    )

    args = parser.parse_args()

    src_root = Path(args.src)
    dst_root = Path(args.dst)

    if not src_root.exists():
        raise FileNotFoundError(f"Source dataset does not exist: {src_root}")

    if dst_root.exists() and args.overwrite:
        print(f"[Info] Removing existing output directory: {dst_root}")
        shutil.rmtree(dst_root)

    dst_root.mkdir(parents=True, exist_ok=True)

    print(f"Source dataset: {src_root}")
    print(f"Output dataset: {dst_root}")
    print(f"Interval: {args.interval}")
    print(f"Offset: {args.offset}")
    print("-" * 60)

    for subset in ["train", "val", "test"]:
        summary = copy_one_subset(
            src_root=src_root,
            dst_root=dst_root,
            subset=subset,
            interval=args.interval,
            offset=args.offset
        )

        print(
            f"{subset}: total={summary['total_images']}, "
            f"copied_images={summary['copied_images']}, "
            f"copied_labels={summary['copied_labels']}, "
            f"missing_labels={summary['missing_labels']}"
        )

    names = [x.strip() for x in args.names.split(",") if x.strip()]
    if len(names) != args.nc:
        print(f"[Warning] nc={args.nc}, but names has {len(names)} items.")

    yaml_path = write_data_yaml(dst_root, args.nc, names)

    print("-" * 60)
    print("Done.")
    print(f"New data.yaml: {yaml_path}")


if __name__ == "__main__":
    main()