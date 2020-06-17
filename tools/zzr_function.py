import cv2
import mmcv
import numpy as np
import pycocotools.mask as maskUtils
from mmcv.image import imread, imwrite
from mmdet.core import tensor2imgs, get_classes

def assembel_mask(results):
    assembel_masks = []
    for result in results:
        hbb_masks = result[1]
        obb_masks = result[-1]
        for i in range(len(hbb_masks)):
            for j in range(len(hbb_masks[i])):
                hbb_mask = hbb_masks[i][j]
                obb_mask = obb_masks[i][j]
                hbb_mask = maskUtils.decode(hbb_mask).astype(np.bool)
                obb_mask = maskUtils.decode(obb_mask).astype(np.bool)
                mask = hbb_mask + obb_mask
                mask = mask.astype(np.uint8)
                mask = maskUtils.encode(
                np.array(mask[:, :, np.newaxis], order='F'))[0]
                result[1][i][j] = mask
        assembel_masks.append(result[:2])
    return assembel_masks

def assembel_mask_V2(results):
    assembel_masks = []
    for result in results:
        hbb_masks  = result[1]
        obb_masks  = result[-1]
        obb_bboxes = result[-2]
        for i in range(len(hbb_masks)):
            for j in range(len(hbb_masks[i])):
                hbb_mask = hbb_masks[i][j]
                obb_mask = obb_masks[i][j]
                hbb_mask = maskUtils.decode(hbb_mask).astype(np.bool)
                obb_mask = maskUtils.decode(obb_mask).astype(np.bool)
                obb_bbox = obb_bboxes[i][j][:8]
                obb_bbox = obb_bbox.astype(np.int32)
                obb_bbox = obb_bbox.reshape(4,2)
                obb_bbox_mask = np.zeros(hbb_mask.shape[:2])
                cv2.fillPoly(obb_bbox_mask, [obb_bbox], 1)
                obb_bbox_mask = obb_bbox_mask.astype(np.bool)
                hbb_mask = np.multiply(obb_bbox_mask, hbb_mask).astype(np.bool)
                mask = hbb_mask + obb_mask
                mask = mask.astype(np.uint8)
                mask = maskUtils.encode(
                np.array(mask[:, :, np.newaxis], order='F'))[0]
                result[1][i][j] = mask
        assembel_masks.append(result[:2])
    return assembel_masks

def tran2obb_results(outputs):
    final_outs = []
    for output in outputs:
        output = [output[0], output[-1]]
        output = tuple(output)
        final_outs.append(output)
    return final_outs

def tran2hbb_results(outputs):
    final_outs = []
    for output in outputs:
        output = [output[0], output[1]]
        output = tuple(output)
        final_outs.append(output)
    return final_outs

def tran2mix_results(outputs, inds=[0,3,4,5,7,8,9,10,11,13,14]):
    final_results = []
    for output in outputs:
        output = list(output)
        for ind in inds:
            output[3][ind] = output[1][ind]
        output = [output[0], output[3]]
        output = tuple(output)
        final_results.append(output)
    return final_results

def show_rmask(data,result, img_norm_cfg, class_names,
            score_thr=0.3, file_name='0.png'):
    
    bbox_result, segm_result, rbbox_result = result
    img_tensor = data['img'][0]
    img_metas = data['img_meta'][0].data[0]
    imgs = tensor2imgs(img_tensor, **img_norm_cfg)
    
    for img, img_meta in zip(imgs, img_metas):
        h, w, _ = img_meta['img_shape']
        img_show = img[:h, :w, :]
        
        bboxes  = np.vstack(bbox_result)
        rbboxes = np.vstack(rbbox_result)

        # draw segmentation masks
        if segm_result is not None:
            segms = mmcv.concat_list(segm_result)
            inds = np.where(bboxes[:, -1] > score_thr)[0]
            for i in inds:
                color_mask = np.random.randint(
                    0, 256, (1, 3), dtype=np.uint8)
                mask = maskUtils.decode(segms[i]).astype(np.bool)
                img_show[mask] = img_show[mask] * 0.5 + color_mask * 0.5
        # draw rbbox
        labels = [
            np.full(bbox.shape[0], i, dtype=np.int32)
                for i, bbox in enumerate(bbox_result)
        ]
        labels = np.concatenate(labels)
        
        img = imread(img_show)
        
        scores = rbboxes[:, -1]
        inds = scores > score_thr
        bboxes = bboxes[inds, :]
        rbboxes = rbboxes[inds, :8]
        labels = labels[inds]
        
        rbbox_color = (0, 255, 0)
        text_color = (0, 255, 0)
        font_scale = 0.5
        
        for rbbox, bbox, label in zip(rbboxes, bboxes, labels):
            bbox_int = bbox.astype(np.int32)
            rbbox_int = rbbox.astype(np.int32)
            rbbox_int = rbbox_int.reshape(4,2)
            cv2.drawContours(img,[rbbox_int],0,rbbox_color,1)
            label_text = class_names[
                label] if class_names is not None else 'cls {}'.format(label)
            if len(bbox) > 4:
                label_text += '|{:.02f}'.format(bbox[-1])
            cv2.putText(img, label_text, (bbox_int[0], bbox_int[1] - 2),
                    cv2.FONT_HERSHEY_COMPLEX, font_scale, text_color)
        
        cv2.imwrite(file_name,img)

def show_mask(data,result, img_norm_cfg, class_names,
            score_thr=0.3, file_name='0.png'):
    
    bbox_result, segm_result = result
    img_tensor = data['img'][0]
    img_metas = data['img_meta'][0].data[0]
    imgs = tensor2imgs(img_tensor, **img_norm_cfg)
    
    for img, img_meta in zip(imgs, img_metas):
        h, w, _ = img_meta['img_shape']
        img_show = img[:h, :w, :]
        
        bboxes  = np.vstack(bbox_result)

        # draw segmentation masks
        if segm_result is not None:
            segms = mmcv.concat_list(segm_result)
            inds = np.where(bboxes[:, -1] > score_thr)[0]
            for i in inds:
                color_mask = np.random.randint(
                    0, 256, (1, 3), dtype=np.uint8)
                mask = maskUtils.decode(segms[i]).astype(np.bool)
                img_show[mask] = img_show[mask] * 0.5 + color_mask * 0.5
        # draw rbbox
        labels = [
            np.full(bbox.shape[0], i, dtype=np.int32)
                for i, bbox in enumerate(bbox_result)
        ]
        labels = np.concatenate(labels)
        
        img = imread(img_show)
        
        scores = bboxes[:, -1]
        inds = scores > score_thr
        bboxes = bboxes[inds, :]
        labels = labels[inds]
        
        bbox_color = (0, 255, 0)
        text_color = (0, 255, 0)
        font_scale = 0.5
        
        for bbox, label in zip(bboxes, labels):
            bbox_int = bbox.astype(np.int32)
            cv2.rectangle(img, (bbox_int[0], bbox_int[1]), (bbox_int[2], bbox_int[3]), bbox_color, 1)
            label_text = class_names[
                label] if class_names is not None else 'cls {}'.format(label)
            if len(bbox) > 4:
                label_text += '|{:.02f}'.format(bbox[-1])
            cv2.putText(img, label_text, (bbox_int[0], bbox_int[1] - 2),
                    cv2.FONT_HERSHEY_COMPLEX, font_scale, text_color)
        
        cv2.imwrite(file_name,img)

def trans2ms_result(result):
    result = list(result)
    for i in range(len(result[0])): # 遍历每一个类别
        for j in range(len(result[0][i])): # 遍历每一个框
            result[0][i][j][-1] = result[1][1][i][j] 
            result[2][i][j][-1] = result[3][1][i][j]
    result[1] = result[1][0]
    result[3] = result[3][0]
    result = tuple(result)
    return result

def trans2mask_score(results):
    ms_results = []
    for result in results:
        result = list(result)
        for i in range(len(result[0])):
            for j in range(len(result[0][i])):
                result[0][i][j][-1] = result[1][1][i][j] 
        result[1] = result[1][0]
        result = tuple(result)
        ms_results.append(result)
    return ms_results

def trans2ms_results(results):
    ms_results = []
    for result in results:
        result = list(result)
        for i in range(len(result[0])):
            for j in range(len(result[0][i])):
                result[0][i][j][-1] = result[1][1][i][j] 
                result[2][i][j][-1] = result[3][1][i][j]
        result[1] = result[1][0]
        result[3] = result[3][0]
        result = tuple(result)
        ms_results.append(result)
    return ms_results

def trans2mask_results_V2(results):
    mask_results = []
    for result in results:
        result = list(result)
        result[1] = result[1][0]
        result = tuple(result)
        mask_results.append(result)
    return mask_results

def trans2mask_results(results):
    mask_results = []
    for result in results:
        result = list(result)
        result[1] = result[1][0]
        result[3] = result[3][0]
        result = tuple(result)
        mask_results.append(result)
    return mask_results

def trans2obb_results(results):
    obb_results = []
    for result in results:
        result = list(result)
        result = [result[0], result[-1]]
        result = tuple(result)
        obb_results.append(result)
    return obb_results

def trans2hbb_results(results):
    hbb_results = []
    for result in results:
        result = list(result)
        result = [result[0], result[1]]
        result = tuple(result)
        hbb_results.append(result)
    return hbb_results

def trans2mix_results(results):
    mix_results = []
    for result in results:
        result = list(result)
        for i in range(len(result[0])):
            for j in range(len(result[0][i])):
                ms_hbb = result[0][i][j][-1]
                ms_obb = result[2][i][j][-1]
                if ms_hbb < ms_obb:
                    result[0][i][j][-1] = ms_obb
                    result[1][i][j] = result[3][i][j]
        result = result[:2]
        result = tuple(result)
        mix_results.append(result)
    return mix_results

def show_bbox(data,result, img_norm_cfg, class_names,
            score_thr=0.3, file_name='0.png'):
    
    bbox_result = result
    img_tensor = data['img'][0]
    img_metas = data['img_meta'][0].data[0]
    imgs = tensor2imgs(img_tensor, **img_norm_cfg)
    
    for img, img_meta in zip(imgs, img_metas):
        h, w, _ = img_meta['img_shape']
        img_show = img[:h, :w, :]
        
        bboxes  = np.vstack(bbox_result)


        # draw rbbox
        labels = [
            np.full(bbox.shape[0], i, dtype=np.int32)
                for i, bbox in enumerate(bbox_result)
        ]
        labels = np.concatenate(labels)
        
        img = imread(img_show)
        
        scores = bboxes[:, -1]
        inds = scores > score_thr
        bboxes = bboxes[inds, :]
        labels = labels[inds]
        
        bbox_color = (0, 255, 0)
        text_color = (0, 255, 0)
        font_scale = 0.5
        
        for bbox, label in zip(bboxes, labels):
            bbox_int = bbox.astype(np.int32)
            cv2.rectangle(img, (bbox_int[0], bbox_int[1]), (bbox_int[2], bbox_int[3]), bbox_color, 1)
            label_text = class_names[
                label] if class_names is not None else 'cls {}'.format(label)
            if len(bbox) > 4:
                label_text += '|{:.02f}'.format(bbox[-1])
            cv2.putText(img, label_text, (bbox_int[0], bbox_int[1] - 2),
                    cv2.FONT_HERSHEY_COMPLEX, font_scale, text_color)
        
        cv2.imwrite(file_name,img)