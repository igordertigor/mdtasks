import io

from mdtasks.schema import FrontMatter
from yaml import safe_dump


def render(
    frontmatter: FrontMatter, content: str | None = None, use_full_spec: bool = False
) -> str:
    buf = io.StringIO()
    safe_dump(frontmatter.model_dump(exclude_none=not use_full_spec), buf)
    fragments = [
        "---",
        buf.getvalue().strip(),
        "---",
    ]
    if content:
        fragments.append(content)
    else:
        fragments.extend(
            [
                "",
                "# <TITLE>",
                "",
                "As a <WHO>,",
                "I want <WHAT>",
                "so that <WHY>",
                "",
                "## Implementation notes",
            ]
        )
    return "\n".join(fragments)
