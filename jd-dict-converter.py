# All.txt，存放需要转换的词组，每行一词，支持两种格式：
#   1. 纯词组：每行一个词组
#   2. 词组+编码：词组\t编码（只提取词组部分）
# jdx.csv，单字的首笔形码，用的 RIME_JD 的单字码表
# jdAllx.csv，最后得到的键道音形码文件

# 导入需要的模块
import glob
import re, csv, os
from pypinyin import lazy_pinyin, Style

print('正在处理，请稍等……（参考： 平均1万词大约10秒时间，转化完成后，窗口会自动关闭）')

# 判断文件是否存在
file_list = ['jdAll.csv', 'jdAllx.csv', 'jdf.csv', 'jdy.csv', 'jdyf.csv', 'pinyin.csv', '已有字词.txt', '已有编码.txt', 'result.dict.yaml']
for file in file_list:
    if os.path.exists(file):
        os.remove(file)

# 把词组存储到 Alltxt 列表中，支持"词组"或"词组\t编码"两种格式
with open('./All.txt', 'r', encoding='UTF-8-SIG') as f:
    Alltxt = []
    for line in f:
        line = line.rstrip()
        if not line:  # 跳过空行
            continue
        # 如果包含制表符，只取第一部分（词组）
        if '\t' in line:
            word = line.split('\t')[0]
            Alltxt.append(word)
        else:
            Alltxt.append(line)

# 使用 pypinyin 为词组注音，并写入 pinyin.csv（不使用多音字，避免pypinyin数据错误）
with open('pinyin.csv', 'w', encoding='UTF-8') as Allpinyin:
    for ci in Alltxt:
        if not ci:  # 跳过空词
            continue

        # 使用默认读音（不使用heteronym，避免错误读音）
        sh = lazy_pinyin(ci, style=Style.INITIALS, strict=False, errors='ignore')
        un = lazy_pinyin(ci, style=Style.FINALS, strict=False, errors='ignore')
        Allpinyin.write(ci + '\t')
        for s, u in zip(sh, un):
            Allpinyin.write(s + '\'' + u + '\t')
        Allpinyin.write('\n')

# 提取含飞键的词组到 jdf.csv，以便另外处理
# 将全拼词组变为列表
with open('pinyin.csv', 'r', encoding='UTF-8') as file1:
    data1 = file1.readlines()
# 提取飞键（识别所有 ch/zh/sh + 'uang 需要双编码）
with open('jdf.csv', 'w', encoding='UTF-8') as file2:
    for line in data1:
        # ch/zh/sh + 'uang 都需要双编码（w/f/e + x 和 w/f/e + m）
        n = re.findall(r".*\t(ch|zh|sh)'uang\t.*", line)
        if n:
            file2.writelines(line)

# 准备把全拼转成键道双拼
dict1 = {'\t\'':'\tx\'', '\tj\'u\t':'\tjl\t', '\tq\'u\t':'\tql\t', '\tx\'u\t':'\txl\t', '\ty\'u\t':'\tyl\t'} # 零声母引导
dict2 = {'\'iu\t':'q\t', '\'ua\t':'q\t', '\'ei\t':'w\t', '\'un\t':'w\t', '\'e\t':'e\t', '\'eng\t':'r\t', '\'uan\t':'t\t', '\'iong\t':'y\t', '\'ong\t':'y\t', '\'ang\t':'p\t', '\'a\t':'s\t', '\'ia\t':'s\t', '\'ie\t':'d\t', '\'ou\t':'d\t', '\'an\t':'f\t', '\'ing\t':'g\t', '\'uai\t':'g\t', '\'ai\t':'h\t', '\'ue\t':'h\t', '\'ve\t':'h\t', '\'er\t':'j\t', '\'u\t':'j\t', '\'i\t':'k\t', '\'o\t':'l\t', '\'uo\t':'l\t', '\'v\t':'l\t', '\'ao\t':'z\t', '\'iang\t':'x\t', '\'iao\t':'c\t', '\'in\t':'b\t', '\'ui\t':'b\t', '\'en\t':'n\t', '\'n\t':'n\t', '\'ian\t':'m\t'} # 韵母

# 飞键韵母的两种编码(关键是 uang 的双编码)
fj_yunmu_1 = {"'uang\t":'m\t', "'ai\t":'h\t', "'an\t":'f\t', "'ang\t":'p\t', "'en\t":'n\t', "'eng\t":'r\t', "'u\t":'j\t', "'un\t":'w\t', "'a\t":'s\t', "'i\t":'k\t', "'ong\t":'y\t', "'ou\t":'d\t', "'ua\t":'q\t', "'uai\t":'g\t', "'uan\t":'t\t', "'ui\t":'b\t', "'uo\t":'l\t', "'ao\t":'z\t', "'e\t":'e\t', "'ei\t":'w\t'}  # 飞键韵母变体1(uang→m)
fj_yunmu_2 = {"'uang\t":'x\t', "'ai\t":'h\t', "'an\t":'f\t', "'ang\t":'p\t', "'en\t":'n\t', "'eng\t":'r\t', "'u\t":'j\t', "'un\t":'w\t', "'a\t":'s\t', "'i\t":'k\t', "'ong\t":'y\t', "'ou\t":'d\t', "'ua\t":'q\t', "'uai\t":'g\t', "'uan\t":'t\t', "'ui\t":'b\t', "'uo\t":'l\t', "'ao\t":'z\t', "'e\t":'e\t', "'ei\t":'w\t'}  # 飞键韵母变体2(uang→x)
# 把词组列表转换为字符串
allPY = "".join(data1)
# 先将特殊编码及零声母搞定
for k, v in dict1.items():
    allPY = allPY.replace(k, v)
# 固定飞键替换
allPY = re.sub("\t(ch)(\')(u)\t", r"\tj\2\3\t", allPY)  # chu → j'u
allPY = re.sub("\t(ch)(\')(ai|ao|an|ang|en|eng|un)\t", r"\tj\2\3\t", allPY)
allPY = re.sub("\t(ch)(\')(a|e|i|ong|ou|ua|uai|uan|uang|ui|uo)\t", r"\tw\2\3\t", allPY)
allPY = re.sub("\t(zh)(\')(u)\t", r"\tq\2\3\t", allPY)  # zhu → q'u
allPY = re.sub("\t(zh)(\')(ai|ao|an|ang|ei|en|eng|un)\t", r"\tq\2\3\t", allPY)
allPY = re.sub("\t(zh)(\')(a|e|i|ong|ou|ua|uai|uan|uang|ui|uo)\t", r"\tf\2\3\t", allPY)
allPY = re.sub("\t(sh)(')", r"\te\2", allPY)
# 飞键韵母替换（使用 fj_yunmu_1，uang→m）（按长度从长到短排序）
for k, v in sorted(fj_yunmu_1.items(), key=lambda x: len(x[0]), reverse=True):
    allPY = allPY.replace(k, v)
# 韵母替换（按长度从长到短排序，避免短韵母破坏长韵母）
for k, v in sorted(dict2.items(), key=lambda x: len(x[0]), reverse=True):
    allPY = allPY.replace(k, v)
# 将键道音码存入 jdy.csv 文件
with open('jdy.csv', 'w', encoding='UTF-8-sig') as file2:
    file2.write(allPY)

# 不管了，直接飞键再运行一遍
with open('jdf.csv', 'r', encoding='UTF-8') as file3:
    data3 = file3.readlines()
allPYf = "".join(data3)
# # 先将特殊编码及零声母搞定
for k, v in dict1.items():
    allPYf = allPYf.replace(k, v)
# # 固定飞键替换
allPYf = re.sub("\t(ch)(\')(u)\t", r"\tj\2\3\t", allPYf)  # chu → j'u
allPYf = re.sub("\t(ch)(\')(ai|ao|an|ang|en|eng|un)\t", r"\tj\2\3\t", allPYf)
allPYf = re.sub("\t(ch)(\')(a|e|i|ong|ou|ua|uai|uan|uang|ui|uo)\t", r"\tw\2\3\t", allPYf)
allPYf = re.sub("\t(zh)(\')(u)\t", r"\tq\2\3\t", allPYf)  # zhu → q'u
allPYf = re.sub("\t(zh)(\')(ai|ao|an|ang|ei|en|eng|un)\t", r"\tq\2\3\t", allPYf)
allPYf = re.sub("\t(zh)(\')(a|e|i|ong|ou|ua|uai|uan|uang|ui|uo)\t", r"\tf\2\3\t", allPYf)
allPYf = re.sub("\t(sh)(')", r"\te\2", allPYf)
# # 飞键韵母替换（使用 fj_yunmu_2，uang→x）（按长度从长到短排序）
for k, v in sorted(fj_yunmu_2.items(), key=lambda x: len(x[0]), reverse=True):
    allPYf = allPYf.replace(k, v)
    
# # 韵母替换（按长度从长到短排序，避免短韵母破坏长韵母）
for k, v in sorted(dict2.items(), key=lambda x: len(x[0]), reverse=True):
    allPYf = allPYf.replace(k, v)
# # 将键道音码存入 jdy.csv 文件
with open('jdyf.csv', 'w', encoding='UTF-8-sig') as file4:
    file4.write(allPYf)

# 输出音形码 - 同时处理标准编码和飞键编码以保持顺序
# 先读取所有标准编码和飞键编码到字典
jdy_dict = {}  # word -> standard_code
jdyf_dict = {}  # word -> flying_key_code

def process_row_to_code(row):
    """将 CSV 行转换为编码"""
    if len(row) == 3:  # 二字词
        try:
            sy1 = row[1][:2]
            sy2 = row[2][:2]
            return sy1+sy2
        except:
            return None
    elif len(row) == 4:  # 三字词
        try:
            s1 = row[1][:1]
            s2 = row[2][:1]
            s3 = row[3][:1]
            return s1+s2+s3
        except:
            return None
    elif len(row) == 5:  # 四字词
        try:
            s1 = row[1][:1]
            s2 = row[2][:1]
            s3 = row[3][:1]
            s4 = row[4][:1]
            return s1+s2+s3+s4
        except:
            return None
    elif len(row) > 5:  # 五字及以上词
        try:
            s1 = row[1][:1]
            s2 = row[2][:1]
            s3 = row[3][:1]
            s4 = row[-1][:1]  # 最后一个字
            return s1+s2+s3+s4
        except:
            return None
    return None

# 读取标准编码
with open('jdy.csv', 'r', newline="", encoding='UTF-8-sig') as csvf:
    rows = csv.reader(csvf, dialect=csv.excel_tab)
    for row in rows:
        while row and row[-1] == '':
            row.pop()
        if row:
            code = process_row_to_code(row)
            if code:
                jdy_dict[row[0]] = code

# 读取飞键编码
with open('jdyf.csv', 'r', newline="", encoding='UTF-8-sig') as csvf:
    rows = csv.reader(csvf, dialect=csv.excel_tab)
    for row in rows:
        while row and row[-1] == '':
            row.pop()
        if row:
            code = process_row_to_code(row)
            if code:
                jdyf_dict[row[0]] = code

# 按照 pinyin.csv 的顺序输出，这样保持 All.txt 的原始顺序
# 同时为每个词输出标准编码和飞键编码(如果存在)
with open('pinyin.csv', 'r', encoding='UTF-8') as f:
    with open('jdAll.csv', 'w', encoding='UTF-8-sig') as jda:
        for line in f:
            word = line.split('\t')[0]
            # 先写标准编码(m变体)
            if word in jdy_dict:
                jda.write(f"{word}\t{jdy_dict[word]}\n")
            # 再写飞键编码(x变体)，紧跟在标准编码后面
            if word in jdyf_dict:
                code_jdy = jdy_dict.get(word, '')
                code_jdyf = jdyf_dict[word]
                # 只有当编码不同时才写入飞键编码
                if code_jdy != code_jdyf:
                    jda.write(f"{word}\t{code_jdyf}\n")

# 去除追加飞键中对编码无影响的三词及以上的 'uang'
# 注意：二字词需要保留双编码（m和x两种），三字及以上只保留一个
# 使用手动去重保持 All.txt 的原始顺序
seen_entries = set()  # 用于去重
result_lines = []

with open('jdAll.csv', 'r', encoding='UTF-8-sig') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        parts = line.split('\t')
        if len(parts) != 2:
            continue

        word = parts[0].replace('\ufeff', '').strip()
        code = parts[1].strip()

        # 跳过分隔行
        if word.startswith('#'):
            continue

        # 二字词：保留所有不同的编码（双编码）
        if len(code) == 4:
            key = f"{word}_{code}"
            if key not in seen_entries:
                seen_entries.add(key)
                result_lines.append(f"{word}\t{code}\n")
        # 三字及以上词：只保留第一个编码（去重）
        else:
            if word not in seen_entries:
                seen_entries.add(word)
                result_lines.append(f"{word}\t{code}\n")

# 写回文件，保持原始顺序
with open('jdAll.csv', 'w', encoding='UTF-8-sig') as f:
    f.writelines(result_lines)

# 将首笔对应码转为字典
dictx = {}
with open('jdx.csv', 'r+', encoding='UTF-8') as f:
    reader=csv.reader(f, dialect=csv.excel_tab)
    for row in reader:
        dictx[row[0]]=row[1]

# 开始添加形码，最核心、最常用的词库可以不加形码以降低码长
# 把音码存为列表
with open('jdAll.csv', 'r', encoding='UTF-8-sig') as file:
    datax = file.readlines()

# 添加形码
with open('jdAllx.csv', 'w', encoding='UTF-8') as jdAllx:
    for cizu in datax:
        # 跳过飞键分割线（格式: #飞键 + tab + 长编码）
        if cizu.startswith('#飞键'):
            jdAllx.write(cizu)
            continue

        # 分割词组和编码
        parts = cizu.strip().split('\t')
        if len(parts) != 2:
            continue

        word, code = parts[0], parts[1]

        # 三字词：添加3个形码
        if len(word) == 3:
            try:
                x1 = dictx[word[0]]
                x2 = dictx[word[1]]
                x3 = dictx[word[2]]
                jdAllx.write(f"{word}\t{code}{x1}{x2}{x3}\n")
            except Exception as e:
                # 字不在形码表中，跳过
                pass
        # 二字词或其他：添加2个形码
        else:
            try:
                x1 = dictx[word[0]]
                x2 = dictx[word[1]]
                jdAllx.write(f"{word}\t{code}{x1}{x2}\n")
            except Exception as e:
                # 字不在形码表中，跳过
                pass

#####################
### Added by Ivan ###
#####################

pattern = r'^.*\t[a-z]*'
output_zc_file = "./已有字词.txt"
output_bm_file = "./已有编码.txt"

# 1. 获取已有的编码和字词
file_list = [output_zc_file, output_bm_file]
for file in file_list:
    if os.path.exists(file):
        os.remove(file)

# 打开输出文件
with open(output_bm_file, 'w', encoding='utf-8') as outfile_bm, open(output_zc_file, 'w', encoding='utf-8') as outfile_zc:
    # 遍历目录下的所有yaml文件
    for filename in glob.glob('./*.dict.yaml'):
        # 打开yaml文件
        with open(filename, 'r', encoding='utf-8') as infile:
            # 读取yaml文件中的所有行
            lines = infile.readlines()

            # 标记是否在需要跳过的 region 内部
            in_skip_region = False
            separator_found = False

            for line in lines:
                # 检测到 ... 分隔符
                if line.strip() == '...':
                    separator_found = True
                    continue

                # 只处理 ... 之后的内容
                if not separator_found:
                    continue

                # 检测需要跳过的 #region（简字、简码等）
                # 只跳过包含"简"字的 region
                if line.strip().startswith('#region') and '简' in line:
                    in_skip_region = True
                    continue

                # 检测 #endregion 结束
                if line.strip().startswith('#endregion') and in_skip_region:
                    in_skip_region = False
                    continue

                # 在需要跳过的 region 内部，跳过
                if in_skip_region:
                    continue

                # 跳过普通注释行和 region 标记行
                if line.strip().startswith('#'):
                    continue

                # 匹配正则表达式，将匹配结果写入输出文件
                if re.search(pattern, line):
                    outfile_bm.write(line.split("\t")[1])      # 编码文件写入编码
                    outfile_zc.write(line.split("\t")[0]+"\n") # 字词文件写入字词

# 2. 读取 已有编码.txt 文件中的内容，存储在集合中
with open(output_bm_file, 'r', encoding='utf-8') as f:
    bm_set = set(line.strip() for line in f)

# 3. 读取 已有字词.txt 文件中的内容，存储在集合中
with open(output_zc_file, 'r', encoding='utf-8') as f:
    zc_set = set(line.strip() for line in f)

temp_list = []  # 使用列表保持 All.txt 的原始顺序
temp_set_dedup = set()  # 用于去重检查
bm_repe_set = set()  # 用于记录当前转换过程中已使用的编码

with open('jdAllx.csv', 'r', encoding='utf-8') as file:
    for line in file:
        parts = line.strip().split('\t')
        if len(parts) != 2:
            continue
        word, line_bm = parts

        # 核心排除逻辑：如果词组已存在于 .dict.yaml 中，直接跳过整个词组
        if word in zc_set:
            continue

        # 处理词组 3 字, 3码空码动态匹配到 6 码
        if len(word) == 3:
            # 检查编码是否在 .dict.yaml 或当前转换中已存在，如果存在就顺延
            if line_bm[0:3] not in bm_set and line_bm[0:3] not in bm_repe_set:
                entry = f"{word}\t{line_bm[0:3]}"
                if entry not in temp_set_dedup:
                    temp_list.append(entry)
                    temp_set_dedup.add(entry)
                    bm_repe_set.add(line_bm[0:3])
            elif line_bm[0:4] not in bm_set and line_bm[0:4] not in bm_repe_set:
                entry = f"{word}\t{line_bm[0:4]}"
                if entry not in temp_set_dedup:
                    temp_list.append(entry)
                    temp_set_dedup.add(entry)
                    bm_repe_set.add(line_bm[0:4])
            elif line_bm[0:5] not in bm_set and line_bm[0:5] not in bm_repe_set:
                entry = f"{word}\t{line_bm[0:5]}"
                if entry not in temp_set_dedup:
                    temp_list.append(entry)
                    temp_set_dedup.add(entry)
                    bm_repe_set.add(line_bm[0:5])
            elif line_bm[0:6] not in bm_set and line_bm[0:6] not in bm_repe_set:
                entry = f"{word}\t{line_bm[0:6]}"
                if entry not in temp_set_dedup:
                    temp_list.append(entry)
                    temp_set_dedup.add(entry)
                    bm_repe_set.add(line_bm[0:6])
            else:
                # 3、4、5、6码都被占用（.dict.yaml或当前转换中），放在6码位置（允许重码）
                entry = f"{word}\t{line_bm[0:6]}"
                if entry not in temp_set_dedup:
                    temp_list.append(entry)
                    temp_set_dedup.add(entry)
        # 处理其它长度的字词, 4码空码动态匹配到 6 码
        else:
            # 检查编码是否在 .dict.yaml 或当前转换中已存在，如果存在就顺延
            if line_bm[0:4] not in bm_set and line_bm[0:4] not in bm_repe_set:
                entry = f"{word}\t{line_bm[0:4]}"
                if entry not in temp_set_dedup:
                    temp_list.append(entry)
                    temp_set_dedup.add(entry)
                    bm_repe_set.add(line_bm[0:4])
            elif line_bm[0:5] not in bm_set and line_bm[0:5] not in bm_repe_set:
                entry = f"{word}\t{line_bm[0:5]}"
                if entry not in temp_set_dedup:
                    temp_list.append(entry)
                    temp_set_dedup.add(entry)
                    bm_repe_set.add(line_bm[0:5])
            elif line_bm[0:6] not in bm_set and line_bm[0:6] not in bm_repe_set:
                entry = f"{word}\t{line_bm[0:6]}"
                if entry not in temp_set_dedup:
                    temp_list.append(entry)
                    temp_set_dedup.add(entry)
                    bm_repe_set.add(line_bm[0:6])
            else:
                # 4、5、6码都被占用（.dict.yaml或当前转换中），放在6码位置（允许重码）
                entry = f"{word}\t{line_bm[0:6]}"
                if entry not in temp_set_dedup:
                    temp_list.append(entry)
                    temp_set_dedup.add(entry)

content = '''---
name: xkjd6.result
version: "v1"
sort: original
...
'''

with open('./result.dict.yaml', 'w', encoding='utf-8') as outfile:
    outfile.write(content)
    for line in temp_list:  # 使用 temp_list 保持 All.txt 的原始顺序
        outfile.write(line+"\n")