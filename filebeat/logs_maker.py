text = ""
line = ""
for i in range(10000):
    line += "randomtext"

for i in range(10**2):
    text += line + "\n"

for i in range(10**10):
    f = open("logs_input_txt/input_log_" + str(i) + ".txt", "w")
    f.write(text)
    f.close()

