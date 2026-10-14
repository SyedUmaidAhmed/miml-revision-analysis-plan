"""Standard MIML evaluation metrics.

Implements the 5 standard multi-label metrics used in MIML literature:
  - Hamming Loss (lower is better)
  - One Error (lower is better)
  - Coverage (lower is better)
  - Ranking Loss (lower is better)
  - Average Precision (higher is better)
"""

import numpy as np
from sklearn.metrics import label_ranking_loss, f1_score


def HammingLoss(y_true, output):
    y_pred = np.where(output > 0.5, 1., 0.)
    num_ins, num_class = y_pred.shape
    miss_pairs = np.sum(y_pred != y_true)
    return miss_pairs / (num_ins * num_class)


def OneErrorLoss(y_true, output):
    loss = 0
    valid_count = 0
    for i in range(len(y_true)):
        if np.sum(y_true[i] == 1) == 0:
            continue
        if y_true[i][np.argmax(output[i])] != 1:
            loss += 1
        valid_count += 1
    return loss / max(valid_count, 1)


def CoverageError(y_true, output):
    num_ins, num_class = output.shape
    label = []
    label_size = []
    for i in range(num_ins):
        temp = y_true[i]
        label_size.append(int(np.sum(temp == 1)))
        idx = [j for j in range(num_class) if temp[j] == 1]
        label.append(idx)
    cover = 0
    valid_count = 0
    for i in range(num_ins):
        if label_size[i] == 0:
            continue
        temp = output[i]
        index = np.argsort(temp)
        temp_min = num_class + 1
        for m in range(label_size[i]):
            loc = np.argwhere(index == label[i][m])[0, 0]
            if loc < temp_min:
                temp_min = loc + 1
        cover += num_class - temp_min + 1
        valid_count += 1
    return (cover / max(valid_count, 1)) - 1


def RankingLoss(y_true, output):
    y_true = np.where(y_true > 0., 1., 0.)
    return label_ranking_loss(y_true, output)


def AveragePrecision(y_true, output):
    num_ins, num_class = output.shape
    label = []
    label_size = []
    for i in range(num_ins):
        temp = y_true[i]
        label_size.append(int(np.sum(temp == 1)))
        idx = [j for j in range(num_class) if temp[j] == 1]
        label.append(idx)
    aveprec = 0
    valid_count = 0
    for i in range(num_ins):
        if label_size[i] == 0:
            continue
        temp = output[i]
        index = np.argsort(temp)
        indicator = np.zeros(num_class)
        for m in range(label_size[i]):
            loc = np.argwhere(index == label[i][m])[0][0]
            indicator[loc] = 1
        summary = 0
        for m in range(label_size[i]):
            loc = np.argwhere(index == label[i][m])[0, 0]
            summary += np.sum(indicator[loc: num_class]) / (num_class - loc)
        aveprec += summary / label_size[i]
        valid_count += 1
    return aveprec / max(valid_count, 1)


def MacroF1(y_true, output):
    y_pred = np.where(output > 0.5, 1., 0.)
    return f1_score(y_true, y_pred, average='macro', zero_division=0)


def MicroF1(y_true, output):
    y_pred = np.where(output > 0.5, 1., 0.)
    return f1_score(y_true, y_pred, average='micro', zero_division=0)


def AllFive(y_true, output):
    return {
        "HammingLoss": HammingLoss(y_true, output),
        "OneError": OneErrorLoss(y_true, output),
        "Coverage": CoverageError(y_true, output),
        "RankingLoss": RankingLoss(y_true, output),
        "AveragePrecision": AveragePrecision(y_true, output),
        "MacroF1": MacroF1(y_true, output),
        "MicroF1": MicroF1(y_true, output),
    }


def optimize_thresholds(y_true, output, metric='hamming', num_steps=100):
    """Find per-label optimal thresholds on validation data."""
    num_labels = y_true.shape[1]
    thresholds = np.full(num_labels, 0.5)
    candidates = np.linspace(0.05, 0.95, num_steps)

    for l in range(num_labels):
        best_score = float('inf') if metric == 'hamming' else float('-inf')
        best_t = 0.5

        for t in candidates:
            preds = (output[:, l] > t).astype(float)
            if metric == 'hamming':
                score = np.mean(preds != y_true[:, l])
                if score < best_score:
                    best_score = score
                    best_t = t
            else:  # f1
                tp = np.sum(preds * y_true[:, l])
                fp = np.sum(preds * (1 - y_true[:, l]))
                fn = np.sum((1 - preds) * y_true[:, l])
                precision = tp / (tp + fp + 1e-8)
                recall = tp / (tp + fn + 1e-8)
                f1 = 2 * precision * recall / (precision + recall + 1e-8)
                if f1 > best_score:
                    best_score = f1
                    best_t = t
        thresholds[l] = best_t

    return thresholds


def HammingLossWithThresholds(y_true, output, thresholds):
    """HammingLoss with per-label thresholds instead of fixed 0.5."""
    y_pred = np.zeros_like(output)
    for l in range(output.shape[1]):
        y_pred[:, l] = (output[:, l] > thresholds[l]).astype(float)
    num_ins, num_class = y_pred.shape
    miss_pairs = np.sum(y_pred != y_true)
    return miss_pairs / (num_ins * num_class)


def AllFiveWithThresholds(y_true, output, thresholds):
    """AllFive metrics but HL and F1 use optimized thresholds."""
    y_pred_opt = np.zeros_like(output)
    for l in range(output.shape[1]):
        y_pred_opt[:, l] = (output[:, l] > thresholds[l]).astype(float)

    num_ins, num_class = y_pred_opt.shape
    hl = np.sum(y_pred_opt != y_true) / (num_ins * num_class)

    return {
        "HammingLoss": hl,
        "OneError": OneErrorLoss(y_true, output),
        "Coverage": CoverageError(y_true, output),
        "RankingLoss": RankingLoss(y_true, output),
        "AveragePrecision": AveragePrecision(y_true, output),
        "MacroF1": f1_score(y_true, y_pred_opt, average='macro', zero_division=0),
        "MicroF1": f1_score(y_true, y_pred_opt, average='micro', zero_division=0),
    }
