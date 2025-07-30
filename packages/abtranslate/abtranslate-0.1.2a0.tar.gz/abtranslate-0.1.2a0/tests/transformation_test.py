from abtranslate.utils.helper  import flatten_list, expand_to_sentence_level, get_structure, apply_structure, is_valid_text
from abtranslate.translator.package import load_argostranslate_model
package = load_argostranslate_model("./tests/example/model_data.argosmodel")

rows = [
    """发动机左侧在飞行前检查中发现有轻微的机油渗漏。技术人员确认渗漏区域位于涡轮壳体附近，并进行了初步清洁。随后安排进一步的检查以确定是否需要更换密封件。

员建议下，更换了左侧发动机的油封并重新紧固相关组件。完成维护后进行了地面试车，未再发现新的渗漏现象。飞机恢复运行状态，记录保留供后续检查使用。""",

    """起落架在落地过程中右侧收回速度明显低于正常值。飞行员报告指示灯延迟亮起约五秒钟，怀疑液压系统响应缓慢。机务团队在停机坪进行了初步排查。

检查结果显示液压油液位偏低，已完成补充。同时对起落架作动筒进行了润滑保养并进行了重复测试。经测试，起落架收放功能恢复正常，未发现进一步异常。"""
]

expanded_sentences = [
    [ # Row 1
        [ # Paragraph 1 in Row 1
            '发动机左侧在飞行前检查中发现有轻微的机油渗漏。', 
            '技术人员确认渗漏区域位于涡轮壳体附近，并进行了初步清洁。', 
            '随后安排进一步的检查以确定是否需要更换密封件。'
        ], 
        #[], (blank) got this if ignore_empty_line=True on fuunction`expand_to_sentence_level` 
        [ # Paragraph 2 in Row 1
            '在机务人员建议下，更换了左侧发动机的油封并重新紧固相关组件。', 
            '完成维护后进行了地面试车，未再发现新的渗漏现象。', 
            '飞机恢复运行状态，记录保留供后续检查使用。']
    ], 
    [ # Row 2
        [ # Paragraph 1 in Row 2
            '起落架在落地过程中右侧收回速度明显低于正常值。', 
            '飞行员报告指示灯延迟亮起约五秒钟，怀疑液压系统响应缓慢。', 
            '机务团队在停机坪进行了初步排查。'
        ], 
        #[],  (blank) got this if ignore_empty_line=True on fuunction`expand_to_sentence_level` 
        [ # Paragraph 2 in Row 2
            '检查结果显示液压油液位偏低，已完成补充。', 
            '同时对起落架作动筒进行了润滑保养并进行了重复测试。', 
            '经测试，起落架收放功能恢复正常，未发现进一步异常。'
        ]
    ]
]

structure = [[3, 3], [3, 3]]

flattened_sentences = [ '发动机左侧在飞行前检查中发现有轻微的机油渗漏。', 
                        '技术人员确认渗漏区域位于涡轮壳体附近，并进行了初步清洁。', 
                        '随后安排进一步的检查以确定是否需要更换密封件。', 
                        '在机务人员建议下，更换了左侧发动机的油封并重新紧固相关组件。', 
                        '完成维护后进行了地面试车，未再发现新的渗漏现象。', 
                        '飞机恢复运行状态，记录保留供后续检查使用。', 
                        '起落架在落地过程中右侧收回速度明显低于正常值。', 
                        '飞行员报告指示灯延迟亮起约五秒钟，怀疑液压系统响应缓慢。', 
                        '机务团队在停机坪进行了初步排查。', 
                        '检查结果显示液压油液位偏低，已完成补充。', 
                        '同时对起落架作动筒进行了润滑保养并进行了重复测试。', 
                        '经测试，起落架收放功能恢复正常，未发现进一步异常。']

tokenized_sentences = [
                        ['▁', '发动机', '左', '侧', '在', '飞行', '前', '检查', '中', '发现', '有', '轻微', '的', '机', '油', '渗', '漏', '。'], 
                        ['▁', '技术人员', '确认', '渗', '漏', '区域', '位于', '涡', '轮', '壳', '体', '附近', ',', '并', '进行了', '初步', '清洁', '。'], 
                        ['▁随后', '安排', '进一步', '的', '检查', '以确定', '是否需要', '更换', '密封', '件', '。'], 
                        ['▁在', '机', '务', '人员', '建议', '下', ',', '更换', '了', '左', '侧', '发动机', '的', '油', '封', '并', '重新', '紧', '固', '相关', '组件', '。'], 
                        ['▁', '完成', '维护', '后', '进行了', '地', '面试', '车', ',', '未', '再', '发现', '新的', '渗', '漏', '现象', '。'], 
                        ['▁', '飞机', '恢复', '运行', '状态', ',', '记录', '保留', '供', '后续', '检查', '使用', '。'], 
                        ['▁', '起', '落', '架', '在', '落', '地', '过程中', '右', '侧', '收回', '速度', '明显', '低于', '正常', '值', '。'], 
                        ['▁', '飞行员', '报告', '指示', '灯', '延迟', '亮', '起', '约', '五', '秒钟', ',', '怀疑', '液', '压', '系统', '响应', '缓慢', '。'], 
                        ['▁', '机', '务', '团队', '在', '停', '机', '坪', '进行了', '初步', '排', '查', '。'], 
                        ['▁', '检查', '结果显示', '液', '压', '油', '液', '位', '偏低', ',', '已完成', '补充', '。'], 
                        ['▁同时', '对', '起', '落', '架', '作', '动', '筒', '进行了', '润', '滑', '保养', '并', '进行了', '重复', '测试', '。'], 
                        ['▁经', '测试', ',', '起', '落', '架', '收', '放', '功能', '恢复正常', ',', '未', '发现', '进一步', '异常', '。']
                    ]

def test_expand_to_sentence_level():
    sentencizer = package.sentencizer
    # print(expand_to_sentence_level(rows, sentencizer))
    expanded = expand_to_sentence_level(rows, sentencizer, ignore_empty_paragraph=True, ignore_empty_row=False)
    struct = get_structure(expanded, ignore_empty=True)
    print(expanded)
    assert struct == structure

def test_flatten_sentences():
    # print(flatten_list(expanded_sentences, inner_type=str))
    assert flatten_list(expanded_sentences, inner_type=str) == flattened_sentences

def test_tokenized_sentences():
    tokenizer = package.tokenizer
    sentences_tok =[]
    for sentence in flattened_sentences:
        sentences_tok.append(tokenizer.encode(sentence))
    # print("Sentence tokenized:\n", sentences_tok)
    assert sentences_tok == tokenized_sentences

def test_detokenized_sentences():
    tokenizer = package.tokenizer
    sentences_detok =[]
    for tokens in tokenized_sentences:
        sentences_detok.append(tokenizer.decode(tokens).replace(",", "，")) 
    print("Sentence detokenized:\n", sentences_detok)
    assert sentences_detok == flattened_sentences

def test_get_structure():
    # print(get_structure(expanded_sentences, ignore_empty=True))
    assert get_structure(expanded_sentences, ignore_empty=True) == structure

def test_apply_structure():
    # print(apply_structure(flattened_sentences, structure))
    assert apply_structure(flattened_sentences, structure) == expanded_sentences

def test_text_validator():
    assert is_valid_text("") == False
    assert is_valid_text("   ") == False
    assert is_valid_text("   ! ") == False
    assert is_valid_text("  .; ! ") == False
    assert is_valid_text("0  .; ! ") == True
    assert is_valid_text("0  .; ab ") == True