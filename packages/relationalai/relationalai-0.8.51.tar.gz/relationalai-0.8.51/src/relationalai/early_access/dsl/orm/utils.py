import re

from relationalai.early_access.dsl.constants import VERBAL_PART_CONNECTION
from relationalai.early_access.dsl.core.utils import camel_to_snake, to_rai_way_string


# Re-adjusted code from dsl/utils.py - that version was used in the dsl
def build_relation_name_from_reading(reading):
    roles = re.findall(r'\{([^}]+)}', reading)
    text_without_concepts = re.sub(r'\{[^}]+}', '|', reading)
    verbal_parts = [text.strip() for text in text_without_concepts.split('|') if text.strip()]

    # Handle postfix on the first player
    if verbal_parts[0].startswith("-"):
    #     postfix = verbal_parts[0].split(" ")[0]
        verbal_parts[0] = verbal_parts[0].replace("-", "")
    # Handle prefix on the first player
    elif "-" in verbal_parts[0].split(" ")[0]:
        verbal_parts.remove(verbal_parts[0])

    rel_name = ""
    if len(roles) == 1:
        if len(verbal_parts) > 0:
            rel_name = to_rai_way_string(verbal_parts[0])
            rel_name = rel_name.replace("_is_", "_")
        if not rel_name:
            rel_name = camel_to_snake(roles[0])
    elif len(roles) == 2:
        s_role = roles[1]
        if len(verbal_parts) > 0:
            rel_name = to_rai_way_string(verbal_parts[0])
            if (verbal_parts[0].strip().startswith(("has", "is")) and not rel_name) or rel_name.endswith("_"):
                    rel_name += camel_to_snake(s_role)
            elif rel_name.endswith("has"):
                rel_name = rel_name.replace("has", camel_to_snake(s_role))
            elif rel_name.endswith("is"):
                rel_name = rel_name.replace("is", camel_to_snake(s_role))
        if verbal_parts[len(verbal_parts)-1].startswith("-"):
            rel_name += to_rai_way_string(verbal_parts[len(verbal_parts)-1])
    else:
        join_parts = [to_rai_way_string(verbal_parts[0], False)]
        for i in range(1, len(roles)):
            role = roles[i]
            if not join_parts[len(join_parts) - 1].endswith(camel_to_snake(role)):
                join_parts.append(camel_to_snake(role.split(":")[0])) # take a role name instead of type if any
            if i < len(roles) - 1 or i < len(verbal_parts):
                if verbal_parts[i].startswith("-"):
                    join_parts.append(to_rai_way_string(verbal_parts[i][1:], False))
                elif verbal_parts[i].endswith("-"):
                    join_parts.append(to_rai_way_string(verbal_parts[i][:-1], False))
                else:
                    join_parts.append(to_rai_way_string(verbal_parts[i], False))
        rel_name = VERBAL_PART_CONNECTION.join(join_parts)
    return rel_name
