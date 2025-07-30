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
    Prepare data, validation, and renaming columns
    :param weight:
    :param data:
    :param position:
    :param source:
    :param target:
    :param interaction:
    :return:
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
    Get interactions based on interval
    :param data: dataframe
    :param interval: interval
    :return: a dataframe with interactions
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
    Calculate weights based on interaction
    :param data: dataframe
    :param weight_func: a function to calculate edge weights
    :return: a dictionary of edge weights
    """
    data['weight'] = data['interaction'].apply(weight_func)
    data = _flatten_weights(data)
    return data


def _flatten_weights(df):
    """
    Flatten weights in the dataframe
    :param df: dataframe
    :return: a dataframe with flattened weights
    """
    return df.explode('source').explode('target')


def agg_weights(data, position, agg_func=lambda x: sum(x)):
    # group by position and source, target, observer
    # raise error if 'weight' column is not found
    if 'weight' not in data.columns:
        raise ValueError("No 'weight' column found. You should run calculate_weights() first.")
    grouped = data.groupby(list(position) + ['source', 'target'])['weight'].agg(agg_func).reset_index()
    return grouped

def _process_column(series):
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
    # check required columns
    for col in position:
        if not pd.api.types.is_numeric_dtype(data[col]):
            raise ValueError(f"Position column '{col}' must be numeric.")

# Infer listener LLM

def generate_prompt(scene_data):
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

