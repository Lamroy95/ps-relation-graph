def interp_value(value, from_interval, to_interval=(10, 100)):
    (a1, a2), (b1, b2) = from_interval, to_interval
    return b1 + ((value - a1) * (b2 - b1) / (a2 - a1))
