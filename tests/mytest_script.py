

import io
from rasm_arch import rasm_arch as rasm


if __name__ == "__main__":

    for ori, rlt, rar, pal in rasm(io.StringIO('کُتِب'), paleo=True):
        print(ori, rlt, rar, pal)

    print(10*'-')

    for word, blocks in rasm(((2, 14,15, None), (2, 15, 1, 1)), paleo=True, blocks=True):
        print(word, *blocks[0], sep='\t')
        if len(blocks)>1:
            for block in blocks[1:]:
                print('-', *block, sep='\t')

    print(10*'-')

    for ori, rlt, rar, pal, ind in rasm(((2, 286, 15, None), (None, None, None, None)), paleo=True):
        print(ori, rlt, rar, pal, ind)
