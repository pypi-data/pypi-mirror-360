import asyncio
import datetime
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import timezone

import numpy as np
import pandas as pd
import requests
from fuzzywuzzy import fuzz
from nltk.corpus import stopwords
from rapidfuzz import process
from vertexai.preview.language_models import TextEmbeddingModel

from src.constants import formatting_rules
from src.io import get_storage_client, logger
from src.prompts.prompt_library import prompt_library
from src.tms import call_tms, set_tms_service_token

tms_domain = os.environ["TMS_DOMAIN"]


class EmbeddingsManager:  # noqa: D101
    def __init__(self, params):  # noqa: D107
        self.params = params
        self.embeddings_dict = {}
        self.embed_model = setup_embed_model()
        self.bucket = self.get_bucket_storage()
        self.embedding_folder = self.embed_model._model_id
        self.embedding_dimension = 768  # TODO: to be reduced

    def get_bucket_storage(self):
        """
        Retrieve the bucket storage object.

        Returns:
            The bucket storage object.
        """
        params = self.params
        storage_client = get_storage_client(params)
        bucket = storage_client.bucket(params["doc_ai_bucket_name"])
        return bucket

    def _find_most_similar_option(self, input_string, option_ids, option_embeddings):
        """
        Find the most similar option to the given input string based on embeddings.

        Args:
            model: The model used for generating embeddings.
            input_string (str): The input string to find the most similar option for.
            option_ids (list): The list of option IDs.
            option_embeddings (np.ndarray): The embeddings of the options.

        Returns:
            The ID of the most similar option.
        """
        try:
            input_embedding = self.embed_model.get_embeddings(
                [input_string], output_dimensionality=self.embedding_dimension
            )[0].values
            similarities = np.dot(option_embeddings, input_embedding)
            idx = np.argmax(similarities)
            return option_ids[idx]
        except Exception as e:
            logger.error(f"Embeddings error: {e}")
            return None

    def load_embeddings(self):
        """
        Load embeddings for container types, ports, and terminals.

        Returns:
            None
        """
        for data_field in [
            "container_types",
            "ports",
            "terminals",
            "depots",
            "item_codes_label",
        ]:
            self.embeddings_dict[data_field] = load_embed_by_data_field(
                self.bucket,
                f"{self.embedding_folder}/{data_field}/output",
                self.embedding_dimension,
            )

    async def update_embeddings(self):
        """
        Update the embeddings dictionary.

        Returns:
            dict: The updated embeddings dictionary with the following keys:
                - "container_types": A tuple containing the container types and their embeddings.
                - "ports": A tuple containing the ports and their embeddings.
                - "terminals": A tuple containing the terminal IDs and their embeddings.
        """
        # Update embeddings dict here.
        # Ensure this method is async if you're calling async operations.
        set_tms_service_token()
        (
            container_types,
            container_type_embeddings,
        ) = self.setup_container_type_embeddings(
            *self.embeddings_dict.get("container_types", ([], []))
        )

        ports, port_embeddings = self.setup_ports_embeddings(
            *self.embeddings_dict.get("ports", ([], []))
        )

        # Setup terminal embeddings
        # Since retrieving terminal attributes requires calling TMS' api to extract terminals by each port,
        # we only do it for new ports.
        prev_port_ids, _ = self.embeddings_dict.get("ports", ([], []))
        added_port_ids = [port for port in ports if port not in prev_port_ids]
        if added_port_ids:
            terminal_ids, terminal_embeddings = self.setup_terminal_embeddings(
                added_port_ids
            )
        else:
            terminal_ids, terminal_embeddings = self.embeddings_dict["terminals"]

        depot_names, depot_embeddings = self.setup_depot_embeddings(
            *self.embeddings_dict.get("depots", ([], []))
        )

        item_code_names, item_code_embeddings = self.setup_item_code_embeddings(
            *self.embeddings_dict.get("item_codes_label", ([], []))
        )

        self.embeddings_dict = {
            "container_types": (container_types, container_type_embeddings),
            "ports": (ports, port_embeddings),
            "terminals": (terminal_ids, terminal_embeddings),
            "depots": (depot_names, depot_embeddings),
            "item_codes_label": (item_code_names, item_code_embeddings),
        }
        return self.embeddings_dict

    def batch_embed(self, option_strings: list[dict], suffix: str):
        """
        Compute embeddings for a batch of option strings and uploads them to a cloud storage bucket.

        Args:
            option_strings (list): A list of option strings to compute embeddings for.
            suffix (str): A suffix to be used in the storage path for the embeddings:
            input & output will be stored under "{bucket}/{parent_folder}/{suffix}/"

        Returns:
            tuple: A tuple containing the option IDs and embeddings.
        """
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        input_path = f"{self.embedding_folder}/{suffix}/input/{now}.jsonl"
        blob = self.bucket.blob(input_path)

        # Convert each dictionary to a JSON string and join them with newlines
        option_strings = [
            {**option, "task_type": "SEMANTIC_SIMILARITY", "output_dimensionality": 256}
            for option in option_strings
        ]
        jsonl_string = "\n".join(json.dumps(d) for d in option_strings)

        # Convert the combined string to bytes
        jsonl_bytes = jsonl_string.encode("utf-8")

        # Upload the bytes to the blob
        blob.upload_from_string(jsonl_bytes, content_type="text/plain")

        # Compute embeddings for the options
        embedding_path = f"{self.embedding_folder}/{suffix}/output"
        assert len(option_strings) <= 30000  # Limit for batch embedding
        batch_resp = self.embed_model.batch_predict(
            dataset=f"gs://{self.bucket.name}/{input_path}",  # noqa
            destination_uri_prefix=f"gs://{self.bucket.name}/{embedding_path}",  # noqa
        )

        if batch_resp.state.name != "JOB_STATE_SUCCEEDED":
            logger.warning(
                f"Batch prediction job failed with state {batch_resp.state.name}"
            )
        else:
            logger.info(f"Embeddings for {suffix} computed successfully.")

        option_ids, option_embeddings = load_embed_by_data_field(
            self.bucket, embedding_path, self.embedding_dimension
        )
        return option_ids, option_embeddings

    def setup_container_type_embeddings(
        self, computed_container_type_ids, computed_container_type_embeddings
    ):
        """
        Set up container type embeddings.

        Args:
            computed_container_type_ids (list): The list of already computed container type IDs.
            computed_container_type_embeddings (list): The list of already computed container type embeddings.

        Returns:
            tuple: A tuple containing the updated container type IDs and embeddings.
        """
        url = (
            f"https://tms.forto.{tms_domain}/api/transport-units/api/types/list"  # noqa
        )
        resp = call_tms(requests.get, url)
        container_types = resp.json()

        container_attribute_strings = [
            dict(
                title=container_type["code"],
                content=" | ".join(
                    [container_type["code"]]
                    + [
                        f"{v}"
                        for k, v in container_type["containerAttributes"].items()
                        if k in ["isoSizeType", "isoTypeGroup", "containerCategory"]
                    ]
                    + [container_type.get(k, "") for k in ["displayName", "notes"]]
                ),
            )
            for container_type in container_types
            if container_type["type"] == "Container"
            and container_type["code"] not in computed_container_type_ids
            and container_type.get("containerAttributes") is not None
        ]
        if not container_attribute_strings:
            logger.info("No new container types found.")
            return computed_container_type_ids, computed_container_type_embeddings

        logger.info("Computing embeddings for container types...")
        container_type_ids, container_type_embeddings = self.batch_embed(
            container_attribute_strings, "container_types"
        )
        return container_type_ids, container_type_embeddings

    def setup_ports_embeddings(self, computed_port_ids, computed_port_embeddings):
        """
        Set up port embeddings.

        Steps:
        - Retrieve active ports from the TMS API
        - Compute embeddings for new tradelane-enabled ports
        - Return ALL port IDs and embeddings.

        Args:
            computed_port_ids (list): The list of previously computed port IDs.
            computed_port_embeddings (list): The list of previously computed port embeddings.

        Returns:
            tuple: A tuple containing ALL port IDs and embeddings.
        """
        url = f"https://tms.forto.{tms_domain}/api/transport-network/api/ports?pageSize=1000000&status=active"  # noqa
        resp = call_tms(requests.get, url)
        resp_json = resp.json()
        if len(resp_json["data"]) != resp_json["_paging"]["totalRecords"]:
            logger.error("Not all ports were returned.")

        new_sea_ports = [
            port
            for port in resp_json["data"]
            if "sea" in port["modes"] and port["id"] not in computed_port_ids
        ]
        if not new_sea_ports:
            logger.info("No new ports found.")
            return computed_port_ids, computed_port_embeddings

        port_attribute_strings = [
            dict(
                title=port["id"],
                content=" ".join(
                    [
                        "port for shipping",
                        add_text_without_space(
                            port["name"]
                        ),  # for cases like QUINHON - Quinhon
                        port["id"],
                    ]
                ),
            )
            for port in new_sea_ports
        ]

        logger.info("Computing embeddings for ports.")
        port_ids, port_embeddings = self.batch_embed(port_attribute_strings, "ports")
        return port_ids, port_embeddings

    def setup_depot_embeddings(self, computed_depot_names, computed_depot_embeddings):
        """
        Set up depot embeddings.

        Steps:
        - Retrieve active depot from the TMS API
        - Compute embeddings for new tdepot
        - Return ALL depot names and embeddings.

        Args:
            computed_depot_names (list): The list of previously computed depot names.
            computed_depot_embeddings (list): The list of previously computed depot embeddings.

        Returns:
            tuple: A tuple containing ALL depot names and embeddings.
        """
        url = f"https://tms.forto.{tms_domain}/api/transport-network/api/depots?pageSize=1000000"  # noqa
        resp = call_tms(requests.get, url)
        resp_json = resp.json()

        new_depots = [
            depot
            for depot in resp_json["data"]
            if depot["name"] not in computed_depot_names
        ]
        if not new_depots:
            logger.info("No new depots found.")
            return computed_depot_names, computed_depot_embeddings

        depot_attribute_strings = [
            dict(
                title=depot["name"],
                content=" | ".join(
                    [
                        "depot",
                        "name - " + depot["name"],
                        "address - " + depot["address"]["fullAddress"],
                    ]
                ),
            )
            for depot in resp_json["data"]
        ]

        logger.info("Computing embeddings for depots.")
        depot_names, depot_embeddings = self.batch_embed(
            depot_attribute_strings, "depots"
        )
        return depot_names, depot_embeddings

    def setup_terminal_embeddings(self, added_port_ids):
        """
        Set up terminal embeddings for `added_port_ids`, using `model`, uploaded to `bucket`.

        Args:
            added_port_ids (list): A list of added port IDs.

        Returns:
            tuple: A tuple containing the ALL terminal IDs and terminal embeddings.
            Not just for the added port IDs.
        """
        terminal_attibute_strings = [
            setup_terminal_attributes(port_id) for port_id in added_port_ids
        ]
        terminal_attibute_strings = sum(terminal_attibute_strings, [])
        if not terminal_attibute_strings:
            logger.info("No new terminals found.")
            return [], np.array([])

        terminal_ids, terminal_embeddings = self.batch_embed(
            terminal_attibute_strings, "terminals"
        )
        return terminal_ids, terminal_embeddings

    def setup_item_code_embeddings(
        self, computed_item_code_names, computed_item_code_embeddings
    ):
        """
        Set up item_code embeddings.

        Steps:
        - Retrieve active item_code from the TMS API
        - Compute embeddings for new titem_code
        - Return ALL item_code names and embeddings.

        Args:
            computed_item_code_names (list): The list of previously computed item_code names.
            computed_item_code_embeddings (list): The list of previously computed item_code embeddings.

        Returns:
            tuple: A tuple containing ALL item_code names and embeddings.
        """
        url = f"https://tms.forto.{tms_domain}/api/catalog/item-codes?transportTypes=fcl&pageSize=1000000"  # noqa
        resp = call_tms(requests.get, url)
        resp_json = resp.json()

        new_item_codes = [
            item_code
            for item_code in resp_json["results"]
            if item_code["id"] not in computed_item_code_names
        ]
        if not new_item_codes:
            logger.info("No new item_codes found.")
            return computed_item_code_names, computed_item_code_embeddings

        item_code_attribute_strings = [
            dict(
                title=item_code["id"],
                content=" | ".join(
                    [
                        item_code["id"],
                        item_code["label"],
                    ]
                ),
            )
            for item_code in resp_json["results"]
        ]

        logger.info("Computing embeddings for item_codes.")
        item_code_names, item_code_embeddings = self.batch_embed(
            item_code_attribute_strings, "item_codes_label"
        )
        return item_code_names, item_code_embeddings


def setup_embed_model():
    """
    Set up and return a text embedding model.

    Returns:
        TextEmbeddingModel: The initialized text embedding model.
    """
    model = TextEmbeddingModel.from_pretrained("text-multilingual-embedding-002")
    return model


def convert_container_number(container_number):
    """
    Convert a container number to ISO standard.

    Args:
        container_number (str): The container number to be converted.

    Returns:
        str: The formatted container number if it is valid, None otherwise.
    """
    if not container_number:
        return
    # 'FFAU2932130--FX34650895-40HC' -> 'FFAU2932130'
    match = re.findall(r"[A-Z]{4}\d{7}", container_number)
    stripped_value = match[0] if match else None

    if not stripped_value:
        stripped_value = "".join(
            filter(lambda char: str.isalnum(char) or char == "/", container_number)
        )

    # This is to catch container number that has the format like: ABCD1234567/40DC or ABCD1234567/SEAL1234567
    formatted_value = stripped_value.split("/")[0]
    if len(formatted_value) != 11:
        return
    # Check if the format is according to the ISO standard
    if not formatted_value[:4].isalpha() or not formatted_value[4:].isdigit():
        return
    return formatted_value


# Clean the date for date obj parse in tms formatting
def clean_date_string(date_str):
    """Remove hours and timezone information from the date string."""
    date_str = date_str.strip()
    if "hrs" in date_str:
        return date_str.replace("hrs", "")
    if "(CET)" in date_str:
        return date_str.replace("(CET)", "")
    return date_str


def extract_date(date_str):
    """
    Extract date from string using european format (day first).

    Check if starts with year, then YYYY-MM-DD, else DD-MM-YYYY
    """
    if all([c.isnumeric() for c in date_str[:4]]):
        dt_obj = pd.to_datetime(date_str, dayfirst=False).to_pydatetime()
    else:
        dt_obj = pd.to_datetime(date_str, dayfirst=True).to_pydatetime()
    return dt_obj


def extract_number(data_field_value):
    """
    Remove everything not a digit and not in [, .].

    Args:
        data_field_value: string

    Returns:
        formatted_value: string

    """
    formatted_value = ""
    for c in data_field_value:
        if c.isnumeric() or c in [",", "."]:
            formatted_value += c

    # First and last characters should not be  [",", "."]
    formatted_value = formatted_value.strip(",.")

    return formatted_value if formatted_value not in ["''", ""] else None


def extract_string(data_field_value):
    """Remove numeric characters from the string.

    Args:
        data_field_value: string

    Returns:
        formatted_value: string

    """
    if not isinstance(data_field_value, str):
        return None

    excluded_chars = [".", ",", ")", "(", " ", "[", "]"]
    formatted_value = "".join(
        c for c in data_field_value if not c.isdigit() and c not in excluded_chars
    )

    return formatted_value if formatted_value not in ["''", ""] else None


def extract_google_embed_resp(prediction_string, embedding_dimension):
    """
    Extract relevant information from the Google Embed API response.

    Args:
        prediction_string (str): The prediction string returned by the Google Embed API.

    Returns:
        dict: A dictionary containing the extracted information.
            - _id (str): The title of the instance.
            - attr_text (str): The content of the instance.
            - embedding (list): The embeddings values from the predictions.

    """
    res = json.loads(prediction_string)
    return dict(
        _id=res["instance"]["title"],
        attr_text=res["instance"]["content"],
        embedding=res["predictions"][0]["embeddings"]["values"][:embedding_dimension],
    )


def load_embed_by_data_field(bucket, embedding_path, embedding_dimension):
    """
    Load embeddings by data field from the specified bucket and embedding path.

    Args:
        bucket (Bucket): The bucket object representing the storage bucket.
        embedding_path (str): The path to the embeddings in the bucket (different by data_field).

    Returns:
        tuple: A tuple containing the option IDs and option embeddings.
            - option_ids (list): A list of option IDs.
            - option_embeddings (ndarray): An array of option embeddings.
    """
    # Retrieve the embeddings from the output files
    blobs = bucket.list_blobs(prefix=embedding_path)
    all_blob_data = []
    for blob in blobs:
        blob_data = blob.download_as_bytes().decode("utf-8").splitlines()
        embeddings = [
            extract_google_embed_resp(data, embedding_dimension) for data in blob_data
        ]
        all_blob_data.extend(embeddings)
    option_ids = [embed["_id"] for embed in all_blob_data]
    option_embeddings = np.stack([embed["embedding"] for embed in all_blob_data])
    return option_ids, option_embeddings


def setup_terminal_attributes(port_id: str):
    """
    Retrieve and format the attributes of active terminals at a given port.

    Args:
        port_id (str): The ID of the port.

    Returns:
        list: A list of dictionaries containing the formatted attributes of active terminals.
              Each dictionary has the following keys:
              - title: The terminal's short code.
              - content: A string representation of the terminal's attributes, including its name,
                         searchable name, and full address.
    """
    url = f"https://gateway.forto.{tms_domain}/api/transport-network/api/ports/{port_id}/terminals/list"  # noqa
    resp = call_tms(requests.get, url)
    terminals = resp.json()
    if len(terminals) == 0:
        return []
    active_terminals = [term for term in terminals if term["isActive"]]
    if len(active_terminals) == 0:
        logger.warning(f"No active terminals found at port {port_id}.")
        return []

    terminal_attibute_strings = [
        dict(
            title=term["name"],
            content=" | ".join(
                [
                    "shipping terminal",
                    "code - " + term["terminalShortCode"],
                    "name - " + modify_terminal_name(term["searchableName"]),
                    "country - " + term["address"]["country"],
                ]
            ),
        )
        for term in active_terminals
    ]
    return terminal_attibute_strings


def modify_terminal_name(text):
    # Find the first occurrence of a word starting with 'K' followed by a number
    # and replace it with 'KAAI' - meaning Quay in Dutch
    match = re.search(r"K(\d+)", text)
    if match:
        # Append "KAAI" followed by the number if a match is found
        text += f" KAAI {match.group(1)}"
    return text


def remove_none_values(d):
    if isinstance(d, dict):
        # Create a new dictionary to store non-None values
        cleaned_dict = {}
        for key, value in d.items():
            cleaned_value = remove_none_values(value)
            if cleaned_value is not None:  # Only add non-None values
                cleaned_dict[key] = cleaned_value
        return cleaned_dict if cleaned_dict else None

    elif isinstance(d, list):
        # Create a new list to store non-None values
        cleaned_list = []
        for item in d:
            cleaned_item = remove_none_values(item)
            if cleaned_item is not None:  # Only add non-None values
                cleaned_list.append(cleaned_item)
        return cleaned_list if cleaned_list else None

    else:
        # Return the value if it's not a dictionary or list
        return d if d is not None else None


def check_formatting_rule(entity_key, document_type_code, rule):
    if (
        document_type_code in formatting_rules.keys()
        and entity_key in formatting_rules[document_type_code].keys()
        and formatting_rules[document_type_code][entity_key] == rule
    ):
        return True
    return False


def convert_invoice_type(data_field_value, params):
    """
    Converts a raw invoice type string to either invoice or creditNote using fuzzy matching.

    Args:
        data_field_value (str): The raw invoice type string from the data.
        params (dict): A dictionary of parameters, including:
            - "lookup_data": A dictionary containing lookup tables.
            - "fuzzy_threshold_invoice_classification": The minimum fuzzy matching score.

    Returns:
        str or None: The standardized invoice type if a match is found, otherwise None.
    """
    lookup_data = params["lookup_data"]["invoice_classification"]
    keywords = list(lookup_data.keys())

    best_match = process.extractOne(
        data_field_value.lower(),
        keywords,
    )
    if best_match:
        best_match_key, score, _ = best_match
        if score >= params["fuzzy_threshold_invoice_classification"]:
            return lookup_data[best_match_key]
    return None


def validate_reverse_charge_value(reverse_charge_sentence_value):
    """
    Validates the reverseChargeSentence value before assigning to line items.

    Args:
        reverse_charge_sentence_value (bool): The formatted value of reverseChargeSentence (True or False).

    Returns:
        bool: The validated reverseChargeSentence value.
    """
    if isinstance(reverse_charge_sentence_value, bool):
        return reverse_charge_sentence_value
    else:
        logger.warning(
            f"Invalid reverseChargeSentence value: {reverse_charge_sentence_value}. Defaulting to False."
        )
        return False


# Function to create KVP dictionary using apply method
def create_kvp_dictionary(df_raw: pd.DataFrame):
    """Create a key-value pair dictionary from the given DataFrame.

    Args:
        df_raw (pd.DataFrame): The input DataFrame containing 'lineitem' and 'Forto SLI' columns.

    return:
        A key-value pair dictionary with 'Processed Lineitem' as key and 'Forto SLI' as value.
    """
    df = df_raw.copy()
    df["Processed Lineitem"] = df["lineitem"].apply(clean_item_description)
    kvp_dict = df.set_index("Processed Lineitem")["Forto SLI"].to_dict()

    return kvp_dict


def remove_dates(lineitem: str):
    """
    This function removes dates in the format "dd Month yyyy" from the given line item string.

    Args:
    lineitem (str): The input string from which dates will be removed.

    Returns:
    str: The string with dates removed.
    """
    # Remove dates in the format dd.mm.yy or dd.mm.yyyy
    lineitem = re.sub(r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b", "", lineitem)

    # Remove dates in the format "dd Month yyyy"
    lineitem = re.sub(
        r"\b\d{1,2} (?:january|february|march|april|may|june|july|august|september|october|november|december|januar|"
        r"februar|märz|mai|juni|juli|oktober|dezember) \d{4}\b",
        "",
        lineitem,
        flags=re.IGNORECASE,
    )

    # Define a list of month abbreviations in English and German
    month_abbreviations = [
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
        "JAN",
        "FEB",
        "MRZ",
        "APR",
        "MAI",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OKT",
        "NOV",
        "DEZ",
    ]

    # Create a regular expression pattern to match month abbreviations
    pattern = r"\b(?:{})\b".format("|".join(month_abbreviations))

    # Remove month abbreviations
    lineitem = re.sub(pattern, "", lineitem, flags=re.IGNORECASE)

    return lineitem


def remove_unwanted_patterns(lineitem: str):
    """
    This function removes dates, month names, and container numbers from the given line item string.

    Args:
    lineitem (str): The input string from which unwanted patterns will be removed.

    Returns:
    str: The string with dates, month names, and container numbers removed.
    """
    # Remove container numbers (4 letters followed by 7 digits)
    lineitem = re.sub(r"\b[A-Z]{4}\d{7}\b", "", lineitem)

    # Remove "HIGH CUBE"
    lineitem = lineitem.replace("HIGH CUBE", "")

    return lineitem


def clean_item_description(lineitem: str, remove_numbers: bool = True):
    """
    This function removes dates, month names, whitespaces, currency patterns and container numbers from the given line item string.  # noqa

    Args:
    lineitem (str): The input string from which unwanted patterns will be removed.

    Returns:
    str: The cleaned string removed.
    """
    currency_codes_pattern = r"\b(USD|EUR|JPY|GBP|CAD|AUD|CHF|CNY|SEK|NZD|KRW|SGD|INR|BRL|ZAR|RUB|MXN|HKD|NOK|TRY|IDR|MYR|PHP|THB|VND|PLN|CZK|HUF|ILS|AED|SAR|QAR|KWD|EGP|NGN|ARS|CLP|COP|PEN|UYU|VEF|INR|PKR|BDT|LKR|NPR|MMK)\b"  # noqa

    # Remove stopwords
    lineitem = remove_stop_words(lineitem)

    # remove dates
    lineitem = remove_dates(lineitem)

    # remove whitespaces
    lineitem = re.sub(r"\s{2,}", " ", lineitem)

    # remove newlines
    lineitem = re.sub(r"\\n|\n", " ", lineitem)

    # Remove the currency codes
    lineitem = re.sub(currency_codes_pattern, "", lineitem, flags=re.IGNORECASE)

    # Remove numbers from the line item
    if (
        remove_numbers
    ):  # Do not remove numbers for the reverse charge sentence as it contains Article number
        lineitem = re.sub(r"\d+", "", lineitem)

    # remove other patterns
    lineitem = remove_unwanted_patterns(lineitem)

    # remove special chars
    lineitem = re.sub(r"[^A-Za-z0-9\s]", " ", lineitem).strip()

    return re.sub(r"\s{2,}", " ", lineitem).strip()


async def format_label(
    entity_k, entity_value, embed_manager, document_type_code, params
):
    llm_client = params["LlmClient"]
    if isinstance(entity_value, dict):  # if it's a nested entity
        format_tasks = [
            format_label(sub_k, sub_v, embed_manager, document_type_code, params)
            for sub_k, sub_v in entity_value.items()
        ]
        return entity_k, {k: v for k, v in await asyncio.gather(*format_tasks)}
    if isinstance(entity_value, list):
        format_tasks = await asyncio.gather(
            *[
                format_label(entity_k, sub_v, embed_manager, document_type_code, params)
                for sub_v in entity_value
            ]
        )
        return entity_k, [v for _, v in format_tasks]
    entity_key = entity_k.lower()
    embeddings_dict = embed_manager.embeddings_dict
    formatted_value = None

    if entity_key.startswith("port"):
        formatted_value = await get_port_code_ai(
            entity_value, llm_client, embed_manager, *embeddings_dict["ports"]
        )
    elif (entity_key == "containertype") or (entity_key == "containersize"):
        formatted_value = embed_manager._find_most_similar_option(
            "container type " + entity_value,
            *embeddings_dict["container_types"],
        )
    elif check_formatting_rule(entity_k, document_type_code, "terminal"):
        formatted_value = embed_manager._find_most_similar_option(
            "shipping terminal " + str(entity_value),
            *embeddings_dict["terminals"],
        )
    elif check_formatting_rule(entity_k, document_type_code, "depot"):
        formatted_value = embed_manager._find_most_similar_option(
            "depot " + str(entity_value),
            *embeddings_dict["depots"],
        )
    elif entity_key.startswith(("eta", "etd", "duedate", "issuedate", "servicedate")):
        try:
            cleaned_data_field_value = clean_date_string(entity_value)
            dt_obj = extract_date(cleaned_data_field_value)
            formatted_value = str(dt_obj.date())
        except ValueError as e:
            logger.info(f"ParserError: {e}")
    elif "cutoff" in entity_key:
        try:
            cleaned_data_field_value = clean_date_string(entity_value)
            dt_obj = extract_date(cleaned_data_field_value)
            if dt_obj.tzinfo is None:
                dt_obj = dt_obj.replace(tzinfo=timezone.utc)
            else:
                dt_obj = dt_obj.astimezone(timezone.utc)
            formatted_value = dt_obj.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        except ValueError as e:
            logger.info(f"ParserError: {e}")
    elif entity_key == "containernumber":
        # Remove all non-alphanumeric characters like ' ', '-', etc.
        formatted_value = convert_container_number(entity_value)
    elif (
        document_type_code in ["finalMbL", "draftMbl"] and entity_key == "measurements"
    ):
        formatted_value = extract_number(entity_value)
    elif any(
        packaging_type in entity_key
        for packaging_type in ["packagingtype", "packagetype", "currency"]
    ):
        # Remove all numeric characters from the string. For example 23CARTONS -> CARTONS
        formatted_value = extract_string(entity_value)
    elif "lineitemdescription" in entity_key:
        formatted_value = clean_item_description(entity_value)
    elif "documenttype" in entity_key:
        formatted_value = convert_invoice_type(entity_value, params)

    # Handle reverseChargeSentence
    elif "reversechargesentence" in entity_key:
        formatted_value = clean_item_description(entity_value, remove_numbers=False)

    elif any(
        numeric_indicator in entity_key
        for numeric_indicator in [
            "weight",
            "quantity",
            "value",
            "amount",
            "totalamount",
            "totalamounteuro",
            "vatamount",
            "vatApplicableAmount",
            "grandTotal",
        ]
    ):
        formatted_value = extract_number(entity_value)

    result = {
        "documentValue": entity_value,
        "formattedValue": formatted_value,
    }
    return entity_k, result


async def get_port_code_ai(
    port: str, llm_client, embed_manager, port_ids, port_embeddings
):
    port_llm = await get_port_code_llm(port, llm_client)

    if port_llm in port_ids:
        return port_llm
    port_text = f"port for shipping {port}"
    return embed_manager._find_most_similar_option(port_text, port_ids, port_embeddings)


async def get_port_code_llm(port: str, llm_client):
    if (
        "postprocessing" in prompt_library.library.keys()
        and "port_code" in prompt_library.library["postprocessing"].keys()
    ):
        # Get the prompt from the prompt library and prepare the response schema for ChatGPT
        prompt = prompt_library.library["postprocessing"]["port_code"]["prompt"]
        response_schema = {
            "type": "json_schema",
            "json_schema": {
                "name": "port",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "port": {
                            "type": "string",
                            "description": f"Get the port code for the given port: {port}",
                        }
                    },
                    "required": ["port"],
                    "additionalProperties": False,
                },
            },
        }

        response = await llm_client.get_unified_json_genai(
            prompt, response_schema=response_schema, model="chatgpt"
        )
        try:
            mapped_port = response["port"]
            return mapped_port
        except json.JSONDecodeError:
            logger.error(f"Error decoding response: {response}")
            return None


async def format_all_entities(result, embed_manager, document_type_code, params):
    """Format the entity values in the result dictionary."""
    # Remove None values from the dictionary
    result = remove_none_values(result)
    if result is None:
        logger.info("No data was extracted.")
        return {}

    # Format all entities recursively
    _, aggregated_data = await format_label(
        None, result, embed_manager, document_type_code, params
    )

    # Process partner invoice on lineitem mapping and reverse charge sentence
    if document_type_code == "partnerInvoice":
        process_partner_invoice(aggregated_data, embed_manager, params)

    logger.info("Data Extraction completed successfully")
    return aggregated_data


def process_partner_invoice(aggregated_data, embed_manager, params):
    """Process the partner invoice data."""
    line_items = aggregated_data.get("lineItem", [])
    # Add debug logging
    logger.info(f"Processing partnerInvoice with {len(line_items)} line items")

    reverse_charge = None
    reverse_charge_info = aggregated_data.get("reverseChargeSentence")

    # Check if reverseChargeSentence exists and has the expected structure
    if isinstance(reverse_charge_info, dict):
        # Get the reverse charge sentence and Check if the reverse charge sentence is present
        rev_charge_sentence = reverse_charge_info.get("formattedValue", "")
        reverse_charge_value = if_reverse_charge_sentence(rev_charge_sentence, params)

        # Assign the reverse charge value to the aggregated data
        reverse_charge_info["formattedValue"] = reverse_charge_value
        reverse_charge = aggregated_data.pop("reverseChargeSentence", None)

    # Process each line item
    for line_item in line_items:
        if line_item.get("lineItemDescription", None) is not None:
            line_item["itemCode"] = associate_forto_item_code(
                embed_manager,
                line_item["lineItemDescription"]["formattedValue"],
                params,
            )

        if reverse_charge:
            # Distribute reverseChargeSentence to all line items
            line_item["reverseChargeSentence"] = reverse_charge


def if_reverse_charge_sentence(sentence: str, params):
    """Check if the reverse charge sentence is present in the line item."""
    reverse_charge_sentences = params["lookup_data"]["reverse_charge_sentences"]
    threshold = params["fuzzy_threshold_reverse_charge"]

    # Check if ("ARTICLE 144", "ART. 144") in the sentence
    if "ARTICLE 144" in sentence or "ART 144" in sentence:
        return False

    # Check if the sentence is similar to any of the reverse charge sentences
    _, is_reverse_charge = get_fuzzy_match_score(
        sentence, reverse_charge_sentences, threshold
    )

    return is_reverse_charge


def add_text_without_space(text):
    """If the cleaned text is different from the original text, append it.
    Useful for port names like QUINHON - Quinhon"""
    cleaned_text = "".join(text.split())
    if text != cleaned_text:
        text += f" {cleaned_text}"
    return text


def remove_stop_words(lineitem: str):
    """Remove stop words in English and German from the given line item string.

    Args:
    lineitem (str): The input string from which stop words will be removed.

    Returns:
    str: The string with stop words removed.
    """
    stop_words = set(stopwords.words("english") + stopwords.words("german")) - {"off"}
    return (
        " ".join(word for word in lineitem.split() if word.lower() not in stop_words)
        .upper()
        .strip()
    )


def compute_score(args):
    """Compute the fuzzy matching score between a new line item and a key."""
    new_lineitem, key = args
    return key, fuzz.ratio(new_lineitem, key)


def get_fuzzy_match_score(target: str, sentences: list, threshold: int):
    """Get the best fuzzy match for a target string from a list of candidates.

    Args:
        target (str): The string to match.
        sentences (list): List of strings to match against.
        threshold (int): Minimum score threshold to consider a match.

    Returns:
        tuple: (best_match, score) if above threshold, else (None, 0)
    """
    # Use multiprocessing to find the best match
    with ThreadPoolExecutor() as executor:
        results = executor.map(compute_score, [(target, s) for s in sentences])

    # Find the best match and score
    best_match, best_score = max(results, key=lambda x: x[1], default=(None, 0))

    # return best_match, best_score
    # If the best match score is above a threshold (e.g., 80), return it
    if best_score >= threshold:
        return best_match, True

    return None, False


def find_matching_lineitem(new_lineitem: str, kvp_dict: dict, threshold=90):
    """Find the best matching line item from the key-value pair dictionary using fuzzy matching.

    Args:
        new_lineitem (str): The new line item to be matched.
        kvp_dict (dict): The key-value pair dictionary with 'Processed Lineitem' as key and 'Forto SLI' as value.
        threshold (int): Minimum score threshold to consider a match.
    Returns:
        str: The best matching 'Forto SLI' value from the dictionary.
    """
    new_lineitem = new_lineitem.upper()

    # Check if the new line item is already in the dictionary
    if new_lineitem in kvp_dict:
        return kvp_dict[new_lineitem]

    # Get the best fuzzy match score for the extracted line item
    best_match, _ = get_fuzzy_match_score(
        new_lineitem, list(kvp_dict.keys()), threshold
    )

    return kvp_dict.get(best_match, None)


def associate_forto_item_code(embed_manager, input_string, params):
    """
    Finds a match for the input string using fuzzy matching first, then embedding fallback.

    1. Tries to find a fuzzy match for input_string against the keys in
       mapping_data using RapidFuzz, requiring a score >= fuzzy_threshold.
    2. If found, returns the corresponding value from mapping_data.
    3. If not found above threshold, calls the embedding_fallback function.

    Args:
        input_string: The string to find a match for.
        mapping_data: The pre-loaded dictionary (keys used for fuzzy search).
        fuzzy_threshold: Min score (0-100) for a fuzzy match to be accepted.

    Returns:
        The matched value (from fuzzy match or embedding), or None if no match found.
    """
    # Get the Forto item code using fuzzy matching
    forto_item_code = find_matching_lineitem(
        new_lineitem=input_string,
        kvp_dict=params["lookup_data"]["item_code"],  # TODO: Parse the KVP dictionary
        threshold=params["fuzzy_threshold_item_code"],
    )

    if forto_item_code is None:
        # 2. Fallback to embedding function if no good fuzzy match
        embeddings_dict = embed_manager.embeddings_dict
        forto_item_code = embed_manager._find_most_similar_option(
            input_string, *embeddings_dict["item_codes_label"]
        )

    result = {"documentValue": input_string, "formattedValue": forto_item_code}
    return result
