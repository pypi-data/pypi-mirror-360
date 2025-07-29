
import subprocess
import os
import tempfile
from ipykernel.kernelbase import Kernel
import json
import re

class VariableFinder:
    def __init__(self, model_lines, position_line, position_column):
        self.model = model_lines  # список строк
        self.position = (position_line, position_column)

    def find_matches(self, pattern):
        matches = []
        for i, line in enumerate(self.model, 1):  # строки нумеруются с 1
            for match in re.finditer(pattern, line):
                matches.append({
                    "range": {"startLineNumber": i},
                    "matches": match.groups()
                })
        return matches

    def find_previous_match(self, pattern):
        for i in range(self.position[0] - 1, -1, -1):
            match = re.search(pattern, self.model[i])
            if match:
                return {
                    "range": {"startLineNumber": i + 1, "startColumn": match.start() + 1},
                    "matches": match.groups()
                }
        return None

    def find_next_match(self, pattern, start_line):
        for i in range(start_line, len(self.model)):
            match = re.search(pattern, self.model[i])
            if match:
                return {
                    "range": {"startLineNumber": i + 1, "startColumn": match.start() + 1},
                }
        return None

    def get_default_vars_names(self, current_line, func_line):
        names = []
        pattern = r'(?:перем|var)\s+([a-zA-Z0-9\u0410-\u044F_,\s]+);'
        matches = self.find_matches(pattern)

        for match in matches:
            line_num = match["range"]["startLineNumber"]
            if current_line == 0 or (func_line < line_num < current_line):
                var_def = match["matches"][-1]
                params = var_def.split(',')
                for param in params:
                    param_name = param.split('=')[0].strip()
                    if param_name not in names:
                        names.append(param_name)
        return names

    def get_loops_var_names_for_current_position(self, pattern):
        names = []
        loop_start = self.find_previous_match(pattern)

        if loop_start:
            start_line = loop_start["range"]["startLineNumber"]
            loop_end = self.find_next_match(r'(?:конеццикла|enddo)', start_line)

            if loop_end:
                end_line = loop_end["range"]["startLineNumber"]
                current_line = self.position[0]

                if start_line < current_line < end_line:
                    names.append(loop_start["matches"][-1])

        return names
    
    def get_assigned_variables(self):
        assigned = set()
        pattern = r'\b([a-zA-Z\u0410-\u044F_][a-zA-Z0-9\u0410-\u044F_]*)\s*='
        for i, line in enumerate(self.model):
            matches = re.findall(pattern, line)
            for var in matches:
                assigned.add(var)
        return list(assigned)


class OneScriptKernel(Kernel):
    implementation = 'OneScript'
    implementation_version = '2.2-stateful-file'
    language = 'onescript'
    language_version = '1.0'
    language_info = {
        'name': 'OneScript',
        'mimetype': 'text/x-csharp',
        'file_extension': '.os',
    }
    banner = """OneScript Kernel"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Этот файл хранит состояние МЕЖДУ ячейками
        self.state_file_handle, self.state_file_path = tempfile.mkstemp(suffix=".dat")
        try:
            # Записываем пустой JSON (`{}`) в файл
            with open(self.state_file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        finally:
            # Закрываем файловый дескриптор (если не использовать with для handle)
            os.close(self.state_file_handle)


    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count}

        # 1. Чтение предыдущего состояния
        with open(self.state_file_path, 'r', encoding='utf-8') as f:
            try:
                prev_state = json.load(f)
            except json.JSONDecodeError:
                prev_state = {}

        # 2. Получение переменных из текущего кода
        source_lines = code.splitlines()
        finder = VariableFinder(source_lines, position_line=1, position_column=1)

        default_vars = finder.get_default_vars_names(current_line=0, func_line=0)
        each_vars = finder.get_loops_var_names_for_current_position(r'(?:для каждого|for each)\s+([a-zA-Z0-9\u0410-\u044F_]+)\s+(?:из|in)')
        for_vars = finder.get_loops_var_names_for_current_position(r'(?:для|for)\s+([a-zA-Z0-9\u0410-\u044F_]+)\s+=.*(?:по|to)')
        assigned_vars = finder.get_assigned_variables()

        all_vars = set(default_vars + each_vars + for_vars + assigned_vars + list(prev_state.keys()))

        missing_vars = [var for var in all_vars if var not in prev_state]
        existing_vars = [var for var in all_vars if var in prev_state]

        # 3. Генерация параметров процедуры
        params_decl = ", ".join(all_vars)
        input_struct = "\n".join([
            f"{var} = ДанныеJSON.{var};" for var in existing_vars
        ] + [
            f"{var} = Неопределено;" for var in missing_vars
        ])
        output_saves = "\n".join(f"""
    Попытка
        ЗаписьJSON = Новый ЗаписьJSON;
        ЗаписьJSON.УстановитьСтроку();
        ЗаписатьJSON(ЗаписьJSON, Новый Структура(\"{var}\", {var}));
        ЗаписьJSON.Закрыть();
        ПеременныеКода.Вставить(\"{var}\", {var});
    Исключение
        упс = Истина;
    КонецПопытки;
    """ for var in all_vars)

        # 4. Формирование полного кода
        state_filename = json.dumps(self.state_file_path)

        full_code = f'''
    Процедура ВыполнениеКода({params_decl})
    {code}
    КонецПроцедуры

    ИмяФайла = {state_filename};
    ЧтениеJSON = Новый ЧтениеJSON;
    ЧтениеJSON.ОткрытьФайл(ИмяФайла);
    ДанныеJSON = ПрочитатьJSON(ЧтениеJSON, Ложь);
    ЧтениеJSON.Закрыть();

    {input_struct}
    ВыполнениеКода({params_decl});

    ПеременныеКода = Новый Структура();
    {output_saves}

    ЗаписьJSON = Новый ЗаписьJSON;
    ЗаписьJSON.ОткрытьФайл(ИмяФайла);
    ЗаписатьJSON(ЗаписьJSON, ПеременныеКода);
    ЗаписьJSON.Закрыть();
    '''

        # 5. Сохраняем и запускаем
        script_file_path = ''
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.os', delete=False, encoding='utf-8') as script_file:
                script_file_path = script_file.name
                script_file.write(full_code)

            process = subprocess.Popen(
                ['oscript', script_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8'
            )
            stdout, stderr = process.communicate()
        finally:
            if os.path.exists(script_file_path):
                os.remove(script_file_path)

        if stderr:
            if not silent:
                # Добавим полный код в stderr-вывод
                error_text = stderr
                self.send_response(self.iopub_socket, 'stream', {
                    'name': 'stderr',
                    'text': error_text
                })
            return {'status': 'error', 'execution_count': self.execution_count}
        else:
            if not silent:
                self.send_response(self.iopub_socket, 'stream', {'name': 'stdout', 'text': stdout })
            return {'status': 'ok', 'execution_count': self.execution_count}


    def do_shutdown(self, restart):
        if os.path.exists(self.state_file_path):
            os.remove(self.state_file_path)
        return super().do_shutdown(restart)

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=OneScriptKernel)
