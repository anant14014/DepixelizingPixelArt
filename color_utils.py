y_threshold = 48
u_threshold = 7
v_threshold = 6

def is_different(color_1, color_2):
    y_diff = abs(color_1[0] - color_2[0])
    u_diff = abs(color_1[1] - color_2[1])
    v_diff = abs(color_1[2] - color_2[2])
    if (y_diff <= y_threshold) and (u_diff <= u_threshold) and (v_diff <= v_threshold):
        return False
    else:
        return True