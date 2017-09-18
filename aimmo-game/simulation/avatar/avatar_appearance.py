class AvatarAppearance:
    """
    The presentation aspect of an avatar.
    """

    def __init__(self, body_stroke, body_fill, eye_stroke, eye_fill, gender=None):
        self.body_stroke = body_stroke
        self.body_fill = body_fill
        self.eye_stroke = eye_stroke
        self.eye_fill = eye_fill

        # Make sure the gender input is correct if provided (ie. male or female).
        if gender is not None:
            if gender.lower().lstrip() == 'female' or gender.lower().lstrip() == 'male':
                self.gender = gender
            else:
                raise ValueError('"Gender incorrect! Must be "male" or "female". ')
