
import json
import os
from common_db import get_db_connection, execute_query

def get_global_variables(version):
    """지정된 버전의 MySQL에서 모든 글로벌 변수를 가져옵니다."""
    conn = get_db_connection(version)
    if not conn:
        print(f"{version}에 연결할 수 없습니다.")
        return None
    
    try:
        variables_list = execute_query(conn, "SHOW GLOBAL VARIABLES", fetch='all')
        # 변수 목록을 딕셔너리로 변환
        variables_dict = {row[0]: row[1] for row in variables_list}
        return variables_dict
    finally:
        if conn.is_connected():
            conn.close()

def compare_variables():
    """두 MySQL 버전의 글로벌 변수를 비교하고 결과를 JSON 파일에 저장합니다."""
    vars80 = get_global_variables('mysql80')
    vars84 = get_global_variables('mysql84')

    if not vars80 or not vars84:
        print("하나 이상의 버전에서 변수를 가져오는 데 실패했습니다.")
        return

    vars80_set = set(vars80.keys())
    vars84_set = set(vars84.keys())

    only_in_80 = sorted(list(vars80_set - vars84_set))
    only_in_84 = sorted(list(vars84_set - vars80_set))
    
    different_values = {}
    common_vars = vars80_set.intersection(vars84_set)
    
    for var in sorted(list(common_vars)):
        # 비교가 의미 없는 동적 값들은 건너뜁니다.
        if var in ['gtid_executed', 'version_comment', 'version', 'hostname', 'report_host', 'server_uuid']:
            continue
            
        val80 = str(vars80[var])
        val84 = str(vars84[var])

        if val80 != val84:
            different_values[var] = {
                "mysql80": val80,
                "mysql84": val84
            }

    results = {
        "summary": {
            "total_in_80": len(vars80),
            "total_in_84": len(vars84),
            "only_in_80": len(only_in_80),
            "only_in_84": len(only_in_84),
            "different_values": len(different_values)
        },
        "only_in_80": only_in_80,
        "only_in_84": only_in_84,
        "different_values": different_values
    }

    output_path = os.path.join(os.path.dirname(__file__), 'variable_comparison.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"변수 비교 결과가 '{output_path}'에 저장되었습니다.")

if __name__ == "__main__":
    compare_variables()
