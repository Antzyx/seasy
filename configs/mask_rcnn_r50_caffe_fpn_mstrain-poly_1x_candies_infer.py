# The new config inherits a base config to highlight the necessary modification
_base_ = '../mask_rcnn/mask_rcnn_r50_fpn_mstrain-poly_3x_coco.py'

# We also need to change the num_classes in head to match the dataset's annotation
model = dict(
    roi_head=dict(
        bbox_head=dict(num_classes=4),
        mask_head=dict(num_classes=4)))

test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(512, 512),
        flip=False,
        transforms=[
            dict(type='Resize', keep_ratio=True),
            dict(type='RandomFlip'),
            dict(
                type='Normalize',
                mean=[123.675, 116.28, 103.53],
                std=[58.395, 57.12, 57.375],
                to_rgb=True),
            dict(type='Pad', size_divisor=32),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img'])
        ])
]

# Modify dataset related settings
dataset_type = 'COCODataset'
classes = ('mms', 'mms_nut', 'skittle', 'bean')
data = dict(
    test=dict(
        img_prefix='CHANGE-ME/seasy_challenge/data/test/images/',
        classes=classes,
        pipeline=test_pipeline,
        ann_file='CHANGE-ME/seasy_challenge/data/test/coco_annotations.json',
        ),
    )

# We can use the pre-trained Mask RCNN model to obtain higher performance
load_from = 'work_dirs/mask_rcnn_r50_caffe_fpn_mstrain-poly_1x_candies/first_try.pth'