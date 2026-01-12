import json
import os
from datetime import datetime

def load_json(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def generate_new_report():
    standalone_data = load_json('variable_comparison.json')
    cluster_data = load_json('cluster_variable_comparison.json')
    test_results_data = load_json('test_results.json') # For general test summary if needed

    report_path = os.path.join(os.path.dirname(__file__), '../../docs/mysql_version_diff_test_new_report.md')

    report_lines = [
        f"# MySQL 8.0 vs 8.4 통합 비교 리포트 (Standalone & Cluster)",
        f"> **보고서 생성일:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "\n## 1. 개요",
        "본 리포트는 Standalone 환경과 InnoDB Cluster 환경에서의 MySQL 8.0.42와 8.4.7 버전 간 차이점을 통합 분석한 결과입니다.",
    ]
    
    # Check if data exists
    if not standalone_data or not cluster_data:
        report_lines.append("\n> **주의:** 비교 데이터 파일이 일부 누락되었습니다. 테스트를 모두 실행했는지 확인하세요.")
        if not standalone_data: report_lines.append("- `variable_comparison.json` (Standalone) 누락")
        if not cluster_data: report_lines.append("- `cluster_variable_comparison.json` (Cluster) 누락")
    
    if standalone_data and cluster_data:
        s_diff = standalone_data.get('different_values', {})
        c_diff = cluster_data.get('different_values', {})
        
        # Classification
        version_driven = {}
        cluster_driven = {}
        
        all_diff_keys = set(s_diff.keys()) | set(c_diff.keys())
        
        for key in all_diff_keys:
            in_s = key in s_diff
            in_c = key in c_diff
            
            if in_s and in_c:
                # In both. Check if values are same
                s_val80 = s_diff[key]['mysql80']
                s_val84 = s_diff[key]['mysql84']
                c_val80 = c_diff[key]['mysql80']
                c_val84 = c_diff[key]['mysql84']
                
                if s_val80 == c_val80 and s_val84 == c_val84:
                    version_driven[key] = s_diff[key]
                else:
                    # Values differ between Standalone and Cluster, so it's interesting.
                    # Maybe categorize as "Environment Dependent" or treat as Cluster Driven nuance
                    cluster_driven[key] = {
                        "mysql80": c_val80,
                        "mysql84": c_val84,
                        "note": f"Standalone: {s_val80} -> {s_val84}"
                    }
            elif in_s and not in_c:
                # Only in Standalone. Why? Maybe Cluster config forced them to be same?
                # Or maybe my logic is inverted.
                # If it's diff in Standalone but NOT in Cluster, it means Cluster config normalized it?
                # Still Version Driven but overridden by Cluster?
                # Let's list it as Version Driven (Standalone Only)
                version_driven[key] = s_diff[key] 
                version_driven[key]['note'] = "Standalone Only"
            elif not in_s and in_c:
                # Only in Cluster. This is purely Cluster Driven.
                cluster_driven[key] = c_diff[key]

        # --- Section 2: Version-driven Diff ---
        report_lines.append(f"\n## 2. Version-driven Diff (기본 버전 차이)")
        report_lines.append("Standalone 환경과 Cluster 환경에서 공통적으로 관찰되거나, MySQL 버전 업그레이드 자체에 기인한 변경 사항입니다.")
        report_lines.append(f"\n 총 **{len(version_driven)}** 개의 파라미터가 변경되었습니다.")
        
        report_lines.append("\n| 변수명 | MySQL 8.0 | MySQL 8.4 | 비고 |")
        report_lines.append("|---|---|---|---|")
        for key, val in sorted(version_driven.items()):
            note = val.get('note', '')
            report_lines.append(f"| `{key}` | {val['mysql80']} | {val['mysql84']} | {note} |")

        # --- Section 3: Cluster-driven Diff ---
        report_lines.append(f"\n## 3. Cluster-driven Diff (클러스터 환경 특화)")
        report_lines.append("InnoDB Cluster 구성으로 인해 추가적으로 발생하거나 변경된 파라미터입니다. (Primary Node 기준)")
        report_lines.append(f"\n 총 **{len(cluster_driven)}** 개의 파라미터가 변경되었습니다.")
        
        report_lines.append("\n| 변수명 | MySQL 8.0 (Cluster) | MySQL 8.4 (Cluster) | 비고 |")
        report_lines.append("|---|---|---|---|")
        for key, val in sorted(cluster_driven.items()):
            note = val.get('note', '')
            report_lines.append(f"| `{key}` | {val['mysql80']} | {val['mysql84']} | {note} |")

    # Write Report
    with open(report_path, 'w') as f:
        f.write("\n".join(report_lines))
    
    print(f"Report generated: {report_path}")

if __name__ == "__main__":
    generate_new_report()
