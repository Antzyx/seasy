# The new config inherits a base config to highlight the necessary modification
_base_ = '../mask_rcnn/mask_rcnn_r50_fpn_mstrain-poly_3x_coco.py'

# We also need to change the num_classes in head to match the dataset's annotation
model = dict(
    roi_head=dict(
        bbox_head=dict(num_classes=4),
        mask_head=dict(num_classes=4)))

# Modify dataset related settings
dataset_type = 'COCODataset'
classes = ('mms', 'mms_nut', 'skittle', 'bean')
data = dict(
    train=dict(
        dataset=dict(
            img_prefix='CHANGE-ME/seasy_challenge/data/render/coco_data/',
            classes=classes,
            pipeline=[
                dict(type='LoadImageFromFile'),
                dict(
                    type='LoadAnnotations',
                    with_bbox=True,
                    with_mask=True,
                    poly2mask=True),
                dict(
                    type='Resize',
                    img_scale=[(512, 512), (512, 512)],
                    multiscale_mode='range',
                    keep_ratio=True),
                dict(type='RandomFlip', flip_ratio=0.5),
                dict(type='PhotoMetricDistortion'),
                dict(type='Corrupt', corruption="gaussian_noise", severity=1, probability=0.5),
                dict(type='Corrupt', corruption="gaussian_noise", severity=1, probability=0.1),
                dict(type='Corrupt', corruption="gaussian_blur", severity=1, probability=0.2),
                dict(type='Corrupt', corruption="snow", severity=1, probability=0.3),
                dict(type='Corrupt', corruption="snow", severity=2, probability=0.1),
                dict(type='Corrupt', corruption="jpeg_compression", severity=1, probability=0.1),
                dict(
                    type='Normalize',
                    mean=[123.675, 116.28, 103.53],
                    std=[58.395, 57.12, 57.375],
                    to_rgb=True),
                dict(type='Pad', size_divisor=32),
                dict(type='DefaultFormatBundle'),
                dict(
                    type='Collect',
                    keys=['img', 'gt_bboxes', 'gt_labels', 'gt_masks'])
            ],
            ann_file='CHANGE-ME/seasy_challenge/data/render/coco_data_medium/coco_annotations.json'),
        ),
    val=dict(
        img_prefix='CHANGE-ME/seasy_challenge/data/render/coco_data_small/',
        classes=classes,
        ann_file='CHANGE-ME/seasy_challenge/data/render/coco_data_small/coco_annotations.json',
        ),
    test=dict(
        img_prefix='CHANGE-ME/seasy_challenge/data/test/images',
        classes=classes,
        ann_file='CHANGE-ME/seasy_challenge/data/test/coco_annotations.json',
        ),
    )

# We can use the pre-trained Mask RCNN model to obtain higher performance
load_from = 'work_dirs/mask_rcnn_r50_caffe_fpn_mstrain-poly_1x_candies/second_try.pth'