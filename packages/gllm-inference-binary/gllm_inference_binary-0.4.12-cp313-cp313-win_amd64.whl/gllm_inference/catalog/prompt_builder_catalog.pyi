from _typeshed import Incomplete
from gllm_inference.catalog.catalog import BaseCatalog as BaseCatalog
from gllm_inference.catalog.component_map import PROMPT_BUILDER_TYPE_MAP as PROMPT_BUILDER_TYPE_MAP
from gllm_inference.multimodal_prompt_builder import MultimodalPromptBuilder as MultimodalPromptBuilder
from gllm_inference.prompt_builder.prompt_builder import BasePromptBuilder as BasePromptBuilder

PROMPT_BUILDER_MODEL_PARAM_MAP: Incomplete
PROMPT_BUILDER_REQUIRED_COLUMNS: Incomplete

class PromptBuilderCatalog(BaseCatalog[BasePromptBuilder | MultimodalPromptBuilder]):
    '''Loads multiple prompt builders from certain sources.

    Attributes:
        components (dict[str, BasePromptBuilder | MultimodalPromptBuilder]): Dictionary of the loaded prompt builders.

    Load from Google Sheets using client email and private key example:
    ```python
    catalog = PromptBuilderCatalog.from_gsheets(
        sheet_id="...",
        worksheet_id="...",
        client_email="...",
        private_key="...",
    )

    prompt_builder = catalog.name
    ```

    Load from Google Sheets using credential file example:
    ```python
    catalog = PromptBuilderCatalog.from_gsheets(
        sheet_id="...",
        worksheet_id="...",
        credential_file_path="...",
    )

    prompt_builder = catalog.name
    ```

    Load from CSV example:
    ```python
    catalog = PromptBuilderCatalog.from_csv(csv_path="...")

    prompt_builder = catalog.name
    ```

    Template Example:
    For an example of how a Google Sheets file can be formatted to be loaded using PromptBuilderCatalog, see:
    https://docs.google.com/spreadsheets/d/1PdlhxDRXP_48LNDzUkk3e_dEe-rs4MNYhGFnSNfuMCQ/edit?usp=drive_link

    For an example of how a CSV file can be formatted to be loaded using PromptBuilderCatalog, see:
    https://drive.google.com/file/d/1Uj83c-jpUncg33ns0derLiGQUTHZ_XUZ/view?usp=drive_link

    Template explanation:
    1. Must include the `name`, `type`, `model`, `system`, and `user` columns.
    2. The `type` column must be filled with one of the following prompt builder types:
        - agnostic
        - hugging_face
        - llama
        - mistral
        - openai
        - multimodal  # Deprecated in version 0.2.20. Will be removed in version 0.5.0.
    3. The `model` column can optionally be filled with an appropriate model name / path.
    4. At least one of the `system` and `user` columns must be filled.
    '''
