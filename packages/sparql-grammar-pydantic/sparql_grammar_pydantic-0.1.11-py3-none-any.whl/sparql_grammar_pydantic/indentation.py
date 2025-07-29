from typing import Generator, Union
from pydantic import BaseModel
from contextlib import contextmanager
class SPARQLGrammarBase(BaseModel):
    indent_level: int = 0

    @staticmethod
    def indent(level: int) -> str:
        return '    ' * level  # 4 spaces per indent level

    def render(self) -> Generator[str, None, None]:
        raise NotImplementedError

    def increase_indent(self):
        self.indent_level += 1

    def decrease_indent(self):
        self.indent_level -= 1

    def reset_indent(self):
        self.indent_level = 0

    def render_with_indent(self) -> Generator[str, None, None]:
        self.reset_indent()
        yield from self.render()

    def indented_yield(self, text: str) -> Generator[str, None, None]:
        yield f"{self.indent(self.indent_level)}{text}"

class SubSelect(SPARQLGrammarBase):
    def render(self) -> Generator[str, None, None]:
        yield from self.indented_yield("SubSelect content")

class GroupGraphPatternSub(SPARQLGrammarBase):
    def render(self) -> Generator[str, None, None]:
        yield from self.indented_yield("GroupGraphPatternSub content")




class GroupGraphPattern(SPARQLGrammarBase):
    content: Union[SubSelect, GroupGraphPatternSub]

    def render(self) -> Generator[str, None, None]:
        yield from self.indented_yield("{\n")
        self.increase_indent()
        yield from self.content.render()
        self.decrease_indent()
        yield from self.indented_yield("\n}")





def render_query(query: SPARQLGrammarBase) -> str:
    return ''.join(query.render_with_indent())

content = GroupGraphPatternSub()
group_graph_pattern = GroupGraphPattern(content=content)

print(render_query(group_graph_pattern))
