import re
import pandas as pd


class ConversationCleaner:
    def __init__(self):
        self.meaningless_phrases = [
            "这边是人工客服，请问有什么可以帮您？",
            "您好，智能客服小飞为您服务！可以点击/:no选择下方问题或输入您的问题/:?",
            "询前表单客户已提交",
            "您好，已进入人工，请问有什么可以帮您",
            "您好，已进入人工服务，请问有什么可以帮您？"
            "为了您账户信息安全，请您提供下姓名全称、注册账户手机号、身份证号后4位帮您核实账户情况哦，谢谢",
            "有新的咨询进来了",
            "询前表单客户已提交",
            "锁定会话",
            "解锁会话",
            "解锁对话",
            "系统发送未响应超时提醒",
            "非常抱歉没有得到您的响应,请问还有什么可以帮您？",
            "非常抱歉没有得到您的响应，如有问题，欢迎您在工作时间随时留言，法定假日除外，感谢您的配合！",
            "系统发送满意度调查",
            "感谢您的咨询，祝您生活愉快，再见！",
            "客户超时未响应，系统关闭会话",
            "您好，请您提供下注册账户手机号，谢谢",
            "。",
            "稍等，为您核实~",
            "----：----",
            "系统发送满意度调查",
            "客户已进行满意度评价",
            "''",
        ]

    def clean_conversation(self, text):
        """
        清理单条对话内容的主函数
        """
        if pd.isna(text) or not isinstance(text, str):
            return ""

        # 按顺序应用所有清理函数
        text = self.remove_robot_messages(text)
        text = self.clean_basic_content(text)
        text = self.remove_sensitive_lines(text)
        text = self.mask_sensitive_info(text)
        text = self.remove_empty_lines(text)
        text = self.clean_messages(text)
        text = self.clean_customer_service_messages(text)
        text = self.concatenate_lines_with_colon(text)
        text = self.remove_sensitive_info_and_responses(text)
        text = self.remove_isolated_customer_lines(text)
        text = self.remove_empty_lines(text)

        # 最终清理
        text = re.sub(r'\s{2,}', ' ', text)  # 删除连续空格
        text = text.replace("----：----", "")
        text = text.replace("-----以下是人工客服消息-----", "")

        return text.strip()

    def clean_basic_content(self, text):
        """删除无意义文本"""
        for phrase in self.meaningless_phrases:
            text = text.replace(phrase, "")
        return text.strip()

    def remove_empty_lines(self, text):
        """删除空白行"""
        if pd.isna(text):
            return ""
        return "\n".join([line for line in text.splitlines() if line.strip()])

    def mask_sensitive_info(self, text):
        """替换敏感信息"""
        if pd.isna(text):
            return text
        text = re.sub(r'(\b\d{3})\d{4}(\d{4}\b)', r'\1****\2', text)
        text = re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', text)
        text = re.sub(r'(\b\d{4})\d{10}(\d{4}\b)', r'\1**********\2', text)
        text = re.sub(r'(\b\d{4})\d{8,11}(\d{4}\b)', r'\1********\2', text)
        return text

    def remove_sensitive_lines(self, text):
        """删除包含特定内容的行"""
        pattern = r"询前表单-提交手机|您好，已进入人工服务|已撤回|【图片】|----：----|x|X"
        return "\n".join([line for line in text.strip().split('\n') if not re.search(pattern, line)])

    def clean_messages(self, text):
        """清理多余的时间信息行"""
        lines = text.strip().split('\n')
        cleaned_lines = []
        skip_next = False
        for i in range(len(lines)):
            if skip_next:
                skip_next = False
                continue
            if re.search(r'\d{4}/\d{1,2}/\d{1,2}', lines[i]):
                if i + 1 < len(lines) and re.search(r'\d{4}/\d{1,2}/\d{1,2}', lines[i + 1]):
                    continue
                else:
                    cleaned_lines.append(lines[i])
            else:
                cleaned_lines.append(lines[i])
        if cleaned_lines and re.search(r'\d{4}/\d{1,2}/\d{1,2}', cleaned_lines[-1]):
            cleaned_lines.pop()
        return '\n'.join(cleaned_lines)

    def remove_robot_messages(self, text):
        """删除机器人服务消息"""
        if '-----以下是机器人服务消息-----' in text and '-----以下是人工客服消息-----' in text:
            start_index = text.index('-----以下是机器人服务消息-----')
            end_index = text.index('-----以下是人工客服消息-----')
            text = text[:start_index] + text[end_index:]
        return text

    def clean_customer_service_messages(self, text):
        """清理客户和客服消息格式"""
        pattern = r'(\S+)\s*\d{4}/\d{1,2}/\d{1,2}\s*\d{1,2}:\d{1,2}:\d{1,2}'
        lines = text.strip().split('\n')
        cleaned_lines = []
        for line in lines:
            match = re.match(pattern, line)
            if match:
                speaker = match.group(1)
                content = line[match.end():].strip()
                cleaned_lines.append(f"{speaker}：{content}")
            else:
                cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)

    def concatenate_lines_with_colon(self, text):
        """连接冒号结尾的行"""
        lines = text.strip().split('\n')
        concatenated_lines = []
        i = 0
        while i < len(lines):
            current_line = lines[i]
            if current_line.endswith("：") and (i + 1 < len(lines)):
                next_line = lines[i + 1].strip()
                if current_line[:-1] != next_line:
                    concatenated_lines.append(f"{current_line}{next_line}")
                else:
                    concatenated_lines.append(current_line)
                i += 1
            else:
                concatenated_lines.append(current_line)
            i += 1
        return '\n'.join(concatenated_lines)

    def remove_isolated_customer_lines(self, text):
        """删除孤立的客户行"""
        lines = text.strip().split('\n')
        return '\n'.join([line for line in lines if line.strip() != "客户："])

    def remove_sensitive_info_and_responses(self, text):
        """删除敏感信息和相关响应"""
        if pd.isna(text):
            return text

        lines = text.split('\n')
        cleaned_lines = []
        skip_next_customer = False
        in_sensitive_block = False

        sensitive_patterns = [
            "为了您账户信息安全",
            "身份证号后四位",
            "身份证后4位",
            "姓名全称",
            "银行卡后四位",
            "提供一下您的",
            "注册手机号码",
            "注册账户手机号",
            "手机号",
            r"\d{11}",
            r"\d{17}[\dXx]",
            r"[\u4e00-\u9fa5]{2,4}\s*\d{18}",
            r"[\u4e00-\u9fa5]{2,4}\s*\d{11}"
        ]

        for line in lines:
            if not line.strip():
                continue

            contains_sensitive = any(pattern in line if isinstance(pattern, str) else bool(re.search(pattern, line))
                                     for pattern in sensitive_patterns)

            if any(phrase in line for phrase in ["为了账户信息安全", "身份证后4位", "完整手机号", "身份证后四位"]):
                skip_next_customer = True
                in_sensitive_block = True
                continue

            if skip_next_customer and line.startswith("客户："):
                skip_next_customer = False
                in_sensitive_block = False
                continue

            if contains_sensitive:
                in_sensitive_block = True
                continue

            if not in_sensitive_block and not contains_sensitive:
                cleaned_line = line
                cleaned_line = re.sub(r'\d{3}\*{4}\d{4}', '', cleaned_line)
                cleaned_line = re.sub(r'\d{6}\*{4}\d{4}', '', cleaned_line)
                cleaned_line = re.sub(r'\d{4}\*{8}\d{4}', '', cleaned_line)

                if cleaned_line.strip():
                    cleaned_lines.append(cleaned_line)

            if in_sensitive_block and line.startswith("客户："):
                in_sensitive_block = False

        result = '\n'.join(cleaned_lines)
        result = re.sub(r'\b\d{4,}\b', '', result)

        result_lines = result.split('\n')
        result_lines = [line for line in result_lines
                        if not (re.match(r'^[\s\W]*[\u4e00-\u9fa5]{2,4}[\s\W]*$', line.strip()) or
                                (('·' in line) and (len(re.findall(r'[\u4e00-\u9fa5]', line)) < 14)))]

        return '\n'.join(result_lines).strip()