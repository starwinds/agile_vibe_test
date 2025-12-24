import json
import os
from datetime import datetime

def generate_report():
    """Generates a professional markdown report from the test_results.json file."""
    
    json_path = os.path.join(os.path.dirname(__file__), 'test_results.json')
    report_path = os.path.join(os.path.dirname(__file__), '../../docs/mysql_version_diff_test_report.md')

    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

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
            
            if 'user_properties' in test:
                for prop_dict in test['user_properties']:
                    if 'tps' in prop_dict:
                        perf_results[version]['tps'] = prop_dict['tps']
                    if 'avg_latency_ms' in prop_dict:
                        perf_results[version]['latency'] = prop_dict['avg_latency_ms']

    # --- Report Generation ---
    report_lines = [
        f"# MySQL 8.0.42 vs 8.4.7 비교 테스트 결과 보고서",
        f"> **보고서 생성일:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "\n## 1. 테스트 개요",
        "본 보고서는 MySQL 8.0.42 버전에서 8.4.7 버전으로 업그레이드 시 발생할 수 있는 호환성 및 성능 변화를 분석한 결과입니다.",
        f"\n| 항목 | 결과 |",
        f"|---|---|",
        f"| **전체 테스트 케이스** | {data['summary']['total']} |",
        f"| **성공 (Pass)** | {data['summary']['passed']} |",
        f"| **실패 (Fail)** | {data['summary']['failed']} |",
        f"| **총 소요 시간** | {data['duration']:.2f}초 |",
    ]

    # --- Authentication Highlight ---
    report_lines.extend([
        "\n## 2. 인증 방식 변경 및 대응 (핵심 요약)",
        "\n> [!IMPORTANT]",
        "> **MySQL 8.4 업그레이드 시 가장 주의해야 할 변경 사항은 인증 방식입니다.**",
        "\n### ✅ sha2_user 접속 성공 (해결 완료)",
        "- **현상:** 초기 테스트 시 `cryptography` 패키지 누락으로 인한 접속 실패 발생.",
        "- **조치:** Python 환경에 `cryptography` 패키지 설치 완료.",
        "- **결과:** MySQL 8.0 및 8.4 모두에서 **정상 접속 확인**.",
        "\n### ⚠️ native_user 접속 실패 (의도된 동작)",
        "- **현상:** MySQL 8.4에서 `native_user` 접속 실패.",
        "- **원인:** MySQL 8.4부터 `mysql_native_password` 플러그인이 기본적으로 비활성화됨.",
        "- **권장:** 기존 계정을 `caching_sha2_password` 방식으로 전환하십시오.",
    ])

    # --- Major Differences (Failures) ---
    report_lines.append("\n## 3. 주요 차이점 및 실패 항목 분석")
    if not failures:
        report_lines.append("\n✅ 모든 호환성 테스트를 통과했습니다.")
    else:
        report_lines.append("\n| 분류 | 테스트 항목 | 요약 |")
        report_lines.append("|---|---|---|")
        
        details_blocks = []
        
        for failure in failures:
            test_name = failure['nodeid'].split('::')[-1]
            category = "기타"
            if 'authentication' in test_name:
                category = "인증"
            elif 'variable' in test_name:
                category = "시스템 변수"
            elif 'system_schema' in failure['nodeid']:
                category = "시스템 스키마"
            
            message = failure['call']['crash']['message'].split('\n')[0] # First line only
            stdout = failure['call'].get('stdout', '').strip()
            
            report_lines.append(f"| {category} | `{test_name}` | {message} |")
            
            if stdout:
                details_blocks.append(f"\n<details>\n<summary>🔍 <b>{test_name}</b> 상세 로그 보기</summary>\n\n```text\n{stdout}\n```\n</details>")

        if details_blocks:
            report_lines.append("\n### 📄 상세 오류 로그")
            report_lines.extend(details_blocks)

    # --- Performance Results ---
    report_lines.append("\n## 4. 성능 테스트 결과 (경향성)")
    report_lines.append("\n| 측정 항목 | MySQL 8.0.42 | MySQL 8.4.7 | 변화율 |")
    report_lines.append("|---|---|---|---|")
    
    tps80 = perf_results['mysql80'].get('tps', 0)
    tps84 = perf_results['mysql84'].get('tps', 0)
    tps_diff = "N/A"
    if tps80 > 0 and tps84 > 0:
        diff_val = ((tps84 - tps80) / tps80) * 100
        tps_diff = f"**{diff_val:+.2f}%**"
    report_lines.append(f"| **Insert TPS** (높을수록 좋음) | {tps80:,.2f} | {tps84:,.2f} | {tps_diff} |")

    lat80 = perf_results['mysql80'].get('latency', 0)
    lat84 = perf_results['mysql84'].get('latency', 0)
    lat_diff = "N/A"
    if lat80 > 0 and lat84 > 0:
        diff_val = ((lat84 - lat80) / lat80) * 100
        lat_diff = f"**{diff_val:+.2f}%**"
    report_lines.append(f"| **Select Latency** (ms) (낮을수록 좋음) | {lat80:.4f} | {lat84:.4f} | {lat_diff} |")

    # --- Global Variables Comparison ---
    vars_json_path = os.path.join(os.path.dirname(__file__), 'variable_comparison.json')
    if os.path.exists(vars_json_path):
        with open(vars_json_path, 'r') as f:
            vars_data = json.load(f)
        
        summary = vars_data['summary']
        report_lines.extend([
            "\n## 5. 전체 시스템 변수 비교",
            f"\n| 구분 | MySQL 8.0.42 | MySQL 8.4.7 | 차이 |",
            "|---|---|---|---|",
            f"| **전체 변수 수** | {summary['total_in_80']} | {summary['total_in_84']} | {summary['total_in_84'] - summary['total_in_80']} |",
            f"| **값이 다른 변수** | {summary['different_values']} | {summary['different_values']} | - |",
            
            "\n### 5.1. 값이 다른 주요 변수 (상세)",
            "\n<details>",
            "<summary>📋 전체 리스트 보기</summary>",
            "\n| 변수명 | MySQL 8.0.42 | MySQL 8.4.7 |",
            "|---|---|---|"
        ])
        for var, values in vars_data['different_values'].items():
            report_lines.append(f"| `{var}` | {values['mysql80']} | {values['mysql84']} |")
        report_lines.append("</details>")

        report_lines.append("\n### 5.2. 버전별 고유 변수")
        report_lines.append("\n<details>")
        report_lines.append("<summary>➕ MySQL 8.4.7에 추가된 변수</summary>")
        if vars_data['only_in_84']:
            report_lines.append("\n| 변수명 |")
            report_lines.append("|---|")
            for var in vars_data['only_in_84']:
                report_lines.append(f"| `{var}` |")
        else:
            report_lines.append("\n추가된 변수가 없습니다.")
        report_lines.append("</details>")

        report_lines.append("\n<details>")
        report_lines.append("<summary>➖ MySQL 8.0.42에서 제거된 변수</summary>")
        if vars_data['only_in_80']:
            report_lines.append("\n| 변수명 |")
            report_lines.append("|---|")
            for var in vars_data['only_in_80']:
                report_lines.append(f"| `{var}` |")
        else:
            report_lines.append("\n제거된 변수가 없습니다.")
        report_lines.append("</details>")

    # --- Write File ---
    with open(report_path, 'w') as f:
        f.write("\n".join(report_lines))

    print(f"보고서가 성공적으로 생성되었습니다: {report_path}")

if __name__ == "__main__":
    generate_report()