from typing import List, Dict, Any, Optional


class BlockConverter:
    def __init__(self):
        pass

    def convert_blocks(self, blocks: List[Dict[str, Any]]) -> str:
        markdown_lines = []
        for block in blocks:
            converted = self._convert_block(block)
            if converted:
                markdown_lines.append(converted)
        return '\n\n'.join(markdown_lines)

    def _convert_block(self, block: Dict[str, Any]) -> Optional[str]:
        block_type = block.get('type')
        if not block_type:
            return None

        handler = getattr(self, f'_handle_{block_type}', None)
        if handler:
            return handler(block)
        return None

    def _handle_paragraph(self, block: Dict[str, Any]) -> str:
        rich_text = block.get('paragraph', {}).get('rich_text', [])
        return self._rich_text_to_markdown(rich_text)

    def _handle_heading_1(self, block: Dict[str, Any]) -> str:
        rich_text = block.get('heading_1', {}).get('rich_text', [])
        text = self._rich_text_to_markdown(rich_text)
        return f"# {text}"

    def _handle_heading_2(self, block: Dict[str, Any]) -> str:
        rich_text = block.get('heading_2', {}).get('rich_text', [])
        text = self._rich_text_to_markdown(rich_text)
        return f"## {text}"

    def _handle_heading_3(self, block: Dict[str, Any]) -> str:
        rich_text = block.get('heading_3', {}).get('rich_text', [])
        text = self._rich_text_to_markdown(rich_text)
        return f"### {text}"

    def _handle_bulleted_list_item(self, block: Dict[str, Any]) -> str:
        rich_text = block.get('bulleted_list_item', {}).get('rich_text', [])
        text = self._rich_text_to_markdown(rich_text)
        return f"- {text}"

    def _handle_numbered_list_item(self, block: Dict[str, Any]) -> str:
        rich_text = block.get('numbered_list_item', {}).get('rich_text', [])
        text = self._rich_text_to_markdown(rich_text)
        return f"1. {text}"

    def _handle_to_do(self, block: Dict[str, Any]) -> str:
        todo_data = block.get('to_do', {})
        checked = todo_data.get('checked', False)
        rich_text = todo_data.get('rich_text', [])
        text = self._rich_text_to_markdown(rich_text)
        checkbox = "[x]" if checked else "[ ]"
        return f"{checkbox} {text}"

    def _handle_code(self, block: Dict[str, Any]) -> str:
        code_data = block.get('code', {})
        language = code_data.get('language', '')
        rich_text = code_data.get('rich_text', [])
        text = self._rich_text_to_markdown(rich_text)
        return f"```{language}\n{text}\n```"

    def _handle_quote(self, block: Dict[str, Any]) -> str:
        rich_text = block.get('quote', {}).get('rich_text', [])
        text = self._rich_text_to_markdown(rich_text)
        lines = text.split('\n')
        return '\n'.join(f"> {line}" for line in lines)

    def _handle_callout(self, block: Dict[str, Any]) -> str:
        rich_text = block.get('callout', {}).get('rich_text', [])
        text = self._rich_text_to_markdown(rich_text)
        return f"> {text}"

    def _handle_divider(self, block: Dict[str, Any]) -> str:
        return "---"

    def _handle_image(self, block: Dict[str, Any]) -> str:
        image_data = block.get('image', {})
        image_type = image_data.get('type')
        
        if image_type == 'external':
            url = image_data.get('external', {}).get('url', '')
            caption = self._get_caption(image_data)
            return f"![{caption}]({url})"
        elif image_type == 'file':
            file_url = image_data.get('file', {}).get('url', '')
            caption = self._get_caption(image_data)
            return f"![{caption}]({file_url})"
        return ""

    def _get_caption(self, image_data: Dict[str, Any]) -> str:
        caption = image_data.get('caption', [])
        if caption:
            return self._rich_text_to_markdown(caption)
        return ""

    def _rich_text_to_markdown(self, rich_text: List[Dict[str, Any]]) -> str:
        result = []
        for item in rich_text:
            text = item.get('plain_text', '')
            annotations = item.get('annotations', {})
            
            if annotations.get('bold'):
                text = f"**{text}**"
            if annotations.get('italic'):
                text = f"*{text}*"
            if annotations.get('strikethrough'):
                text = f"~~{text}~~"
            if annotations.get('code'):
                text = f"`{text}`"
            
            link = item.get('href')
            if link:
                text = f"[{text}]({link})"
            
            result.append(text)
        return ''.join(result)
