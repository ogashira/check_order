from typing import List

class GetIdx:

    @staticmethod
    def get_idx(col: List[str], col_name: str)-> int:
        idx: int = -1
        if not col:
            return idx
        if not col_name:
            return idx

        for i, code in enumerate(col):
            if code == col_name:
                idx = i
                break
        
        return idx

