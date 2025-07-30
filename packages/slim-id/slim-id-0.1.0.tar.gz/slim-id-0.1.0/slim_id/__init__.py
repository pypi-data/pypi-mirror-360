
# 短いIDの生成ツール [slim_id]

import sys
import secrets	# 暗号学的乱数生成装置 (ハードウエアエントロピー等を用いて予測不可能にしてある)
from sout import sout

# アルファベット一覧辞書
ab_dic = {
	"16": "0123456789abcdef",
	"base64url": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_",
}

# ab指定から具体的なアルファベットのリストに変換
def get_ab_list(ab):
	# abの形式エラー
	err = Exception("[slim-id error] invalid ab format.")
	# カスタム指定の場合はそのまま受理する
	if type(ab) == type([]):
		ab_list = ab
		for e in ab_list:
			if type(e) != type(""): raise err
			if len(e) != 1: raise err
		return ab_list
	if type(ab) != type(""): raise err
	if ab not in ab_dic: raise err
	ab_list = ab_dic[ab]
	return ab_list

# ID生成 [slim_id]
def gen(
	exists,	# 既存のDBに存在するかを判定する関数
	length = 5,	# 基本長 (衝突時には自動的に長くなる)
	ab = "base64url",	# アルファベットの種類 (base64url...urlセーフな64進数, 16...16進)
):
	if length > 65536: raise Exception("[slim-id error] The maximum length of an ID that can be generated with slim-id is 65536.")
	ab_list = get_ab_list(ab)	# ab指定から具体的なアルファベットのリストに変換
	seq_ls = [secrets.choice(ab_list) for _ in range(length)]
	ret_id = "".join(seq_ls)
	# 衝突時はlengthを長くする
	if exists(ret_id) is True:
		return gen(exists, length + 1, ab)
	return ret_id

# コマンドラインからの利用
def cmd_func():
	# 引数の解釈
	args = {k: int(e) for e, k in zip(sys.argv[1:], "LN")}
	# 生成
	for _ in range(args.get("N", 1)):
		print(gen(
			lambda e: False,
			length = args.get("L", 30),
		))
