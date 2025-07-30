import json
import time
from typing import Tuple, Optional
import pandas as pd
from tqdm import tqdm


def prepare_data(
        data: pd.DataFrame,
        position: Tuple[str, ...],
        source: str = 'source',
        target: str = 'target',
        interaction: str = 'interaction',
        weight: Optional[str] = None,
):
    """
    Prepare the input data for analysis by validating, sorting, and renaming columns.

    Args:
        data (pd.DataFrame): The input dataframe containing interaction data.
        position (Tuple[str, ...]): Column names used for positional indexing.
        source (str, optional): Name of the source column. Defaults to 'source'.
        target (str, optional): Name of the target column. Defaults to 'target'.
        interaction (str, optional): Name of the interaction column. Defaults to 'interaction'.
        weight (Optional[str], optional): Name of the weight column, if any. Defaults to None.

    Returns:
        pd.DataFrame: The processed dataframe ready for analysis.

    Raises:
        ValueError: If required columns are missing or position columns are not numeric.
    """
    # check required columns
    required_columns = list(position) + [source, target]
    if weight:
        required_columns.append(weight)
    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"""Missing required columns.\nExpected: {required_columns}\nFound: {data.columns.tolist()}""")

    # examine data
    _check_numeric_position(data, position)

    # sort by position
    df = data.sort_values(by=list(position)).reset_index(drop=True)

    # use multi-index for quick interval selection
    df.set_index(list(position), inplace=True)

    # rename columns
    df = df.rename(columns={source: 'source', target: 'target'})
    if interaction:
        df = df.rename(columns={interaction: 'interaction'})

    # Process 'source', 'target', 'observer' columns to ensure lists
    df['source'] = _process_column(df['source'])
    df['target'] = _process_column(df['target'])

    if weight:
        df = df.rename(columns={weight: 'weight'})
        df['weight'] = df['weight'].astype(float)
        df = _flatten_weights(df)

    return df

def segment(data, start=None, end=None, position=None):
    """
    Extract a subset of interactions based on a specified interval.

    Args:
        data (pd.DataFrame): The dataframe containing interaction data.
        start (tuple, optional): The starting position of the interval. Defaults to None.
        end (tuple, optional): The ending position of the interval. Defaults to None.
        position (tuple, optional): Column names used for positional indexing. Required if multi-indexing is needed. Defaults to None.

    Returns:
        pd.DataFrame: A dataframe containing interactions within the specified interval.

    Raises:
        ValueError: If multi-level time steps are required but position columns are not provided.
    """
    if (len(start) > 1 or len(end) > 1) and not isinstance(data.index, pd.MultiIndex):
        if position is None:
            raise ValueError("Position columns required for multi-level time step.")
        data.set_index(list(position), inplace=True)
    idx = pd.IndexSlice
    interval = data.loc[idx[start:end], :].copy()

    return interval


def calculate_weights(data, weight_func=lambda x: len(x)):
    """
    Calculate weights for each interaction based on a provided weight function.

    Args:
        data (pd.DataFrame): The dataframe containing interaction data.
        weight_func (Callable, optional): A function that takes an interaction entry and returns a numerical weight. Defaults to lambda x: len(x).

    Returns:
        pd.DataFrame: The dataframe with an added 'weight' column and flattened weights.
    """
    data['weight'] = data['interaction'].apply(weight_func)
    data = _flatten_weights(data)
    return data


def _flatten_weights(df):
    """
    Expand the dataframe so that each source-target pair has its own row.

    This is useful when the 'source' and 'target' columns contain lists,
    ensuring that each interaction is represented as a single row.

    Args:
        df (pd.DataFrame): The dataframe with potential list-like 'source' and 'target' columns.

    Returns:
        pd.DataFrame: The exploded dataframe with individual source-target pairs.
    """
    return df.explode('source').explode('target')


def agg_weights(data, position, agg_func=lambda x: sum(x)):
    """
    Aggregate weights by grouping interactions based on positional columns and source-target pairs.

    Args:
        data (pd.DataFrame): The dataframe containing interaction data with weights.
        position (Tuple[str, ...]): Column names used for positional indexing (excluding the line identifier).
        agg_func (Callable, optional): The aggregation function to apply to the weights. Defaults to sum.

    Returns:
        pd.DataFrame: The aggregated dataframe with summed weights for each group.

    Raises:
        ValueError: If the 'weight' column is missing from the dataframe.
    """
    # group by position and source, target, observer
    # raise error if 'weight' column is not found
    if 'weight' not in data.columns:
        raise ValueError("No 'weight' column found. You should run calculate_weights() first.")
    grouped = data.groupby(list(position) + ['source', 'target'])['weight'].agg(agg_func).reset_index()
    return grouped

def _process_column(series):
    """
    Process a dataframe column to ensure each cell contains a list of unique, stripped string items.

    Args:
        series (pd.Series): The column to process.

    Returns:
        pd.Series: The processed column with each cell as a list of unique, stripped strings.
    """
    def clean_cell(cell):
        if isinstance(cell, list):
            items = cell
        elif isinstance(cell, str):
            items = [item.strip() for item in cell.strip('[]').split(',')]
        else:
            items = [str(cell).strip()]
        return pd.unique([str(item).strip() for item in items])

    return series.apply(clean_cell)


def _check_numeric_position(data, position):
    """
    Validate that all position columns contain numeric data types.

    Args:
        data (pd.DataFrame): The dataframe containing position columns.
        position (Tuple[str, ...]): Column names used for positional indexing.

    Raises:
        ValueError: If any position column does not have a numeric data type.
    """
    # check required columns
    for col in position:
        if not pd.api.types.is_numeric_dtype(data[col]):
            raise ValueError(f"Position column '{col}' must be numeric.")

# Infer listener LLM

def generate_prompt(scene_data):
    """
    Generate a formatted prompt for the language model to identify listeners in dialogue lines.

    Args:
        scene_data (Dict[str, Any]): A dictionary containing scene descriptions and dialogue lines.

    Returns:
        str: A formatted prompt string to be sent to the language model.
    """
    prompt = f"""
    Scene Description: {scene_data['Scene_Description']}

    Dialogue Lines:
    """
    for line in scene_data['Lines']:
        prompt += f"Line {line['Line_ID']} - {line['Speaker']}: \"{line['Line']}\"\n"

    prompt += """
    For each line, identify the listeners from the characters present. Provide the results in JSON format only, following this exact structure:

    {
      "listeners": {
        "1": ["Listener1", "Listener2"],
        "2": ["Listener3"],
        ...
      }
    }
    """

    # print(">> prompt:\n", prompt)

    return prompt


def infer_scene_listeners(client, model_name, prompt, *, mode="openai", max_tokens=200):
    """
    Use a language model to infer listeners for each dialogue line in a scene.

    Args:
        client: The API client for interacting with the language model.
        model_name (str): The name of the language model to use.
        prompt (str): The prompt string generated for the language model.
        mode (str, optional): The service provider ("openai" or "anthropic"). Defaults to "openai".
        max_tokens (int, optional): The maximum number of tokens for the response. Defaults to 200.

    Returns:
        Dict[str, List[str]]: A dictionary mapping line IDs to lists of listeners.

    Notes:
        - Ensures the response is valid JSON and adheres to the expected structure.
        - Implements error handling for JSON decoding and other exceptions.
    """
    listeners_json = ""
    listeners_data = {}
    try:
        if mode == "openai":
            import openai
            response = client.chat.completions.create(
                # model="gpt-4o-mini",
                model=model_name,
                messages=[
                    {"role": "system",
                     "content": "You are an assistant that identifies listeners for each line in a conversation. Respond only with JSON following the specified format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                n=1,
                stop=None,
                temperature=0.3
            )
            # print(">> response:\n", response)
            # print(">> response.choices[0].message.content:\n", response.choices[0].message.content)
            listeners_json = response.choices[0].message.content

            # Validate that the response is proper JSON and matches the expected structure
            listeners_data = json.loads(listeners_json)
        elif mode == "anthropic":
            import anthropic
            response = client.messages.create(
                model=model_name,
                messages=[
                    {"role": "user",
                     "content": "You are an assistant that identifies listeners for each line in a conversation. Respond only with JSON following the specified format.\n" + prompt}
                ],
                max_tokens=max_tokens
            )
            # print(">> response:\n", response)
            # print(">> response.choices[0].message.content:\n", response.content[0].text)
            listeners_data = json.loads(response.content[0].text)
        if "listeners" in listeners_data and isinstance(listeners_data["listeners"], dict):
            return listeners_data["listeners"]
        else:
            print("JSON response does not match the expected format.")
            return {}
    except json.JSONDecodeError:
        print("Failed to decode JSON. Response was:", listeners_json)
        return {}
    except Exception as e:
        print(f"Error inferring listeners for scene: {e}")
        return {}

def infer_listeners(data: pd.DataFrame,
                    position: Tuple[str, ...],
                    speaker: str = 'speaker',
                    dialogue: str = 'dialogue',
                    action: Optional[str] = None,
                    scene_description: Optional[str] = None,
                    client: Optional = None,
                    model: Optional[str] = None,
                    mode: str = "openai",
                    max_tokens: int = 200,
                    gap: float = 1.0
                    ) -> pd.DataFrame:
    """
    Infer listeners for each dialogue line across different scenes using a language model.

    Args:
        data (pd.DataFrame): The dataframe containing interaction data.
        position (Tuple[str, ...]): Column names used for positional indexing.
        speaker (str, optional): Name of the speaker column. Defaults to 'speaker'.
        dialogue (str, optional): Name of the dialogue column. Defaults to 'dialogue'.
        action (Optional[str], optional): Name of the action notes column. Defaults to None.
        scene_description (Optional[str], optional): Name of the scene description column. Defaults to None.
        client (Optional, optional): The API client for interacting with the language model. Defaults to None.
        model (Optional[str], optional): The name of the language model to use. Defaults to None.
        mode (str, optional): The service provider ("openai" or "anthropic"). Defaults to "openai".
        max_tokens (int, optional): The maximum number of tokens for the response. Defaults to 200.
        gap (float, optional): Delay between API requests to prevent rate limiting. Defaults to 1.0.

    Returns:
        pd.DataFrame: The dataframe with an added 'listener' column containing inferred listeners.

    Raises:
        ValueError: If required columns are missing or position columns are not numeric.
    """
    required_columns = list(position) + [speaker, dialogue]
    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"""Missing required columns.\nExpected: {required_columns}\nFound: {data.columns.tolist()}""")

    _check_numeric_position(data, position)
    df = data.sort_values(by=list(position)).reset_index(drop=True)

    df = df.rename(columns={speaker: 'speaker'})
    if dialogue:
        df = df.rename(columns={dialogue: 'dialogue'})
    else:
        df['dialogue'] = None
    if action:
        df = df.rename(columns={action: 'action'})
    else:
        df['action'] = None
    if scene_description:
        df = df.rename(columns={scene_description: 'scene_description'})
    else:
        df['scene_description'] = None

    # Process 'source', 'target', 'observer' columns to ensure lists
    df['speaker'] = _process_column(df['speaker'])

    # print(df)
    # check data type of speaker column elements
    # print(df.iloc[0]['speaker'])
    # print(type(df.iloc[0]['speaker']))

    # return

    grouped = df.groupby(list(position[:-1]))
    scene_json = []
    df['listener'] = None
    # use tqdm for progress bar
    # for scene_number, group in grouped
    for scene_number, group in tqdm(grouped, desc='Processing scenes', unit='scene'):
        # print(">> scene_number:", scene_number)
        # print(">> group:\n", group)
        scene_data = {
            "Scene_Description": group['scene_description'].iloc[0],
            "Lines": [
                {
                    "Line_ID": int(row[position[-1]]),
                    "Speaker": list(row['speaker']),
                    "Line": row['dialogue'],
                    "Action_Notes": row['action']
                }
                for _, row in group.iterrows()
            ]
        }
        # print(">> scene_data before inference:\n", json.dumps(scene_data, indent=4))

        # Infer listeners for the entire scene
        prompt = generate_prompt(scene_data)
        listeners = infer_scene_listeners(client, model, prompt, mode=mode, max_tokens=max_tokens)

        # Assign listeners to each line
        for line in scene_data["Lines"]:
            line_id = line["Line_ID"]
            line["Listeners"] = listeners.get(str(line_id), [])
            # for row with column position[-1] == line_id, assign listeners
            df.loc[(df[list(position[:-1])].eq(scene_number)).all(axis=1) &
                   (df[position[-1]] == line_id), 'listener'] = str(line["Listeners"])

        # print(">> scene_data after inference:\n", json.dumps(scene_data, indent=4))
        scene_json.append(scene_data)
        time.sleep(gap)  # Adjust delay as needed
    return df

