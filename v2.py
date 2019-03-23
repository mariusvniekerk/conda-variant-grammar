
# %%

import yaml
import toolz

from conda_build.utils import ensure_list
import conda_build.variants as variants
from conda.models.version import VersionOrder


def parse_variant(variant_file_str: str, config=None):
    if not config:
        from conda_build.config import Config
        config = Config()
    from conda_build.metadata import select_lines, ns_cfg
    contents = select_lines(variant_file_str, ns_cfg(config), variants_in_place=False)
    content = yaml.load(contents, Loader=yaml.loader.BaseLoader) or {}
    variants.trim_empty_keys(content)
    return content


# %%
v1 = parse_variant("""\
foo:
    - 1.10
bar:
    - 2
""")

v2 = parse_variant("""\
foo:
    - 1.2
bar:
    - 3
""")

v3 = parse_variant("""\
baz:
    - 1
bar:
    - 3
""")

v4 = parse_variant("""\
baz:
    - 1
bar:
    - 0
    - 6
""")


def variant_key_add(k, v_left, v_right, ordering=None):

    def _version_order(v):
        if ordering is not None:
            return ordering.index(v)
        else:
            try:
                return VersionOrder(v)
            except:
                return v


    v_left, v_right = ensure_list(v1[k]), ensure_list(v2[k])
    out_v = []
    common_length = min(len(v_left), len(v_right))
    for i in range(common_length):
        e_l, e_r = v_left[i], v_right[i]
        print(i, e_l, e_r)
        if _version_order(e_l) < _version_order(e_r):
            out_v.append(e_r)
        else:
            out_v.append(e_l)
    # Tail items
    for vs in (v_left, v_right):
        if len(vs) > common_length:
            out_v.extend(vs[common_length:])

    return out_v



def variant_add(v1: dict, v2: dict):
    """Adds the two variants together"""
    left = set(v1.keys()).difference(v2.keys())
    right = set(v2.keys()).difference(v1.keys())

    joint = set(v1.keys()) & set(v2.keys())

    joint_variant = {}
    for k in joint:
        v_left, v_right = ensure_list(v1[k]), ensure_list(v2[k])
        joint_variant[k] = variant_key_add(k, v_left, v_right)

    out = {
        **toolz.keyfilter(lambda k: k in left, v1),
        **toolz.keyfilter(lambda k: k in right, v2),
        **joint_variant
    }

    return out


# %%

variant_add(v1, v2)

# %%

variant_add(v1, v3)

# %%

variant_add(v2, v3)
# %%

variant_add(v1, variant_add(v2, v3))

# %%

variant_add(v1, v4)


# %%

variant_add(v4, v1)