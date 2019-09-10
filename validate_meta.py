import metastring

strs = ['2019-02-21_key1-val1_key2-val2',
        '2019-02-22_key1-val1_key2-val2',
        '2019-02-23_key1--val1_key2-val2',
        '2019-02-24_key1-val1_key2-val2']

valid=[]
for s in strs:
    try:
       metastring.metastring(s)
       valid.append(s)
    except:
        continue

print(valid)
