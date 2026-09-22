from typing import Dict, List

from .config import TOPIC_MAP


def get_topic_for_dataset(dataset: str) -> str:
    dataset_name = dataset.lower().strip()
    if dataset_name not in TOPIC_MAP:
        raise ValueError(f"Unsupported dataset '{dataset}'. Available datasets: {sorted(TOPIC_MAP.keys())}")
    return TOPIC_MAP[dataset_name]


def list_topics() -> Dict[str, str]:
    return dict(TOPIC_MAP)


def list_topic_names() -> List[str]:
    return list(TOPIC_MAP.values())
