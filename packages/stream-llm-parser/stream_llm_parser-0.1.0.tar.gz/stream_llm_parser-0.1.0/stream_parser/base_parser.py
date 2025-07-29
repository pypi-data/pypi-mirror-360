from typing import Callable, Literal

from pydantic import BaseModel

import logging

logger = logging.getLogger("stream_parser")

class SpecialTokenConfig(BaseModel):
    bot: str
    eot: str
    bot_func: Callable[[str], Literal["maybe_match", "match", "not_match"]] | None = None
    eot_func: Callable[[str], Literal["maybe_match", "match", "not_match"]] | None = None
    keep_bot: bool = False
    keep_eot: bool = False
    token_type: str = ""
    stream: bool = False
    sub_special_tokens: dict[str, "SpecialTokenConfig"] = {}

    def model_post_init(self, __context):
        if not self.bot_func:
            self.bot_func = self.get_default_bot_func
        if not self.eot_func:
            self.eot_func = self.get_default_eot_func

    def get_default_bot_func(self, text: str) -> Literal["maybe_match", "match", "not_match"]:
        if text.startswith(self.bot):
            return "match"
        if text == self.bot[: (len(text))]:
            return "maybe_match"
        return "not_match"

    def get_default_eot_func(self, text: str) -> Literal["maybe_match", "match", "not_match"]:
        if text.endswith(self.eot):
            return "match"
        elif self._suffix_prefix_same(text, self.eot):
            return "maybe_match"
        else:
            return "not_match"

    def _suffix_prefix_same(self, s1: str, s2: str):
        """
        return True if end(s1) == beg(s2)
        """
        l1, l2 = len(s1), len(s2)
        assert l2 > 0

        if s1 and (l2 >= l1) and (s2[:l1] == s1):
            return True
        return False


class StreamSpecialTokenParser:
    def __init__(
        self,
        token_type_map: dict[str, SpecialTokenConfig] = {},
        default_state: str = "text",
        default_token_type: str = "text",
    ):
        self.token_type_map = token_type_map
        for k, v in self.token_type_map.items():
            if not v.token_type:
                v.token_type = k

        self.default_state = default_state
        self.default_token_type = default_token_type
        self.buffer = ""
        self.is_first = True
        self.sub_token_parser: StreamSpecialTokenParser | None = None
        self._reset_state()

    def _reset_state(self):
        self.state = "text"

    def _clear(self):
        self.state = "text"
        self.buffer = ""
        self.is_first = True

    def postprocess_stream(self, delta_text: str, final=False):
        for res in self._postprocess_stream(delta_text, final=final):
            type_ = res["type"]
            content = res.get("content", "")
            meta = res.get("meta")
            state = res.get("state", "")
            config = self.token_type_map.get(state)
            if config and config.sub_special_tokens:
                if meta == "begin":
                    yield res
                    self.sub_token_parser = StreamSpecialTokenParser(
                        token_type_map=config.sub_special_tokens,
                        default_state=state,
                        default_token_type=config.token_type,
                    )
                elif meta == "end":
                    if self.sub_token_parser:
                        for sub_res in self.sub_token_parser.postprocess_stream(content, final=True):
                            yield sub_res
                        self.sub_token_parser = None
                    yield res
                else:
                    assert self.sub_token_parser is not None
                    for sub_res in self.sub_token_parser.postprocess_stream(content):
                        yield sub_res
            else:
                yield res

    def _postprocess_stream(self, delta_text: str, final=False):
        if final:
            yield from self._postprocess_final()
            return

        for c in delta_text:
            yield from self._process(c)
            self.is_first = False
        if self.buffer:
            if self.state == "text":
                yield {"type": self.default_token_type, "content": self.buffer, "state": self.default_state}
                self.buffer = ""
                self._reset_state()
            elif self.state in self.token_type_map:
                st_conf = self.token_type_map[self.state]
                if st_conf.stream:
                    yield {"type": st_conf.token_type, "content": self.buffer, "state": self.state}
                    self.buffer = ""

    def _postprocess_final(self):
        if self.buffer.strip():
            if self.state == "text":
                yield {"type": self.default_token_type, "content": self.buffer, "state": self.default_state}
                self.buffer = ""
                self._reset_state()
            elif self.state in self.token_type_map:
                st_conf = self.token_type_map[self.state]
                yield {"type": st_conf.token_type, "content": self.buffer, "state": self.state}
                self.buffer = ""
                self._reset_state()

    def _process(self, c: str):
        if self.state == "text":
            for key, st_conf in self.token_type_map.items():
                assert st_conf.bot_func
                r = st_conf.bot_func(c)
                if r in ("maybe_match", "match"):
                    if self.buffer:
                        yield {"type": self.default_token_type, "content": self.buffer, "state": self.default_state}
                        self._reset_state()
                    if r == "match":
                        yield {"type": st_conf.token_type, "content": "", "meta": "begin", "state": key}
                        self.state = key
                        if st_conf.keep_bot:
                            self.buffer = c
                        else:
                            self.buffer = ""
                    elif r == "maybe_match":
                        self.state = "special_start"
                        self.buffer = c
                    return
            self.buffer += c

        elif self.state == "special_start":
            for key, st_conf in self.token_type_map.items():
                assert st_conf.bot_func
                r = st_conf.bot_func(self.buffer + c)
                if r == "match":
                    yield {"type": st_conf.token_type, "content": "", "meta": "begin", "state": key}
                    if st_conf.keep_bot:
                        self.buffer += c
                    else:
                        self.buffer = (self.buffer + c).removeprefix(st_conf.bot)
                    self.state = key
                    return
                elif r == "maybe_match":
                    self.buffer += c
                    return
            self._reset_state()
            yield from self._process(c)

        elif self.state in self.token_type_map:
            st_conf = self.token_type_map[self.state]
            assert st_conf.eot_func

            if st_conf.stream:
                r = st_conf.eot_func(c)
                if r == "maybe_match":
                    if self.buffer:
                        yield {"type": st_conf.token_type, "content": self.buffer, "state": self.state}
                    self.buffer = c
                    self.state = f"special_end_{self.state}"
                elif r == "match":
                    if self.buffer:
                        yield {"type": st_conf.token_type, "content": self.buffer, "state": self.state}
                    if st_conf.keep_eot:
                        yield {"type": st_conf.token_type, "content": c, "meta": "eot", "state": self.state}

                    yield {"type": st_conf.token_type, "content": "", "meta": "end", "state": self.state}
                    self.buffer = ""
                    self._reset_state()
                else:
                    self.buffer += c
            else:
                self.buffer += c
                r = st_conf.eot_func(self.buffer)
                if r == "match":
                    if st_conf.keep_eot:
                        special_content = self.buffer
                    else:
                        special_content = self.buffer.removesuffix(st_conf.eot)
                    if special_content:
                        yield {"type": st_conf.token_type, "content": special_content, "state": self.state}

                    yield {"type": st_conf.token_type, "content": "", "meta": "end", "state": self.state}
                    self.buffer = ""
                    self._reset_state()
        elif self.state.startswith("special_end_"):
            cur_state = self.state.removeprefix("special_end_")
            st_conf = self.token_type_map[cur_state]
            assert st_conf.stream
            assert st_conf.eot_func

            r = st_conf.eot_func(self.buffer + c)
            if r == "match":
                if st_conf.keep_eot:
                    yield {
                        "type": st_conf.token_type,
                        "content": self.buffer + c,
                        "meta": "eot",
                        "state": cur_state,
                    }
                yield {"type": st_conf.token_type, "content": "", "meta": "end", "state": cur_state}
                self.buffer = ""
                self._reset_state()
                return
            elif r == "not_match":
                self.state = cur_state
                yield from self._process(c)
            else:
                self.buffer += c
                return


if __name__ == "__main__":
    from rich import print

    def split_by(text: str, batch: int):
        """
        Split the text into batches of size `batch`.
        """
        if not text:
            return []
        return [text[i : i + batch] for i in range(0, len(text), batch)]

    test_input = '这是一个测试![](example.jpg)包含一些工具调用<tool_call>{"name": "web_search2", "arguments": "hello world2"}</tool_call>\n<tool_call>{"name": "web_search", "arguments": "hello world"}</tool_call>， 以及<image>图片<video>视频<audio>audio_test</audio>mmm</video>haha</image>和以及普通文本'
    
    p = StreamSpecialTokenParser(token_type_map={
            "image": SpecialTokenConfig(
                bot="<image>",
                eot="</image>",
                stream=True,
                sub_special_tokens={
                    "video": SpecialTokenConfig(
                        bot="<video>",
                        eot="</video>",
                        sub_special_tokens={
                            "audio": SpecialTokenConfig(
                                bot="<audio>",
                                eot="</audio>",
                            ),
                        }
                    ),
                }
            ),
            "markdown": SpecialTokenConfig(
                bot="![](",
                eot=")",
                token_type="image",
            ),
            "tool": SpecialTokenConfig(
                bot="<tool_call>",
                eot="</tool_call>",
            ),
        })
    for delta in split_by(test_input, 4):
        print(f"Processing delta: {delta!r}")
        for res in p.postprocess_stream(delta):
            print(res)
