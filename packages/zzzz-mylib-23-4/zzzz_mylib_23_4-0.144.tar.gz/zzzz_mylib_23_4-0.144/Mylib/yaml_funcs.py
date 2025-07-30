import yaml
from box import ConfigBox  # để trả về object dạng truy cập bằng chấm
from box.exceptions import BoxValueError  # để bắt lỗi file trống


def read_yaml(path_to_yaml: str) -> ConfigBox:
    """reads yaml file and returns

    Args:
        path_to_yaml (Path): path like input

    Raises:
        ValueError: if yaml file is empty
        e: empty file

    Returns:
        ConfigBox: _description_
    """
    try:
        with open(path_to_yaml, "r", encoding="utf-8") as yaml_file:
            content = yaml.safe_load(yaml_file)
            print(f"yaml file: {path_to_yaml} loaded successfully")
            return ConfigBox(content)
    except BoxValueError:
        raise ValueError("yaml file is empty")
    except Exception as e:
        raise e


def sub_param_for_yaml_file(src_path: str, des_path: str, replace_dict: dict):
    """Substitue params in src_path and save in des_path

    Args:
        replace_dict (dict): key: item needed to replace, value: item to replace
        VD:
        ```python
        replace_dict = {
            "${P}": data_transformation,
            "${T}": model_name,
            "${E}": evaluation,
        }

        ```
    """

    with open(src_path, "r", encoding="utf-8") as file:
        config_data = yaml.safe_load(file)

    config_str = yaml.dump(config_data, default_flow_style=False)

    for key, value in replace_dict.items():
        config_str = config_str.replace(key, value)

    with open(des_path, "w", encoding="utf-8") as file:
        file.write(config_str)

    print(f"Đã thay thế các tham số trong {src_path} lưu vào {des_path}")


def get_model_from_yaml_52(yaml):
    """Get model từ yaml gồm model + index của model <br>

    Có các dạng sau:

    1.
    ```
    XGBClassifier(n_estimators=300,max_depth=40)|0
    ```

    2.
    ```
    class_name: CustomStackingClassifier|0
    estimators:
        - LogisticRegression(C = 0.1)
        - GaussianNB(var_smoothing=1e-8)
        - SGDClassifier(alpha=10, loss='log_loss')
    final_estimator: LogisticRegression(C = 0.1)
    ```

    Returns:
        (model, model_index): _description_
    """
    if isinstance(yaml, dict):
        model_index = yaml["class_name"].split("|")[1]
        yaml["class_name"] = yaml["class_name"].split("|")[0]
        model = stringToObjectConverter.convert_MLmodel_yaml_to_object(yaml)

        return model, model_index

    model_index = yaml.split("|")[1]
    model = stringToObjectConverter.convert_MLmodel_yaml_to_object(yaml.split("|")[0])
    return model, model_index


def get_models_from_yaml_52(yaml: list):
    """Get các models từ yaml, gồm có  model và index của model, có dạng sau:

    ```
    - LogisticRegression(C = 0.1)|0
    -
        class_name: CustomStackingClassifier|1
        estimators:
            - LogisticRegression(C = 0.1)
            - GaussianNB(var_smoothing=1e-8)
            - SGDClassifier(alpha=10, loss='log_loss')
        final_estimator: LogisticRegression(C = 0.1)
    ```


    Returns:
        (models, model_indices): _description_
    """
    a = [get_model_from_yaml_52(item) for item in yaml]
    models, model_indices = zip(*a)
    return list(models), list(model_indices)
