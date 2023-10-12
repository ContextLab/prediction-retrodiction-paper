import numpy as np
# import tensorflow as tf
# import tensorflow_hub as hub

# embed1 = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

# def cal_similarity(text1, text2, method='cosine', embed=embed1):
    
#     if isinstance(text1, str):
#         text1 = [text1]
#     if isinstance(text2, str):
#         text2 = [text2]

#     v1 = embed(text1)[0]
#     v2 = embed(text2)[0]
    
#     if method == 'cosine':  # range:(-1,1)
#         similarity = np.inner(v1,v2)
#     elif method == 'angle':  # range:(0,1)
#         similarity = 1 - np.arccos(np.clip(np.inner(v1,v2), -1 ,1)) / np.pi
#     return similarity

def to_str(num):
    if num < 10:
        return '0'+str(num)
    else:
        return str(num)