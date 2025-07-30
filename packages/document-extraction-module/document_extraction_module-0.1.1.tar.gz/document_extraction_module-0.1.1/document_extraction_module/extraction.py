# from openai import AsyncOpenAI
import argparse
from openai import AsyncOpenAI
import json
import asyncio
from aiolimiter import AsyncLimiter
from pydantic import BaseModel
from typing import Type
from .prompt_processing import generate_prompt_template, generate_prompt_from_schema, PromptSchema
from .extraction_class_type import ExtractionClass, AIAgentClass, ExtractionClassTelangana,AIAgentClassTelangana
from .file_process import base_64_conversation
from .landing_ai_parse import landing_ai_vision_parser, retrieve_page_wise_parse
from .config import (
    MAX_RETRY,
    OPENAI_API_KEY,
    OPEN_AI_EXTRACTION_MODEL,
    OPEN_AI_PARSE_FORMATING_MODEL,
    ASYNC_OPENAI_RATE_LIMIT,
    ASYNC_OPEN_AI_TIME_PERIOD,
    ASYNC_CONCURRENCY_LIMIT
)


client = AsyncOpenAI(api_key=OPENAI_API_KEY)
rate_limiter = AsyncLimiter(max_rate=ASYNC_OPENAI_RATE_LIMIT, time_period=ASYNC_OPEN_AI_TIME_PERIOD)


async def limited_task(sem: asyncio.Semaphore, coro):
    """
    Wraps a coroutine with a semaphore to limit concurrent execution.

    Args:
        sem (asyncio.Semaphore): The semaphore controlling concurrency.
        coro (Coroutine): The coroutine to run.

    Returns:
        Any: The result of the coroutine.
    """
    async with sem:
        return await coro
    

async def extract_fields_async(input_type: str = "PDF", 
                               base_64: list = [], 
                               text_input: list = [], 
                               page_number: int = 0,
                               prompt: str = "",
                               extraction_schema_class: Type[BaseModel]=BaseModel) -> dict:
    """
    Asynchronously extracts structured fields from a document input (PDF, image, or plain text)
    using a prompt-based schema-driven extraction pipeline.

    Args:
        input_type (str): The type of input provided. Must be one of `"PDF"`, `"IMAGE"`, or `"TEXT"`.
        base_64 (list): List of Base64-encoded string of the input image or PDF page (used if input_type is "PDF" or "IMAGE").
        text_input (list): List of Raw text input (used if input_type is "TEXT").
        page_number (int): Page number associated with the input, used for tracking multi-page documents.
        prompt_schema (PromptSchema, optional): A schema defining the structure of the prompt to be used for extraction.

    Returns:
        dict: A dictionary containing the parsed and extracted fields from the input, along with the page number.

    Raises:
        ValueError: If `input_type` is not one of `"PDF"`, `"IMAGE"`, or `"TEXT"`.

    Note:
        - The function uses a rate limiter to control the number of requests sent to the OpenAI API.
        - The function is designed to be used in an asynchronous context (e.g., within an `async` function).
        - The `ExtractionClass`, `AIAgentClass`, and `OutputExampleClass` are expected to be defined in the module.
        - Currently we take one image and one PDF document at a time 
        - base_64 and page_numberare list parameters, they are expected to be single item if we do not want to extract multiple pages at once.

    Example:
        ```python
        result = await extract_fields_async(
            input_type="TEXT",
            text_input="Property Description: Survey No. 123...",
            page_number=1
        )
        print(result)
        ```
    """
    if input_type in ["PDF", "IMAGE"]:
        # Convert PDF to base64 images
        content = [
            { "type": "input_text", "text": prompt},
            { "type": "input_text", "text": f"PAGE NUMBER of the PDF: {page_number}"},
        ]

        for image in base_64:
            content.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{image}",
            })

    elif input_type == "TEXT":
        # Encode text input to base64
        content = [
            { "type": "input_text", "text": prompt},
            { "type": "input_text", "text": f"PAGE NUMBER of the PDF: {page_number}"},
        ]

        for text in text_input:
            content.append({
                "type": "input_text",
                "text": text,
            })

    else:
        raise ValueError("Unsupported file type. Use 'PDF' or 'IMAGE'.")
    

    for retry in range(MAX_RETRY):
        async with rate_limiter:
            try:
                response = await client.responses.create(
                    model=OPEN_AI_EXTRACTION_MODEL,
                    input=[
                        {
                            "role": "system",
                            "content": [
                                { "type": "input_text", "text": f"\n\n Extract the all fields from the input and return only valid JSON (no explanations or extra text):\n\n"}
                            ]
                        },
                        {
                            "role": "user",
                            "content": content
                        }
                    ],
                    temperature=0.1,       
                )
                break
            except:
                if retry < MAX_RETRY-1:
                    continue
                # latest changes
                else:
                    parsed_content = {"page": page_number}
                    return parsed_content

    parsed_content = await parse_response_content(response.output_text, extraction_schema_class)
    parsed_content["page"] = page_number

    print(f"Parsed content for page {page_number}")
    return parsed_content


async def parse_response_content(response_content: str, extraction_schema_class: Type[BaseModel]) -> dict:
    """
    Attempts to parse the response content into a valid JSON structure. If initial parsing fails,
    it sends the content to a language model for correction into a structured format using the 
    `ExtractionClass` schema.

    Args:
        response_content (str): The raw string content returned from the initial extraction response,
            expected to be a JSON string or close to valid JSON.

    Returns:
        dict: A dictionary representation of the parsed content. If parsing via the model is successful, 
            the corrected and validated structure is returned. Returns an empty dictionary on failure.

    Raises:
        None

    Example:
        ```python
        # If ExtractionClass is of type `{"name": "John", "age": 30}`
        parsed = await parse_response_content('{"name": "John", "age": 30}')
        print(parsed)  # {'name': 'John', 'age': 30}
        ```
    """
    try:
        return json.loads(response_content)
    except json.JSONDecodeError:
        # Try to extract a JSON snippet from the response
        async with rate_limiter:
            for retry in range(MAX_RETRY):
                try:
                    response = await client.responses.parse(
                        model=OPEN_AI_PARSE_FORMATING_MODEL,
                        input=[
                            {
                                "role": "system",
                                "content": "You are an expert at structured data JSON creation. You will be given a text with almost like a JSON strucuture in text format from an extraction solution and your job would be to convert it to Valid JSON strcture provided below.",
                            },
                            {"role": "user", "content": f"{response_content}"},
                        ],
                        text_format=extraction_schema_class,
                        temperature=0.1,
                    )
                    break
                except:
                    if retry < MAX_RETRY-1:
                        continue
                    else:
                        return response


        if response and isinstance(response, extraction_schema_class):
            return response
        else:
            return {}


async def extract_multiple_pages_async(input_type: str="", 
                                       file_name: str="", 
                                       base64_images: list=[], 
                                       text_inputs: list=[], 
                                       combine_pages: bool=False,
                                       prompt: str = "",
                                       extraction_schema_class: Type[BaseModel] = BaseModel) -> dict:
    """
    Asynchronously extracts structured data from multiple pages of input, which can be PDF, 
    raw image, or plain text. The function supports parallel extraction of multiple pages and 
    aggregates the results into a final response.

    Args:
        input_type (str): The type of input provided. Must be one of `"PDF"`, `"IMAGE"`, or `"TEXT"`.
        base64_images (list): A list of base64-encoded image strings, one per page. Required if 
            `input_type` is `"PDF"` or `"IMAGE"`.
        text_inputs (list): List of plain text strings used when `input_type` is `"TEXT"`.
        combine_pages (bool): Currently unused. If set to `True`, it can be used to combine all 
            base64 images into one document and extract at once. Default is `False`.

    Returns:
        dict: A dictionary with a `"response"` key containing a list of extracted data for each page.
              Each element in the list corresponds to one page of input and includes the parsed content.

    Raises:
        ValueError: If `input_type` is not one of `"PDF"`, `"IMAGE"`, or `"TEXT"`.

    Example:
        ```python
        response = await extract_multiple_pages_async(
            input_type="PDF",
            base64_images=["<base64_str_page1>", "<base64_str_page2>"]
        )
        print(response["response"][0])  # Parsed result from page 1
        ```
    """
    sem = asyncio.Semaphore(ASYNC_CONCURRENCY_LIMIT)

    final_response = {"response": [], "file_name": file_name}
    
    tasks = []

    if combine_pages:
        if input_type in ["PDF", "IMAGE"]:
            tasks.append(limited_task(sem, extract_fields_async(input_type=input_type, base_64=base64_images, page_number=0, prompt=prompt, extraction_schema_class=extraction_schema_class)))
        elif input_type == "TEXT":
            tasks.append(limited_task(sem, extract_fields_async(input_type=input_type, text_input=text_inputs, page_number=0, prompt=prompt, extraction_schema_class=extraction_schema_class)))
        else:
            raise ValueError("Unsupported file type. Use 'PDF', 'IMAGE', or 'TEXT'.")
    else:
        if input_type in ["PDF", "IMAGE"]:
            for idx, base64_image in enumerate(base64_images):
                tasks.append(limited_task(sem, extract_fields_async(input_type=input_type, base_64=[base64_image], page_number=idx, prompt=prompt, extraction_schema_class=extraction_schema_class)))
        elif input_type == "TEXT":
            for idx, text in enumerate(text_inputs):
                tasks.append(limited_task(sem, extract_fields_async(input_type=input_type, text_input=[text], page_number=idx, prompt=prompt, extraction_schema_class=extraction_schema_class)))
        else:
            raise ValueError("Unsupported file type. Use 'PDF', 'IMAGE', or 'TEXT'.")
    
    results = await asyncio.gather(*tasks)

    for result in results:
        final_response["response"].append(result)

    return final_response    
    

async def extract_multiple_pdfs(input_paths: list[str], 
                                output_paths: list[str], 
                                parser: bool = False, 
                                save_parse: bool = False, 
                                parsing_json_dir_path: str = "", 
                                combine_pages: bool = False,
                                prompt: str = "",
                                extraction_schema_class: Type[BaseModel] = BaseModel) -> list[dict]:
    """
    Asynchronously extracts structured data from multiple PDF documents using either direct
    image-based extraction or a pre-parsing text method. This function limits the number of
    concurrently processed PDFs to avoid overloading the system or hitting API rate limits.

    Args:
        input_paths (list[str]): List of file paths to the input PDF documents.
        output_paths (list[str]): List of file paths where the output JSON results should be saved.
        parser (bool, optional): If True, uses a parsing model to extract structured text before field extraction.
        save_parse (bool, optional): If True and parser is enabled, saves parsed results to disk.
        parsing_json_dir_path (str, optional): Directory path where parsed results will be saved if `save_parse` is True.

    Returns:
        list[dict]: A list of dictionaries, each representing the extracted results for a PDF.

    Raises:
        ValueError: If the lengths of `input_paths` and `output_paths` do not match.

    Example:
        ```python
        results = await extract_multiple_pdfs(
            input_paths=["/path/to/doc1.pdf", "/path/to/doc2.pdf"],
            output_paths=["/path/to/output1.json", "/path/to/output2.json"]
        )
        print(results[0])  # Structured data extracted from the first PDF
        ```
    """
    sem = asyncio.Semaphore(ASYNC_CONCURRENCY_LIMIT)

    tasks = []

    if parser:
        parsed_responses = await landing_ai_vision_parser(document_path_or_url=input_paths, save_parse=save_parse, result_save_dir=parsing_json_dir_path)
        
        for pdf, pdf_path in zip(parsed_responses, input_paths):
            page_level_text = retrieve_page_wise_parse(parsed_result=pdf)

            pdf_name = pdf_path.split("/")[-1]
            tasks.append(limited_task(sem, extract_multiple_pages_async(input_type="TEXT", file_name=pdf_name, text_inputs=page_level_text, combine_pages=combine_pages, prompt=prompt, extraction_schema_class=extraction_schema_class)))
    else:
        for pdf_path in input_paths:
            base64_images = base_64_conversation(input_type="PDF", file_path=pdf_path)

            pdf_name = pdf_path.split("/")[-1]
            tasks.append(limited_task(sem, extract_multiple_pages_async(input_type="PDF", file_name=pdf_name, base64_images=base64_images, combine_pages=combine_pages, prompt=prompt, extraction_schema_class=extraction_schema_class)))
    
    multi_pdf_extraction_result = await asyncio.gather(*tasks)
    
    for pdf_extraction, output_path in zip(multi_pdf_extraction_result, output_paths):
        with open(output_path, "w") as f:
            json.dump(pdf_extraction, f, indent=2)

    return multi_pdf_extraction_result


if __name__ == "__main__":    
    async def main():
        import os
        parser = argparse.ArgumentParser(description="Batch process PDFs and save results.")
        parser.add_argument("--pdf_folder", required=True, help="Path to the folder containing PDF files")
        parser.add_argument("--output_folder", required=True, help="Path to the folder to store output files")
        args = parser.parse_args()
        # Collect all PDF files using os.listdir
        document_paths = []
        output_paths = []

        for filename in sorted(os.listdir(args.pdf_folder)):
            if filename.lower().endswith(".pdf"):
                full_path = os.path.join(args.pdf_folder, filename)
                document_paths.append(full_path)

                output_filename = f"{os.path.splitext(filename)[0]}_telangana.json"
                output_path = os.path.join(args.output_folder, output_filename)
                output_paths.append(output_path)




        # document_paths = ["/home/murari/Desktop/ec-doc-title-check/telangana-extra/152.pdf"]
        # output_paths = ["/home/murari/Desktop/ec-doc-title-check/152_telangana.json"]

        extraction_template = generate_prompt_template(ExtractionClassTelangana)
        ai_agent_template = generate_prompt_template(AIAgentClassTelangana)
        # output_example_template = generate_prompt_template(OutputExampleClass)

        schema = PromptSchema(
            ai_agent_information=ai_agent_template,
            extract_fields=extraction_template,
            # output_example=output_example_template,
        )

        prompt = generate_prompt_from_schema(schema.model_dump())
        
        multi_pdf_extraction_result = await extract_multiple_pdfs(input_paths=document_paths, output_paths=output_paths, parser=False, combine_pages=False, prompt=prompt,extraction_schema_class=ExtractionClassTelangana)

        print(len(multi_pdf_extraction_result))  
        print(len(multi_pdf_extraction_result[0]))
    asyncio.run(main())
    