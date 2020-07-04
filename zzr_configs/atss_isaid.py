# model settings
model = dict(
    type='ATSS',
    pretrained='/disk2/zzr/resnet50.pth',
    backbone=dict(
        type='ResNet',
        depth=50,
        num_stages=4,
        out_indices=(0, 1, 2, 3),
        frozen_stages=1,
        norm_cfg=dict(type='BN', requires_grad=False),
        style='pytorch'),
    neck=dict(
        type='FPN',
        in_channels=[256, 512, 1024, 2048],
        out_channels=256,
        start_level=1,
        add_extra_convs=True,
        extra_convs_on_inputs=False,  # use P5
        num_outs=5,
        relu_before_extra_convs=True),
    bbox_head=dict(
        type='ATSSHead',
        num_classes=16,
        in_channels=256,
        stacked_convs=4,
        feat_channels=256,
        anchor_scales=[8],
        anchor_ratios=[1.0],
        anchor_strides=[8, 16, 32, 64, 128],
        anchor_base_sizes=None,
        target_means=(.0, .0, .0, .0),
        target_stds=(0.1, 0.1, 0.2, 0.2),
        train_cfg=dict(
            assigner=dict(
                type='ATSSAssigner',
                topk=9),
            smoothl1_beta=0.11,
            gamma=2.0,
            alpha=0.25,
            allowed_border=-1,
            pos_weight=-1,
            debug=False)))
# training and testing settings
train_cfg = dict(
    assigner=dict(
        type='ATSSAssigner',
        topk=9),
    smoothl1_beta=0.11,
    gamma=2.0,
    alpha=0.25,
    allowed_border=-1,
    pos_weight=-1,
    debug=False)
test_cfg = dict(
    nms_pre=1000,
    min_bbox_size=0,
    score_thr=0.05,
    nms=dict(type='nms', iou_thr=0.5),
    max_per_img=100)
# dataset settings
dataset_type = 'iSAIDDataset'
data_root = '/disk2/zzr/dataset_isaid/'
img_norm_cfg = dict(
    mean=[102.9801, 115.9465, 122.7717], std=[1.0, 1.0, 1.0], to_rgb=False)
data = dict(
    imgs_per_gpu=2,
    workers_per_gpu=0,
    train=dict(
        type=dataset_type,
        balance_cat=False,
        # ann_file=data_root + 'train/instancesonly_filtered_train_useful_standard.json',
        # img_prefix=data_root + 'train/images/',
        ann_file=data_root + 'val/instancesonly_filtered_val_standard.json',
        img_prefix=data_root + 'val/images/',
        img_scale=(800, 800),
        img_norm_cfg=img_norm_cfg,
        size_divisor=32,
        flip_ratio=0.5,
        with_mask=False,
        with_crowd=False,
        with_label=True),
    val=dict(
        type=dataset_type,
        ann_file=data_root + 'val/instancesonly_filtered_val_standard.json',
        img_prefix=data_root + 'val/images/',
        img_scale=(800, 800),
        img_norm_cfg=img_norm_cfg,
        size_divisor=32,
        flip_ratio=0,
        with_mask=False,
        with_crowd=False,
        with_label=True),
    test=dict(
        type=dataset_type,
        ann_file=data_root + 'val/instancesonly_filtered_val_standard.json',
        img_prefix=data_root + 'val/images/',
        img_scale=(800, 800),
        img_norm_cfg=img_norm_cfg,
        size_divisor=32,
        flip_ratio=0,
        with_mask=False,
        with_crowd=False,
        with_label=False,
        test_mode=True))
# optimizer
optimizer = dict(
    type='SGD',
    lr=0.00125,
    momentum=0.9,
    weight_decay=0.0001,
    paramwise_options=dict(bias_lr_mult=2., bias_decay_mult=0.))
optimizer_config = dict(grad_clip=None)
# learning policy
lr_config = dict(
    policy='step',
    warmup='constant',
    warmup_iters=500,
    warmup_ratio=1.0 / 3,
    step=[8, 11])
checkpoint_config = dict(interval=1)
# yapf:disable
log_config = dict(
    interval=50,
    hooks=[
        dict(type='TextLoggerHook'),
        # dict(type='TensorboardLoggerHook')
    ])
# yapf:enable
# runtime settings
total_epochs = 12
# device_ids = range(4)
dist_params = dict(backend='nccl')
log_level = 'INFO'
work_dir = '/disk2/zzr/work_dirs/atss_isaid'
load_from = None
resume_from = None
workflow = [('train', 1)]