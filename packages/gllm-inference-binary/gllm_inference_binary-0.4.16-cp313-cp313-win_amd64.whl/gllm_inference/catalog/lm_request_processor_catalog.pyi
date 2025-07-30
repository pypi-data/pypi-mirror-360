from _typeshed import Incomplete
from gllm_inference.catalog.catalog import BaseCatalog as BaseCatalog, logger as logger
from gllm_inference.catalog.component_map import LM_INVOKER_TYPE_MAP as LM_INVOKER_TYPE_MAP, OUTPUT_PARSER_TYPE_MAP as OUTPUT_PARSER_TYPE_MAP, PROMPT_BUILDER_TYPE_MAP as PROMPT_BUILDER_TYPE_MAP
from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker as BaseLMInvoker
from gllm_inference.multimodal_lm_invoker.multimodal_lm_invoker import BaseMultimodalLMInvoker as BaseMultimodalLMInvoker
from gllm_inference.multimodal_prompt_builder.multimodal_prompt_builder import MultimodalPromptBuilder as MultimodalPromptBuilder
from gllm_inference.output_parser.output_parser import BaseOutputParser as BaseOutputParser
from gllm_inference.prompt_builder.prompt_builder import BasePromptBuilder as BasePromptBuilder
from gllm_inference.request_processor import LMRequestProcessor as LMRequestProcessor

LM_REQUEST_PROCESSOR_REQUIRED_COLUMNS: Incomplete

class LMRequestProcessorCatalog(BaseCatalog[LMRequestProcessor]):
    '''Loads multiple LM request processors from certain sources.

    Attributes:
        components (dict[str, LMRequestProcessor]): Dictionary of the loaded LM request processors.

    Load from Google Sheets using client email and private key example:
    ```python
    catalog = LMRequestProcessorCatalog.from_gsheets(
        sheet_id="...",
        worksheet_id="...",
        client_email="...",
        private_key="...",
    )

    lm_request_processor = catalog.name
    ```

    Load from Google Sheets using credential file example:
    ```python
    catalog = LMRequestProcessorCatalog.from_gsheets(
        sheet_id="...",
        worksheet_id="...",
        credential_file_path="...",
    )

    lm_request_processor = catalog.name
    ```

    Load from CSV example:
    ```python
    catalog = LMRequestProcessorCatalog.from_csv(csv_path="...")

    lm_request_processor = catalog.name
    ```

    Template Example:
    For an example of how a Google Sheets file can be formatted to be loaded using LMRequestProcessorCatalog, see:
    https://docs.google.com/spreadsheets/d/1uZLBGS1LaHzFxa8sEmtg5hX5YtjON3G5TPe9fgAruks/edit?usp=drive_link

    For an example of how a CSV file can be formatted to be loaded using LMRequestProcessorCatalog, see:
    https://drive.google.com/file/d/1IkbUPawMSwwTZyAryCUy94INHbxgJSEG/view?usp=drive_link

    Template explanation:
    1. Must include the following columns:
        - name
        - prompt_builder_type
        - prompt_builder_kwargs
        - prompt_builder_system_template
        - prompt_builder_user_template
        - lm_invoker_type
        - lm_invoker_kwargs
        - lm_invoker_env_kwargs
        - output_parser_type
        - output_parser_kwargs
    2. The `prompt_builder_type` column must be filled with one of the following prompt builder types:
        - prompt_builder
        - agnostic
        - hugging_face
        - llama
        - mistral
        - openai
        - multimodal
       In v0.5.0, this column will be removed, as only the `PromptBuilder` class will be supported.
    3. The `prompt_builder_kwargs` column can optionally be filled with a dictionary of keyword arguments to be passed
       to the prompt builder in the format of a valid JSON string.
    4. At least one of the `prompt_builder_system_template` and `prompt_builder_user_template` columns must be filled.
    5. The `lm_invoker_type` column must be filled with one of the following LM invoker types:
        - anthropic
        - anthropic_multimodal
        - azure_openai
        - google_generativeai
        - google_generativeai_multimodal
        - langchain
        - openai
        - openai_compatible
        - openai_multimodal
        - tgi
    6. The `lm_invoker_kwargs` column can optionally be filled with a dictionary of keyword arguments to be passed
       to the LM invoker in the format of a valid JSON string:
        - The keys must be the LM invoker\'s parameters names.
        - The values must be the values to be passed to the corresponding LM invoker\'s parameters.
    7. The `lm_invoker_env_kwargs` column can optionally be filled with a dictionary of keyword arguments to be passed
       to the LM invoker in the format of a valid JSON string:
        - The keys must be the LM invoker\'s parameters names.
        - The values must be the keys of the environment variables whose values will be passed to the corresponding
          LM invoker\'s parameters.
    8. The `output_parser_type` column must be filled with one of the following output parser types:
        - none
        - json
    9. The `output_parser_kwargs` column can optionally be filled with a dictionary of keyword arguments to be passed
       to the output parser in the format of a valid JSON string.
    '''
