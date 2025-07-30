
# 短いIDの生成ツール [slim_id]
# 【動作確認 / 使用例】

import sys
from sout import sout
from ezpip import load_develop
# 短いIDの生成ツール [slim_id]
slim_id = load_develop("slim_id", "../", develop_flag = True)

id_dic = {}

def exists(arg_id):
	return (arg_id in id_dic)

# ID生成 [slim_id]
s_id = slim_id.gen(exists)
id_dic[s_id] = True
print(s_id)

# ID生成 [slim_id]
s_id = slim_id.gen(
	exists,	# 既存のDBに存在するかを判定する関数
	length = 7,	# 基本長 (衝突時には自動的に長くなる)
	ab = "16",	# アルファベットの種類 (base64url...urlセーフな64進数, 16...16進, 文字のリスト...カスタム指定)
)
id_dic[s_id] = True
print(s_id)

# カスタムアルファベット指定
s_id = slim_id.gen(
	exists,	# 既存のDBに存在するかを判定する関数
	length = 7,	# 基本長 (衝突時には自動的に長くなる)
	ab = list("0123456789"),	# アルファベットの種類 (base64url...urlセーフな64進数, 16...16進, 文字のリスト...カスタム指定)
)
id_dic[s_id] = True
print(s_id)
