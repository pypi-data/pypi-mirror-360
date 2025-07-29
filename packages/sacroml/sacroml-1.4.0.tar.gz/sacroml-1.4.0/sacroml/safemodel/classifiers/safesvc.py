"""Privacy protected Support Vector Classifier."""

from __future__ import annotations

import copy

import numpy as np
from dictdiffer import diff

from sacroml.safemodel.safemodel import SafeModel

from .dp_svc import DPSVC


class SafeSVC(SafeModel, DPSVC):
    """Privacy protected Support Vector Classifier."""

    def __init__(
        self,
        C: float = 1.0,
        gamma: str | float = "scale",
        dhat: int = 1000,
        eps: float = 10,
        **kwargs: dict,
    ) -> None:
        """Initialise a differentially private SVC."""
        SafeModel.__init__(self)
        DPSVC.__init__(self, C=C, gamma=gamma, dhat=dhat, eps=eps, **kwargs)
        self.model_type: str = "SVC"
        self.ignore_items = [
            "model_save_file",
            "ignore_items",
            "train_features",
            "train_labels",
            "unique_labels",
            "train_labels",
            "weights",
            "noisy_weights",
        ]
        self.examine_seperately_items = ["platt_transform", "svc"]

    def fit(self, train_features: np.ndarray, train_labels: np.ndarray) -> None:
        """Fit model and store model dict."""
        super().fit(train_features, train_labels)
        self.saved_model = copy.deepcopy(self.__dict__)

    def additional_checks(
        self, curr_separate: dict, saved_separate: dict
    ) -> tuple[str, str]:
        """SVC specific checks."""
        msg = ""
        disclosive = False
        for item in self.examine_seperately_items:
            diffs_list = list(
                diff(curr_separate[item].__dict__, saved_separate[item].__dict__)
            )
            if len(diffs_list) > 0:
                disclosive = True
                if len(diffs_list) == 1:
                    msg += f"structure {item} has one difference.\n"
                else:
                    msg += f"structure {item} has several differences.\n"

        return msg, disclosive
