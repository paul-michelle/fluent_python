import desc_old_fashioned_name_setting_deco as desc_feat_deco
import desc_via_meta


@desc_feat_deco.named_fields
class User:                             # Without class deco: "ValueError: None cannot be an empty string."
    name = desc_feat_deco.NonBlank()    # With class deco: "ValueError: email cannot be an empty string."
    email = desc_feat_deco.NonBlank()

    def __init__(self, name, email):
        self.name = name
        self.email = email


class Consumer(metaclass=desc_via_meta.ModelMeta):

    name = desc_via_meta.NonBlankField()
    email = desc_via_meta.NonBlankField()

    def __init__(self, name, email):
        self.name = name
        self.email = email
