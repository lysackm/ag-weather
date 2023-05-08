import traceback

try:
    f = open("jgjkfjgklfjgfdk.txt", "r")
except:
    tb = traceback.format_exc()
    f = open("tb_error.txt", "w")
    f.write(tb)
    f.close()