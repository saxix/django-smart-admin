#  :copyright: Copyright (c) 2018-2021. OS4D Ltd - All Rights Reserved
#  :license: Commercial
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Written by Stefano Apostolico <s.apostolico@gmail.com>, February 2021

def as_bool(value):
    return value not in ["", "0", "None", 0, None, "on"]
