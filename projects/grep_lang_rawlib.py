import os
import yaml
import pandas as pd

directory = "/home/hehuang/Github/myproto_oss-fuzz/projects"

data = []

def check_code_file(filepath, language):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            for line in lines:
                if 'FuzzedDataProvider' in line:
                    if language == 'jvm' and 'jazzer.api.FuzzedDataProvider' in line:
                        return True
                    elif language == 'python' and 'atheris' in line:
                        return True
                    elif language == 'c++' and 'fuzzer/FuzzedDataProvider.h' in line:
                        return True
                    else:
                        return line.strip()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
    return False

for root, dirs, files in os.walk(directory):
    for file in files:
        if file == 'project.yaml':
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as stream:
                try:
                    yaml_content = yaml.safe_load(stream)
                    if 'language' in yaml_content:
                        folder_name = os.path.basename(root)
                        language = yaml_content['language'].lower()
                        code_check = ''
                        for code_file in os.listdir(root):
                            code_path = os.path.join(root, code_file)
                            if os.path.isfile(code_path):
                                check_result = check_code_file(code_path, language)
                                if check_result:
                                    code_check = check_result
                                    break
                        data.append([folder_name, language, code_check])
                except yaml.YAMLError as exc:
                    print(exc)

df = pd.DataFrame(data, columns=['Project Name', 'Language', 'FuzzedDataProvider Lib'])

df = df.sort_values(by=['Project Name'], ascending=True)

excel_path = 'output_lang_rawlib.csv'
df.to_csv(excel_path, index=False)

print(f'Data saved to {excel_path}')