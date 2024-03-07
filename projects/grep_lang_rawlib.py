import os
import yaml
import pandas as pd

directory = "/home/hehuang/Github/myproto_oss-fuzz/projects"

language_extensions = {
    'jvm': ['.java'],
    'c++': ['.cpp', '.cc', '.cxx', '.h', '.hpp'],
    'c': ['.c', '.cpp', '.cc', '.h'],
    'python': ['.py'],
    'javascript': ['.js']
}

data = []

count_artificial = 0

def check_code_file(filepath, language):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            for line in lines:
                if 'FuzzedDataProvider' in line:
                    if language == 'jvm' and 'jazzer.api.FuzzedDataProvider' in line:
                        return 'Jazzer'
                    elif language == 'python' and 'atheris' in line:
                        return 'Atheris'
                    elif language == 'c++' or language == 'c' and 'fuzzer/FuzzedDataProvider.h' in line:
                        return 'LLVM'
                    elif language == 'javascript' and 'jazzer.js' in line:
                        return 'Jazzer.js'
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

                        code_check_results_set = set()
                        for code_file in os.listdir(root):
                            code_path = os.path.join(root, code_file)
                            if os.path.isfile(code_path):
                                check_result = check_code_file(code_path, language)
                                if check_result :
                                    code_check_results_set.add(str(check_result))
                        code_check_results = list(code_check_results_set)

                        found_language_files = False
                        extensions = language_extensions.get(language, [])
                        for ext in extensions:
                            for code_file in os.listdir(root):
                                if code_file.endswith(ext):
                                    found_language_files = True
                                    break
                            if found_language_files:
                                break
                        found_language_files_result = ''
                        if not found_language_files:
                            found_language_files_result = '目录下没有源文件，需要进Docker取Fuzz代码'

                        if code_check_results and not found_language_files:
                            print(folder_name)
                            print(language)
                            print(code_check_results)
                            print(found_language_files)
                            print('出问题了')
                            print('----------')

                        artificial_focus = ''
                        if not code_check_results and found_language_files:
                            artificial_focus = '需要人工检查'
                            count_artificial += 1

                    data.append([folder_name, language, '|'.join(code_check_results), found_language_files_result, artificial_focus])
                except yaml.YAMLError as exc:
                    print(exc)

df = pd.DataFrame(data, columns=['Project Name', 'Language', 'FuzzedDataProvider Lib', 'Holding', 'Artificial focus'])

df = df.sort_values(by=['Project Name'], ascending=True)

excel_path = 'output_lang_rawlib.csv'
df.to_csv(excel_path, index=False)

print(f'Data saved to {excel_path}')
print('Artificial focus Count: ' + str(count_artificial))
