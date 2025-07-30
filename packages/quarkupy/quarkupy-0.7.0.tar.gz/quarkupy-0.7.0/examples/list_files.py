"""Manual chaining (i.e. outside of lattices) of Quarks for RAG ingest"""

import os
from urllib.parse import urlparse

import dotenv
import pandas as pd
from halo import Halo

import quarkupy.lib as q
import quarkupy.lib.context as qc

# Configs
dotenv.load_dotenv()

API_KEY = os.environ.get("QUARK_API_KEY")
API_END_POINT = "https://demo.quarklabs.ai/api/quark"

if API_KEY is None or API_KEY == "":
    raise ValueError("QUARK_API_KEY environment variable not set")

PRINT_DATASETS = False
PRINT_QUARK_METRICS = True
PRINT_QUARK_HISTORY = False
SPINNER = "dots"

host_url = urlparse(API_END_POINT)
url_root = f"{host_url.scheme}://{host_url.netloc}"


async def main():
    print(q.__banner__)

    manager = qc.ContextManager(
        base_url=host_url.geturl()
    )

    with Halo(text="💠 Getting files...", spinner=SPINNER):
        files = await manager.get_files()
        files_df: pd.DataFrame = files.to_pandas()

    print("Files:\n")
    print(files_df)

    with Halo(text="💠 Getting classifiers...", spinner=SPINNER):
        classifiers = await manager.get_classifiers()
        class_df: pd.DataFrame = classifiers.to_pandas()

    print("Classifiers:\n")
    print(class_df)

    with Halo(text="💠 Getting extractors...", spinner=SPINNER):
        extractors = await manager.get_extractors()
        extractors_df = extractors.to_pandas()

    print("Extractors:\n")
    print(extractors_df)

    with Halo(text=f"💠 Getting classifier {class_df.iloc[0].name} text...", spinner=SPINNER):
        classifier_text = await manager.get_classifier_text(class_df.iloc[0].classifier_id)
        classifier_text_df = classifier_text.to_pandas()

    print(f"Classifier {class_df.iloc[0].name} Text:\n")
    print(classifier_text_df)

    with Halo(text=f"💠 Getting classifier {class_df.iloc[0].name} text...", spinner=SPINNER):
        extractor_text = await manager.get_extractor_text(extractors_df.iloc[0].extractor_id)
        extractor_text_df = extractor_text.to_pandas()

    print(f"Extractor {extractors_df.iloc[0].name} Text:\n")
    print(extractor_text_df)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
