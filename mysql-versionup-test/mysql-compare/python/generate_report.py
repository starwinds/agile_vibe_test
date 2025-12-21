import json
import os
from datetime import datetime

def generate_report():
    """Generates a markdown report from the test_results.json file."""
    
    json_path = os.path.join(os.path.dirname(__file__), 'test_results.json')
    report_path = os.path.join(os.path.dirname(__file__), '../../docs/mysql_version_diff_test_report.md')

    with open(json_path, 'r') as f:
        data = json.load(f)

    # --- Data Processing ---
    failures = []
    perf_results = {"mysql80": {}, "mysql84": {}}

    for test in data['tests']:
        if test['outcome'] == 'failed':
            failures.append(test)
        
        if test['outcome'] == 'passed' and 'test_perf_simple' in test['nodeid']:
            version = 'mysql80' if '[mysql80]' in test['nodeid'] else 'mysql84'
            
            # Extract data from user_properties
            if 'user_properties' in test:
                for prop_dict in test['user_properties']:
                    if 'tps' in prop_dict:
                        perf_results[version]['tps'] = prop_dict['tps']
                    if 'avg_latency_ms' in prop_dict:
                        perf_results[version]['latency'] = prop_dict['avg_latency_ms']

    # --- Report Generation ---
    report_lines = [
        f"# MySQL 8.0.42 vs 8.4.7 비교 테스트 자동화 보고서",
        f"**보고서 생성일:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"\n## 1. 테스트 요약",
        f"- **전체 테스트:** {data['summary']['total']}",
        f"- **성공:** {data['summary']['passed']}",
        f"- **실패:** {data['summary']['failed']}",
        f"- **실행 시간:** {data['duration']:.2f}초",
        "\n## 2. 주요 차이점 분석 (실패 항목)",
    ]

    if not failures:
        report_lines.append("\n모든 테스트를 통과했습니다. 주요 버전 차이점이 발견되지 않았습니다.")
    else:
        report_lines.append("\n| 테스트 분류 | 내용 |\n|---|---|\n")
        for failure in failures:
            test_name = failure['nodeid'].split('::')[-1]
            category = "알 수 없음"
            if 'authentication' in test_name:
                category = "인증 (Authentication)"
            elif 'variable' in test_name:
                category = "시스템 변수 (System Variable)"
            
            message = failure['call']['crash']['message']
            report_lines.append(f"| **{category}** | `{test_name}`<br>{message} |")

    report_lines.append("\n## 3. 성능 테스트 결과 (경향성)")
    report_lines.append("\n| 측정 항목 | MySQL 8.0.42 | MySQL 8.4.7 | 비교 |\n|---|---|---|---|\n")
    
    tps80 = perf_results['mysql80'].get('tps', 0)
    tps84 = perf_results['mysql84'].get('tps', 0)
    tps_diff = "N/A"
    if tps80 > 0 and tps84 > 0:
        tps_diff = f"{((tps84 - tps80) / tps80) * 100:+.2f}%"
    report_lines.append(f"| Insert TPS (높을수록 좋음) | {tps80:,.2f} | {tps84:,.2f} | **{tps_diff}** |")

    lat80 = perf_results['mysql80'].get('latency', 0)
    lat84 = perf_results['mysql84'].get('latency', 0)
    lat_diff = "N/A"
    if lat80 > 0 and lat84 > 0:
        lat_diff = f"{((lat84 - lat80) / lat80) * 100:+.2f}%"
    report_lines.append(f"| Select Latency (ms) (낮을수록 좋음) | {lat80:.4f} | {lat84:.4f} | **{lat_diff}** |")


    # --- Write File ---
    with open(report_path, 'w') as f:
        f.write("\n".join(report_lines))

    print(f"보고서가 성공적으로 생성되었습니다: {report_path}")

if __name__ == "__main__":
    generate_report()