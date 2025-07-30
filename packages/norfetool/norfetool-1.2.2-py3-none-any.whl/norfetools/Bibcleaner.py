import os
import re
from pathlib import Path

class Bib:
    FIELDS_TO_REMOVE = {
        'file', 'abstract', 'keywords', 'shorttitle', 'urldate',
        'langid', 'isbn', 'lccn', 'copyright'
    }

    _LOWERCASE_WORDS = {
        'of', 'and', 'in', 'on', 'for', 'the', 'with', 'by', 'to', 'at',
        'as', 'from', 'but', 'or', 'nor'
    }

    _FULL_UPPER_ACRONYMS = {
        'ACS', 'JACS', 'PNAS', 'IEEE', 'RSC', 'JCP', 'NIST',
        'AIP', 'SIAM', 'NIPS', 'AAAS', 'APS', 'ES&T'
    }

    @classmethod
    def find_all_tex_files(cls, root_dir):
        tex_files = []
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith('.tex'):
                    tex_files.append(os.path.join(dirpath, filename))
        return tex_files

    @classmethod
    def replace_inline_math(cls, tex_file_list):
        for filepath in tex_file_list:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            content = content.replace(r'\(', '$').replace(r'\)', '$')
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)

    @classmethod
    def generate_clean_bib(cls, input_bib_path, tex_files, output_bib_path):
        # 提取 cite key
        cite_keys = cls._extract_cite_keys(tex_files)
        # 创建中间 bib 文件
        intermediate_path = output_bib_path + ".tmp"
        cls._filter_bib_entries(input_bib_path, cite_keys, intermediate_path)
        # 清理中间 bib 文件并写入目标
        cls._clean_bib_file(intermediate_path, output_bib_path)
        os.remove(intermediate_path)

    # 以下为内部函数

    @classmethod
    def _extract_cite_keys(cls, tex_files):
        cite_keys = set()
        cite_pattern = re.compile(r'\\cite\{([^}]*)\}')
        for filepath in tex_files:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                matches = cite_pattern.findall(content)
                for match in matches:
                    keys = [key.strip() for key in match.split(',')]
                    cite_keys.update(keys)
        return cite_keys

    @classmethod
    def _filter_bib_entries(cls, input_bib_path, used_keys, output_bib_path):
        with open(input_bib_path, 'r', encoding='utf-8') as bib_file:
            content = bib_file.read()
        entry_pattern = re.compile(r'@[\w]+\{([^,]+),[\s\S]*?\n\}', re.MULTILINE)
        entries = list(entry_pattern.finditer(content))
        selected_entries = [entry.group(0).strip() for entry in entries if entry.group(1).strip() in used_keys]
        with open(output_bib_path, 'w', encoding='utf-8') as out_file:
            out_file.write('\n\n'.join(selected_entries))

    @classmethod
    def _clean_bib_file(cls, input_path, output_path):
        entries = cls._parse_bib_file_lines(input_path)
        cleaned = [cls._clean_bib_entry(e) for e in entries]
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(cleaned))

    @classmethod
    def _split_authors_safe(cls, s):
        authors, buffer, brace_level, i = [], '', 0, 0
        while i < len(s):
            if s[i:i+5] == ' and ' and brace_level == 0:
                authors.append(buffer.strip())
                buffer, i = '', i + 5
                continue
            buffer += s[i]
            brace_level += (s[i] == '{') - (s[i] == '}')
            i += 1
        if buffer:
            authors.append(buffer.strip())
        return authors

    @classmethod
    def _clean_author(cls, raw):
        if raw.startswith('{{') and raw.endswith('}}'):
            raw = raw[1:-1]
        elif raw.startswith('{') and raw.endswith('}'):
            inner = raw[1:-1]
            if ' and ' in inner:
                raw = inner

        authors = cls._split_authors_safe(raw)
        cleaned = []
        for author in authors:
            author = author.strip()
            if author.startswith('{') and author.endswith('}'):
                inner = author[1:-1]
                if inner.count('{') == inner.count('}'):
                    author = inner
            if ',' in author and author.count(',') == 1:
                parts = [p.strip() for p in author.split(',', 1)]
                author = f"{parts[1]} {parts[0]}"
            cleaned.append(author)
        return '{' + ' and '.join(cleaned) + '}'

    @classmethod
    def _format_journal(cls, journal):
        words = journal.split()
        formatted = []
        for word in words:
            upper = word.upper()
            if upper in cls._FULL_UPPER_ACRONYMS:
                formatted.append(upper)
            elif word.lower() in cls._LOWERCASE_WORDS:
                formatted.append(word.lower())
            else:
                formatted.append(word.capitalize())
        return ' '.join(formatted)

    @classmethod
    def _parse_bib_file_lines(cls, input_path):
        entries = []
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_entry, brace_level = [], 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('@'):
                if current_entry:
                    entries.append('\n'.join(current_entry))
                    current_entry = []
                current_entry.append(line.rstrip())
                brace_level = line.count('{') - line.count('}')
            elif current_entry:
                current_entry.append(line.rstrip())
                brace_level += line.count('{') - line.count('}')
                if brace_level <= 0:
                    entries.append('\n'.join(current_entry))
                    current_entry = []

        if current_entry:
            entries.append('\n'.join(current_entry))
        return entries

    @classmethod
    def _clean_bib_entry(cls, entry_text):
        lines = entry_text.splitlines()
        header, fields, field_order = lines[0], {}, []
        current_field, buffer, brace_level = None, [], 0

        for line in lines[1:]:
            stripped = line.strip()
            if '=' in stripped and brace_level == 0:
                if current_field:
                    value = '\n'.join(buffer).strip().rstrip(',')
                    fields[current_field.lower()] = value
                    field_order.append(current_field.lower())
                current_field, buffer = stripped.split('=', 1)[0].strip(), [stripped.split('=', 1)[1].strip()]
                brace_level = buffer[0].count('{') - buffer[0].count('}')
            else:
                buffer.append(stripped)
                brace_level += stripped.count('{') - stripped.count('}')

        if current_field and buffer:
            value = '\n'.join(buffer).strip().rstrip(',')
            fields[current_field.lower()] = value
            field_order.append(current_field.lower())

        for f in cls.FIELDS_TO_REMOVE:
            fields.pop(f, None)

        if 'author' in fields:
            fields['author'] = cls._clean_author(fields['author'])
        if 'journal' in fields:
            val = fields['journal'].strip()
            if val.startswith('{') and val.endswith('}'):
                val = val[1:-1]
            fields['journal'] = '{' + cls._format_journal(val) + '}'

        new_entry = [header]
        for key in field_order:
            if key in fields:
                new_entry.append(f"  {key} = {fields[key]},")
        new_entry.append('}')
        return '\n'.join(new_entry)

